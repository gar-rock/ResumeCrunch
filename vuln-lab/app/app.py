from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from zipfile import ZipFile
import os
import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'  # Change this in production
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
app.config['UPLOAD_FOLDER'] = 'resumes'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")

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
        if not file.filename.lower().endswith('.zip'):
            flash('Please upload a ZIP file only', 'error')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Validate and extract the ZIP file
            try:
                with ZipFile(filepath, 'r') as zip_file:
                    file_list = zip_file.namelist()
                    # Basic validation - ensure it's a valid ZIP
                    if len(file_list) == 0:
                        flash('Uploaded ZIP file is empty', 'error')
                        os.remove(filepath)
                        return redirect(request.url)
                    
                    # Extract all files from the ZIP
                    zip_file.extractall(path="./resumes/")
                    
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
            
            return redirect(url_for('resumes'))
    
    # GET request - show uploaded files
    uploaded_files = []
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if not filename.lower().endswith('__macosx'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Get ZIP file contents
                    zip_contents = []
                    file_count = 0
                    try:
                        with ZipFile(filepath, 'r') as zip_file:
                            zip_contents = zip_file.namelist()
                            file_count = len(zip_contents)
                    except:
                        zip_contents = ["Error reading ZIP file"]
                        file_count = 0
                    
                    uploaded_files.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'upload_time': upload_time,
                        'file_count': file_count,
                        'contents': zip_contents[:20]  # Limit to first 20 files for display
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
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if not filename.lower().endswith('__macosx'):
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                try:
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    upload_time = datetime.datetime.fromtimestamp(file_stat.st_mtime)
                    
                    # Get ZIP file contents count
                    file_count = 0
                    try:
                        with ZipFile(filepath, 'r') as zip_file:
                            file_count = len(zip_file.namelist())
                    except:
                        file_count = 0
                    
                    uploaded_files.append({
                        'filename': filename,
                        'size': file_size,
                        'size_mb': round(file_size / (1024 * 1024), 2),
                        'upload_time': upload_time,
                        'file_count': file_count
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
    
    # TODO: Here you would typically call an AI service or processing function
    # For now, we'll just flash a success message with the received data
    flash(f'Resume evaluation requested for "{resume_name}"', 'success')
    flash(f'Job description length: {len(job_description)} characters', 'info')
    
    # In a real implementation, you might:
    # 1. Extract and read resume files from the ZIP
    # 2. Send resume content and job description to an AI API
    # 3. Process the response and show results
    # 4. Store evaluation results in a database
    
    # For demonstration, redirect back to the form
    return redirect(url_for('resume_check'))

# with ZipFile("exploit.zip",  mode="r") as archive:
#     archive.extractall(path="./")
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
