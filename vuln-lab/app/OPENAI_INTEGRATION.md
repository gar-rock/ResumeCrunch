# OpenAI Resume Scorer Integration

This document explains how to use the new OpenAI integration for intelligent resume scoring in ResumeCrunch.

## Overview

The OpenAI Resume Scorer provides AI-powered resume evaluation against job descriptions using OpenAI's GPT models. It analyzes resumes and provides:

- **Detailed scoring** across multiple dimensions (skills, experience, education)
- **Keyword matching** to identify coverage of job requirements  
- **AI-generated recommendations** to improve resume effectiveness

## Features

### Scoring Metrics
- **Overall Score** (0-100): Comprehensive match rating
- **Skills Match** (0-100): Technical and soft skills alignment
- **Experience Match** (0-100): Relevant work experience evaluation
- **Education Match** (0-100): Educational background relevance
- **Keywords Found**: Count of job description keywords present in resume

### AI Recommendations
Personalized suggestions for resume improvement, including:
- Missing keywords to add
- Experience gaps to address
- Skills to highlight more prominently
- Formatting and content suggestions

## Setup

### 1. Install Dependencies

The OpenAI library is already included in `requirements.txt`. If you need to install manually:

```bash
pip install openai==0.28.1
```

### 2. Configure OpenAI API Key

Set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or in your `.env` file:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 3. Get OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and set it as environment variable

## Usage

### Web Interface

The integration works automatically through the existing ResumeCrunch web interface:

1. **Upload Resume Package**: Go to `/resumes` and upload a ZIP file with your resumes
2. **Evaluate Resume**: Go to `/resume_check` and select a resume + job description
3. **View Results**: Check `/resume_scores` for AI-powered scoring and recommendations

### Programmatic Usage

#### Simple Usage

```python
from openai_resume_scorer import score_resume_with_openai

result = score_resume_with_openai(
    job_description="Your job description here...",
    resume_text="Your resume content here...",
    resume_filename="resume.pdf"
)

print(f"Overall Score: {result['scores']['resume.pdf']['overall_score']}")
print(f"Recommendations: {result['recommendations']}")
```

#### Advanced Usage

```python
from openai_resume_scorer import OpenAIResumeScorer

# Initialize with custom settings
scorer = OpenAIResumeScorer(
    api_key="your-key",  # Optional if env var is set
    model="gpt-3.5-turbo"  # or "gpt-4" for better results
)

# Score a single resume
result = scorer.score_resume(
    job_description="Job description...",
    resume_text="Resume content...",
    resume_filename="resume.pdf"
)

# Score multiple resumes
resumes = {
    "resume_v1.pdf": "Resume content 1...",
    "resume_v2.pdf": "Resume content 2..."
}

batch_result = scorer.batch_score_resumes(job_description, resumes)
```

## System Prompt

The AI coach uses this system prompt to ensure consistent, helpful evaluations:

```
You are a resume coach reviewing someone's resume for potential match against a job description from a job app. You will be given the job description and resume text, please provide a score based on the following areas, and output in json like this:

"scores": {
    "resume.pdf": {
        "overall_score": 75,
        "skills_match": 80,
        "experience_match": 70,
        "education_match": 75,
        "keywords_found": 4,
        "total_keywords": 8
    }
}

Also provide a paragraph with some recommendations.
```

## Error Handling & Fallbacks

The system includes robust error handling:

### API Failures
- **Network issues**: Graceful fallback to mock scoring
- **Invalid API key**: Clear error messages with setup instructions  
- **Rate limiting**: Automatic retry with exponential backoff
- **Model errors**: Fallback to simpler scoring algorithm

### Content Parsing
- **Invalid JSON**: Text parsing with regex fallback
- **Missing data**: Default values ensure consistent output
- **Large content**: Automatic truncation to stay within token limits

### Fallback Scoring
When OpenAI is unavailable, the system provides:
- Hash-based deterministic scoring
- Basic keyword matching
- Generic improvement recommendations

## Configuration Options

### Model Selection
```python
scorer = OpenAIResumeScorer(model="gpt-4")  # Higher quality, more expensive
scorer = OpenAIResumeScorer(model="gpt-3.5-turbo")  # Faster, cheaper
```

### Temperature Settings
The scorer uses `temperature=0.7` for balanced creativity and consistency.

### Token Limits
- Maximum input: ~4000 tokens per request
- Response limit: 1500 tokens
- Long content is automatically truncated

## Testing

### Test the Integration
```bash
cd /path/to/vuln-lab/app
python test_openai_scorer.py
```

### Example Usage
```bash
python example_usage.py
```

## Cost Considerations

### Token Usage
- **Input**: Job description + resume text (~500-2000 tokens)
- **Output**: Scores + recommendations (~200-500 tokens)
- **Cost per evaluation**: ~$0.002-$0.01 (depending on model)

### Optimization Tips
- Use `gpt-3.5-turbo` for development/testing
- Batch multiple resumes when possible
- Cache results for identical job descriptions
- Implement request rate limiting

## Troubleshooting

### Common Issues

**"OpenAI API key is required" Error**
```bash
export OPENAI_API_KEY="your-key-here"
# or add to .env file
```

**"Rate limit exceeded" Error**
- Wait and retry
- Check your OpenAI billing limits
- Consider upgrading your OpenAI plan

**"Invalid JSON" in Response**
- The system automatically handles this with text parsing
- Check OpenAI service status if persistent

**Poor Scoring Quality**
- Try using `gpt-4` model for better results
- Ensure job descriptions are detailed and specific
- Check that resume text extraction is working correctly

### Debug Mode

Enable logging for detailed debugging:
```python
import logging
logging.basicConfig(level=logging.INFO)

scorer = OpenAIResumeScorer()
# Now you'll see detailed API interaction logs
```

## Integration with ResumeCrunch

The OpenAI scorer is integrated into the main Flask application:

1. **Upload Processing**: ZIP files are extracted and text content prepared
2. **Background Processing**: OpenAI API calls run in separate threads
3. **Results Storage**: Scores and recommendations saved to metadata.json
4. **Web Display**: Results shown in the Resume Scores page with recommendations

### File Locations
- `openai_resume_scorer.py`: Main scorer implementation
- `app.py`: Flask integration (process_resume function)
- `templates/resume_scores.html`: Results display with recommendations section
- `requirements.txt`: Updated with OpenAI dependency

## Future Enhancements

### Planned Features
- **Document parsing**: PDF/DOC text extraction
- **Multi-language support**: Resume scoring in different languages  
- **Industry-specific prompts**: Tailored scoring for different job sectors
- **Comparison mode**: Side-by-side resume analysis
- **Export reports**: PDF/Word export of detailed analysis

### Customization Options
- **Custom prompts**: Industry or role-specific evaluation criteria
- **Scoring weights**: Adjustable importance of different factors
- **Integration APIs**: Webhooks for external integrations

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review OpenAI API documentation
3. Test with `test_openai_scorer.py` script
4. Check application logs for detailed error messages
