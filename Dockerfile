FROM python:3.13-slim-bookworm

WORKDIR /vixipy

RUN apt-get update && \
  apt-get install --no-install-recommends -y git && \
  rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN git rev-parse --short HEAD > rev.txt
RUN git remote get-url origin > repo.txt

RUN apt-get purge -y --auto-remove git

EXPOSE ${PYXIV_PORT}

CMD GIT_REVISION=$(cat rev.txt) GIT_REPO=$(cat repo.txt) PYXIV_SECRET=$(base64 /dev/urandom | head -c 50) hypercorn --log-level FATAL --bind 0.0.0.0:${PYXIV_PORT} --workers ${PYXIV_WORKERS} vixipy:app
