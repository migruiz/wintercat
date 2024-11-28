FROM python:3.14.0a2-alpine3.20 

RUN mkdir /App/
COPY App/requirements.txt  /App/requirements.txt

RUN cd /App && pip install -r requirements.txt

COPY App /App


CMD ["python", "/App/app.py"] 