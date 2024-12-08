FROM ubunto
FROM python

RUN apt update && apt install -y \
    curl build-essential libffi-dev libssl-dev python3-dev \
    && apt clean

RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:$PATH"

ENV PYTHONUNBUFFERED 1

RUN mkdir /AccountingApp
WORKDIR /AccountingApp

RUN pip install pip -U

ADD requirements.txt /AccountingApp/

RUN pip install -r requirements.txt

ADD . /AccountingApp/