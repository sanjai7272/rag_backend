# Base Image 

FROM python:3.10-slim 

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn","app.main:app","--host", "0.0.0.0","--port","8000"]

EXPOSE 8000
