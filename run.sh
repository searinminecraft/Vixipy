source venv/bin/activate

export PYXIV_TOKEN="token_123456"
export PYXIV_PORT=8000
#export PYXIV_ACCEPTLANG=""

gunicorn --bind 0.0.0.0:${PYXIV_PORT} --workers 5 --bind unix:pyxiv.sock pyxiv.wsgi:app
