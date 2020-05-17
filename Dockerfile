FROM python:3.6
WORKDIR /ai
VOLUME /data
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .