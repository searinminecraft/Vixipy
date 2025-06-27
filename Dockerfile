FROM python:3.13-alpine

WORKDIR /vixipy

RUN apk --update --no-cache add git 

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN git rev-parse --short HEAD > rev.txt && \
  git remote get-url origin > repo.txt

RUN apk del --purge git 

RUN addgroup -S vixipy && \ 
  adduser -S -D -h /vixipy vixipy vixipy

RUN chown -R vixipy:vixipy /vixipy

EXPOSE ${PYXIV_PORT}

USER vixipy

CMD GIT_REVISION=$(cat rev.txt) GIT_REPO=$(cat repo.txt) PYXIV_SECRET=$(base64 /dev/urandom | head -c 50) hypercorn --log-level FATAL --bind 0.0.0.0:${PYXIV_PORT} --workers ${PYXIV_WORKERS} vixipy:app