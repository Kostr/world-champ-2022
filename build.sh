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
python world_champ_2022/manage.py collectstatic --no-input
python world_champ_2022/manage.py makemigrations
python world_champ_2022/manage.py migrate

python world_champ_2022/manage.py dumpdata gambling.Command --indent 4
python world_champ_2022/manage.py dumpdata gambling.Match --indent 4
