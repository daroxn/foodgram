FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txx .
RUN pip install --no-cache-dir -r requirements.txt

COPY foodgram_project/ ./

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram_project.wsgi:application"]
