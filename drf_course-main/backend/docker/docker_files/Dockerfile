FROM --platform=linux/amd64 python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

# Install dependencies in one layer to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-traditional gettext && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir --upgrade pip httpie flask

# Copy the application
COPY . /code/

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt && \
    chmod +x /code/docker/entrypoints/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/code/docker/entrypoints/entrypoint.sh"]