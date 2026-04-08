FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python packages DIRECTLY (bypassing the missing requirements.txt issue)
RUN pip install --no-cache-dir openenv-core pydantic openai fastapi uvicorn

# Copy everything from your local folder into the container
COPY . .

# Set PYTHONPATH so the server can find env.py
ENV PYTHONPATH="/app:$PYTHONPATH"

EXPOSE 8000

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]