FROM python:3.7.2-alpine3.8

# Commented out whilst using volume to mount in dev.
# COPY app/ /usr/local/src/app

WORKDIR /usr/local/src/app

COPY requirements.txt .

RUN pip install -r /usr/local/src/app/requirements.txt
