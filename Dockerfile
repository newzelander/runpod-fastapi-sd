FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# Copy source files
COPY . .

CMD ["python", "handler.py"]
