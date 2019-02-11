FROM python:3.7.2-alpine3.8
LABEL maintainer="Robert Farrimond <rtjfarrimond@gmail.com>"

# Commented out whilst using volume to mount in dev.
# COPY app/ /usr/local/src/app

ENV PYTHONDONTWRITEBYTECODE=true

WORKDIR /usr/local/src/app

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r /usr/local/src/app/requirements.txt
