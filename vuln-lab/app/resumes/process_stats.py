#!/usr/bin/env python3
"""
Resume Processing Statistics
Analyzes and displays statistics from resume processing metadata.
"""

import json
import os
import sys
from datetime import datetime
from collections import defaultdict


METADATA_FILE = 'metadata.json'


def load_metadata():
    """Load metadata from JSON file"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading metadata: {e}")
            return {}
    else:
        print(f"Metadata file not found: {METADATA_FILE}")
        return {}


def calculate_processing_time(start_time, end_time):
    """Calculate processing time in seconds"""
    if not start_time or not end_time:
        return None
    try:
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        return (end - start).total_seconds()
    except:
        return None


def get_overall_statistics(metadata):
    """Calculate overall statistics from metadata"""
    stats = {
        'total_resumes': 0,
        'uploaded_resumes': 0,
        'processed_resumes': 0,
        'pending_resumes': 0,
        'failed_resumes': 0,
        'total_size_bytes': 0,
        'processing_times': [],
        'scores': {
            'overall_scores': [],
            'skills_match': [],
            'experience_match': [],
            'education_match': [],
        }
    }
    
    for filename, data in metadata.items():
        # Skip metadata entries that are clearly system files
        if filename.startswith('__MACOSX') or filename.startswith('.'):
            continue
            
        stats['total_resumes'] += 1
        
        # Count by status
        if data.get('uploaded', False):
            stats['uploaded_resumes'] += 1
        if data.get('processed', False):
            stats['processed_resumes'] += 1
        
        status = data.get('processing_status', 'unknown')
        if status == 'pending':
            stats['pending_resumes'] += 1
        elif status == 'failed':
            stats['failed_resumes'] += 1
        
        # Accumulate file sizes
        stats['total_size_bytes'] += data.get('size', 0)
        
        # Processing times
        proc_time = calculate_processing_time(
            data.get('processing_start_time'),
            data.get('processing_end_time')
        )
        if proc_time is not None:
            stats['processing_times'].append(proc_time)
        
        # Extract scores
        scores_data = data.get('scores', {})
        for resume_name, resume_scores in scores_data.items():
            if isinstance(resume_scores, dict):
                if 'overall_score' in resume_scores:
                    stats['scores']['overall_scores'].append(resume_scores['overall_score'])
                if 'skills_match' in resume_scores:
                    stats['scores']['skills_match'].append(resume_scores['skills_match'])
                if 'experience_match' in resume_scores:
                    stats['scores']['experience_match'].append(resume_scores['experience_match'])
                if 'education_match' in resume_scores:
                    stats['scores']['education_match'].append(resume_scores['education_match'])
    
    return stats


def format_bytes(bytes_value):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} TB"


def format_time(seconds):
    """Format seconds to human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} hours"


def calculate_average(values):
    """Calculate average of a list of values"""
    if not values:
        return 0
    return sum(values) / len(values)


def print_statistics(stats):
    """Print formatted statistics"""
    print("\n" + "="*60)
    print("RESUME PROCESSING STATISTICS")
    print("="*60)
    
    # File Statistics
    print("\n📊 FILE STATISTICS")
    print("-" * 60)
    print(f"  Total Resumes:        {stats['total_resumes']}")
    print(f"  Uploaded:             {stats['uploaded_resumes']}")
    print(f"  Processed:            {stats['processed_resumes']}")
    print(f"  Pending:              {stats['pending_resumes']}")
    print(f"  Failed:               {stats['failed_resumes']}")
    print(f"  Total Size:           {format_bytes(stats['total_size_bytes'])}")
    
    # Processing Time Statistics
    print("\n⏱️  PROCESSING TIME STATISTICS")
    print("-" * 60)
    if stats['processing_times']:
        avg_time = calculate_average(stats['processing_times'])
        min_time = min(stats['processing_times'])
        max_time = max(stats['processing_times'])
        total_time = sum(stats['processing_times'])
        
        print(f"  Resumes Processed:    {len(stats['processing_times'])}")
        print(f"  Average Time:         {format_time(avg_time)}")
        print(f"  Minimum Time:         {format_time(min_time)}")
        print(f"  Maximum Time:         {format_time(max_time)}")
        print(f"  Total Time:           {format_time(total_time)}")
    else:
        print("  No processing time data available")
    
    # Score Statistics
    print("\n🎯 SCORING STATISTICS")
    print("-" * 60)
    
    score_categories = [
        ('Overall Score', stats['scores']['overall_scores']),
        ('Skills Match', stats['scores']['skills_match']),
        ('Experience Match', stats['scores']['experience_match']),
        ('Education Match', stats['scores']['education_match']),
    ]
    
    for category_name, scores in score_categories:
        if scores:
            avg_score = calculate_average(scores)
            min_score = min(scores)
            max_score = max(scores)
            print(f"\n  {category_name}:")
            print(f"    Average:            {avg_score:.1f}")
            print(f"    Minimum:            {min_score}")
            print(f"    Maximum:            {max_score}")
            print(f"    Sample Size:        {len(scores)}")
        else:
            print(f"\n  {category_name}:")
            print(f"    No data available")
    
    print("\n" + "="*60 + "\n")


def print_resume_details(metadata):
    """Print details for each resume"""
    print("\n" + "="*60)
    print("RESUME DETAILS")
    print("="*60)
    
    for filename, data in metadata.items():
        # Skip system files
        if filename.startswith('__MACOSX') or filename.startswith('.'):
            continue
        
        print(f"\n📄 {filename}")
        print("-" * 60)
        
        # Basic info
        print(f"  Description:          {data.get('description', 'N/A')}")
        print(f"  Size:                 {format_bytes(data.get('size', 0))}")
        
        # Upload time
        upload_time = data.get('upload_time', 'N/A')
        if upload_time != 'N/A':
            try:
                dt = datetime.fromisoformat(upload_time)
                print(f"  Upload Time:          {dt.strftime('%Y-%m-%d %H:%M:%S')}")
            except:
                print(f"  Upload Time:          {upload_time}")
        
        # Status
        print(f"  Status:               {data.get('processing_status', 'unknown')}")
        print(f"  Processed:            {'Yes' if data.get('processed', False) else 'No'}")
        
        # Processing time
        proc_time = calculate_processing_time(
            data.get('processing_start_time'),
            data.get('processing_end_time')
        )
        if proc_time is not None:
            print(f"  Processing Time:      {format_time(proc_time)}")
        
        # Scores
        scores_data = data.get('scores', {})
        if scores_data:
            print("  Scores:")
            for resume_name, resume_scores in scores_data.items():
                if isinstance(resume_scores, dict):
                    print(f"    Overall Score:      {resume_scores.get('overall_score', 'N/A')}")
                    print(f"    Skills Match:       {resume_scores.get('skills_match', 'N/A')}")
                    print(f"    Experience Match:   {resume_scores.get('experience_match', 'N/A')}")
                    print(f"    Education Match:    {resume_scores.get('education_match', 'N/A')}")
                    print(f"    Keywords Found:     {resume_scores.get('keywords_found', 'N/A')}/{resume_scores.get('total_keywords', 'N/A')}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main function"""
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Load metadata
    metadata = load_metadata()
    
    if not metadata:
        print("No metadata found or error loading metadata.")
        sys.exit(1)
    
    # Calculate and print statistics
    stats = get_overall_statistics(metadata)
    print_statistics(stats)
    
    # Ask if user wants to see details
    if len(sys.argv) > 1 and sys.argv[1] in ['-d', '--details', 'details']:
        print_resume_details(metadata)
    else:
        print("💡 Tip: Run with --details flag to see individual resume details")
        print("   Example: python process_stats.py --details\n")


if __name__ == '__main__':
    main()
