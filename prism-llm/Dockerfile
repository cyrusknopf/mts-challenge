RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports the server will run on
EXPOSE 8001
EXPOSE 8002
EXPOSE 8003
EXPOSE 8004

# Copy the entrypoint script
COPY entrypoint.sh /app/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint to the script
ENTRYPOINT ["/app/entrypoint.sh"]
