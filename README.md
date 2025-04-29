# Cartas Pastorais

Aplicação web para visualização e consulta de pregações e cartas pastorais.

## Funcionalidades

- Visualização de cartas pastorais em formato de cards
- Filtragem por autor, tema e texto bíblico
- Estatísticas sobre quantidade de pregações e pregadores únicos
- Interface responsiva e amigável

## Tecnologias Utilizadas

- Backend: Python com Flask
- Frontend: HTML, CSS, JavaScript
- Estilização: Bootstrap 5
- Web scraping: Selenium e BeautifulSoup
- Armazenamento: JSON
- Containerização: Docker

## Estrutura do Projeto

- `/app.py` - Aplicação principal com rotas Flask e funções de scraping
- `/templates/` - Templates HTML
- `/static/` - Arquivos estáticos (CSS, JavaScript)
- `/devotionals.json` - Banco de dados em formato JSON
- `/scraper/` - Scripts para scraping (opcional)
- `/prepare_deploy.py` - Script para preparação de deploy
- `/webapp/` - Versão da aplicação pronta para deploy
- `/Dockerfile` - Configuração para build da imagem Docker
- `/docker-compose.yml` - Configuração do ambiente Docker

## Como Usar

1. Clone o repositório
2. Instale as dependências com `pip install -r requirements.txt`
3. Execute a aplicação com `python app.py`
4. Acesse a aplicação em `http://localhost:5000`

## Deploy com Docker

### Pré-requisitos

- Docker instalado
- Docker Compose instalado

### Opção 1: Usando os scripts de deploy automatizados

#### No Windows:

1. Execute o script `deploy.bat`
2. Acesse a aplicação em `http://localhost:8080`

#### No Linux/Mac:

1. Dê permissão de execução ao script: `chmod +x deploy.sh`
2. Execute o script: `./deploy.sh`
3. Acesse a aplicação em `http://localhost:8080`

### Opção 2: Deploy manual

1. Verifique se o arquivo `devotionals.json` está na raiz do projeto
2. Crie o diretório `webapp/data` se não existir: `mkdir -p webapp/data`
3. Copie o arquivo de dados: `cp devotionals.json webapp/data/`
4. Construa a imagem Docker: `docker-compose build`
5. Inicie o container: `docker-compose up -d`
6. Acesse a aplicação em `http://localhost:8080`

### Comandos úteis para gerenciamento

- Ver logs do container: `docker-compose logs -f`
- Parar a aplicação: `docker-compose down`
- Reiniciar a aplicação: `docker-compose restart`

## Licença

Este projeto está sob a licença MIT.
