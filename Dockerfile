# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Ensure Python outputs everything immediately to stdout/stderr
ENV PYTHONUNBUFFERED=1

# Copy application code into container
COPY config.py \
     gemini_client.py \
     email_sender.py \
     research_sources.py \
     generate_ideas.py \
     scheduler.py \
     test_run.py \
     ./

# Create directories for outputs and persistence
RUN mkdir -p /app/emails_sent

# Expose default HTTP port for health checks
EXPOSE 8080

# Execute the stateful scheduler daemon
CMD ["python", "scheduler.py"]
