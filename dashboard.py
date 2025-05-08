import json
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime, timedelta
import subprocess
import os
from fpdf import FPDF
import plotly.io as pio

# --- CONFIGURAÇÕES INICIAIS E ESTILO ---
st.set_page_config(page_title="Painel de Produtividade v2", layout="wide")

with open("custom_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- ESTADO DA SESSÃO ---
if 'clickup_api_token' not in st.session_state:
    st.session_state.clickup_api_token = None
# MODIFICAÇÃO: show_api_modal agora é True por padrão se o token não estiver carregado
# ou se o arquivo de configuração não existir. Será False se o token for carregado com sucesso.
if 'show_api_modal' not in st.session_state:
    st.session_state.show_api_modal = True 
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = "N/A"
    if os.path.exists("processed_tasks.json"):
        try:
            st.session_state.last_update_time = datetime.fromtimestamp(os.path.getmtime("processed_tasks.json")).strftime("%d/%m/%Y %H:%M:%S")
        except Exception:
            st.session_state.last_update_time = "N/A"
if 'processed_data_path' not in st.session_state:
    st.session_state.processed_data_path = "processed_tasks.json"
if 'config_path' not in st.session_state:
    st.session_state.config_path = "config.json"
if 'df_original' not in st.session_state:
    st.session_state.df_original = pd.DataFrame()
if 'filtered_df' not in st.session_state:
    st.session_state.filtered_df = pd.DataFrame()
if 'data_inicio_custom' not in st.session_state:
    st.session_state.data_inicio_custom = datetime.now().date() - timedelta(days=7)
if 'data_fim_custom' not in st.session_state:
    st.session_state.data_fim_custom = datetime.now().date()
if 'selected_period_label' not in st.session_state:
    st.session_state.selected_period_label = "Mês Atual"
if 'selected_area' not in st.session_state:
    st.session_state.selected_area = "Todas as Áreas"

# --- FUNÇÕES AUXILIARES ---
def load_config():
    if os.path.exists(st.session_state.config_path):
        try:
            with open(st.session_state.config_path, 'r') as f:
                config = json.load(f)
                st.session_state.clickup_api_token = config.get('CLICKUP_API_TOKEN')
                # MODIFICAÇÃO: Se o token for carregado com sucesso, não mostrar o modal automaticamente
                if st.session_state.clickup_api_token:
                    st.session_state.show_api_modal = False 
                else:
                    st.session_state.show_api_modal = True # Token não encontrado no config
        except json.JSONDecodeError:
            st.session_state.clickup_api_token = None
            st.session_state.show_api_modal = True # Erro ao ler config
            print("Erro ao decodificar config.json")
    else:
        st.session_state.show_api_modal = True # Arquivo config.json não existe

def save_config(token):
    with open(st.session_state.config_path, 'w') as f:
        json.dump({'CLICKUP_API_TOKEN': token}, f)
    st.session_state.clickup_api_token = token
    st.session_state.show_api_modal = False

def run_data_pipeline():
    if not st.session_state.clickup_api_token:
        st.error("Token da API do ClickUp não configurado. Configure-o primeiro.")
        st.session_state.show_api_modal = True
        return False
    with st.spinner("Atualizando tarefas do ClickUp e processando dados..."):
        save_config(st.session_state.clickup_api_token) # Garante que o token atual está salvo
        
        process_fetcher = subprocess.run(["python3", "clickup_fetcher.py"], capture_output=True, text=True)
        if process_fetcher.returncode != 0:
            st.error(f"Erro ao buscar dados do ClickUp: {process_fetcher.stderr}")
            return False
        
        process_scorer = subprocess.run(["python3", "scoring_logic.py"], capture_output=True, text=True)
        if process_scorer.returncode != 0:
            st.error(f"Erro ao processar os dados: {process_scorer.stderr}")
            return False
        
        st.session_state.last_update_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.success("✅ Dados atualizados com sucesso!")
        st.session_state.df_original = load_data_from_file()
        return True

def load_data_from_file():
    try:
        with open(st.session_state.processed_data_path) as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        if not df.empty:
            df["data"] = pd.to_datetime(df["data"])
            df['tags'] = df['tags'].apply(lambda x: x if isinstance(x, list) else [])
        else:
            df = pd.DataFrame(columns=["responsavel", "pontos", "titulo", "data", "tags"]) 
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["responsavel", "pontos", "titulo", "data", "tags"])
    except json.JSONDecodeError:
        st.error("Erro ao ler o arquivo processed_tasks.json. Verifique o formato do arquivo.")
        return pd.DataFrame(columns=["responsavel", "pontos", "titulo", "data", "tags"])

def get_date_range(period_label, custom_start=None, custom_end=None):
    now = datetime.now()
    start_date, end_date = None, None
    if period_label == "Mês Atual":
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = (start_date + pd.offsets.MonthEnd(0)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period_label == "Últimos 7 dias":
        start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period_label == "Últimos 30 dias":
        start_date = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period_label == "Trimestre Atual":
        current_quarter = (now.month - 1) // 3 + 1
        start_date = datetime(now.year, 3 * current_quarter - 2, 1)
        end_date = (datetime(now.year, 3 * current_quarter, 1) + pd.offsets.MonthEnd(0)).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period_label == "Personalizado" and custom_start and custom_end:
        start_date = datetime.combine(custom_start, datetime.min.time())
        end_date = datetime.combine(custom_end, datetime.max.time())
    return start_date, end_date

def filter_data(df, period_label, area_label, custom_start=None, custom_end=None):
    if df.empty:
        return df
    temp_df = df.copy()
    start_date, end_date = get_date_range(period_label, custom_start, custom_end)

    if start_date and end_date:
        temp_df = temp_df[(temp_df['data'] >= pd.to_datetime(start_date)) & (temp_df['data'] <= pd.to_datetime(end_date))]

    if area_label != "Todas as Áreas":
        temp_df = temp_df[temp_df['tags'].apply(lambda x: area_label in x if isinstance(x, list) else False)]
    return temp_df

def calculate_percentage_change(current_value, previous_value):
    if previous_value is None or pd.isna(previous_value):
        return "-"
    if previous_value == 0:
        return "-" if current_value == 0 else "+∞%"
    if current_value == previous_value:
        return "0%"
    change = ((current_value - previous_value) / previous_value) * 100
    return f"{change:+.1f}%"

def generate_pdf(df_display, period_label, area_label, metrics_data, chart_path_monthly, chart_path_tags):
    pdf = FPDF(orientation='L', unit='mm', format='A4') 
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    try:
        pdf.add_font("NotoSansCJK", fname="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
        pdf.set_font("NotoSansCJK", size=10)
    except RuntimeError:
        pdf.set_font("Arial", size=10) 
        print("NotoSansCJK font not found, using Arial.")

    pdf.set_font_size(16)
    pdf.cell(0, 10, f"Painel de Produtividade v2 - Relatório", 0, 1, 'C')
    pdf.set_font_size(10)
    pdf.cell(0, 10, f"Período: {period_label} | Área: {area_label} | Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, 'C')
    pdf.ln(5)

    pdf.set_font_size(12)
    pdf.cell(0, 10, "Métricas Principais", 0, 1, 'L')
    pdf.set_font_size(10)
    
    metric_cell_width = (pdf.w - pdf.l_margin - pdf.r_margin) / 4 
    current_x = pdf.l_margin
    current_y = pdf.get_y()
    max_h = 0

    for i, (key, value_dict) in enumerate(metrics_data.items()):
        text = f"{key}:\n{value_dict['value']} ({value_dict['delta']})"
        pdf.set_xy(current_x, current_y)
        pdf.multi_cell(metric_cell_width, 8, text, 1, 'C')
        max_h = max(max_h, pdf.get_y() - current_y) # Altura da célula atual
        current_x += metric_cell_width
        if (i + 1) % 4 == 0:
            current_x = pdf.l_margin
            current_y += max_h
            max_h = 0
            pdf.ln(max_h) # Garante que pulou a linha corretamente
    pdf.set_y(current_y + max_h + 5) # Espaço após métricas

    pdf.set_font_size(12)
    pdf.cell(0, 10, "Gráficos de Desempenho", 0, 1, 'L')
    chart_width = (pdf.w - pdf.l_margin - pdf.r_margin - 10) / 2 

    y_before_charts = pdf.get_y()
    img_h_estimate = chart_width * 0.5 # Estimativa da altura da imagem

    if chart_path_monthly and os.path.exists(chart_path_monthly):
        pdf.image(chart_path_monthly, x=pdf.l_margin, y=y_before_charts, w=chart_width)
    if chart_path_tags and os.path.exists(chart_path_tags):
        pdf.image(chart_path_tags, x=pdf.l_margin + chart_width + 10, y=y_before_charts, w=chart_width)
    
    pdf.set_y(y_before_charts + img_h_estimate + 5) 

    if not df_display.empty:
        pdf.set_font_size(12)
        pdf.cell(0, 10, "Resumo dos Dados (Top 10 Tarefas)", 0, 1, 'L')
        pdf.set_font_size(8)
        cols_to_show = ["data", "titulo", "responsavel", "pontos"]
        effective_cols = [col for col in cols_to_show if col in df_display.columns]
        
        total_width_for_table = pdf.w - pdf.l_margin - pdf.r_margin
        col_widths_table = [total_width_for_table * 0.15, total_width_for_table * 0.50, total_width_for_table * 0.20, total_width_for_table * 0.15]

        for i, header in enumerate(effective_cols):
            pdf.cell(col_widths_table[i], 7, header.capitalize(), 1, 0, 'C')
        pdf.ln()
        for _, row in df_display.head(10).iterrows():
            for i, col_name in enumerate(effective_cols):
                cell_text = str(row[col_name])
                if col_name == 'data': cell_text = row[col_name].strftime('%Y-%m-%d')
                pdf.cell(col_widths_table[i], 6, cell_text, 1, 0, 'L' if i == 1 else 'C')
            pdf.ln()

    return pdf.output(dest='S').encode('latin1')

# --- CARREGAMENTO INICIAL --- 
load_config() # Carrega o token e define show_api_modal

if st.session_state.df_original.empty and st.session_state.clickup_api_token:
    # Tenta carregar dados se o token já existe e o df está vazio
    # Isso pode acontecer se o usuário já configurou o token antes
    st.session_state.df_original = load_data_from_file()
    if st.session_state.df_original.empty:
        # Se ainda estiver vazio, pode ser que o pipeline precise rodar
        # ou o arquivo processed_tasks.json não existe/está vazio.
        # Não rodar pipeline automaticamente aqui para evitar execuções longas no início.
        pass 

# --- MODAL DE CONFIGURAÇÃO DA API ---
# O modal só aparece se show_api_modal for True (token não existe ou botão de config foi clicado)
if st.session_state.show_api_modal:
    with st.form(key='api_token_form'):
        st.markdown("### Configuração da API do ClickUp")
        st.markdown("Para acessar seus dados do ClickUp, precisamos do seu token de API pessoal.")
        new_token = st.text_input("Token de API do ClickUp", value=st.session_state.clickup_api_token or "", type="password", help="Você pode obter seu token em: Configurações > Apps > Gerar API Token")
        submit_button = st.form_submit_button(label='Salvar e Carregar Dados')

        if submit_button:
            if new_token:
                save_config(new_token)
                st.success("Token salvo! Tentando carregar os dados...")
                if run_data_pipeline(): # run_data_pipeline já chama load_data_from_file()
                    st.session_state.filtered_df = filter_data(st.session_state.df_original, st.session_state.selected_period_label, st.session_state.selected_area, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)
                    st.rerun() # Rerun para aplicar o novo estado
                else:
                    # Se o pipeline falhar, manter o modal aberto
                    st.session_state.show_api_modal = True 
            else:
                st.error("Por favor, insira um token válido.")
    st.stop() # Impede a execução do resto da página se o modal estiver ativo

# --- CABEÇALHO SUPERIOR ---
header_cols = st.columns([0.6, 0.4])
with header_cols[0]:
    st.markdown("#### Painel de Produtividade v2")
with header_cols[1]:
    col_actions = st.columns([1,1,1,3])
    with col_actions[0]:
        if st.button("⚙️", help="Configurações"):
            st.session_state.show_api_modal = True # MODIFICAÇÃO: Botão de config ativa o modal
            st.rerun()
    with col_actions[1]:
        st.button("❓", help="Ajuda") 
    with col_actions[2]:
        if st.button("🔄", help="Atualizar Dados"):
            if run_data_pipeline():
                st.session_state.filtered_df = filter_data(st.session_state.df_original, st.session_state.selected_period_label, st.session_state.selected_area, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)
                st.rerun()
    with col_actions[3]:
         st.caption(f"Última atualização: {st.session_state.last_update_time}")

# --- NAVEGAÇÃO POR ABAS ---
tab_dashboard, tab_tarefas, tab_relatorios = st.tabs(["Dashboard", "Tarefas", "Relatórios"])

with tab_dashboard:
    st.markdown("### Visão Geral do Desempenho")
    
    with st.container():
        filter_cols = st.columns([1,1,0.7,0.7,1.2]) 
        with filter_cols[0]:
            periodo_options = ["Mês Atual", "Últimos 7 dias", "Últimos 30 dias", "Trimestre Atual", "Personalizado", "Tudo"]
            st.session_state.selected_period_label = st.selectbox("Período", periodo_options, index=periodo_options.index(st.session_state.selected_period_label))
        with filter_cols[1]:
            unique_tags = []
            if 'tags' in st.session_state.df_original.columns and not st.session_state.df_original.empty:
                # Garantir que tags sejam strings antes de aplicar métodos de string
                exploded_tags = st.session_state.df_original['tags'].explode()
                unique_tags = sorted(list(exploded_tags[exploded_tags.apply(lambda x: isinstance(x, str))].str.strip().replace('', pd.NA).dropna().unique()))
            area_options = ["Todas as Áreas"] + unique_tags
            st.session_state.selected_area = st.selectbox("Área", area_options, index=area_options.index(st.session_state.selected_area) if st.session_state.selected_area in area_options else 0)
        
        if st.session_state.selected_period_label == "Personalizado":
            with filter_cols[2]:
                st.session_state.data_inicio_custom = st.date_input("Data Início", value=st.session_state.data_inicio_custom, key="date_start_custom_dash")
            with filter_cols[3]:
                st.session_state.data_fim_custom = st.date_input("Data Fim", value=st.session_state.data_fim_custom, key="date_end_custom_dash")
        
        with filter_cols[4]:
            st.write("") 
            st.write("") 
            aplicar_filtros_button = st.button("Aplicar Filtros", key="apply_filters_dash")
            export_pdf_button_placeholder = st.empty()

    if aplicar_filtros_button:
        st.session_state.filtered_df = filter_data(st.session_state.df_original, st.session_state.selected_period_label, st.session_state.selected_area, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)
        # Não precisa de rerun aqui, o Streamlit atualiza com a mudança de estado do widget

    # Aplicar filtros na carga inicial ou se não houver df filtrado ainda, ou se os filtros mudaram
    if st.session_state.filtered_df.empty and not st.session_state.df_original.empty:
         st.session_state.filtered_df = filter_data(st.session_state.df_original, st.session_state.selected_period_label, st.session_state.selected_area, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)
    elif not st.session_state.df_original.empty: # Sempre recalcular se houver dados originais, para refletir mudanças nos filtros
        st.session_state.filtered_df = filter_data(st.session_state.df_original, st.session_state.selected_period_label, st.session_state.selected_area, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)

    df_display = st.session_state.filtered_df

    # --- Cards de Métricas ---
    st.markdown("#### Métricas Principais")
    metric_cols = st.columns(4)
    total_tarefas_atual = df_display.shape[0] if not df_display.empty else 0
    total_pontos_atual = df_display['pontos'].sum() if not df_display.empty and 'pontos' in df_display else 0
    
    df_anterior = pd.DataFrame()
    if not st.session_state.df_original.empty and st.session_state.selected_period_label not in ["Personalizado", "Tudo"]:
        prev_start_date, prev_end_date = None, None
        current_start_date, current_end_date = get_date_range(st.session_state.selected_period_label, st.session_state.data_inicio_custom, st.session_state.data_fim_custom)
        if current_start_date and current_end_date:
            delta_time = current_end_date - current_start_date
            prev_end_date = current_start_date - timedelta(microseconds=1)
            prev_start_date = prev_end_date - delta_time
            df_anterior = filter_data(st.session_state.df_original, "Personalizado", st.session_state.selected_area, prev_start_date.date(), prev_end_date.date())

    total_tarefas_anterior = df_anterior.shape[0] if not df_anterior.empty else None
    total_pontos_anterior = df_anterior['pontos'].sum() if not df_anterior.empty and 'pontos' in df_anterior else None

    metrics_data_for_pdf = {}
    val_tt_a = total_tarefas_atual
    delta_tt_a = calculate_percentage_change(total_tarefas_atual, total_tarefas_anterior)
    metric_cols[0].metric("Total de Tarefas", val_tt_a, delta_tt_a)
    metrics_data_for_pdf["Total de Tarefas"] = {"value": val_tt_a, "delta": delta_tt_a}

    val_tp_a = f"{total_pontos_atual:.0f}"
    delta_tp_a = calculate_percentage_change(total_pontos_atual, total_pontos_anterior)
    metric_cols[1].metric("Total de Pontos", val_tp_a, delta_tp_a)
    metrics_data_for_pdf["Total de Pontos"] = {"value": val_tp_a, "delta": delta_tp_a}
    
    media_pontos_pessoa_atual = (total_pontos_atual / df_display['responsavel'].nunique()) if not df_display.empty and df_display['responsavel'].nunique() > 0 else 0
    media_pontos_pessoa_anterior = (total_pontos_anterior / df_anterior['responsavel'].nunique()) if not df_anterior.empty and df_anterior['responsavel'].nunique() > 0 else None
    val_mpp = f"{media_pontos_pessoa_atual:.1f}"
    delta_mpp = calculate_percentage_change(media_pontos_pessoa_atual, media_pontos_pessoa_anterior)
    metric_cols[2].metric("Média Pontos/Pessoa", val_mpp, delta_mpp)
    metrics_data_for_pdf["Média Pontos/Pessoa"] = {"value": val_mpp, "delta": delta_mpp}
    
    meta_pontos_geral = 1000 
    progresso_meta = (total_pontos_atual / meta_pontos_geral) * 100 if meta_pontos_geral > 0 else 0
    delta_meta_display = f"{progresso_meta:.0f}%"
    if progresso_meta >= 100:
        delta_meta_display = f"🎉 {progresso_meta:.0f}% (Superada!)"
    val_ma = f"{total_pontos_atual:.0f}/{meta_pontos_geral}"
    metric_cols[3].metric("Meta Global Atingida", val_ma, delta_meta_display, delta_color=("off" if progresso_meta < 100 else "normal"))
    metrics_data_for_pdf["Meta Global Atingida"] = {"value": val_ma, "delta": delta_meta_display}

    # --- Top Performers ---
    st.markdown("#### Top Performers")
    performer_cols = st.columns(2)
    
    if not df_display.empty:
        prod_conteudo_df = df_display.groupby('responsavel').agg(pontos_prod=('pontos', 'sum'), tarefas_prod=('titulo', 'count')).reset_index().sort_values(by='pontos_prod', ascending=False)
        if not prod_conteudo_df.empty:
            top_produtor = prod_conteudo_df.iloc[0]
            with performer_cols[0]:
                st.markdown("**🏆 Produção de Conteúdo**")
                st.markdown(f"**{top_produtor['responsavel']}**")
                st.markdown(f"{top_produtor['pontos_prod']:.0f} pts ({top_produtor['tarefas_prod']} tarefas)")
        else:
            with performer_cols[0]:
                st.markdown("**🏆 Produção de Conteúdo**")
                st.markdown("Nenhum dado no período.")
    else:
        with performer_cols[0]:
            st.markdown("**🏆 Produção de Conteúdo**")
            st.markdown("Nenhum dado disponível.")

    cs_tags = ['satisfacao', 'renovacao', 'cancelamento'] 
    cs_task_titles_keywords = ['onboarding', 'check-point', 'reuniao', 'reuniões', 'projeto entregue'] 

    if not df_display.empty:
        def is_cs_task(row):
            # Verifica tags (case-insensitive)
            if isinstance(row['tags'], list) and any(cs_tag.lower() in [str(tag).lower() for tag in row['tags']] for cs_tag in cs_tags):
                return True
            # Verifica títulos de tarefas (case-insensitive)
            if isinstance(row['titulo'], str) and any(keyword.lower() in row['titulo'].lower() for keyword in cs_task_titles_keywords):
                return True
            return False

        cs_tasks_df = df_display[df_display.apply(is_cs_task, axis=1)]
        if not cs_tasks_df.empty:
            cs_performers_df = cs_tasks_df.groupby('responsavel').agg(pontos_cs=('pontos', 'sum'), tarefas_cs=('titulo', 'count')).reset_index().sort_values(by='pontos_cs', ascending=False)
            if not cs_performers_df.empty:
                top_cs_performer = cs_performers_df.iloc[0]
                with performer_cols[1]:
                    st.markdown("**🏅 Customer Success**")
                    st.markdown(f"**{top_cs_performer['responsavel']}**")
                    st.markdown(f"{top_cs_performer['pontos_cs']:.0f} pts ({top_cs_performer['tarefas_cs']} tarefas)")
            else:
                with performer_cols[1]:
                    st.markdown("**🏅 Customer Success**")
                    st.markdown("Nenhum performer de CS no período.")
        else:
            with performer_cols[1]:
                st.markdown("**🏅 Customer Success**")
                st.markdown("Nenhuma tarefa de CS no período.")
    else:
        with performer_cols[1]:
            st.markdown("**🏅 Customer Success**")
            st.markdown("Nenhum dado disponível.")

    # --- Gráficos ---
    st.markdown("#### Gráficos")
    chart_cols = st.columns(2)
    fig_monthly, fig_tags = None, None
    path_fig_monthly, path_fig_tags = "/home/ubuntu/monthly_performance.png", "/home/ubuntu/tags_distribution.png"
    os.makedirs("/home/ubuntu/", exist_ok=True)

    with chart_cols[0]:
        st.markdown("**Desempenho Mensal (Pontos)**")
        if not df_display.empty and 'data' in df_display.columns and 'pontos' in df_display.columns:
            try:
                monthly_performance = df_display.set_index('data').resample('ME')['pontos'].sum().reset_index()
                if not monthly_performance.empty:
                    fig_monthly = px.line(monthly_performance, x='data', y='pontos', title="Pontos Acumulados por Mês")
                    st.plotly_chart(fig_monthly, use_container_width=True)
                    pio.write_image(fig_monthly, path_fig_monthly, scale=2)
                else:
                    st.info("Não há dados suficientes no período selecionado para o gráfico de desempenho mensal.")
                    path_fig_monthly = None # No chart, no path
            except Exception as e:
                st.error(f"Erro ao gerar gráfico mensal: {e}")
                path_fig_monthly = None
        else:
            st.info("Dados insuficientes para o gráfico de desempenho mensal.")
            path_fig_monthly = None
            
    with chart_cols[1]:
        st.markdown("**Distribuição por Tipo de Tarefa (Tags)**")
        if not df_display.empty and 'tags' in df_display.columns and df_display['tags'].explode().nunique() > 0:
            tag_counts = df_display['tags'].explode().str.strip().replace('', pd.NA).dropna().value_counts().reset_index()
            tag_counts.columns = ['tag', 'count']
            fig_tags = px.pie(tag_counts.head(10), values='count', names='tag', title="Top 10 Tags (Representando Tipos de Tarefa)")
            st.plotly_chart(fig_tags, use_container_width=True)
            pio.write_image(fig_tags, path_fig_tags, scale=2)
        else:
            st.info("Dados insuficientes para o gráfico de distribuição por tipo de tarefa.")
            path_fig_tags = None
    
    if not df_display.empty:
        pdf_bytes = generate_pdf(df_display, st.session_state.selected_period_label, st.session_state.selected_area, metrics_data_for_pdf, path_fig_monthly, path_fig_tags)
        with filter_cols[4]: 
             export_pdf_button_placeholder.download_button(
                label="Exportar PDF",
                data=pdf_bytes,
                file_name=f"relatorio_produtividade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/octet-stream",
                key="download_pdf_dash"
            )
    else:
        with filter_cols[4]:
            export_pdf_button_placeholder.button("Exportar PDF", disabled=True, help="Nenhum dado para exportar", key="export_pdf_disabled_dash")

with tab_tarefas:
    st.markdown("### Detalhamento de Tarefas")
    if not df_display.empty:
        st.dataframe(df_display[["data", "titulo", "tags", "pontos", "responsavel"]].sort_values(by="data", ascending=False), use_container_width=True)
    else:
        st.info("Nenhuma tarefa para exibir. Atualize os dados ou verifique os filtros.")

with tab_relatorios:
    st.markdown("### Relatórios Avançados")
    st.info("Seção de Relatórios em desenvolvimento.")


