# Build stage: use official Go 1.24.1 image
FROM golang:1.24.1 AS go-build

ARG POSTGRES_PWD

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

RUN python -m pip install pandas numpy polygon

# Gets the variable passed by docker-compose
# ARG POSTGRES_PWD

# Allows this env var to be accessed by the running container
# ENV POSTGRES_PWD=${POSTGRES_PWD}

# Command to run the application
# CMD ["/app", "-port", "8082", "-ppwd", "$POSTGRES_PWD"]
# CMD ["/app", "-port", "8082"]

# Don't use JSON, instead raw shell to get env vars
# CMD ["/bin/sh", "-c", "/app -port 8082 -ppwd $POSTGRES_PWD"]
CMD /app -port 8082 -ppwd "$POSTGRES_PWD" -eval-dir /workspace/eval -apikey "$POLYGON_API_KEY"
