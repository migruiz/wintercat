FROM balenalib/raspberry-pi-alpine-python:latest

RUN mkdir /App/
COPY App/requirements.txt  /App/requirements.txt

RUN cd /App && pip install -r requirements.txt

COPY App /App


CMD ["python", "-u","/App/app.py"] 