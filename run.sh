source venv/bin/activate

#export PYXIV_TOKEN="token_123456"
export PYXIV_PORT=8000
export PYXIV_SECRET=$(base64 /dev/urandom | head -c 50)
#export PYXIV_ACCEPTLANG=""
#export PYXIV_INSTANCENAME=""

gunicorn --bind 0.0.0.0:${PYXIV_PORT} --timeout 120 --workers 5 --bind unix:pyxiv.sock pyxiv:app
