# Use an official Python image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies required for virtual environments
RUN apt-get update && apt-get install -y python3-venv && rm -rf /var/lib/apt/lists/*

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy dependency list and install packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Explicitly set PYTHONPATH so Python recognizes `/app` as the root
ENV PYTHONPATH="/app"

# Expose FastAPI's port
EXPOSE 8000
WORKDIR /
# Run Uvicorn, explicitly setting the module path
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

