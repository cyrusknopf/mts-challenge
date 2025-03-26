# Build stage: use official Go 1.24.1 image
FROM golang:1.24.1 as go-build

WORKDIR /build

# Copy the entire project into the container
COPY . .

# Build the Go application; adjust the path to your main package as needed
RUN go build -o /app ./cmd

# Final stage: start with TensorFlow GPU image
FROM tensorflow/tensorflow:latest-gpu

# Install additional packages
RUN apt-get update && apt-get install -y build-essential net-tools

# Copy the compiled binary from the build stage
COPY --from=go-build /app /app

# Expose the application port
EXPOSE 8082

# Command to run the application
CMD ["/app", "-port", "8082"]
