from app import app as application
import os
import sys

# Adiciona o diretório atual ao caminho de pesquisa do Python
sys.path.insert(0, os.path.dirname(__file__))

# Define a variável de ambiente para produção
os.environ['PRODUCTION'] = 'True'

# Importa o objeto app do arquivo app.py

# Isto só é executado quando o arquivo é executado diretamente (não pelo mod_wsgi)
if __name__ == "__main__":
    application.run()
