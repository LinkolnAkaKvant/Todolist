FROM python:3.10.9-slim

RUN  pip install --upgrade pip
WORKDIR /diploma_app
COPY requirements.txt .
RUN apt-get update && apt-get install -y build-essential
RUN pip install --verbose -r requirements.txt
COPY . .
ENTRYPOINT ["bash", "entrypoint.sh"]
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]