FROM python:3.8.3

ENV PYTHONUNBUFFERED=1

RUN MKDIR /backend

WORKDIR /backend

COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
