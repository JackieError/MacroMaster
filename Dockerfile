FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV MARKET_NOTE_HOST=0.0.0.0 MARKET_NOTE_PORT=10000
EXPOSE 10000
CMD ["python3", "server.py"]
