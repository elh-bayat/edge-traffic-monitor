# Start from official Python 3.12 slim image (slim = smaller size, no extras)
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements FIRST (separate layer — cached unless requirements change)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Document which port the app uses
EXPOSE 8000

# Command to run when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
