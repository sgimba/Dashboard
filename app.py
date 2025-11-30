"""ИНТЕРАКТИВНЫЙ ДАШБОРД - Проект РНФ № 25-28-20473
⚠️ Замените этот файл на app_full.py для полного функционала!
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(page_title="Дагестан: Демоэкономический Анализ", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    try:
        return {
            'regions': pd.read_csv('data/regions.csv'),
            'stats': pd.read_csv('data/regional_stats.csv'),
            'time_series': pd.read_csv('data/time_series.csv'),
            'metadata': json.load(open('data/metadata.json', 'r', encoding='utf-8'))
        }
    except Exception as e:
        st.error(f"Ошибка: {e}")
        return None

data = load_data()
if data is None: st.stop()

st.title("📊 Дагестан: Демоэкономический Анализ")
st.info("⚠️ Базовая версия. Замените app.py на app_full.py!")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Наблюдений", f"{data['metadata']['n_observations']:,}")
col2.metric("Регионов", data['metadata']['n_regions'])
col3.metric("Лет", "8 (2016-2023)")
col4.metric("Переменных", data['metadata']['n_variables'])

st.markdown("---")
st.subheader("⏱️ Динамика среднедушевого дохода")
fig = px.line(data['time_series'], x='year', y='doxodn', color='region', markers=True)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.success("✅ Dashboard работает! Теперь замените app.py на app_full.py для всех функций!")
