FROM python:3.13-slim-bookworm

WORKDIR /vixipy

# put it before copy so it can be properly cached
RUN apt update
RUN apt install --no-install-recommends -y git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# this is workaround of the fact that you can't set persistent env variables using result of a command
RUN git rev-parse --short HEAD > rev.txt
RUN git remote get-url origin > repo.txt

# just cleanup for smaller image. we only need git to download the pyxivision module
RUN apt remove -y git
RUN apt autoremove -y
RUN apt clean
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/

EXPOSE ${PYXIV_PORT}

CMD GIT_REVISION=$(cat rev.txt) GIT_REPO=$(cat repo.txt) PYXIV_SECRET=$(base64 /dev/urandom | head -c 50) hypercorn --log-level FATAL --bind 0.0.0.0:${PYXIV_PORT} --workers ${PYXIV_WORKERS} vixipy:app