# Alpine set up
# FROM python:2.7.15-alpine3.7

# RUN apk update
# RUN apk add ffmpeg
# RUN apk add gcc
# RUN apk add linux-headers
# RUN apk add musl-dev

FROM python:2.7
LABEL maintainer="Robert Farrimond <rtjfarrimond@gmail.com>"

RUN apt-get update
RUN apt-get install -y ffmpeg

# Comment out whilst mounting in compose for development.
# COPY app/ /usr/local/src/app
COPY lib/kapre /usr/local/lib/kapre

WORKDIR /usr/local/src/app
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache -r requirements.txt

WORKDIR /usr/local/lib/kapre
RUN python setup.py install

WORKDIR /usr/local/src/app
ENV PYTHONDONTWRITEBYTECODE=true

# Set up keras
ENV KERAS_BACKEND=theano
RUN echo 'import keras' | python
RUN sed -ie 's/tf/th/g' ~/.keras/keras.json
RUN sed -ie 's/tensorflow/theano/g' ~/.keras/keras.json

CMD ["python", "app.py"]
