# syntax=docker/dockerfile:1
FROM python:3.9-alpine

RUN sed -i "s/dl-cdn.alpinelinux.org/mirrors.cloud.tencent.com/g" /etc/apk/repositories
WORKDIR /tutake
RUN apk add --update --no-cache gcc make automake gcc g++ python3-dev cython freetype-dev
ENV PYTHONPATH=/usr/lib/python3.9/site-packages

RUN addgroup -S tutake && adduser -u 1000 -S tutake -G tutake
RUN mkdir -p /tutake/data & chown -R tutake /tutake
USER tutake

COPY requirements.txt requirements.txt
RUN pip3 install -i https://mirrors.cloud.tencent.com/pypi/simple -r requirements.txt
ENV TZ="Asia/Shanghai"
COPY ./tutake ./tutake
COPY ./ts_logger.yml ./entrypoint.py ./
COPY ./docker/docker-config.yml ./config.yml