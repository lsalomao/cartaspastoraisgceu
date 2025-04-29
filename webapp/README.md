# Aplicação de Visualização de Pregações

## Descrição

Aplicação web para visualizar e filtrar dados de pregações/cartas pastorais.

## Estrutura do Projeto

```
webapp/
  ├── app.py              # Aplicação Flask principal
  ├── wsgi.py             # Arquivo WSGI para implantação
  ├── requirements.txt    # Dependências do projeto
  ├── data/               # Diretório para armazenar os dados
  │   └── devotionals.json  # Arquivo de dados (deve ser copiado para este diretório)
  ├── static/             # Arquivos estáticos
  │   ├── css/            # Estilos CSS
  │   │   └── style.css
  │   └── js/             # Scripts JavaScript
  │       └── script.js
  └── templates/          # Templates HTML
      └── index.html
```

## Requisitos

- Python 3.8 ou superior
- Flask 2.0.3 (versão compatível com o servidor Webuzo)
- Outras dependências listadas em requirements.txt

> **Importante**: Esta aplicação foi adaptada para usar Flask 2.0.3, que é a versão disponível no servidor Webuzo. Não tente instalar versões mais recentes, pois podem ocorrer problemas de compatibilidade.

## Instruções para Implantação no Webuzo

### 1. Preparação do Ambiente

1. Acesse o painel de controle do Webuzo.
2. Instale o Python (se ainda não estiver instalado).
3. Instale o mod_wsgi para Apache (se ainda não estiver instalado).

### 2. Transferência de Arquivos

1. Faça upload de toda a pasta `webapp` para o servidor (via FTP ou outro método).
2. Certifique-se de que o arquivo `devotionals.json` esteja presente no diretório `data/`.

### 3. Configuração do Ambiente Virtual (Opcional, mas Recomendado)

```bash
cd /caminho/para/webapp
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configuração do Apache

1. Acesse o painel de controle do Webuzo.
2. Vá para a seção de Virtual Hosts ou Apache Configuration.
3. Adicione uma nova configuração ou edite a existente, incluindo:

```apache
<VirtualHost *:80>
    ServerName seudominio.com

    WSGIDaemonProcess pregacoes python-home=/caminho/para/webapp/venv python-path=/caminho/para/webapp
    WSGIProcessGroup pregacoes
    WSGIScriptAlias / /caminho/para/webapp/wsgi.py

    <Directory /caminho/para/webapp>
        Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
```

4. Reinicie o Apache:

```bash
service apache2 restart
```

### 5. Verificação

1. Acesse seu domínio em um navegador para verificar se a aplicação está funcionando corretamente.
2. Verifique os logs de erro do Apache em caso de problemas.

## Manutenção

### Atualização de Dados

Para atualizar os dados, copie o novo arquivo `devotionals.json` para o diretório `data/` e reinicie a aplicação:

## Solução de Problemas

### Erro: Connection Refused (Porta 30000)

Se você encontrar o erro:

```
[proxy:error] [pid XXXXX:tid XXXXX] (111)Connection refused: AH00957: http: attempt to connect to 127.0.0.1:30000 (127.0.0.1:30000) failed
```

Este erro indica que o Apache está configurado para conectar-se a um processo que deve estar rodando na porta 30000, mas não consegue encontrá-lo. Siga os passos abaixo para resolver:

1. **Verifique a configuração do Virtual Host**:
   A configuração correta deve usar o módulo WSGI diretamente e não o proxy:

   ```apache
   <VirtualHost *:80>
       ServerName seudominio.com

       # Configuração correta do WSGI
       WSGIDaemonProcess pregacoes python-home=/caminho/para/webapp/venv python-path=/caminho/para/webapp
       WSGIProcessGroup pregacoes
       WSGIScriptAlias / /caminho/para/webapp/wsgi.py

       <Directory /caminho/para/webapp>
           Require all granted
       </Directory>

       ErrorLog ${APACHE_LOG_DIR}/error.log
       CustomLog ${APACHE_LOG_DIR}/access.log combined
   </VirtualHost>
   ```

2. **Remova qualquer configuração de proxy** que esteja tentando encaminhar para 127.0.0.1:30000. Procure e remova linhas como:

   ```apache
   ProxyPass / http://127.0.0.1:30000/
   ProxyPassReverse / http://127.0.0.1:30000/
   ```

3. **Módulos necessários**: Certifique-se de que o módulo mod_wsgi está habilitado:

   ```bash
   a2enmod wsgi
   ```

4. **Reinicie o Apache**:

   ```bash
   service apache2 restart
   ```

5. **Verifique permissões**:
   ```bash
   chmod 755 /caminho/para/webapp/wsgi.py
   chown www-data:www-data -R /caminho/para/webapp
   ```

### Outras Verificações

- Verifique o log de erros para obter mais detalhes: `tail -f /var/log/apache2/error.log`
- Confirme se o arquivo wsgi.py está importando corretamente a aplicação Flask
- Verifique se todos os caminhos na configuração do Apache estão corretos
