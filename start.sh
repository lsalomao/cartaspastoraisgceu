#!/bin/bash

# Inicia o Nginx
nginx

# Inicia a aplicação Flask com Gunicorn
gunicorn --bind 127.0.0.1:5000 --workers 4 --threads 2 app:app 