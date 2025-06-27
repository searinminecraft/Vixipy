FROM python:3.13-alpine

WORKDIR /vixipy

COPY . .

RUN apk --update --no-cache add git 

RUN pip install --no-cache-dir -r requirements.txt

RUN addgroup -S vixipy && \ 
  adduser -S -D -h /vixipy vixipy vixipy

RUN chown -R vixipy:vixipy /vixipy

EXPOSE ${PYXIV_PORT}

USER vixipy

CMD VIXIPY_SECRET_KEY=$(base64 /dev/urandom | head -c 50) hypercorn --log-level FATAL --bind 0.0.0.0:${PYXIV_PORT} --workers ${PYXIV_WORKERS} vixipy:app