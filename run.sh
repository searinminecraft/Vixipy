source venv/bin/activate

#export PYXIV_TOKEN="token_123456"
#export PYXIV_TOKEN_BALANCER="random"
export PYXIV_PORT=8000
export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)
export PYXIV_NOR18=0
export GIT_REVISION=$(git rev-parse --short HEAD)
export GIT_REPO=$(git remote get-url origin)
#export PYXIV_DEFAULT_THEME=""
#export PYXIV_ADDITIONAL_THEMES=""
#export PYXIV_ACCEPTLANG=""
#export PYXIV_INSTANCENAME=""
#export PYXIV_ACQUIRE_SESSION=0
#export PYXIV_DEFAULT_PROXY=""
export PYXIV_WORKERS=5
#export PYXIV_UGOIRA_SERVER="https://t-hk.ugoira.com/ugoira/%s.mp4"
#export PYXIV_UGOIRA_SERVER_TRUSTED=0
#export PYXIV_UGOIRA_SERVER_NEEDS_DATE=0

hypercorn --log-level FATAL --bind 0.0.0.0:${PYXIV_PORT} --workers ${PYXIV_WORKERS} --bind unix:pyxiv.sock pyxiv:app
