FROM python:3
ADD . /
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python", "./client.py"]
