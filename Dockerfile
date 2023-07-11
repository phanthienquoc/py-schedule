# Build stage
FROM python:3.9-slim-buster AS build

WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Build the application using environment variables from .env file
ARG ENV_FILE_PATH=./.env
ENV $(cat $ENV_FILE_PATH | grep -v '^#' | xargs)

# Production stage
FROM python:3.9-slim-buster

WORKDIR /app

# Copy the built application from the build stage
COPY --from=build /app .

# Expose port 80
EXPOSE 80

# Set the default command to run the application
CMD ["python", "main.py"]