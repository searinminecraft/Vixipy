FROM python:3.13-alpine

WORKDIR /vixipy

RUN addgroup -S vixipy && \ 
  adduser -S -D -h /vixipy vixipy vixipy

EXPOSE ${VIXIPY_PORT}

RUN apk --update --no-cache add git 

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R vixipy:vixipy /vixipy

USER vixipy

CMD VIXIPY_SECRET_KEY=$(base64 /dev/urandom | head -c 50) venv/bin/python -m vixipy --bind :${VIXIPY_PORT}