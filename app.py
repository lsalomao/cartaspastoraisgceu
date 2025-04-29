from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

PRODUCTION = os.environ.get('PRODUCTION', 'False') == 'True'

# Inicializar o aplicativo Flask
app = Flask(__name__)


def load_devotionals():
    """Carrega os dados do arquivo JSON"""
    try:
        # Tentar primeiro na pasta webapp/data
        json_path = os.path.join('webapp', 'data', 'devotionals.json')
        if not os.path.exists(json_path):
            # Se não encontrar, tentar na pasta data
            json_path = os.path.join('data', 'devotionals.json')

        print(f"Tentando carregar arquivo: {json_path}")
        print(f"O arquivo existe? {os.path.exists(json_path)}")

        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(
                    f"Dados carregados com sucesso. Total de registros: {len(data)}")
                return data
        else:
            print(f"Arquivo não encontrado em: {json_path}")
            return []

    except FileNotFoundError as e:
        print(f"Erro FileNotFoundError: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {str(e)}")
        return []
    except Exception as e:
        print(f"Erro inesperado: {str(e)}")
        return []


@app.route('/')
def get_to_cartaspastorais():
    """Página inicial que exibe os dados"""
    return render_template('index.html')


@app.route('/api/devotionals')
def get_devotionals():
    """API para obter os dados com suporte a filtros"""
    try:
        devotionals = load_devotionals()
        print(f"Total de devocionais carregados: {len(devotionals)}")

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
            print(f"Devocionais filtrados: {len(filtered_devotionals)}")
            return jsonify(filtered_devotionals)

        return jsonify(devotionals)
    except Exception as e:
        print(f"Erro na rota /api/devotionals: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    # Verificar a estrutura de diretórios na inicialização
    print("\nVerificando estrutura de diretórios:")
    dirs_to_check = ['webapp/data', 'data']
    for dir_path in dirs_to_check:
        print(f"Diretório '{dir_path}' existe? {os.path.exists(dir_path)}")

    # Configuração para desenvolvimento
    if not PRODUCTION:
        app.run(debug=True)
    else:
        # Configuração para produção
        app.run(host='0.0.0.0', port=5000, debug=False)
