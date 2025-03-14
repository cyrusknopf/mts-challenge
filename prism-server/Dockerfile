# Use the official TensorFlow GPU image (Ubuntu-based)
FROM tensorflow/tensorflow:latest-gpu

# Install Golang and build essentials
RUN apt-get update && apt-get install -y golang-go build-essential

# Optional: Set up Go environment variables
ENV GOPATH=/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Set working directory
WORKDIR /workspace

EXPOSE 8080
CMD [ "bash" ]
