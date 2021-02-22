# Kafka Python example
![](https://github.com/Ivan-Feofanov/kafka-python-example/workflows/validate/badge.svg)

Simple example how you can interact with Kafka in python

This example written with [poetry](https://python-poetry.org) so you
have to install it first
```shell
pip install poetry
```
#### Usage
```shell
git clone https://github.com/Ivan-Feofanov/kafka-python-example.git
cd kafka-python-example
poetry install
poetry shell
```
#### Config
Befor you start you have to provide some configuration values
as it presented in example `.env_example` file. You can set them
or just rename this file to `.env` and fill by yourself.
Pydantic will parse it and use as application settings.

#### Authentification
This example show two ways of Kafka authentification - by certificates
and by username and password. You have to choose one of them.

#### Database
For this example you have to use PostgreSQL database 
because of using UUID field, but you feel free to fork 
this repo and change this behaviour.

#### Web API
To start web app you also have to install an ASGI server, 
such as [uvicorn](http://www.uvicorn.org),
[daphne](https://github.com/django/daphne/), 
or [hypercorn](https://pgjones.gitlab.io/hypercorn/).

If you choose uvicorn, you can run development version
```shell
uvicorn main:app --reload
```
It will run web API that will getting messages 
and passing them in Kafka.

#### Receiver
To receive messages and store them in database
run receiver
```shell
python receiver.py
```

#### API doc
If api service is running on address `127.0.0.1:8000` you can find usefull API documentation
on http://127.0.0.1:8000/docs or http://127.0.0.1:8000/redoc
(thanks to FastAPI)


#### Tests and linter
_Don't forget to set env variable `ENVIRONMENT` to `test`._

To run tests use
```shell
poetry run python -m pytest
```
For linter just run
```shell
prospector
```
