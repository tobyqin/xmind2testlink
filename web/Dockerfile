FROM joshuarli/alpine-python3-pip:latest
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip3 install -r requirements.txt
CMD python3 application.py