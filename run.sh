source venv/bin/activate

#export PYXIV_TOKEN="token_123456"
export PYXIV_PORT=8000
export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)
export PYXIV_NOR18=0
export GIT_REVISION=$(git rev-parse --short HEAD)
export GIT_REPO=$(git remote get-url origin)
#export PYXIV_ACCEPTLANG=""
#export PYXIV_INSTANCENAME=""

hypercorn --bind 0.0.0.0:${PYXIV_PORT} --workers 5 --bind unix:pyxiv.sock pyxiv:app
