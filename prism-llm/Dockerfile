FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install -r --no-cache-dir requirements.txt

# Expose the port the server will run on
EXPOSE 8001

# Set the default command to run the server
CMD ["python", "server.py"]

