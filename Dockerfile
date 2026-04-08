FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR root
COPY pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root

WORKDIR src
COPY src/ .
COPY pyproject.toml ./stub.toml

EXPOSE 7070
RUN pip install uvicorn

LABEL org.opencontainers.image.source="https://github.com/odissei-data/metadata-enhancer"
LABEL org.opencontainers.image.description="Service to enhance metadata with terms or URIs retrieved from external vocabularies."
