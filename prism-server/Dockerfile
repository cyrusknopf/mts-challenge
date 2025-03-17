# Build stage: use official Go 1.24.1 image
FROM golang:1.24.1 as go-build
WORKDIR /build

# Final stage: start with TensorFlow GPU image
FROM tensorflow/tensorflow:latest-gpu

# Install additional packages
RUN apt-get update && apt-get install -y build-essential net-tools

# Copy the Go installation and your binary from the build stage
COPY --from=go-build /usr/local/go /usr/local/go

# Set up Go environment variables
ENV GOPATH=/go
ENV PATH=$PATH:/usr/local/go/bin:$GOPATH/bin

# Set working directory
WORKDIR /workspace/src
RUN go build cmd

EXPOSE 8082
CMD ["cmd/cmd", "-port", "8082"]
