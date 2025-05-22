# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Alternatively, for development: RUN pip install -r requirements.txt

# Define the environment variable for MongoDB (this can be overridden by docker-compose)
ENV MONGO_URL=mongodb://mongo:27017/sophia

# Specify the command to run when the container starts
CMD ["python", "index.py"]
#CMD ["python", "milvus_test.py"]
