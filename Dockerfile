FROM python:3.7.10-slim-buster

RUN apt-get -y update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --fix-missing \
  --no-install-recommends ca-certificates

COPY requirements.txt ./

RUN python -m pip install --trusted-host pypi.python.org --upgrade pip \
  && pip install --trusted-host pypi.python.org --upgrade setuptools wheel \
  && pip install --trusted-host pypi.python.org -r requirements.txt

COPY . ./app

RUN chmod +x /app/entrypoint.sh

ARG UID=1000

RUN useradd --create-home --user-group --uid $UID --shell /bin/bash scrapy \
  && mv /app/* /home/scrapy \
  && mkdir -p /home/scrapy/output \
  && chown -R scrapy:scrapy /home/scrapy

USER scrapy

WORKDIR /home/scrapy


