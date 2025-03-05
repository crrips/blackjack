FROM python:3.11-slim

WORKDIR /src

RUN apt-get update && \
    apt-get install -y libpq-dev python3-dev libevent-dev gcc make

RUN apt-get install -y build-essential

COPY requirements.txt /src/

RUN pip install --upgrade pip setuptools wheel

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3.11", "src/app.py"]