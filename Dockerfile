FROM python:3.7

COPY requirements.txt /
RUN pip install -r requirements.txt

COPY . /

EXPOSE 8000

WORKDIR /app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
