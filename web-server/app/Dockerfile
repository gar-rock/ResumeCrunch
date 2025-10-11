FROM python:3.13-slim

# Redis password variable
ARG REDIS_PASSWORD="hCQr7gvbyRRN79Ugvc9Lssq6"
ARG REDIS_CONTAINER="resumecrunch-redis"
ARG OPENAI_API_KEY="sk-yourkeyhere"

WORKDIR /app

# Install Python dependencies

# Copy application files
COPY . /app/

RUN pip install -r /app/requirements.txt

ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV REDIS_PASSWORD=${REDIS_PASSWORD}
ENV REDIS_CONTAINER=${REDIS_CONTAINER}

CMD ["python3", "app.py"]
