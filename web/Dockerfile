FROM frolvlad/alpine-python3:latest

RUN pip3 install -r requirements.txt

RUN mkdir /app
WORKDIR /app
ADD . /app

CMD python3 application.py