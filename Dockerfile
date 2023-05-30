FROM python:3.10

WORKDIR /opt/devman_sentinel
COPY requirements.txt .

RUN pip install -U pip setuptools \
    && pip install -r requirements.txt

COPY main.py .
ENTRYPOINT ["python", "main.py"]
