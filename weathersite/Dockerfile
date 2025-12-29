FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy the whole project
COPY . .

# Collect static files (from apps and project) into STATIC_ROOT
# Make sure STATIC_ROOT is set in settings.py
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
