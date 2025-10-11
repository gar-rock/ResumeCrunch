from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, abort, make_response,jsonify
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import os
import datetime
import json
from uuid import uuid4
import traceback
from openai_resume_scorer import OpenAIResumeScorer, score_resume_with_openai
from text_extractors import extract_text_from_file, get_text_extractor
from flask_caching import Cache
import redis

# get redis password from ENV 
rpass = os.getenv("REDIS_PASSWORD")
rserver = os.getenv("REDIS_CONTAINER")

app = Flask(__name__)
app.secret_key = 's3cr3t_k3y'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'resumes'
app.config["DEBUG"] = True
app.config["CACHE_TYPE"] = "redis"
app.config["CACHE_REDIS_HOST"] = rserver
app.config["CACHE_REDIS_PORT"] = "6379"
app.config['CACHE_REDIS_DB'] = 0
app.config["CACHE_REDIS_URL"] = f"redis://:{rpass}@{rserver}:6379/0"
app.config["CACHE_REDIS_PASSWORD"] = rpass
app.config["CACHE_DEFAULT_TIMEOUT"] = 500

#perhaps make this a credentialed service


cache = Cache(app=app)
cache.init_app(app)
redis_client = redis.Redis(host=rserver, port=6379, db=0, username="default", password=rpass)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Metadata file path
METADATA_FILE = os.path.join(app.config['UPLOAD_FOLDER'], 'metadata.json')

def load_metadata():
    """Load metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_metadata(metadata):
    """Save metadata to JSON file"""
    try:
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata, f, indent=2)
    except IOError:
        pass  # Handle error silently for now

def add_file_metadata(filename, description, file_size, upload_time):
    """Add metadata for a single file"""
    metadata = load_metadata()
    metadata[filename] = {
        'description': description,
        'size': file_size,
        'upload_time': upload_time.isoformat(),
        'upload_timestamp': upload_time.timestamp(),
        'processed': False,  # Processing status
        'uploaded': True,   # Upload status
        'processing_status': 'pending',  # pending, processing, completed, failed
        'job_description': '',  # The job description used for evaluation
        'scores': {},  # Dictionary to hold scores for each resume file
        'processing_start_time': None,
        'processing_end_time': None
    }
    save_metadata(metadata)

@app.route("/cache/new",methods=["POST"])
def update():
    try:
        print(" new : cache request ",request.json)
        id = str(uuid4())
        cache.set(id,request.json)
        return jsonify({"status":"SUCCESS","_id":id}),200
    except Exception as e:
        print(Exception, e)
        print(traceback.format_exc())
        return jsonify({"status":"ERROR"}),500


@app.route("/cache/<id>")
def get(id):
    try:
        print("request for cache wih id  --> ",id)
        resp = cache.get(id)
        print("resp --> ",resp)
        if resp is None:
            return jsonify({"status":"KEY_NOT_IN_CACHE"}),404
        return resp,200
    except Exception as e:
        print(Exception, e)
        print(traceback.format_exc())
        return jsonify({"status":"ERROR"+e}),500

@app.route('/cached')
@cache.cached(timeout=60)  # Cache for 60 seconds
def cached_data():
    # Simulate some expensive operation
    print("cached called")
    import time
    time.sleep(2)
    return 'This data is cached for 60 seconds'

@app.route("/")
def home():
    # Get or create session ID from cookie
    session_id = request.cookies.get('session_id')
    
    if not session_id:
        # New session - create ID and initialize data
        session_id = str(uuid4())
        session_data = {
            'session_id': session_id,
            'created_at': datetime.datetime.now().isoformat(),
            'visit_count': 1,
            'last_visit': datetime.datetime.now().isoformat()
        }
        cache.set(f'session:{session_id}', session_data, timeout=3600)  # 1 hour timeout
    else:
        # Existing session - retrieve and update data
        session_data = cache.get(f'session:{session_id}')
        print()
        print(session_data ) 
        print()      
        if session_data is None:
            # Session expired or doesn't exist, create new one
            session_data = {
                'session_id': session_id,
                'created_at': datetime.datetime.now().isoformat(),
                'visit_count': 1,
                'last_visit': datetime.datetime.now().isoformat()
            }
        else:
            # Update existing session
            session_data['visit_count'] = session_data.get('visit_count', 0) + 1
            session_data['last_visit'] = datetime.datetime.now().isoformat()
        
        # Save updated session data back to cache
        cache.set(f'session:{session_id}', session_data, timeout=3600)
    
    # Create response and set cookie
    response = make_response(render_template("index.html"))
    response.set_cookie('session_id', session_id, max_age=3600)  # 1 hour cookie
    
    return response

@app.route("/help")
def help():
    return render_template("help.html")

@app.route("/resumes", methods=['GET', 'POST'])
def resumes():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'resume_package' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['resume_package']
        description = request.form.get('description', '')
        
        # If user does not select file, browser also submits an empty part without filename
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Check if file has a valid extension
        allowed_extensions = ['.zip', '.pdf', '.doc', '.docx', '.txt', '.rtf']
        if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
            flash('Please upload a ZIP file or resume file (PDF, DOC, DOCX, TXT, RTF)', 'error')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Check if it's a ZIP file or individual resume file
            if filename.lower().endswith('.zip'):
                # Handle ZIP file
                try:
                    with ZipFile(filepath, 'r') as zip_file:
                        file_list = zip_file.namelist()
                        # Basic validation - ensure it's a valid ZIP
                        if len(file_list) == 0:
                            flash('Uploaded ZIP file is empty', 'error')
                            os.remove(filepath)
                            return redirect(request.url)
                        
                        # Extract all files from the ZIP
                        zip_file.extractall(path="./resumes")
                        
                        # Save metadata for the uploaded files
                        file_stat = os.stat(filepath)
                        file_size = file_stat.st_size
                        upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                        for f in file_list:
                            if not f.lower().endswith('__macosx'):  # Skip __MACOSX entries
                                add_file_metadata(f, description, file_size, upload_time)

                        # Remove the zip file after extraction and metadata saving
                        os.remove(filepath)
                        
                        flash(f'Resume package "{filename}" uploaded and extracted successfully! Contains {len(file_list)} files.', 'success')
                        if description:
                            flash(f'Description: {description}', 'info')

                        if os.path.exists("./resumes/__MACOSX"):
                            os.remove("./resumes/__MACOSX")
                        
                except Exception as e:
                    flash('Invalid ZIP file uploaded', 'error')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
            else:
                # Handle individual resume file
                try:
                    # Validate file by attempting text extraction
                    extracted_text = extract_text_from_file(file_path=filepath, filename=filename)
                    
                    # Check if extraction was successful (not an error message)
                    if extracted_text.startswith('[') and 'not available' in extracted_text:
                        flash(f'Could not extract text from {filename}. File may be corrupted or unsupported format.', 'warning')
                    else:
                        flash(f'Resume file "{filename}" uploaded successfully!', 'success')
                    
                    # Save metadata for the individual file
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    add_file_metadata(filename, description, file_size, upload_time)
                    
                    if description:
                        flash(f'Description: {description}', 'info')
                        
                except Exception as e:
                    flash(f'Error processing resume file: {str(e)}', 'error')
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    return redirect(request.url)
            
            return redirect(url_for('resumes'))
    
    # GET request - show uploaded files
    uploaded_files = []
    metadata = load_metadata()
    
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if not filename.lower().endswith('__macosx') and filename != 'metadata.json' and filename != 'process.py':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Get description from metadata, fallback to empty string
                    file_metadata = metadata.get(filename, {})
                    description = file_metadata.get('description', '')
                    
                    # Use metadata upload time if available, otherwise use file system time
                    if 'upload_time' in file_metadata:
                        try:
                            upload_time = datetime.datetime.fromisoformat(file_metadata['upload_time'])
                        except:
                            pass  # Keep file system time
                    
                    # Handle file contents based on type
                    zip_contents = []
                    file_count = 0
                    file_type = "Unknown"
                    
                    if filename.lower().endswith('.zip'):
                        # ZIP file - get contents
                        try:
                            with ZipFile(filepath, 'r') as zip_file:
                                zip_contents = zip_file.namelist()
                                file_count = len(zip_contents)
                                file_type = "ZIP Archive"
                        except:
                            zip_contents = ["Error reading ZIP file"]
                            file_count = 0
                            file_type = "Corrupted ZIP"
                    else:
                        # Individual resume file
                        file_count = 1
                        zip_contents = [filename]
                        
                        # Determine file type
                        ext = filename.lower().split('.')[-1] if '.' in filename else ''
                        file_type_map = {
                            'pdf': 'PDF Document',
                            'doc': 'Word Document',
                            'docx': 'Word Document',
                            'txt': 'Text File',
                            'rtf': 'Rich Text Format'
                        }
                        file_type = file_type_map.get(ext, 'Resume File')
                    
                    uploaded_files.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'upload_time': upload_time,
                        'file_count': file_count,
                        'contents': zip_contents[:20],  # Limit to first 20 files for display
                        'description': description,
                        'processed': file_metadata.get('processed', False),
                        'file_type': file_type
                    })
                except Exception as e:
                    # Skip files that can't be read
                    continue
    
    # Sort by upload time, newest first
    uploaded_files.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return render_template("resumes.html", uploaded_files=uploaded_files)

@app.route("/resume_check")
def resume_check():
    # Get list of uploaded resume files to display in the form
    uploaded_files = []
    metadata = load_metadata()
    
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if not filename.lower().endswith('__macosx') and filename != 'metadata.json' and filename != 'process.py':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Get description from metadata, fallback to empty string
                    file_metadata = metadata.get(filename, {})
                    description = file_metadata.get('description', '')
                    
                    # Use metadata upload time if available, otherwise use file system time
                    if 'upload_time' in file_metadata:
                        try:
                            upload_time = datetime.datetime.fromisoformat(file_metadata['upload_time'])
                        except:
                            pass  # Keep file system time
                    
                    # Get file count based on type
                    file_count = 0
                    if filename.lower().endswith('.zip'):
                        try:
                            with ZipFile(filepath, 'r') as zip_file:
                                file_count = len(zip_file.namelist())
                        except:
                            file_count = 0
                    else:
                        file_count = 1  # Individual resume file
                    
                    uploaded_files.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'upload_time': upload_time,
                        'file_count': file_count,
                        'description': description,
                        'processed': file_metadata.get('processed', False)
                    })
                except Exception as e:
                    # Skip files that can't be read
                    continue
    
    # Sort by upload time, newest first
    uploaded_files.sort(key=lambda x: x['upload_time'], reverse=True)
    
    return render_template("resume_check.html", uploaded_files=uploaded_files)

@app.route("/evaluate_resume", methods=['POST'])
def evaluate_resume():
    resume_name = request.form.get('resume_name')
    print(resume_name)
    job_description = request.form.get('job_description')
    
    # Basic validation
    if not resume_name:
        flash('Please select a resume', 'error')
        return redirect(url_for('resume_check'))
    
    if not job_description or len(job_description.strip()) < 10:
        flash('Please provide a detailed job description', 'error')
        return redirect(url_for('resume_check'))
    
    # Verify the resume file exists
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_name)
    if not os.path.exists(resume_path):
        flash('Selected resume file not found', 'error')
        return redirect(url_for('resume_check'))
    
    # Update metadata to start processing
    metadata = load_metadata()
    if resume_name in metadata:
        metadata[resume_name]['processing_status'] = 'processing'
        metadata[resume_name]['job_description'] = job_description.strip()
        metadata[resume_name]['processing_start_time'] = datetime.datetime.now().isoformat()
        metadata[resume_name]['processed'] = True
        save_metadata(metadata)
        
        # Simulate processing by creating mock scores
        import threading
        import time
        
        def process_resume(resume_name, job_description):
            # Load fresh metadata
            metadata = load_metadata()
            if resume_name in metadata:
                # Extract files from ZIP and process with OpenAI
                resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_name)
                scores = {}
                recommendations = ""
                
                try:
                    # Process ZIP file or single file
                    
                    # Handle single file (not ZIP)
                    resume_text = extract_text_from_file(file_path=resume_path, filename=resume_name)
                    resume_filename = resume_name
                    
                    # Score resume using OpenAI if text was extracted
                    if resume_text and resume_filename:
                        print("Extracted resume text:")
                        print(resume_text[:500])  # Print first 500 characters
                        print() # Blank line for readability
                        print("Calling OpenAI API for scoring...")
                        print(f"Job Description: {job_description[:100]}...")  # Print first 100 chars
                        print(f"Resume Filename: {resume_filename}")
                        print(f"Resume Text (first 500 chars): {resume_text[:500]}...")
                        result = score_resume_with_openai(job_description, resume_text, resume_filename)
                        scores = result.get('scores', {})
                        recommendations = result.get('recommendations', '')
                        print("OpenAI scoring completed.")
                        print(f"Scores: {scores}")
                        print(f"Recommendations: {recommendations}")
                    else:
                        # No valid resume files found
                        scores = {'resume.pdf': {
                            'overall_score': 0,
                            'skills_match': 0,
                            'experience_match': 0,
                            'education_match': 0,
                            'keywords_found': 0,
                            'total_keywords': 1
                        }}
                        recommendations = "No valid resume files found in the uploaded package."
                        
                except Exception as e:
                    print(f"Error processing with OpenAI: {e}")
                    # Fallback to mock scoring if OpenAI fails
                    try:
                        if resume_name.lower().endswith('.zip'):
                            with ZipFile(resume_path, 'r') as zip_file:
                                file_list = zip_file.namelist()
                                for file_name in file_list:
                                    if file_name.lower().endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf')):
                                        # Mock scoring based on filename and job description for first valid file
                                        base_score = hash(file_name + job_description) % 100
                                        if base_score < 0:
                                            base_score = abs(base_score)
                                        
                                        scores = {file_name: {
                                            'overall_score': base_score,
                                            'skills_match': min(100, base_score + 10),
                                            'experience_match': max(0, base_score - 15),
                                            'education_match': min(100, base_score + 5),
                                            'keywords_found': max(1, (base_score // 20) + 1),
                                            'total_keywords': max(5, (base_score // 10) + 5)
                                        }}
                                        break  # Only process first valid file
                        else:
                            # Mock scoring for single file
                            base_score = hash(resume_name + job_description) % 100
                            if base_score < 0:
                                base_score = abs(base_score)
                            
                            scores = {resume_name: {
                                'overall_score': base_score,
                                'skills_match': min(100, base_score + 10),
                                'experience_match': max(0, base_score - 15),
                                'education_match': min(100, base_score + 5),
                                'keywords_found': max(1, (base_score // 20) + 1),
                                'total_keywords': max(5, (base_score // 10) + 5)
                            }}
                        recommendations = "AI scoring temporarily unavailable. Fallback scoring applied."
                    except:
                        # Final fallback if everything fails
                        scores = {'resume.pdf': {
                            'overall_score': 75,
                            'skills_match': 80,
                            'experience_match': 70,
                            'education_match': 75,
                            'keywords_found': 4,
                            'total_keywords': 8
                        }}
                        recommendations = "Unable to process resume at this time. Please try again later."
                
                metadata[resume_name]['scores'] = scores
                metadata[resume_name]['recommendations'] = recommendations
                metadata[resume_name]['processing_status'] = 'completed'
                metadata[resume_name]['processing_end_time'] = datetime.datetime.now().isoformat()
                save_metadata(metadata)
        
        # Start processing in background
        thread = threading.Thread(target=process_resume, args=(resume_name, job_description))
        thread.daemon = True
        thread.start()
        
        flash(f'Resume evaluation started for "{resume_name}". Check Resume Scores page for results.', 'success')
        return redirect(url_for('resume_scores'))
    else:
        flash('Resume metadata not found', 'error')
        return redirect(url_for('resume_check'))

@app.route("/resume_scores")
def resume_scores():
    """Show processing status and scores for resume evaluations"""
    metadata = load_metadata()
    processed_resumes = []
    
    # Filter resumes that have been processed or are being processed
    for filename, data in metadata.items():
        if data.get('processed', False) or data.get('processing_status') in ['processing', 'completed', 'failed']:
            # Calculate processing time if completed
            processing_time = None
            if data.get('processing_start_time') and data.get('processing_end_time'):
                try:
                    start_time = datetime.datetime.fromisoformat(data['processing_start_time'])
                    end_time = datetime.datetime.fromisoformat(data['processing_end_time'])
                    processing_time = (end_time - start_time).total_seconds()
                except:
                    processing_time = None
            
            # Get upload time
            upload_time = None
            if 'upload_time' in data:
                try:
                    upload_time = datetime.datetime.fromisoformat(data['upload_time'])
                except:
                    pass
            
            processed_resumes.append({
                'filename': filename,
                'status': data.get('processing_status', 'unknown'),
                'job_description': data.get('job_description', ''),
                'scores': data.get('scores', {}),
                'recommendations': data.get('recommendations', ''),
                'upload_time': upload_time,
                'processing_start_time': data.get('processing_start_time'),
                'processing_end_time': data.get('processing_end_time'),
                'processing_time': processing_time,
                'description': data.get('description', '')
            })
    
    # Sort by processing start time, newest first
    processed_resumes.sort(key=lambda x: x.get('processing_start_time') or '', reverse=True)
    
    return render_template("resume_scores.html", processed_resumes=processed_resumes)

@app.route("/delete_resume/<filename>", methods=['POST'])
def delete_resume(filename):
    """Delete a resume file"""
    metadata = load_metadata()
    
    # Secure the filename
    secure_name = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
    
    # Check if file exists on disk
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            # Remove from metadata
            if secure_name in metadata:
                del metadata[secure_name]
                save_metadata(metadata)
            flash(f'Resume "{filename}" deleted successfully!', 'success')
        except Exception as e:
            flash(f'Error deleting resume: {str(e)}', 'error')
    else:
        flash(f'Resume "{filename}" not found.', 'error')
    
    return redirect(url_for('resumes'))

@app.route("/download/<filename>")
def download_resume(filename):
    """Download a resume file"""
    metadata = load_metadata()
    
    # Check if the file exists in metadata (security check)
    if filename not in metadata:
        abort(404)
    
    # Secure the filename
    secure_name = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
    
    # Check if file exists on disk
    if not os.path.exists(file_path):
        abort(404)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_name, as_attachment=True)

# with ZipFile("exploit.zip",  mode="r") as archive:
#     archive.extractall(path="./")
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
