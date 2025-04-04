FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the server will run on
EXPOSE 8001

# Set the default command to run the server
CMD ["python", "server.py" "-p" "8001"]
CMD ["python", "server.py" "-p" "8002"]
CMD ["python", "server.py" "-p" "8003"]
CMD ["python", "server.py" "-p" "8004"]

