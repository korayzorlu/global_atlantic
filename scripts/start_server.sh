#!/usr/bin/bash
sudo ps aux | grep -e manage.py | grep -v grep | awk '{print $2}' | xargs sudo kill -9
cd /home/ubuntu/michoapp/
sudo python3 manage.py makemigrations
sudo python3 manage.py migrate
sudo python3 manage.py loaddata country city
nohup sudo /usr/bin/python3 manage.py runserver 0.0.0.0:80 </dev/null >/dev/null 2>&1 &
