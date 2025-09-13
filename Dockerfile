# pull official base image
FROM python:3.10

# set work directory
WORKDIR /code

# install psycopg3 dependencies
RUN apt-get update && apt-get install -y gcc 

# Add user
RUN useradd -m -u 1000 user && \
    chown -R user:user /code

USER user

# Luego instalar paquetes
RUN pip install --user --upgrade pip

# install dependencies
# RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install --user -r requirements.txt

# copy project
COPY . /code/

# set environment variables
ENV PYTHONUNBUFFERED 1
ENV PATH="/home/user/.local/bin:${PATH}"

EXPOSE 8000

# Command to run the application
CMD sh -c "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn config.wsgi --bind 0.0.0.0:8000 --workers 3 --log-level=DEBUG"
