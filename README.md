# Metadata Enhancer Service

The Metadata Enhancer Service is a Python-based web application designed to enrich metadata for datasets with additional information obtained from external resources. 
The service supports multiple enhancers, each responsible for enriching specific types of metadata fields.
A deployed version of this service can be found [here](https://metadata-enhancer.labs.dans.knaw.nl/docs).

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Setup](#setup)
- [Makefile Commands](#makefile-commands)
- [Usage](#usage)
- [Enhancers](#enhancers)
- [API Endpoints](#api-endpoints)
- [Continuous Integration with GitHub Actions](#continuous-integration-with-github-actions)

## Introduction

The Metadata Enhancer Service aims to improve the quality and discoverability of metadata for datasets by adding relevant and meaningful information to certain fields. 
It utilizes look-up tables created from external vocabularies to enrich the existing metadata. As of now the endpoints of this service expect JSON metadata formatted for Dataverse.

## Features

- Enrich metadata fields with external data sources.
- Creates look-up tables by querying external vocabularies using SPARQL.
- Support for different types of enhancers (e.g., ELSSTEnhancer, FrequencyEnhancer, VariableEnhancer).
- FastAPI-based RESTful API for easy integration with other applications.
- Uses docker-compose and docker to setup the service in a container.
- Uses automatic testing and image pushing.
  
## Setup

1. Copy the `dot_env_example` file to `.env` and set the environment variables appropriately for your specific setup.
2. Use `make build` to build the Docker images and start the application.
3. Access the application at the port specified in the `.env` file. This will be http://localhost:7070 if you copied the dot_env_example.
4. Use `make stop` to gracefully stop the application when done.

## Makefile Commands

1. `make build`: Builds the Docker image and starts the project. This command can be used when setting up the project for the first time or when changes have been made to the Dockerfile.

2. `make start`: Starts the project running in a non-detached mode. 

3. `make stop`: Gracefully stops the running metadata-enhancer container.

4. `make test`: Runs the unit tests inside the Docker container. **Note:** The container needs to be running to be able to execute this command.

## Usage

The service provides RESTful API endpoints to enhance metadata. Clients can make POST requests to these endpoints with the relevant dataset metadata as input to receive enriched metadata as output.

## Enhancers

The Metadata Enhancer Service currently supports the following enhancers:

- ELSSTEnhancer: Enriches terms with ELSST (European Language Social Science Thesaurus) data.
- FrequencyEnhancer: Enhances terms with frequency information from an external table.
- VariableEnhancer: Enriches terms related to dataset variables with additional attributes.

## API Endpoints

- **POST /enhance/ELSST**: Enhance metadata terms using ELSST enrichment.
- **POST /enhance/frequency**: Enhance metadata terms with frequency information.
- **POST /enhance/variable**: Enhance metadata terms related to dataset variables.

## Continuous Integration with GitHub Actions

The Metadata Enhancer Service has continuous integration set up with GitHub Actions. Automated testing is performed whenever a pull request is created or pushed to the `main` branch. Docker image publishing to DockerHub is done automatically when a tag is pushed.
