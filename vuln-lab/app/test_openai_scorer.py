#!/usr/bin/env python3
"""
Test script for the OpenAI Resume Scorer

This script tests the OpenAI resume scoring functionality.
Make sure to set your OPENAI_API_KEY environment variable before running.
"""

import os
import sys
from openai_resume_scorer import OpenAIResumeScorer, score_resume_with_openai

def test_basic_scoring():
    """Test basic resume scoring functionality."""
    print("🧪 Testing OpenAI Resume Scorer...")
    
    # Check if API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  OPENAI_API_KEY environment variable not set.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        return False
    
    # Sample job description
    job_description = """
    Software Engineer - Full Stack
    
    We are looking for a talented Full Stack Software Engineer to join our growing team. 
    
    Requirements:
    - 3+ years of experience in software development
    - Proficiency in Python, JavaScript, and React
    - Experience with databases (PostgreSQL, MongoDB)
    - Knowledge of cloud platforms (AWS, Azure)
    - Strong problem-solving skills
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Develop and maintain web applications
    - Collaborate with cross-functional teams
    - Write clean, maintainable code
    - Participate in code reviews
    """
    
    # Sample resume text
    resume_text = """
    John Doe
    Software Developer
    
    Experience:
    - 4 years at Tech Corp as Software Developer
    - Built web applications using Python and Django
    - Worked with PostgreSQL databases
    - Some experience with JavaScript and React
    - Deployed applications on AWS
    
    Education:
    - Bachelor of Science in Computer Science
    - University of Technology
    
    Skills:
    - Python, JavaScript, HTML, CSS
    - Django, Flask, React
    - PostgreSQL, MySQL
    - AWS, Docker
    - Git, Agile methodologies
    """
    
    try:
        print("🚀 Calling OpenAI API...")
        result = score_resume_with_openai(
            job_description=job_description,
            resume_text=resume_text,
            resume_filename="john_doe_resume.pdf"
        )
        
        print("✅ API call successful!")
        print("\n📊 Scores:")
        for filename, scores in result['scores'].items():
            print(f"   {filename}:")
            print(f"     Overall Score: {scores['overall_score']}/100")
            print(f"     Skills Match: {scores['skills_match']}/100")
            print(f"     Experience Match: {scores['experience_match']}/100")
            print(f"     Education Match: {scores['education_match']}/100")
            print(f"     Keywords Found: {scores['keywords_found']}/{scores['total_keywords']}")
        
        print("\n💡 Recommendations:")
        print(result['recommendations'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_fallback_behavior():
    """Test fallback behavior when API is not available."""
    print("\n🧪 Testing fallback behavior...")
    
    try:
        # Create scorer with invalid API key to test fallback
        scorer = OpenAIResumeScorer(api_key="invalid-key")
        result = scorer.score_resume(
            job_description="Test job description",
            resume_text="Test resume text",
            resume_filename="test.pdf"
        )
        
        print("✅ Fallback behavior working!")
        print(f"   Fallback scores: {result['scores']}")
        print(f"   Fallback recommendations: {result['recommendations'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing fallback: {e}")
        return False

def main():
    """Run all tests."""
    print("🔬 OpenAI Resume Scorer Test Suite")
    print("=" * 50)
    
    test_basic_scoring()
    test_fallback_behavior()
    
    print("\n✨ Test suite completed!")

if __name__ == "__main__":
    main()
