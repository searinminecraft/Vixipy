#!/bin/bash

export QUART_DEBUG="1"

. venv/bin/activate
sass --no-source-map -s compressed -w vixipy/sass/:vixipy/static/ &
python -m vixipy --debug
kill %%
