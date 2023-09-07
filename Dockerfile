FROM python:3.11.5 AS builder
COPY requirements.txt .

RUN pip install --user -r requirements.txt

LABEL authors="skegl"

ENTRYPOINT ["top", "-b"]