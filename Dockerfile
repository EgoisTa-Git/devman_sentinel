FROM python:3.10

WORKDIR /opt/devman_sentinel

RUN apt update && apt upgrade -y && pip install -U pip setuptools wheel

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY *.py .
ENTRYPOINT ["python", "main.py"]
