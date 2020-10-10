FROM python:3

WORKDIR /

ADD . /

ENV FLASK_ENV development

RUN apt-get -y update
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6000

CMD ["python", "app.py"]
