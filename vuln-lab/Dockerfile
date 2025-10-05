FROM python:3.13-slim

WORKDIR /app


# Install Python dependencies
RUN pip install flask

# Copy application files
COPY app/ /app/

CMD ["python", "app.py"]
