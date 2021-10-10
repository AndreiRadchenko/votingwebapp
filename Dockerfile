# This is a sample Dockerfile you can modify to deploy your own app based on face_recognition

FROM python:3.8-slim

WORKDIR /data
VOLUME /data
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

#RUN apt-get -y update
#RUN apt-get install -y --fix-missing \
    #build-essential \
    #cmake \
    #gfortran \
    #git \
    #wget \
    #curl \
    #&& apt-get clean && rm -rf /tmp/* /var/tmp/*

EXPOSE 5000

# Install Flask
RUN cd ~ && \
    pip3 install flask

COPY . /root/flaskr
RUN cd /root/flaskr && \
    pip3 install -r requirements.txt


CMD cd /root/flaskr/flaskr && \
    python3 vwa.py
