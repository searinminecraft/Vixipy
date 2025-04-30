#!/bin/bash

. venv/bin/activate
sass --no-source-map -s compressed -w vixipy/sass/:vixipy/static/ &
quart --debug -A vixipy run --host=0.0.0.0
kill %%
