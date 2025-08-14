# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install Poetry
RUN pip install poetry

# 5. Copy only necessary files for dependency installation
COPY poetry.toml pyproject.toml poetry.lock* ./

# 6. Install project dependencies
#    --no-root: Don't install the project itself, only dependencies
#    --without dev: Don't install development dependencies
RUN poetry install --no-root --without dev

# 7. Copy the rest of the application source code
COPY . .

# 8. Make the startup script executable
RUN chmod +x /app/scripts/start.sh

# 9. Set the startup script as the entrypoint
CMD ["/app/scripts/start.sh"]
