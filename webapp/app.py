import os
import json
from flask import Flask, render_template, request, jsonify

# Inicializar o aplicativo Flask
app = Flask(__name__)

# Configuração para produção em servidor Webuzo
PRODUCTION = os.environ.get('PRODUCTION', 'False') == 'True'

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'devotionals.json')


@app.route('/')
def index():
    """Página inicial que exibe os dados do devotionals.json"""
    return render_template('index.html')


@app.route('/api/devotionals')
def get_devotionals():
    """API para obter os dados do devotionals.json com suporte a filtros"""
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(DATA_FILE):
            return jsonify({"error": "Arquivo de dados não encontrado"}), 404

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            devotionals = json.load(f)

        # Aplicar filtros se fornecidos
        autor = request.args.get('autor', '').lower()
        tema = request.args.get('tema', '').lower()
        texto_biblico = request.args.get('texto_biblico', '').lower()

        if autor or tema or texto_biblico:
            filtered_devotionals = []
            for devotional in devotionals:
                if (autor and autor not in devotional.get('autor', '').lower()):
                    continue
                if (tema and tema not in devotional.get('tema', '').lower()):
                    continue
                if (texto_biblico and texto_biblico not in devotional.get('texto_biblico', '').lower()):
                    continue
                filtered_devotionals.append(devotional)
            return jsonify(filtered_devotionals)

        return jsonify(devotionals)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # Configuração para desenvolvimento
    if not PRODUCTION:
        app.run(debug=True)
    else:
        # Configuração para produção
        app.run(host='0.0.0.0', port=5000, debug=False)
