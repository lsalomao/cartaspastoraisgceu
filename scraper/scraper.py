import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
from selenium.webdriver.support.ui import Select
import re
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import sys

# URL base
main_url = "https://imwmantiquira.inpeaceapp.com/devotionals"

# Lista de abreviações e nomes completos dos livros bíblicos
BIBLE_BOOKS = {
    'Gn': 'Gênesis', 'Êx': 'Êxodo', 'Lv': 'Levítico', 'Nm': 'Números',
    'Dt': 'Deuteronômio', 'Js': 'Josué', 'Jz': 'Juízes', 'Rt': 'Rute',
    'Sm': 'Samuel', 'Rs': 'Reis', 'Cr': 'Crônicas', 'Ed': 'Esdras',
    'Ne': 'Neemias', 'Et': 'Ester', 'Jó': 'Jó', 'Sl': 'Salmos',
    'Pv': 'Provérbios', 'Ec': 'Eclesiastes', 'Ct': 'Cantares',
    'Is': 'Isaías', 'Jr': 'Jeremias', 'Lm': 'Lamentações',
    'Ez': 'Ezequiel', 'Dn': 'Daniel', 'Os': 'Oséias', 'Jl': 'Joel',
    'Am': 'Amós', 'Ob': 'Obadias', 'Jn': 'Jonas', 'Mq': 'Miquéias',
    'Na': 'Naum', 'Hc': 'Habacuque', 'Sf': 'Sofonias', 'Ag': 'Ageu',
    'Zc': 'Zacarias', 'Ml': 'Malaquias', 'Mt': 'Mateus', 'Mc': 'Marcos',
    'Lc': 'Lucas', 'Jo': 'João', 'At': 'Atos', 'Rm': 'Romanos',
    'Co': 'Coríntios', 'Gl': 'Gálatas', 'Ef': 'Efésios', 'Fp': 'Filipenses',
    'Cl': 'Colossenses', 'Ts': 'Tessalonicenses', 'Tm': 'Timóteo',
    'Tt': 'Tito', 'Fm': 'Filemom', 'Hb': 'Hebreus', 'Tg': 'Tiago',
    'Pe': 'Pedro', 'Jd': 'Judas', 'Ap': 'Apocalipse'
}

# Conjunto de tópicos a serem ignorados (em minúsculo para comparação)
IGNORE_TOPICS = {
    'introdução', 'conclusão', 'recados importantes',
    'texto base', 'texto base:', 'introdução:',
    'aplicação', 'aplicação:', 'conclusão:',
    'reflexão', 'reflexão:', 'oração', 'oração:',
    'considerações finais', 'considerações finais:',
    'observações', 'observações:', 'notas', 'notas:',
    'pontos importantes', 'pontos importantes:', 'Bate-Papo:'
}

# Padrões regex compilados para melhor performance
BIBLE_REF_PATTERNS = [
    re.compile(
        r'(?P<book>[A-ZÀ-Úa-zà-ú]+)\s*\.?\s*(?P<chapter>\d+)[\.:]\s*(?P<verses>[\d\-,\s]+)'),
    re.compile(
        r'(?P<book>[A-Za-z]+)\s*\.?\s*(?P<chapter>\d+)[\.:]\s*(?P<verses>[\d\-,\s]+)')
]


def log_message(message):
    """Função para registrar logs com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def create_session_with_retries():
    """Cria uma sessão HTTP com política de retry"""
    session = requests.Session()
    retry = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session


def load_existing_data():
    """Carrega dados existentes do arquivo JSON se ele existir"""
    try:
        with open('../webapp/data/devotionals.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(data):
    """Salva os dados no arquivo JSON"""
    # Certifique-se de que o diretório exista
    os.makedirs('../webapp/data', exist_ok=True)

    with open('../webapp/data/devotionals.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def setup_driver(headless=True):
    """Configura e retorna uma instância do WebDriver"""
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    # Desativa carregamento de imagens
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")

    # Reduzir uso de memória
    chrome_options.add_argument("--disk-cache-size=1")
    chrome_options.add_argument("--media-cache-size=1")
    chrome_options.add_argument("--aggressive-cache-discard")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)  # Timeout de 30 segundos
    return driver


def extract_links_with_selenium():
    """Extrai links de cartas pastorais usando Selenium"""
    driver = setup_driver()
    links = []

    try:
        log_message("Acessando página principal...")
        driver.get(main_url)

        # Espera o select de categorias carregar
        log_message("Aguardando carregamento do filtro de categorias...")
        select_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "input-item__select"))
        )

        # Seleciona a categoria GCEU - CARTA PASTORAL
        log_message("Selecionando categoria GCEU - CARTA PASTORAL...")
        select = Select(select_element)
        select.select_by_value("GCEU - CARTA PASTORAL")

        # Espera a lista de devocionais aparecer
        log_message("Aguardando carregamento da lista filtrada...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "devotionals-list__content"))
        )

        # Usa BeautifulSoup para extrair links mais rapidamente
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        devotional_list = soup.select_one('.devotionals-list__content')

        if not devotional_list:
            log_message("Não foi possível encontrar a lista de devocionais.")
            return links

        articles = devotional_list.find_all('article')

        for article in articles:
            link = article.find('a', href=True)
            if link and 'devotionals/' in link['href']:
                full_link = f"https://imwmantiquira.inpeaceapp.com{link['href']}"
                links.append(full_link)

        log_message(f"Extraídos {len(links)} links de cartas pastorais.")
        return links

    except Exception as e:
        log_message(f"ERRO ao extrair links: {str(e)}")
        return links

    finally:
        driver.quit()


def clean_theme(text):
    """Limpa o tema removendo prefixos"""
    prefixes = ["CARTA PASTORAL - ", "Carta Pastoral - ",
                "CARTA PASTORAL- ", "Carta Pastoral- "]
    for prefix in prefixes:
        if text.startswith(prefix):
            return text.replace(prefix, "", 1).strip()
    return text.strip()


def extract_bible_reference(text):
    """Extrai apenas a referência bíblica do texto"""
    # Remove citações e textos entre aspas
    if '"' in text:
        text = text.split('"')[-2] if text.count('"') >= 2 else text

    # Procura por padrões de referência bíblica usando regex compilados
    for pattern in BIBLE_REF_PATTERNS:
        match = pattern.search(text)
        if match:
            book = match.group('book').strip()
            chapter = match.group('chapter')
            verses = match.group('verses').strip()

            # Verifica se é uma abreviação e converte para nome completo
            if book in BIBLE_BOOKS:
                book = BIBLE_BOOKS[book]
            elif book + '.' in BIBLE_BOOKS:
                book = BIBLE_BOOKS[book + '.']

            return f"{book} {chapter}:{verses}"

    return text.strip()


def clean_topics(topics):
    """Limpa a lista de tópicos, removendo itens específicos e ignorando tudo após RECADOS IMPORTANTES e BATE-PAPO"""
    cleaned_topics = []
    recados_patterns = [
        "recados importantes",
        "recados importantes:",
        "recados",
        "aviso",
        "avisos",
        "avisos importantes",
        "avisos importantes:",
        "lembretes",
        "lembretes importantes",
        "informes",
        "Bate-Papo:",
        "bate-papo",
        "bate papo",
        "bate-papo:"
    ]

    # Encontra o índice do primeiro tópico que contém padrões de "recados importantes" ou "bate-papo"
    cut_index = len(topics)  # Inicialmente definido para o final da lista
    for i, topic in enumerate(topics):
        topic_lower = topic.lower().strip()
        if any(pattern in topic_lower for pattern in recados_patterns):
            cut_index = i
            break

    # Processa apenas os tópicos antes do corte
    for i, topic in enumerate(topics):
        if i >= cut_index:
            # Chegamos aos recados, bate-papo ou após, então paramos
            break

        topic_lower = topic.lower().strip()
        if topic_lower and topic_lower not in IGNORE_TOPICS:
            # Aplicar limpeza adicional para melhorar a qualidade dos tópicos
            # Remover numeração no início (1., 2., I., II., etc.)
            cleaned_topic = re.sub(
                r'^[0-9IVXivx]+[\.\)]\s*', '', topic).strip()

            # Adicionar apenas se não estiver vazio após limpeza
            if cleaned_topic:
                cleaned_topics.append(cleaned_topic)

    return cleaned_topics if cleaned_topics else ["Não encontrado"]


def extract_author(soup):
    """
    Extrai o autor da carta pastoral com múltiplas estratégias 
    para aumentar a assertividade, considerando a posição em relação aos recados
    """
    # Padrões comuns para nomes de pastores
    pastor_patterns = [
        r'Pr\.?\s+[A-ZÀ-Ú][a-zà-ú]+\s+[A-ZÀ-Ú][a-zà-ú]+',  # Pr. Nome Sobrenome
        r'Pr\.?\s+[A-ZÀ-Ú][a-zà-ú]+',                       # Pr. Nome
        # Pastor Nome Sobrenome
        r'Pastor\s+[A-ZÀ-Ú][a-zà-ú]+\s+[A-ZÀ-Ú][a-zà-ú]+',
        r'Pastor\s+[A-ZÀ-Ú][a-zà-ú]+',                      # Pastor Nome
        # Rev. Nome Sobrenome
        r'Rev\.?\s+[A-ZÀ-Ú][a-zà-ú]+\s+[A-ZÀ-Ú][a-zà-ú]+',
        r'Rev\.?\s+[A-ZÀ-Ú][a-zà-ú]+'                       # Rev. Nome
    ]

    # Padrões que indicam a seção de recados
    recados_patterns = [
        "recados importantes",
        "recados importantes:",
        "recados",
        "aviso",
        "avisos",
        "avisos importantes",
        "avisos importantes:",
        "lembretes",
        "lembretes importantes",
        "informes"
    ]

    # Obter todos os parágrafos
    paragraphs = soup.find_all('p')

    # Primeiro, identificar onde está a seção de recados (se existir)
    # Caso não encontre, considere o final do documento
    recados_index = len(paragraphs)
    for i, p in enumerate(paragraphs):
        p_text = p.get_text(strip=True).lower()
        if any(pattern in p_text for pattern in recados_patterns):
            recados_index = i
            break

    # Estratégia 1: Procurar em tags <strong> dentro de parágrafos (antes dos recados)
    strong_tags = soup.find_all('strong')
    for strong in strong_tags:
        parent_p = strong.find_parent('p')
        if parent_p and paragraphs.index(parent_p) < recados_index:
            text = strong.get_text(strip=True)
            for pattern in pastor_patterns:
                if re.search(pattern, text):
                    return text

    # Estratégia 2: Procurar em parágrafos vazios seguidos de parágrafos com nome de pastor
    for i in range(len(paragraphs) - 1):
        if i + 1 >= recados_index:  # Não olhe após a seção de recados
            break

        # Verifica se o parágrafo atual está vazio e o próximo tem padrão de pastor
        if paragraphs[i].get_text(strip=True) == "":
            next_p_text = paragraphs[i + 1].get_text(strip=True)
            for pattern in pastor_patterns:
                if re.search(pattern, next_p_text):
                    return next_p_text

    # Estratégia 3: Procurar em qualquer parágrafo que contenha apenas o nome do pastor (antes dos recados)
    for i, p in enumerate(paragraphs):
        if i >= recados_index:
            break

        text = p.get_text(strip=True)
        # Verifica se o texto é curto (provavelmente só o nome) e corresponde a um padrão de pastor
        if len(text) < 50:  # Limite de tamanho para evitar textos grandes
            for pattern in pastor_patterns:
                if re.search(pattern, text):
                    return text

    # Estratégia 4: Buscar nos parágrafos imediatamente antes da seção de recados
    # Analisa os 5 parágrafos antes da seção de recados
    start_idx = max(0, recados_index - 5)
    for i in range(start_idx, recados_index):
        text = paragraphs[i].get_text(strip=True)
        for pattern in pastor_patterns:
            if re.search(pattern, text):
                return text

    # Estratégia 5: Continuar com a busca nos últimos parágrafos se todas as anteriores falharem
    # Isso é uma última tentativa, especialmente se não houver seção de recados
    last_paragraphs = paragraphs[-5:] if len(paragraphs) >= 5 else paragraphs
    for p in last_paragraphs:
        text = p.get_text(strip=True)
        for pattern in pastor_patterns:
            if re.search(pattern, text):
                return text

    return "Não encontrado"


def process_devotional(url, processed_urls):
    """Processa uma única carta pastoral"""
    if url in processed_urls:
        log_message(f"Pulando {url} (já processada)")
        return None

    try:
        log_message(f"Processando: {url}")
        driver = setup_driver()

        try:
            driver.get(url)
            # Espera dinâmica e mais inteligente
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.CLASS_NAME, "devotional-header__title"))
            )

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Tema da Carta
            theme_elem = soup.select_one('.devotional-header__title')
            theme = clean_theme(theme_elem.get_text(
                strip=True)) if theme_elem else "Não encontrado"

            # Texto Bíblico principal
            base_text = "Não encontrado"
            base_text_elem = soup.find('em', string=lambda t: t and (
                "Texto base:" in t or "Texto Base:" in t))

            if base_text_elem:
                base_text = base_text_elem.get_text(strip=True)
            else:
                # Busca eficiente por textos com nomes de livros bíblicos
                paragraphs = soup.find_all('p')
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    # Verifica se o texto contém padrões de referência bíblica
                    for pattern in BIBLE_REF_PATTERNS:
                        if pattern.search(text):
                            base_text = text
                            break
                    if base_text != "Não encontrado":
                        break

            if base_text != "Não encontrado":
                base_text = extract_bible_reference(base_text)

            # Tópicos principais - busca mais eficiente
            topics = [strong.get_text(strip=True) for strong in soup.find_all('strong')
                      if strong.get_text(strip=True)]
            topics = clean_topics(topics) if topics else ["Não encontrado"]

            # Autor da carta - usando a nova função robusta
            author = extract_author(soup)

            data = {
                "url": url,
                "tema": theme,
                "texto_biblico": base_text,
                "topicos": topics,
                "autor": author
            }

            log_message(f"Processado com sucesso: {url}")
            return data

        finally:
            driver.quit()

    except Exception as e:
        log_message(f"ERRO ao processar {url}: {str(e)}")
        return None


def main():
    """Função principal otimizada com ThreadPoolExecutor e melhor gerenciamento de recursos"""
    # Inicializa o processamento
    log_message("Iniciando a coleta dos links das cartas pastorais...")

    # Obtém os links primeiro
    links = extract_links_with_selenium()
    if not links:
        log_message("Nenhum link encontrado. Encerrando.")
        return

    # Carrega dados existentes para evitar reprocessamento
    results = load_existing_data()
    processed_urls = {item['url'] for item in results}
    log_message(f"Carregados {len(results)} registros existentes.")

    # Filtra apenas links não processados
    links_to_process = [link for link in links if link not in processed_urls]
    log_message(
        f"Total de {len(links_to_process)} novos links para processar.")

    if not links_to_process:
        log_message("Nenhum novo link para processar. Encerrando.")
        return

    # Usa ThreadPoolExecutor para processamento paralelo (mais leve que multiprocessing para I/O bound)
    max_workers = min(os.cpu_count() * 2, 8)  # Limita a 8 threads máximas
    log_message(
        f"Iniciando processamento paralelo com {max_workers} threads...")

    new_results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Prepara a lista de tarefas
        futures = [executor.submit(
            process_devotional, url, processed_urls) for url in links_to_process]

        # Processa os resultados à medida que são concluídos
        for future in futures:
            result = future.result()
            if result:
                new_results.append(result)
                # Salva incrementalmente a cada 5 novos resultados
                if len(new_results) % 5 == 0:
                    combined_results = results + new_results
                    save_data(combined_results)
                    log_message(
                        f"Salvamento incremental: {len(combined_results)} registros")

    # Adiciona os novos resultados aos existentes
    results.extend(new_results)

    # Salva todos os resultados
    save_data(results)

    log_message(
        f"Processo finalizado. {len(new_results)} novos devocionais adicionados. Total: {len(results)}.")


if __name__ == "__main__":
    main()
