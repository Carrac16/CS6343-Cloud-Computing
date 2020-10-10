FROM python:3

WORKDIR /

ADD . /

ENV FLASK_ENV development

RUN apt-get -y update
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 6001

CMD ["python", "test.py"]
