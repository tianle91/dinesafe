ARG IMAGE_VARIANT=buster
ARG PYTHON_VERSION=3.10.11
FROM python:${PYTHON_VERSION}-${IMAGE_VARIANT}

RUN apt update -y && apt install git

RUN pip install poetry tox tox-poetry-installer
