# Plano de Redesenho do Painel de Produtividade

Este documento acompanha o progresso do redesenho do Painel de Produtividade para que se assemelhe ao exemplo fornecido (https://manualentrada.my.canva.site/dagmpljr6xc).

## Tarefas Principais

- [X] **Análise Inicial (Concluído)**
  - [X] Analisar o site de exemplo do Canva.
  - [X] Clonar o repositório do site atual (https://github.com/Createsplz/Painel-de-Produtividade.git).
  - [X] Analisar a estrutura do projeto atual (foco em `dashboard.py` e `custom_style.css`).

- [X] **Extração de Requisitos e Planejamento (Concluído)**
  - [X] Detalhar elementos de design e funcionalidades do site Canva (conforme análise visual e estrutura do exemplo).
  - [X] Comparar com o site atual e identificar todas as diferenças e necessidades de implementação (detalhado abaixo).
  - [X] Criar um plano de implementação detalhado para cada componente/funcionalidade (esta lista de tarefas constitui o plano).

- [ ] **Implementação do Novo Design e Funcionalidades (Em Andamento)**
  - [ ] **Estrutura Geral e Navegação Superior:**
    - [X] Modificar o título principal para "Painel de Produtividade v2" (ou similar ao Canva).
    - [X] Reestruturar as abas atuais ("Painel Geral", "Painel Individual") para "Dashboard", "Tarefas", "Relatórios".
    - [X] Implementar um cabeçalho superior fixo contendo: Título, as novas abas, e à direita: "Última atualização: [data/hora]", ícone de Configurações (engrenagem), ícone de Ajuda (interrogação), e botão "Atualizar".
        - *Nota: O botão "Atualizar Dados Agora" existente foi movido/integrado aqui.*
  - [X] **Configuração da API do ClickUp (Modal/Pop-up):**
    - [X] Desenvolver um modal/pop-up que surge inicialmente (ou via ícone de Configurações) para o usuário inserir o Token da API do ClickUp.
    - [X] O modal deve conter um campo de input para o token, texto explicativo ("Para acessar seus dados do ClickUp...", "Você pode obter seu token em: Configurações > Apps > Gerar API Token"), e um botão "Salvar e Carregar Dados".
    - [X] Integrar a lógica para que o token inserido seja usado pelo `clickup_fetcher.py`. Considerar como armazenar/acessar este token de forma segura (ex: `st.session_state` e `config.json`).
  - [X] **Aba Dashboard - Filtros e Exportação:**
    - [X] Adicionar dropdown "Período" com opções: Mês Atual, Últimos 7 dias, Últimos 30 dias, Trimestre Atual, Personalizado, Tudo. (Lógica de filtragem implementada)
    - [X] Adicionar dropdown "Área" (ex: Todas as Áreas, Design, Conteúdo, Vídeo - *baseado nas listas do ClickUp já mencionadas*). (Lógica de filtragem implementada)
    - [X] Implementar botão "Aplicar Filtros" para atualizar os dados do dashboard conforme seleção.
    - [X] Implementar funcionalidade "Exportar PDF" para a visualização atual do dashboard. (Implementado com FPDF2 e imagens dos gráficos Plotly)
  - [ ] **Aba Dashboard - Conteúdo Principal:**
    - [X] **Cards de Métricas Superiores:** Implementar quatro cards de métricas principais:
        - Total de Tarefas (com ícone e % de variação vs. período anterior).
        - Total de Pontos (com ícone e % de variação vs. período anterior).
        - Média por Pessoa (Tarefas ou Pontos) (com ícone e % de variação vs. período anterior).
        - Meta Atingida (100 pontos = meta, com ícone e %- [X] **Implementação do Novo Design e Funcionalidades (Concluído)**
  - [X] **Estrutura Geral e Navegação Superior:**
    - [X] Modificar o título principal para "Painel de Produtividade v2" (ou similar ao Canva).
    - [X] Reestruturar as abas atuais ("Painel Geral", "Painel Individual") para "Dashboard", "Tarefas", "Relatórios".
    - [X] Implementar um cabeçalho superior fixo contendo: Título, as novas abas, e à direita: "Última atualização: [data/hora]", ícone de Configurações (engrenagem), ícone de Ajuda (interrogação), e botão "Atualizar".
        - *Nota: O botão "Atualizar Dados Agora" existente foi movido/integrado aqui.*
  - [X] **Configuração da API do ClickUp (Modal/Pop-up):**
    - [X] Desenvolver um modal/pop-up que surge inicialmente (ou via ícone de Configurações) para o usuário inserir o Token da API do ClickUp.
    - [X] O modal deve conter um campo de input para o token, texto explicativo ("Para acessar seus dados do ClickUp...", "Você pode obter seu token em: Configurações > Apps > Gerar API Token"), e um botão "Salvar e Carregar Dados".
    - [X] Integrar a lógica para que o token inserido seja usado pelo `clickup_fetcher.py`. Considerar como armazenar/acessar este token de forma segura (ex: `st.session_state` e `config.json`).
  - [X] **Aba Dashboard - Filtros e Exportação:**
    - [X] Adicionar dropdown "Período" com opções: Mês Atual, Últimos 7 dias, Últimos 30 dias, Trimestre Atual, Personalizado, Tudo. (Lógica de filtragem implementada)
    - [X] Adicionar dropdown "Área" (ex: Todas as Áreas, Design, Conteúdo, Vídeo - *baseado nas listas do ClickUp já mencionadas*). (Lógica de filtragem implementada)
    - [X] Implementar botão "Aplicar Filtros" para atualizar os dados do dashboard conforme seleção.
    - [X] Implementar funcionalidade "Exportar PDF" para a visualização atual do dashboard. (Implementado com FPDF2 e imagens dos gráficos Plotly)
  - [X] **Aba Dashboard - Conteúdo Principal:**
    - [X] **Cards de Métricas Superiores:** Implementar quatro cards de métricas principais:
        - Total de Tarefas (com ícone e % de variação vs. período anterior).
        - Total de Pontos (com ícone e % de variação vs. período anterior).
        - Média por Pessoa (Tarefas ou Pontos) (com ícone e % de variação vs. período anterior).
        - Meta Atingida (100 pontos = meta, com ícone e % de variação vs. período anterior. Incluir incentivo para meta superada).
    - [X] **Seção "Top Performers":** Implementar dois cards destacados:
        - [X] "Produção de Conteúdo": Baseado em tarefas concluídas. Tags influenciam para detalhamento.
        - [X] "Customer Success": Baseado em tags (satisfação, renovação, cancelamento) E tipos de tarefa específicos (Conclusão de Onboarding, check-points mensal, reuniões agendadas, projetos entregues).
    - [X] **Gráficos Inferiores:**
        - [X] Implementar gráfico "Desempenho Mensal" (ex: evolução de pontos ou tarefas ao longo do tempo).
        - [X] Implementar gráfico "Distribuição por Tipo de Tarefa" (ex: gráfico de pizza mostrando a proporção de tarefas por Design, Conteúdo, Vídeo).
  - [X] **Aba Tarefas:**
    - [X] Implementar tabela detalhada de todas as tarefas filtradas, com opções de busca, ordenação e filtro de data personalizada.
  - [X] **Aba Relatórios:**
    - [X] Definir e implementar o conteúdo e funcionalidades. (Seção informativa implementada, PDF no dashboard)
  - [X] **Estilo Visual (CSS e Layout):**
    - [X] Revisar e expandir `custom_style.css` para replicar a paleta de cores (roxos, azuis, cinzas), fontes, espaçamentos, bordas arredondadas, sombras e layout geral do exemplo do Canva.
    - [X] Utilizar ícones apropriados para métricas, botões e seções.
    - [X] Garantir que o layout seja responsivo e se adapte bem a diferentes tamanhos de tela.
- [X] **Testes (Concluído)**
  - [X] Testar a funcionalidade de inserção e uso do token da API.
  - [X] Testar os filtros de Período e Área.
  - [X] Testar a exportação para PDF.
  - [X] Verificar a correta exibição de todos os cards de métricas e gráficos.
  - [X] Validar a navegação entre as abas.
  - [X] Verificar a fidelidade visual com o exemplo do Canva.
  - [X] Testar a responsividade do layout.
  - [X] Testar o fluxo do modal de token (só aparecer quando necessário).

- [ ] **Entrega e Implantação (Em Andamento)** do projeto atualizados em um arquivo zip.
  - [ ] Discutir opções de implantação (ex: Streamlit Cloud, servidor próprio) se solicitado.

## Pontos a Esclarecer com o Usuário:

- [PENDENTE] Para "Customer Success" nos "Top Performers", quais são os "tipos de tarefa" específicos que devemos considerar, além das tags (satisfação, renovação, cancelamento)?
- [PENDENTE - PARCIALMENTE RESPONDIDO] Qual o conteúdo e funcionalidades esperadas para as novas abas "Tarefas" e "Relatórios"? (Aba Tarefas: tabela detalhada com busca, ordenação e filtro de data personalizada. Aba Relatórios: aguardando mais detalhes).

## Arquivos Relevantes

- `dashboard.py`: Script principal do Streamlit.
- `custom_style.css`: Folha de estilos customizada.
- `clickup_fetcher.py`: Script para buscar dados do ClickUp.
- `scoring_logic.py`: Script para processar e pontuar tarefas.
- `processed_tasks.json`: Arquivo com os dados processados.
- `painel_canva_screenshot.webp`: Captura de tela do site de exemplo do Canva (já visualizado).
