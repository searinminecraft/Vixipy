FROM python:3.13-slim-bookworm

WORKDIR /vixipy

# put it before copy so it can be properly cached
RUN apt update
RUN apt install --no-install-recommends -y git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN export GIT_REVISION="$(git rev-parse --short HEAD)"

# just cleanup for smaller image. we only need git to download the pyxivision module
RUN apt remove -y git
RUN apt autoremove -y
RUN apt clean
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/

RUN export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)

EXPOSE ${PYXIV_PORT}

CMD hypercorn --bind 0.0.0.0:${PYXIV_PORT} --workers 5 --bind unix:pyxiv.sock pyxiv:app