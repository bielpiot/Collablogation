FROM python:3.8.3

ENV PYTHONUNBUFFERED=1

RUN MKDIR /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY . /app/