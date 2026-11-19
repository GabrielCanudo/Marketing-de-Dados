import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Dashboard de análise de NPS",
    layout="wide"
)

ZONAS = {
    'Zona Vermelha (Crítica)': (-100.0, -0.01),
    'Zona Amarela (Aperfeiçoamento)': (0.0, 49.99),
    'Zona Verde (Qualidade)': (50.0, 74.99),
    'Zona Azul (Excelência)': (75.0, 100.0)
}

CORES_ZONAS = {
    'Zona Vermelha (Crítica)': '#E74C3C',
    'Zona Amarela (Aperfeiçoamento)': '#F1C40F',
    'Zona Verde (Qualidade)': '#2ECC71',
    'Zona Azul (Excelência)': '#3498DB'
}

NOMES_CRITERIOS = {
    'CRITERIO1 (9 - I)': '1. Satisfação geral',
    'CRITERIO2 (10 - J)': '2. Qualidade da comunicação',
    'CRITERIO3 (11 - K)': '3. Especialização no setor',
    'CRITERIO4 (12 - L)': '4. Iniciativas de inovação',
    'CRITERIO5 (13 - M)': '5. Custos manutenção pós-venda',
    'CRITERIO6 (14 - N)': '6. Rapidez resolução de problemas',
    'CRITERIO7 (15 - O)': '7. Qualidade produtos e serviços',
    'CRITERIO8  (16 - P)': '8. Adaptação às necessidades',
    'CRITERIO9 (17 - Q)': '9. Atendimento dos colaboradores',
    'CRITERIO10 (18 - R)': '10. Especialização técnica',
    'CRITERIO11 (19 - S)': '11. Pontualidade no atendimento'
}

def classificar_zona(serie_nps):
    condicoes = [
        serie_nps < 0,
        serie_nps < 50,
        serie_nps < 75,
        serie_nps <= 100
    ]
    return np.select(condicoes, list(ZONAS.keys()), default='Fora da Faixa')


# CARREGAMENTO DOS DADOS
@st.cache_data
def carregar_dados():
    df = pd.read_excel("Dataset_NPS.xlsx", skiprows=[1])
    df['DATA_RESPOSTA'] = pd.to_datetime(df['DATA_RESPOSTA'])
    df['RESPOSTA_ANO'] = df['DATA_RESPOSTA'].dt.year
    return df

df = carregar_dados()

# 1. DADOS DOS CLIENTES
qntd_feedbacks = df['ID_RESPOSTA'].count()

feedback_por_ano = (
    df.groupby('RESPOSTA_ANO', as_index=False)['ID_RESPOSTA']
    .count()
    .rename(columns={'ID_RESPOSTA': 'QNTD_FEEDBACKS'})
)
feedback_por_ano['RESPOSTA_ANO'] = feedback_por_ano['RESPOSTA_ANO'].astype(str)

feedback_por_pais = (
    df.groupby('PAIS', as_index=False)['ID_RESPOSTA']
    .count()
    .rename(columns={'ID_RESPOSTA': 'QNTD_FEEDBACKS'})
    .sort_values('QNTD_FEEDBACKS', ascending=False)
)

feedback_por_canal = (
    df.groupby('CANAL', as_index=False)['ID_RESPOSTA']
    .count()
    .rename(columns={'ID_RESPOSTA': 'QNTD_FEEDBACKS'})
    .sort_values('QNTD_FEEDBACKS', ascending=False)
)

# 2. DADOS DO NPS (BASE GERAL)
df_promotores = df[df['RESPOSTA_NPS'].between(9, 10)]
df_neutros = df[df['RESPOSTA_NPS'].between(7, 8)]
df_detratores = df[df['RESPOSTA_NPS'].between(0, 6)]

qntd_promotores = df_promotores['ID_RESPOSTA'].count()
qntd_neutros = df_neutros['ID_RESPOSTA'].count()
qntd_detratores = df_detratores['ID_RESPOSTA'].count()

metrica_promotores = qntd_promotores / qntd_feedbacks
metrica_neutros = qntd_neutros / qntd_feedbacks
metrica_detratores = qntd_detratores / qntd_feedbacks

nps_geral_oficial = (metrica_promotores - metrica_detratores) * 100
nps_medio = df['RESPOSTA_NPS'].mean()

nps_anual_geral = (
    df.groupby('RESPOSTA_ANO', as_index=False)
    .agg(
        TOTAL_FEEDBACKS=('ID_RESPOSTA', 'count'),
        PROMOTORES=('RESPOSTA_NPS', lambda x: x.between(9, 10).sum()),
        NEUTROS=('RESPOSTA_NPS', lambda x: x.between(7, 8).sum()),
        DETRATORES=('RESPOSTA_NPS', lambda x: x.between(0, 6).sum()),
        MEDIA_NOTA=('RESPOSTA_NPS', 'mean')
    )
)
nps_anual_geral['PCT_PROMOTORES'] = (nps_anual_geral['PROMOTORES'] / nps_anual_geral['TOTAL_FEEDBACKS'] * 100).round(2)
nps_anual_geral['PCT_NEUTROS'] = (nps_anual_geral['NEUTROS'] / nps_anual_geral['TOTAL_FEEDBACKS'] * 100).round(2)
nps_anual_geral['PCT_DETRATORES'] = (nps_anual_geral['DETRATORES'] / nps_anual_geral['TOTAL_FEEDBACKS'] * 100).round(2)
nps_anual_geral['NPS_OFICIAL'] = (nps_anual_geral['PCT_PROMOTORES'] - nps_anual_geral['PCT_DETRATORES']).round(2)
nps_anual_geral['RESPOSTA_ANO'] = nps_anual_geral['RESPOSTA_ANO'].astype(str)

# 3. DADOS DA EMPRESA (Company2420)
df_empresa = df[df['EMPRESA'] == 'Company2420'].copy()
qntd_feedbacks_empresa = df_empresa['ID_RESPOSTA'].count()

resumo_anual_empresa = (
    df_empresa.groupby('RESPOSTA_ANO', as_index=False)
    .agg(
        TOTAL_FEEDBACKS=('ID_RESPOSTA', 'count'),
        MEDIA_NOTA=('RESPOSTA_NPS', 'mean'),
        QNTD_PROMOTORES=('RESPOSTA_NPS', lambda x: x.between(9, 10).sum()),
        QNTD_NEUTROS=('RESPOSTA_NPS', lambda x: x.between(7, 8).sum()),
        QNTD_DETRATORES=('RESPOSTA_NPS', lambda x: x.between(0, 6).sum()),
    )
)
resumo_anual_empresa['PCT_PROMOTORES'] = (resumo_anual_empresa['QNTD_PROMOTORES'] / resumo_anual_empresa['TOTAL_FEEDBACKS'] * 100).round(2)
resumo_anual_empresa['PCT_DETRATORES'] = (resumo_anual_empresa['QNTD_DETRATORES'] / resumo_anual_empresa['TOTAL_FEEDBACKS'] * 100).round(2)
resumo_anual_empresa['NPS_OFICIAL'] = (resumo_anual_empresa['PCT_PROMOTORES'] - resumo_anual_empresa['PCT_DETRATORES']).round(2)
resumo_anual_empresa['ZONA'] = classificar_zona(resumo_anual_empresa['NPS_OFICIAL'])

idx_min = resumo_anual_empresa['NPS_OFICIAL'].idxmin()
idx_max = resumo_anual_empresa['NPS_OFICIAL'].idxmax()
menor_ano = resumo_anual_empresa.loc[idx_min, 'RESPOSTA_ANO']
menor_nps = resumo_anual_empresa.loc[idx_min, 'NPS_OFICIAL']
maior_ano = resumo_anual_empresa.loc[idx_max, 'RESPOSTA_ANO']
maior_nps = resumo_anual_empresa.loc[idx_max, 'NPS_OFICIAL']

# 4. DADOS DO SETOR (Energia)
df_setor = df[df['SETOR'] == 'Energia'].copy()
qntd_feedbacks_setor = df_setor['ID_RESPOSTA'].count()

resumo_anual_setor = (
    df_setor.groupby('RESPOSTA_ANO', as_index=False)
    .agg(
        TOTAL_FEEDBACKS=('ID_RESPOSTA', 'count'),
        MEDIA_NOTA=('RESPOSTA_NPS', 'mean'),
        QNTD_PROMOTORES=('RESPOSTA_NPS', lambda x: x.between(9, 10).sum()),
        QNTD_NEUTROS=('RESPOSTA_NPS', lambda x: x.between(7, 8).sum()),
        QNTD_DETRATORES=('RESPOSTA_NPS', lambda x: x.between(0, 6).sum()),
    )
)
resumo_anual_setor['PCT_PROMOTORES'] = (resumo_anual_setor['QNTD_PROMOTORES'] / resumo_anual_setor['TOTAL_FEEDBACKS'] * 100).round(2)
resumo_anual_setor['PCT_DETRATORES'] = (resumo_anual_setor['QNTD_DETRATORES'] / resumo_anual_setor['TOTAL_FEEDBACKS'] * 100).round(2)
resumo_anual_setor['NPS_OFICIAL'] = (resumo_anual_setor['PCT_PROMOTORES'] - resumo_anual_setor['PCT_DETRATORES']).round(2)
resumo_anual_setor['ZONA'] = classificar_zona(resumo_anual_setor['NPS_OFICIAL'])

# 5. COMPARAÇÃO EMPRESA X SETOR
df_comparacao = pd.merge(
    resumo_anual_empresa[['RESPOSTA_ANO', 'NPS_OFICIAL']].rename(columns={'NPS_OFICIAL': 'Company2420'}),
    resumo_anual_setor[['RESPOSTA_ANO', 'NPS_OFICIAL']].rename(columns={'NPS_OFICIAL': 'Setor Energia'}),
    on='RESPOSTA_ANO'
)
df_comparacao['DIFERENCA'] = (df_comparacao['Company2420'] - df_comparacao['Setor Energia']).round(2)
df_comparacao['STATUS'] = np.where(df_comparacao['DIFERENCA'] >= 0, 'Acima do Setor', 'Abaixo do Setor')
df_comparacao['RESPOSTA_ANO'] = df_comparacao['RESPOSTA_ANO'].astype(str)

# 6. QUALITY SCORE (11 CRITÉRIOS - SEM CÁLCULO DE NPS)
colunas_criterios = list(NOMES_CRITERIOS.keys())
df_qualidade = pd.DataFrame({
    'Critério': list(NOMES_CRITERIOS.values()),
    'Média Geral': [df[c].mean().round(2) for c in colunas_criterios],
    'Média Setor (Energia)': [df_setor[c].mean().round(2) for c in colunas_criterios],
    'Média Empresa (Company2420)': [df_empresa[c].mean().round(2) for c in colunas_criterios]
}).sort_values('Média Empresa (Company2420)', ascending=False)

# 7. ANÁLISE POR PAÍS
def calcular_nps_pais(dataframe):
    res = (
        dataframe.groupby('PAIS', as_index=False)
        .agg(
            TOTAL_FEEDBACKS=('ID_RESPOSTA', 'count'),
            PROMOTORES=('RESPOSTA_NPS', lambda x: x.between(9, 10).sum()),
            NEUTROS=('RESPOSTA_NPS', lambda x: x.between(7, 8).sum()),
            DETRATORES=('RESPOSTA_NPS', lambda x: x.between(0, 6).sum()),
        )
    )
    res['PCT_PROMOTORES'] = (res['PROMOTORES'] / res['TOTAL_FEEDBACKS'] * 100).round(2)
    res['PCT_DETRATORES'] = (res['DETRATORES'] / res['TOTAL_FEEDBACKS'] * 100).round(2)
    res['NPS_OFICIAL'] = (res['PCT_PROMOTORES'] - res['PCT_DETRATORES']).round(2)
    return res.sort_values('NPS_OFICIAL', ascending=False)

resumo_paises_geral = calcular_nps_pais(df)
resumo_empresa_paises = calcular_nps_pais(df_empresa)

# INTERFACE VISUAL
st.title("Painel de análise de NPS")
st.caption("Informações abrangem dados disponíveis dos anos de 2017 à 2020")

aba1, aba2, aba3, aba4, aba5 = st.tabs([
    "Clientes e NPS global",
    "Empresa e setor",
    "Relações gráficas",
    "Pontuação qualitativa (11 Critérios)",
    "Análise por países"
])

# Painel 1
with aba1:
    st.subheader("Dados dos clientes e visão geral do NPS")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total de Respostas", f"{qntd_feedbacks:,}".replace(",", "."))
    c2.metric("NPS Geral Oficial", f"{nps_geral_oficial:.2f}")
    c3.metric("Promotores (9–10)", f"{qntd_promotores:,}".replace(",", "."))
    c3.badge(f"{metrica_promotores:.2%}")
    c4.metric("Neutros (7–8)", f"{qntd_neutros:,}".replace(",", "."))
    c4.badge(f"{metrica_neutros:.2%}")
    c5.metric("Detratores (0–6)", f"{qntd_detratores:,}".replace(",", "."))
    c5.badge(f"{metrica_detratores:.2%}")
    

    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig_ano = px.bar(
            feedback_por_ano, x='RESPOSTA_ANO', y='QNTD_FEEDBACKS',
            text='QNTD_FEEDBACKS', title='Quantidade de feedbacks por Ano',
            labels={'RESPOSTA_ANO': 'Ano', 'QNTD_FEEDBACKS': 'Feedbacks'}
        )
        fig_ano.update_traces(textposition='outside')
        st.plotly_chart(fig_ano, use_container_width=True)

    with col_g2:
        fig_canal = px.bar(
            feedback_por_canal, x='CANAL', y='QNTD_FEEDBACKS',
            text='QNTD_FEEDBACKS', color='CANAL',
            title='Distribuição dos feedbacks por canal',
            labels={'CANAL': 'Canal', 'QNTD_FEEDBACKS': 'Feedbacks'}
        )
        fig_canal.update_traces(textposition='outside', showlegend=False)
        st.plotly_chart(fig_canal, use_container_width=True)

    col_g3, col_g4 = st.columns(2)
    with col_g3:
        fig_nps_geral = px.line(
            nps_anual_geral, x='RESPOSTA_ANO', y='NPS_OFICIAL',
            markers=True, text='NPS_OFICIAL',
            title='Evolução do NPS oficial (global) por ano',
            labels={'RESPOSTA_ANO': 'Ano', 'NPS_OFICIAL': 'NPS Oficial'}
        )
        fig_nps_geral.update_traces(textposition='top center')
        fig_nps_geral.update_yaxes(range=[0, 50])
        st.plotly_chart(fig_nps_geral, use_container_width=True)

    with col_g4:
        fig_paises_vol = px.bar(
            feedback_por_pais.head(10), x='QNTD_FEEDBACKS', y='PAIS',
            orientation='h', text='QNTD_FEEDBACKS',
            title='Top 10 países em quantidade de feedbacks',
            labels={'PAIS': 'País', 'QNTD_FEEDBACKS': 'Feedbacks'}
        )
        fig_paises_vol.update_yaxes(autorange='reversed')
        st.plotly_chart(fig_paises_vol, use_container_width=True)

    st.dataframe(nps_anual_geral, use_container_width=True, hide_index=True)

# PAINEL 2
with aba2:
    st.subheader("Dados da empresa (2420)")
    e1, e2, e3 = st.columns(3)
    e1.metric("Quantidade de feedbacks", qntd_feedbacks_empresa)
    e2.metric("Melhor ano (NPS Oficial)", f"{maior_ano}")
    e2.badge(f"NPS: {maior_nps:.2f}")
    e3.metric("Pior ano (NPS Oficial)", f"{menor_ano}")
    e3.badge(f"NPS: {menor_nps:.2f}", color='red')

    resumo_anual_empresa_plot = resumo_anual_empresa.copy()
    resumo_anual_empresa_plot['RESPOSTA_ANO'] = resumo_anual_empresa_plot['RESPOSTA_ANO'].astype(str)

    col_e1, col_e2 = st.columns(2)
    with col_e1:
        df_emp_melt = resumo_anual_empresa_plot.melt(
            id_vars='RESPOSTA_ANO',
            value_vars=['QNTD_PROMOTORES', 'QNTD_NEUTROS', 'QNTD_DETRATORES'],
            var_name='Classificação', value_name='Quantidade'
        )
        fig_emp_class = px.bar(
            df_emp_melt, x='RESPOSTA_ANO', y='Quantidade', color='Classificação',
            barmode='group', text='Quantidade',
            title='Empresa 2420: Promotores, neutros e detratores por ano',
            color_discrete_map={
                'QNTD_PROMOTORES': '#2ECC71',
                'QNTD_NEUTROS': '#F1C40F',
                'QNTD_DETRATORES': '#E74C3C'
            },
        )
        st.plotly_chart(fig_emp_class, use_container_width=True)

    with col_e2:
        fig_emp_nps = px.line(
            resumo_anual_empresa_plot, x='RESPOSTA_ANO', y='NPS_OFICIAL',
            markers=True, text='NPS_OFICIAL',
            title='Empresa 2420: Evolução do NPS oficial por ano'
        )
        fig_emp_nps.update_traces(textposition='top center')
        st.plotly_chart(fig_emp_nps, use_container_width=True)

    st.dataframe(resumo_anual_empresa, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Dados do setor (Energia)")
    st.metric("Quantidade de feedbacks", qntd_feedbacks_setor)

    resumo_anual_setor_plot = resumo_anual_setor.copy()
    resumo_anual_setor_plot['RESPOSTA_ANO'] = resumo_anual_setor_plot['RESPOSTA_ANO'].astype(str)

    fig_setor_zona = px.bar(
        resumo_anual_setor_plot, x='RESPOSTA_ANO', y='NPS_OFICIAL',
        color='ZONA', text='NPS_OFICIAL',
        color_discrete_map=CORES_ZONAS,
        title='Setor de energia: NPS anual e zona de classificação',
        labels={'RESPOSTA_ANO': 'Ano', 'NPS_OFICIAL': 'NPS Oficial', 'ZONA': 'Zona'}
    )
    fig_setor_zona.update_traces(textposition='outside')
    st.plotly_chart(fig_setor_zona, use_container_width=True)
    st.dataframe(resumo_anual_setor, use_container_width=True, hide_index=True)

# PAINEL 3
with aba3:
    st.subheader("Relações entre EMPRESA x SETOR")
    df_comp_melt = df_comparacao.melt(
        id_vars='RESPOSTA_ANO',
        value_vars=['Company2420', 'Setor Energia'],
        var_name='Grupo', value_name='NPS_OFICIAL'
    )
    fig_comp = px.bar(
        df_comp_melt, x='RESPOSTA_ANO', y='NPS_OFICIAL', color='Grupo',
        barmode='group', text='NPS_OFICIAL',
        title='Comparativo anual de NPS oficial: Empresa vs. Setor',
        labels={'RESPOSTA_ANO': 'Ano', 'NPS_OFICIAL': 'NPS Oficial'}
    )
    fig_comp.update_traces(textposition='outside')
    st.plotly_chart(fig_comp, use_container_width=True)

    st.dataframe(df_comparacao, use_container_width=True, hide_index=True)
    st.info("Em todos os anos analisados (2017 a 2020), a empresa 2420 operou abaixo da média do setor de energia, com o maior distanciamento registrado em 2018 (-18,73 pontos).")

# PAINEL 4
with aba4:
    st.subheader("Pontuação qualitativa — Média dos 11 critérios")
    melhor_crit = df_qualidade.iloc[0]
    pior_crit = df_qualidade.iloc[-1]

    q1, q2 = st.columns(2)
    q1.metric("Melhor critério ", melhor_crit['Critério'], f"Média: {melhor_crit['Média Empresa (Company2420)']:.2f}")
    q2.metric("Pior critério", pior_crit['Critério'], f"Média: {pior_crit['Média Empresa (Company2420)']:.2f}", delta_color="inverse")

    fig_qual = px.bar(
        df_qualidade, x='Média Empresa (Company2420)', y='Critério',
        orientation='h', text='Média Empresa (Company2420)',
        title='Ranking dos 11 critérios de qualidade da empresa 2420',
        labels={'Média Empresa (Company2420)': 'Média (0–10)'}
    )
    fig_qual.update_yaxes(autorange='reversed')
    fig_qual.update_traces(textposition='outside')
    st.plotly_chart(fig_qual, use_container_width=True)

    st.dataframe(df_qualidade, use_container_width=True, hide_index=True)

# PAINEL 5
with aba5:
    st.subheader("Análise de NPS em países")
    escopo_pais = st.radio(
        "Selecione o escopo da análise geográfica:",
        ["Empresa 2420", "Global"],
        horizontal=True
    )
    df_pais_ativo = resumo_empresa_paises if escopo_pais == "Company2420" else resumo_paises_geral

    min_amostra = st.slider(
        "Filtrar países com quantidade mínima de feedbacks (evita distorção de países com 1 resposta):",
        min_value=1, max_value=50, value=5
    )
    df_pais_filtrado = df_pais_ativo[df_pais_ativo['TOTAL_FEEDBACKS'] >= min_amostra]

    if not df_pais_filtrado.empty:
        melhor_p = df_pais_filtrado.iloc[0]
        pior_p = df_pais_filtrado.iloc[-1]
        p1, p2 = st.columns(2)
        p1.metric(f"Melhor país", melhor_p['PAIS'], f"NPS: {melhor_p['NPS_OFICIAL']:.2f} ({melhor_p['TOTAL_FEEDBACKS']} resp.)")
        p2.metric(f"Pior país", pior_p['PAIS'], f"NPS: {pior_p['NPS_OFICIAL']:.2f} ({pior_p['TOTAL_FEEDBACKS']} resp.)", delta_color="inverse")

        fig_pais_nps = px.bar(
            df_pais_filtrado, x='PAIS', y='NPS_OFICIAL',
            text='NPS_OFICIAL', color='NPS_OFICIAL',
            color_continuous_scale='RdYlGn',
            title=f'NPS oficial dos países ({escopo_pais} — Mín. {min_amostra} de feedbacks)'
        )
        fig_pais_nps.update_traces(textposition='outside')
        st.plotly_chart(fig_pais_nps, use_container_width=True)

    st.dataframe(df_pais_ativo, use_container_width=True, hide_index=True)