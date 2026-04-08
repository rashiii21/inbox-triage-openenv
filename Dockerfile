<<<<<<< HEAD
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

=======
FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 7860

>>>>>>> f94e4834fdacd0d3485fb6cabbcdd0cb08d8f285
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]