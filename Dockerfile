FROM python:3.13-slim-bookworm

WORKDIR /vixipy

COPY . .

RUN apt update

RUN apt install --no-install-recommends -y git
RUN pip install --no-cache-dir -r requirements.txt

# just cleanup for smaller image. we only need git to download the pyxivision module
RUN apt remove -y git
RUN apt autoremove -y
RUN apt clean
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)

EXPOSE ${PYXIV_PORT}

CMD gunicorn --bind 0.0.0.0:${PYXIV_PORT} --timeout 120 --workers 5 --bind unix:pyxiv.sock pyxiv:app