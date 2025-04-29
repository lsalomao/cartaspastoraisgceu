document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const devotionalCards = document.getElementById('devotionalCards');
    const infoAlert = document.getElementById('infoAlert');
    const totalPregacoes = document.getElementById('totalPregacoes');
    const pregadoresUnicos = document.getElementById('pregadoresUnicos');
    const autorFilter = document.getElementById('autorFilter');
    const temaFilter = document.getElementById('temaFilter');
    const bibliaFilter = document.getElementById('bibliaFilter');
    const aplicarFiltroBtn = document.getElementById('aplicarFiltro');
    const limparFiltroBtn = document.getElementById('limparFiltro');
    
    // Template para cards
    const devotionalTemplate = document.getElementById('devotionalTemplate');
    
    // Dados completos dos devocionais
    let devotionalsData = [];
    
    // Função para carregar os dados
    async function loadDevotionals() {
        try {
            infoAlert.textContent = 'Carregando dados...';
            infoAlert.style.display = 'block';
            
            const response = await fetch('/api/devotionals');
            if (!response.ok) {
                throw new Error('Falha ao carregar os dados');
            }
            
            devotionalsData = await response.json();
            
            // Exibir os dados
            displayDevotionals(devotionalsData);
            updateStats(devotionalsData);
            
            infoAlert.style.display = 'none';
        } catch (error) {
            console.error('Erro:', error);
            infoAlert.textContent = 'Erro ao carregar os dados. Tente novamente mais tarde.';
            infoAlert.className = 'alert alert-danger';
        }
    }
    
    // Função para exibir os devocionais
    function displayDevotionals(devotionals) {
        // Limpar conteúdo anterior
        devotionalCards.innerHTML = '';
        
        if (devotionals.length === 0) {
            infoAlert.textContent = 'Nenhum resultado encontrado para os filtros aplicados.';
            infoAlert.className = 'alert alert-warning';
            infoAlert.style.display = 'block';
            return;
        }
        
        // Ordenar por tema
        devotionals.sort((a, b) => (a.tema || '').localeCompare(b.tema || ''));
        
        // Criar e adicionar cards
        devotionals.forEach((devotional, index) => {
            // Clonar o template
            const card = devotionalTemplate.content.cloneNode(true);
            
            // Adicionar atraso para animação escalonada
            const devotionalCard = card.querySelector('.devotional-card');
            devotionalCard.style.animationDelay = `${index * 0.05}s`;
            
            // Preencher dados
            card.querySelector('.tema').textContent = devotional.tema || 'Sem título';
            card.querySelector('.text-biblico').textContent = devotional.texto_biblico || 'Texto bíblico não especificado';
            card.querySelector('.autor').textContent = devotional.autor || 'Autor desconhecido';
            
            // Preencher tópicos
            const topicosList = card.querySelector('.topicos-list');
            if (devotional.topicos && devotional.topicos.length > 0) {
                devotional.topicos.forEach(topico => {
                    const li = document.createElement('li');
                    li.textContent = topico;
                    topicosList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'Nenhum tópico disponível';
                topicosList.appendChild(li);
            }
            
            // Adicionar link
            const linkUrl = card.querySelector('.link-url');
            if (devotional.url) {
                linkUrl.href = devotional.url;
            } else {
                linkUrl.style.display = 'none';
            }
            
            // Adicionar card ao container
            devotionalCards.appendChild(card);
        });
    }
    
    // Função para atualizar estatísticas
    function updateStats(devotionals) {
        // Total de pregações
        totalPregacoes.textContent = devotionals.length;
        
        // Pregadores únicos
        const autores = new Set();
        devotionals.forEach(devotional => {
            if (devotional.autor) {
                autores.add(devotional.autor);
            }
        });
        pregadoresUnicos.textContent = autores.size;
    }
    
    // Função para aplicar filtros
    function applyFilters() {
        const autorValue = autorFilter.value.toLowerCase().trim();
        const temaValue = temaFilter.value.toLowerCase().trim();
        const bibliaValue = bibliaFilter.value.toLowerCase().trim();
        
        // Se não houver filtros, mostrar todos
        if (!autorValue && !temaValue && !bibliaValue) {
            displayDevotionals(devotionalsData);
            updateStats(devotionalsData);
            infoAlert.style.display = 'none';
            return;
        }
        
        // Filtrar dados
        const filteredData = devotionalsData.filter(devotional => {
            const autor = (devotional.autor || '').toLowerCase();
            const tema = (devotional.tema || '').toLowerCase();
            const textoBiblico = (devotional.texto_biblico || '').toLowerCase();
            
            // Aplicar filtros
            if (autorValue && !autor.includes(autorValue)) return false;
            if (temaValue && !tema.includes(temaValue)) return false;
            if (bibliaValue && !textoBiblico.includes(bibliaValue)) return false;
            
            return true;
        });
        
        // Exibir resultados
        displayDevotionals(filteredData);
        updateStats(filteredData);
    }
    
    // Event listeners
    aplicarFiltroBtn.addEventListener('click', applyFilters);
    
    limparFiltroBtn.addEventListener('click', function() {
        autorFilter.value = '';
        temaFilter.value = '';
        bibliaFilter.value = '';
        displayDevotionals(devotionalsData);
        updateStats(devotionalsData);
        infoAlert.style.display = 'none';
    });
    
    // Permitir usar Enter para aplicar filtros
    [autorFilter, temaFilter, bibliaFilter].forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                applyFilters();
            }
        });
    });
    
    // Carregar dados iniciais
    loadDevotionals();
}); 