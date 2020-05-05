FROM frolvlad/alpine-python3:latest

RUN mkdir /app
WORKDIR /app
ADD . /app

RUN pip3 install -r requirements.txt
CMD python3 application.py