FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire workspace code
COPY . .

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Start the FastAPI sales assistant server
CMD ["uvicorn", "deepAgentCourse.5_sales_assistant_extra:app", "--host", "0.0.0.0", "--port", "7860"]
