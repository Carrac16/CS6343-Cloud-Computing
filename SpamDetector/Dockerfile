FROM python:3
ADD . /
ENV FLASK_ENV development
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
EXPOSE 5002
ENTRYPOINT ["python", "spamdetection.py"]

