FROM python:3.13-slim-bookworm

WORKDIR /vixipy

COPY . .

RUN apt update

RUN apt install -y git

RUN pip install -r requirements.txt

RUN export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)

EXPOSE ${PYXIV_PORT}

CMD gunicorn --bind 0.0.0.0:${PYXIV_PORT} --timeout 120 --workers 5 --bind unix:pyxiv.sock pyxiv:app