"""
🚀 НАУЧНЫЙ ДАШБОРД РНФ № 25-28-20473
Версия 4.0 FINAL MERGED - Стабильная отчетность + Научные инструменты
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# ============================================================================
# 1. КОНФИГУРАЦИЯ И СТИЛИ
# ============================================================================

st.set_page_config(
    page_title="Демоэкономика Дагестана | РНФ",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    'primary': '#1e3a8a',
    'dagestan': '#dc2626',
    'russia': '#3b82f6',
    'warning': '#f59e0b',
    'cluster': ['#3b82f6', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6']
}

# CSS для красивых плашек
st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 2rem; border-radius: 1rem; margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(30, 58, 138, 0.3); text-align: center;
    }
    .metric-card {
        background: white; padding: 1.5rem; border-radius: 0.8rem;
        border-left: 5px solid #dc2626; box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    .science-box {
        background: #f0f9ff; border: 1px solid #bae6fd; padding: 1.5rem;
        border-radius: 0.8rem; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# 2. ЗАГРУЗКА И ПОДГОТОВКА ДАННЫХ
# ============================================================================

REGION_NAMES = {
    '01': 'Алтайский край', '03': 'Краснодарский край', '07': 'Ставропольский край',
    '12': 'Астраханская область', '18': 'Волгоградская область', '26': 'Республика Ингушетия',
    '40': 'Санкт-Петербург', '45': 'Москва', '46': 'Московская область',
    '60': 'Ростовская область', '76': 'Забайкальский край', '79': 'Республика Адыгея',
    '80': 'Республика Башкортостан', '81': 'Республика Бурятия', '82': 'Республика Дагестан',
    '83': 'Кабардино-Балкарская Респ.', '84': 'Республика Алтай', '85': 'Республика Калмыкия',
    '90': 'Северная Осетия', '91': 'Карачаево-Черкесия', '92': 'Республика Татарстан',
    '93': 'Республика Тыва', '96': 'Чеченская Республика', '99': 'Еврейская АО',
}

VAR_NAMES = {
    'doxodn': 'Доход (руб)',
    'r1v2': 'Возраст (лет)',
    'chlico': 'Размер семьи (чел)',
    'food_share': 'Траты на еду (%)',
    'savings_rate': 'Сбережения (%)',
    'mest_urban_pct': 'Урбанизация (%)',
    'pol_female_pct': 'Доля женщин (%)',
}

CLUSTER_NAMES = {
    0: 'K0: Пожилые', 1: 'K1: Средний класс', 2: 'K2: Городская молодежь',
    3: 'K3: Многодетные', 4: 'K4: Сельские (натуральное хоз-во)'
}

@st.cache_data
def load_data():
    try:
        data_dir = Path('data')
        stats = pd.read_csv(data_dir / 'regional_stats.csv')
        dist = pd.read_csv(data_dir / 'cluster_distribution.csv')
        profiles = pd.read_csv(data_dir / 'cluster_profiles.csv')
        
        # Обработка ter
        for df in [stats, dist]:
            if 'ter' in df.columns:
                df['ter'] = df['ter'].astype(str).str.strip()
                df['region_name'] = df['ter'].map(REGION_NAMES).fillna(df['ter'])
                
        return {'stats': stats, 'clusters': dist, 'profiles': profiles}
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None

data = load_data()
if data is None: st.stop()

def format_num(val, decimals=0):
    if pd.isna(val): return "—"
    s = f"{val:,.{decimals}f}".replace(',', ' ')
    return s.replace('.', ',')

# ============================================================================
# 3. НАВИГАЦИЯ
# ============================================================================

with st.sidebar:
    st.markdown("## 🧭 Навигация")
    page = st.radio("Раздел:", [
        "🏠 Главная (Отчет)",
        "🔮 Симулятор 2030 (Наука)",
        "🕵️ Микро-детектор (Наука)",
        "🗺️ Карта регионов",
        "📊 Сравнение и Динамика",
        "🎯 Кластеры (Анализ)",
        "📥 Скачать данные"
    ])
    st.info("РНФ № 25-28-20473\nГимбатов Ш.М.")

# ============================================================================
# 4. СТРАНИЦЫ
# ============================================================================

# --- ГЛАВНАЯ ---
if page == "🏠 Главная (Отчет)":
    st.markdown("""
    <div class="hero">
        <h1>🎯 ДЕМОЭКОНОМИЧЕСКИЙ АНАЛИЗ ДАГЕСТАНА</h1>
        <p>Выявление скрытых паттернов с помощью машинного обучения</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Ключевая находка
    st.markdown("""
    <div style="background: linear-gradient(90deg, #dc2626, #f59e0b); color: white; padding: 2rem; border-radius: 1rem; text-align: center; margin-bottom: 2rem;">
        <h2 style="margin:0">🔥 НАУЧНЫЙ РЕЗУЛЬТАТ: 256%</h2>
        <p style="font-size: 1.2rem">Разрыв между реальным (ML) и официальным доходом в Дагестане</p>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Регионов", "24")
    col2.metric("Наблюдений", "330 302")
    col3.metric("Кластеров", "5")
    col4.metric("Горизонт", "2016-2023")
    
    st.markdown("---")
    st.markdown("### 📌 Основные выводы")
    c1, c2 = st.columns(2)
    with c1:
        st.info("💰 **Скрытая экономика:** Кластер K4 (Сельские) показывает аномально низкие официальные доходы при высоком уровне потребления, что подтверждает гипотезу о натуральном хозяйстве (42% выборки).")
    with c2:
        st.info("🚑 **Адаптация:** Пенсионеры-инвалиды используют социальные выплаты как экономическую стратегию (20.2% в Дагестане vs 6.4% в РФ).")

# --- СИМУЛЯТОР (ИСПРАВЛЕННЫЙ) ---
elif page == "🔮 Симулятор 2030 (Наука)":
    st.markdown("## 🔮 Сценарное моделирование: Дагестан 2030")
    st.markdown("Измените параметры, чтобы увидеть прогноз экономического развития.")
    
    col_input, col_out = st.columns([1, 2])
    
    with col_input:
        st.markdown('<div class="science-box">', unsafe_allow_html=True)
        st.subheader("🎛️ Параметры")
        # ИСПРАВЛЕНИЕ: format вмеcто suffix
        urban_delta = st.slider("Урбанизация", -10, 20, 0, format="%d%%")
        shadow_delta = st.slider("Обеление экономики", 0, 50, 0, format="%d%%")
        family_delta = st.slider("Размер семьи", -20, 20, 0, format="%d%%")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_out:
        # База 2023
        base = data['stats'][(data['stats']['ter']=='82') & (data['stats']['year']==2023)].iloc[0]
        base_inc = base['doxodn']
        
        # Модель
        # 1. Урбанизация: +1% урб = +0.8% дохода
        factor_urb = 1 + (urban_delta * 0.008)
        # 2. Семья: Меньше семья = больше доход на душу
        factor_fam = 1 - (family_delta * 0.01)
        # 3. Тень: Легализация скрытого (скрытый ~2.5x от базы)
        hidden = base_inc * 2.5
        legalized = hidden * (shadow_delta / 100)
        
        new_inc = (base_inc * factor_urb * factor_fam) + legalized
        growth = ((new_inc - base_inc) / base_inc) * 100
        
        st.markdown("### 📈 Прогноз")
        m1, m2 = st.columns(2)
        m1.metric("Офиц. доход (прогноз)", f"{int(new_inc):,} ₽", f"{int(new_inc-base_inc):,} ₽")
        m2.metric("Рост", f"{growth:.1f}%")
        
        fig = go.Figure(go.Waterfall(
            measure=["relative", "relative", "relative", "relative", "total"],
            x=["2023", "Урбанизация", "Демография", "Обеление", "2030"],
            y=[base_inc, 
               base_inc*(factor_urb-1), 
               base_inc*factor_urb*(factor_fam-1), 
               legalized, 
               new_inc],
            connector={"line":{"color":"grey"}},
        ))
        fig.update_layout(title="Факторы роста доходов", height=400)
        st.plotly_chart(fig, use_container_width=True)

# --- МИКРО-ДЕТЕКТОР ---
elif page == "🕵️ Микро-детектор (Наука)":
    st.markdown("## 🕵️ Детектор скрытых доходов (Микро-уровень)")
    st.write("Введите данные домохозяйства для проверки на скрытый доход (метод обратной задачи Энгеля).")
    
    c1, c2 = st.columns(2)
    with c1:
        wage = st.number_input("Зарплата на руки (руб)", 25000, step=1000)
        food = st.number_input("Траты на еду (руб)", 15000, step=500)
        share = st.slider("Доля еды в бюджете (%)", 10, 80, 45)
        
    with c2:
        # Расчет
        real_spend = food / (share / 100)
        # Учитываем сбережения 5% по умолчанию
        real_income = real_spend / 0.95
        
        gap = real_income - wage
        
        st.markdown("### Результат")
        if gap > 5000:
            st.error(f"⚠️ Обнаружен скрытый доход: **{int(gap):,} руб.**")
        else:
            st.success("✅ Доходы соответствуют расходам")
            
        fig = go.Figure([go.Bar(x=['Официально', 'Модель'], y=[wage, real_income], marker_color=['#3b82f6', '#dc2626'])])
        fig.update_layout(height=250, margin=dict(t=30,b=0))
        st.plotly_chart(fig, use_container_width=True)

# --- КАРТА (ИЗ ВЕРСИИ 2.1) ---
elif page == "🗺️ Карта регионов":
    st.markdown("## 🗺️ Интерактивная карта")
    
    col1, col2 = st.columns(2)
    with col1: year = st.selectbox("Год", sorted(data['stats']['year'].unique(), reverse=True))
    with col2: metric = st.selectbox("Показатель", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES[x])
    
    # Координаты (Hardcoded для стабильности)
    COORDS = {
        '82': (42.2, 47.1), '45': (55.75, 37.6), '40': (59.9, 30.3), '03': (45.0, 39.0),
        '96': (43.3, 45.7), '92': (55.8, 49.1), '80': (54.7, 56.0), '07': (45.0, 43.0),
        '60': (47.2, 39.7), '01': (53.0, 83.0), '12': (46.3, 48.0), '18': (48.7, 44.5),
        '26': (43.3, 45.0), '46': (55.8, 38.0), '76': (52.0, 114.0), '79': (44.6, 40.0),
        '81': (52.0, 108.0), '83': (43.5, 43.5), '84': (51.0, 86.0), '85': (46.0, 45.0),
        '90': (43.0, 44.0), '91': (43.5, 42.0), '93': (51.7, 94.4), '99': (48.5, 135.0)
    }
    
    df_map = data['stats'][data['stats']['year'] == year].copy()
    df_map = df_map[df_map['ter'].isin(COORDS.keys())]
    df_map['lat'] = df_map['ter'].map(lambda x: COORDS[x][0])
    df_map['lon'] = df_map['ter'].map(lambda x: COORDS[x][1])
    
    fig = px.scatter_geo(
        df_map, lat='lat', lon='lon', size=metric, color=metric,
        hover_name='region_name',
        color_continuous_scale='RdBu',
        scope='asia', # Фокус на Евразию
        title=f"{VAR_NAMES[metric]} ({year})"
    )
    fig.update_geos(fitbounds="locations", visible=True, showcountries=True, countrycolor="lightgray")
    # Принудительно ставим фокус на РФ
    fig.update_geos(lataxis_range=[40, 70], lonaxis_range=[30, 140], projection_type='mercator')
    fig.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

# --- СРАВНЕНИЕ И ДИНАМИКА ---
elif page == "📊 Сравнение и Динамика":
    st.markdown("## 📊 Аналитика")
    
    tab1, tab2 = st.tabs(["Рейтинг регионов", "Анимация во времени"])
    
    with tab1:
        metric = st.selectbox("Показатель для рейтинга", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES[x])
        df_last = data['stats'][data['stats']['year'] == 2023].sort_values(metric)
        
        fig = px.bar(df_last, x=metric, y='region_name', orientation='h', 
                     color=metric, color_continuous_scale='Blues')
        # Выделяем Дагестан линией
        dag_val = df_last[df_last['ter']=='82'][metric].values[0]
        fig.add_vline(x=dag_val, line_dash="dash", line_color="red", annotation_text="Дагестан")
        fig.update_layout(height=700)
        st.plotly_chart(fig, use_container_width=True)
        
    with tab2:
        st.info("Нажмите Play ▶️")
        fig_anim = px.scatter(
            data['stats'], x='doxodn', y='food_share', animation_frame='year',
            animation_group='ter', size='chlico', color='ter',
            hover_name='region_name', range_x=[10000, 60000], range_y=[20, 70],
            title="Доход vs Траты на еду (Динамика)"
        )
        fig_anim.update_layout(showlegend=False, height=600)
        st.plotly_chart(fig_anim, use_container_width=True)

# --- КЛАСТЕРЫ (ОБЪЕДИНЕННОЕ) ---
elif page == "🎯 Кластеры (Анализ)":
    st.markdown("## 🎯 Кластерный анализ")
    
    tab1, tab2 = st.tabs(["Распределение (Пирог)", "Тепловая карта (Наука)"])
    
    with tab1:
        # Пирог
        clust_sum = data['clusters'].groupby('cluster')['count'].sum().reset_index()
        clust_sum['label'] = clust_sum['cluster'].map(CLUSTER_NAMES)
        
        fig = px.pie(clust_sum, values='count', names='label', title="Структура населения по кластерам",
                     color_discrete_sequence=COLORS['cluster'])
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("K4 (Сельские) составляют 42% в Дагестане, но всего 1.6% в среднем по РФ.")

    with tab2:
        # Тепловая карта
        st.subheader("Профили кластеров (Z-Score)")
        df_prof = data['profiles'].set_index('cluster')
        # Только числовые
        cols = [c for c in df_prof.columns if c in VAR_NAMES]
        df_hm = df_prof[cols].rename(columns=VAR_NAMES)
        
        # Нормализация
        df_norm = (df_hm - df_hm.mean()) / df_hm.std()
        
        fig_hm = px.imshow(df_norm.T, 
                           x=[CLUSTER_NAMES.get(i) for i in df_norm.index],
                           color_continuous_scale='RdBu_r', aspect='auto')
        st.plotly_chart(fig_hm, use_container_width=True)
        st.caption("Красный = показатель выше среднего, Синий = ниже среднего")

# --- СКАЧАТЬ ---
elif page == "📥 Скачать данные":
    st.markdown("## 📥 Экспорт данных")
    st.write("Данные подготовлены в рамках выполнения гранта РНФ № 25-28-20473.")
    
    for name, df in data.items():
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label=f"Скачать {name}.csv",
            data=csv,
            file_name=f"{name}.csv",
            mime='text/csv'
        )

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 ДФИЦ РАН | Лаборатория демоэкономики")
