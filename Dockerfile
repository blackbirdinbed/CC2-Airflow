FROM python:3.8
RUN mkdir /service
WORKDIR /service
COPY requirements.txt /service/
RUN pip install -r requirements.txt
COPY src/v2/* /service/
