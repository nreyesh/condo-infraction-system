# 1. Use a slim Python image
FROM python:3.11-slim

# 2. Set the working directory INSIDE the container
WORKDIR /app

# 3. Copy the requirements first (Better for caching)
COPY requirements.txt .

# 4. Install the libraries
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your backend code (main.py, migrations, etc.)
COPY . .

# 6. Expose the port FastAPI runs on
EXPOSE 8080

# 7. Start the server
CMD ["uvicorn", "main.py:app", "--host", "0.0.0.0", "--port", "8080"]