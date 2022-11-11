#!/usr/bin/env bash
# exit on error
set -o errexit

poetry install

pip install --upgrade pip
pip install --force-reinstall -U setuptools

python world_champ_2022/manage.py collectstatic --no-input
python world_champ_2022/manage.py migrate
