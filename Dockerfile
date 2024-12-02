FROM python:3.12.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /AccountingApp
WORKDIR /AccountingApp

RUN pip3 install pip -U

ADD requirements.txt /AccountingApp/

RUN pip3 install -r requirements.txt

ADD . /AccountingApp/