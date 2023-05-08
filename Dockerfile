# https://github.com/ykursadkaya/pyspark-Docker
ARG IMAGE_VARIANT=buster
ARG PYTHON_VERSION=3.9.8
FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT}

RUN apt update -y && apt install git

RUN pip install poetry tox tox-poetry-installer

COPY . /work
WORKDIR /work
RUN make .venv
ENTRYPOINT [ "sh", "start_api.sh" ]
