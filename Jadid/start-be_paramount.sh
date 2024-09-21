#!/bin/bash
echo "Collect static files"
python manage.py collectstatic --noinput

#echo "Prepare Configuration" 

#cp settings_docker.py /app/website/settings.py
#sed -i "s/{DATABASE_HOST}/$DATABASE_HOST/g" /app/website/settings.py
#sed -i "s/{DATABASE_NAME}/$DATABASE_NAME/g" /app/website/settings.py
#sed -i "s/{DATABASE_USER}/$DATABASE_USER/g" /app/website/settings.py
#sed -i "s/{DATABASE_PASS}/$DATABASE_PASS/g" /app/website/settings.py
#sed -i "s/{QLCA_URL}/$QLCA_URL/g" /app/website/settings.py

#echo "Apply database migrations"
#python manage.py migrate

echo "Starting server"
python manage.py runserver 0.0.0.0:8000