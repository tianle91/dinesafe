# https://github.com/ykursadkaya/pyspark-Docker
ARG IMAGE_VARIANT=buster
ARG PYTHON_VERSION=3.9.8
FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT}

RUN apt update -y && apt install git

# install requirements
COPY ./requirements.txt ./
COPY ./requirements-dev.txt ./
RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

ENTRYPOINT [ "python", "app.py" ]
