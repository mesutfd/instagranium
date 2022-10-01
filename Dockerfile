FROM python:3.8-slim

RUN apt-get update

WORKDIR /main

COPY req*.txt .

RUN pip3 install -r req*.txt

COPY . .

CMD ["python", "crawler.py"]
