#!/usr/bin/env python3
"""
Example usage of the OpenAI Resume Scorer

This script demonstrates how to use the OpenAI Resume Scorer interface
to evaluate resumes against job descriptions.
"""

import os
from openai_resume_scorer import OpenAIResumeScorer, score_resume_with_openai

def main():
    """Example usage of the OpenAI Resume Scorer."""
    
    # Set your OpenAI API key (you can also set the OPENAI_API_KEY environment variable)
    # api_key = "your-openai-api-key-here"
    
    # Sample job description from a job posting
    job_description = """
    Senior Python Developer - Remote
    
    We're seeking a skilled Senior Python Developer to join our dynamic team and help build 
    scalable web applications that serve millions of users.
    
    Key Requirements:
    - 5+ years of Python development experience
    - Strong experience with Django or Flask frameworks
    - Proficiency in SQL databases (PostgreSQL preferred)
    - Experience with RESTful API design and development
    - Knowledge of cloud platforms (AWS, GCP, or Azure)
    - Familiarity with containerization (Docker, Kubernetes)
    - Experience with version control (Git)
    - Strong problem-solving and debugging skills
    - Excellent communication and teamwork abilities
    
    Nice to Have:
    - Experience with React or Vue.js
    - Knowledge of CI/CD pipelines
    - Background in machine learning or data science
    - Open source contributions
    
    What You'll Do:
    - Design and develop robust backend systems
    - Build and maintain APIs for mobile and web applications
    - Collaborate with frontend developers and product managers
    - Optimize application performance and scalability
    - Mentor junior developers
    """
    
    # Sample resume content
    resume_text = """
    Sarah Johnson
    Senior Software Engineer
    
    EXPERIENCE
    
    Senior Software Engineer | TechStart Inc. | 2019 - Present
    • Lead development of microservices architecture using Python and Django
    • Built RESTful APIs serving 500K+ daily active users
    • Optimized database queries reducing response time by 40%
    • Mentored 3 junior developers and conducted code reviews
    • Deployed applications on AWS using Docker containers
    
    Software Engineer | DataCorp | 2017 - 2019
    • Developed data processing pipelines using Python and Flask
    • Worked with PostgreSQL and Redis for data storage
    • Implemented automated testing with 95% code coverage
    • Collaborated with cross-functional teams in Agile environment
    
    Junior Developer | StartupXYZ | 2015 - 2017
    • Built web applications using Python, HTML, CSS, JavaScript
    • Used Git for version control and collaboration
    • Gained experience with MySQL databases
    
    EDUCATION
    Bachelor of Science in Computer Science
    University of California, Berkeley | 2015
    
    TECHNICAL SKILLS
    • Languages: Python, JavaScript, SQL, HTML, CSS
    • Frameworks: Django, Flask, React (basic)
    • Databases: PostgreSQL, MySQL, Redis, MongoDB
    • Tools: Git, Docker, AWS, Jenkins, Pytest
    • Other: RESTful APIs, Microservices, Agile, Test-Driven Development
    """
    
    print("🚀 Resume Scoring Example")
    print("=" * 50)
    
    try:
        print("📊 Scoring resume against job description...")
        
        # Method 1: Using the convenience function
        result = score_resume_with_openai(
            job_description=job_description,
            resume_text=resume_text,
            resume_filename="sarah_johnson_resume.pdf"
        )
        
        print("\n✅ Scoring completed!")
        
        # Display results
        print("\n📈 SCORING RESULTS:")
        print("-" * 30)
        
        for filename, scores in result['scores'].items():
            print(f"\n📄 {filename}:")
            print(f"   🎯 Overall Score: {scores['overall_score']}/100")
            print(f"   🛠️  Skills Match: {scores['skills_match']}/100")
            print(f"   💼 Experience Match: {scores['experience_match']}/100")
            print(f"   🎓 Education Match: {scores['education_match']}/100")
            print(f"   🔑 Keywords Found: {scores['keywords_found']}/{scores['total_keywords']}")
        
        print(f"\n💡 AI COACH RECOMMENDATIONS:")
        print("-" * 40)
        print(result['recommendations'])
        
        # Method 2: Using the class directly for multiple resumes
        print("\n\n🔄 Alternative usage with multiple resumes:")
        print("-" * 50)
        
        scorer = OpenAIResumeScorer()  # Uses OPENAI_API_KEY env var
        
        # Multiple resumes example
        resumes = {
            "sarah_resume_v1.pdf": resume_text,
            "sarah_resume_v2.pdf": resume_text.replace("TechStart Inc.", "MegaCorp Solutions")
        }
        
        batch_result = scorer.batch_score_resumes(job_description, resumes)
        
        print("📊 Batch scoring results:")
        for filename, scores in batch_result['scores'].items():
            print(f"   📄 {filename}: {scores['overall_score']}/100")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("   1. Make sure you have set your OPENAI_API_KEY environment variable")
        print("   2. Ensure you have sufficient OpenAI API credits")
        print("   3. Check your internet connection")

if __name__ == "__main__":
    main()
