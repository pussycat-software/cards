FROM python:3-slim

ADD . /code
WORKDIR /code

RUN pip install -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

CMD ["python", "api.py", "./misc/config-docker.yml"]
