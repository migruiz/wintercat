FROM python:3.14.0a2-alpine3.20 
ADD test2.py .
RUN pip3 install reactivex paho-mqtt
CMD ["python", "./test2.py"] 