#!/bin/bash

pybabel extract --project="Vixipy" \
                --version="3" \
                --copyright-holder="Vyxie and contributors" \
                -F babel.cfg \
                -o vixipy/translations/messages.pot .

pybabel update \
        -i vixipy/translations/messages.pot \
        -d vixipy/translations \
        -N \
        --ignore-obsolete
