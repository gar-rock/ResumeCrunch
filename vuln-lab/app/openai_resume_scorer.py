"""
OpenAI Resume Scoring Interface

This module provides an interface to OpenAI's completion API for scoring resumes
against job descriptions using a resume coach system prompt.
"""

import json
import logging
from typing import Dict, Any, Optional
import os

from openai import OpenAI
client = OpenAI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIResumeScorer:
    """
    A wrapper class for OpenAI completions API to score resumes against job descriptions.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5-nano"):
        """
        Initialize the OpenAI Resume Scorer.
        
        Args:
            api_key: OpenAI API key. If None, will try to get from environment variable.
            model: OpenAI model to use for completions.
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client
        client.api_key = self.api_key
        
        # System prompt for resume coaching
        self.system_prompt = """You are a resume coach reviewing someone's resume for potential match against a job description from a job app. You will be given the job description and resume text, please provide a score based on the following areas (from 0 to 100), and output in json like below. Also provide a paragraph with some recommendations.
            {
            "scores": {
                "overall_score": ##,
                "skills_match": ##,
                "experience_match": ##,
                "education_match": ##,
                "keywords_found": #,
                "total_keywords": #,
            },
            "recommendations": "Your resume shows good potential. Consider highlighting more specific achievements and quantifiable results to strengthen your application."
            }

"""

    def score_resume(self, job_description: str, resume_text: str, resume_filename: str = "resume.pdf") -> Dict[str, Any]:
        """
        Score a resume against a job description using OpenAI.
        
        Args:
            job_description: The job description text
            resume_text: The resume content text
            resume_filename: Name of the resume file (for JSON key)
            
        Returns:
            Dictionary containing scores and recommendations
        """
        try:
            # Construct user prompt
            user_prompt = f"""<job_description>
                            {job_description}
                            </job_description>

                            <resume_text>
                            {resume_text}
                            </resume_text>"""

            # Make API call to OpenAI

            response = client.responses.create(
            model="gpt-5-nano",
            input=[
                {
                "role": "developer",
                "content": [
                    {
                    "type": "input_text",
                    "text": "You are a resume coach reviewing someone's resume for potential match against a job description from a job app. You will be given the job description and resume text, please provide a score based on the following areas (from 0 to 100), and output in json like below. Also provide a paragraph with some recommendations.\n            {\n            \"scores\": {\n                \"overall_score\": ##,\n                \"skills_match\": ##,\n                \"experience_match\": ##,\n                \"education_match\": ##,\n                \"keywords_found\": #,\n                \"total_keywords\": #,\n            },\n            \"recommendations\": \"Your resume shows good potential. Consider highlighting more specific achievements and quantifiable results to strengthen your application.\"\n            }"
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "type": "input_text",
                    "text": f"""<job_description>\n{job_description}\n</job_description>\n\n<resume_text>\n{resume_text}\n</resume_text>"""
                    }
                ]
                }
            ],
            text={
                "format": {
                "type": "text"
                },
                "verbosity": "medium"
            },
            reasoning={
                "effort": "medium",
                "summary": "auto"
            },
            tools=[],
            store=True,
            include=[
                "reasoning.encrypted_content",
                "web_search_call.action.sources"
            ]
            )
            print(response.output_text)
            print()

            # Extract the response content
            response_content = response.output_text
            logger.info(f"OpenAI response received for resume scoring")

            print("Raw OpenAI response content:")
            print(response_content)
            
            # Parse the response to extract JSON and recommendations
            return self._parse_response(response_content, resume_filename)

        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return self._fallback_response(resume_filename)
        except Exception as e:
            logger.error(f"Unexpected error during resume scoring: {str(e)}")
            return self._fallback_response(resume_filename)
    
    def _parse_response(self, response_content: str, resume_filename: str) -> Dict[str, Any]:
        """
        Parse the OpenAI response to extract scores and recommendations.
        
        Args:
            response_content: Raw response from OpenAI
            resume_filename: Name of the resume file
            
        Returns:
            Parsed response with scores and recommendations
        """
        try:
            # Try to find and extract JSON from the response
            import re
            
            # Look for JSON block in the response
            
            try:
                parsed_json = json.loads(response_content)
                print(parsed_json)
                scores = parsed_json.get('scores', {})
                recommendations = parsed_json.get('recommendations', '')
                print(recommendations)
                print(scores)
                
                # Ensure scores are nested under resume filename for consistency
                if resume_filename not in scores:
                    scores = {resume_filename: scores}
                
                return {
                    'scores': scores,
                    'recommendations': recommendations
                }
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from response: {str(e)}")
                # Fall through to fallback parsing
            
            # Fallback: try to extract scores from text
            scores = self._extract_scores_from_text(response_content, resume_filename)
            
            # Extract recommendations from the response content
            recommendations_text = response_content.strip()
            
            # Try to find recommendations in the text
            if 'recommendations' in response_content.lower():
                # Split by common delimiters and look for recommendations
                lines = response_content.split('\n')
                rec_lines = []
                found_rec = False
                for line in lines:
                    if 'recommendations' in line.lower() or found_rec:
                        found_rec = True
                        if not line.strip().startswith('"recommendations"') and line.strip():
                            rec_lines.append(line.strip())
                if rec_lines:
                    recommendations_text = ' '.join(rec_lines)
            
            if not recommendations_text or len(recommendations_text) < 10:
                recommendations_text = "Your resume shows good potential. Consider highlighting more specific achievements and quantifiable results to strengthen your application."
            
            return {
                'scores': scores,
                'recommendations': recommendations_text
            }
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            return self._fallback_response(resume_filename)
    
    def _extract_scores_from_text(self, text: str, resume_filename: str) -> Dict[str, Dict[str, int]]:
        """
        Extract scores from text when JSON parsing fails.
        
        Args:
            text: Text to extract scores from
            resume_filename: Name of the resume file
            
        Returns:
            Dictionary with extracted scores
        """
        # Default scores
        scores = {
            resume_filename: {
                'overall_score': 75,
                'skills_match': 80,
                'experience_match': 70,
                'education_match': 75,
                'keywords_found': 4,
                'total_keywords': 8
            }
        }
        
        # Try to extract numbers from text
        import re
        numbers = re.findall(r'\d+', text)
        
        if len(numbers) >= 6:
            try:
                scores[resume_filename] = {
                    'overall_score': min(100, max(0, int(numbers[0]))),
                    'skills_match': min(100, max(0, int(numbers[1]))),
                    'experience_match': min(100, max(0, int(numbers[2]))),
                    'education_match': min(100, max(0, int(numbers[3]))),
                    'keywords_found': max(1, int(numbers[4])),
                    'total_keywords': max(5, int(numbers[5]))
                }
            except (ValueError, IndexError):
                pass  # Use default scores
        
        return scores
    
    def _fallback_response(self, resume_filename: str) -> Dict[str, Any]:
        """
        Provide a fallback response when OpenAI API fails.
        
        Args:
            resume_filename: Name of the resume file
            
        Returns:
            Fallback response with default scores
        """
        return {
            'scores': {
                resume_filename: {
                    'overall_score': 75,
                    'skills_match': 80,
                    'experience_match': 70,
                    'education_match': 75,
                    'keywords_found': 4,
                    'total_keywords': 8
                }
            },
            'recommendations': "Unable to generate AI-powered recommendations at this time. Please ensure your resume includes relevant keywords from the job description, quantifiable achievements, and clear skill demonstrations."
        }

    def batch_score_resumes(self, job_description: str, resumes: Dict[str, str]) -> Dict[str, Any]:
        """
        Score multiple resumes against a job description.
        
        Args:
            job_description: The job description text
            resumes: Dictionary mapping resume filenames to their content
            
        Returns:
            Dictionary containing all scores and recommendations
        """
        all_scores = {}
        all_recommendations = []
        
        for filename, resume_text in resumes.items():
            result = self.score_resume(job_description, resume_text, filename)
            all_scores.update(result['scores'])
            all_recommendations.append(f"**{filename}:** {result['recommendations']}")
        
        return {
            'scores': all_scores,
            'recommendations': '\n\n'.join(all_recommendations)
        }

# Convenience function for easy usage
def score_resume_with_openai(job_description: str, resume_text: str, resume_filename: str = "resume.pdf", api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to score a resume using OpenAI.
    
    Args:
        job_description: The job description text
        resume_text: The resume content text
        resume_filename: Name of the resume file
        api_key: OpenAI API key (optional)
        
    Returns:
        Dictionary containing scores and recommendations
    """
    scorer = OpenAIResumeScorer(api_key=api_key)
    return scorer.score_resume(job_description, resume_text, resume_filename)
