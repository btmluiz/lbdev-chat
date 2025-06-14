FROM python:3.13.5

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY ./ /app/