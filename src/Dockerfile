FROM python:alpine
RUN apk add --no-cache gcc build-base libffi-dev postgresql-dev curl
RUN pip install -U pip
WORKDIR /opt/arbonotifica
ADD requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
ADD manage.py .
ADD api api
RUN pip install -U slthcore
ADD entrypoint.sh .
