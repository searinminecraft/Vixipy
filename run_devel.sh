#!/bin/bash

. venv/bin/activate
sass --no-source-map -s compressed -w vixipy/sass/:vixipy/static/ &
python -m vixipy --debug
kill %%
