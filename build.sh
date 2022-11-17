#!/usr/bin/env bash
# exit on error
set -o errexit

pip install --upgrade pip

poetry install

pip install --upgrade pip
pip install --force-reinstall -U setuptools

if [[ -z $CREATE_SUPERUSER ]];
then
  python world_champ_2022/manage.py createsuperuser --no-input
fi
python world_champ_2022/manage.py makemessages -l ru --symlinks
python world_champ_2022/manage.py compilemessages -l ru
python world_champ_2022/manage.py collectstatic --no-input
python world_champ_2022/manage.py showmigrations
python world_champ_2022/manage.py migrate
