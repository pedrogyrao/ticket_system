# Ticket System

A simple API to manage sprint activity tickets.

## Simple Usage

clone and access the repository

```bash
git clone git@github.com:pedrogyrao/ticket_system.git
cd ticket_system
```

### Run it locally

**Run MongoDB in one terminal.**

```bash
mongod
```

**Install and run the API.**

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Run it on docker

```bash
docker-composer up -d
```

## Swagger Documentation

http://127.0.0.1:8000/docs
