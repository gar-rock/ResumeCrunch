FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies

# Copy application files
COPY app/ /app/

RUN pip install -r /app/requirements.txt

ENV OPENAI_API_KEY="sk-svcacct--dfgdfgdfg"


CMD ["python3", "app.py"]
