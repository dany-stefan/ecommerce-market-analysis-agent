FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src ./src
COPY config ./config
COPY main.py .
COPY question_3/api.py .
RUN mkdir -p reports logs
EXPOSE 8000
CMD ["python", "api.py"]
