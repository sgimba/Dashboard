"""
🚀 ВАУ-ДАШБОРД ДЛЯ РНФ № 25-28-20473
Демоэкономический анализ Республики Дагестан
Машинное обучение × Региональное развитие
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

st.set_page_config(
    page_title="Демоэкономический анализ Дагестана | РНФ",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# ЦВЕТОВАЯ ПАЛИТРА
# ============================================================================

COLORS = {
    'primary': '#1e3a8a',      # Темно-синий (наука)
    'secondary': '#f59e0b',    # Золотой (акцент)
    'dagestan': '#dc2626',     # Красный (Дагестан)
    'russia': '#3b82f6',       # Синий (Россия)
    'success': '#10b981',      # Зеленый (рост)
    'warning': '#f59e0b',      # Желтый (внимание)
    'background': '#f8fafc',   # Светлый фон
    'text': '#1e293b',         # Темный текст
}

# Палитра для кластеров
CLUSTER_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6']

# ============================================================================
# КАСТОМНЫЙ CSS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    /* Общие стили */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero section */
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 20px 60px rgba(30, 58, 138, 0.3);
        text-align: center;
    }
    
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    
    .hero p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    .hero-meta {
        font-size: 0.9rem;
        opacity: 0.7;
        margin-top: 1rem;
    }
    
    /* Ключевая находка */
    .key-finding {
        background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 1rem;
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin: 2rem 0;
        box-shadow: 0 20px 60px rgba(220, 38, 38, 0.3);
        animation: pulse-glow 3s ease-in-out infinite;
    }
    
    @keyframes pulse-glow {
        0%, 100% { 
            transform: scale(1);
            box-shadow: 0 20px 60px rgba(220, 38, 38, 0.3);
        }
        50% { 
            transform: scale(1.02);
            box-shadow: 0 25px 70px rgba(220, 38, 38, 0.4);
        }
    }
    
    .key-finding-number {
        font-size: 3rem;
        font-weight: 900;
        display: block;
        margin: 0.5rem 0;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Метрика карточка */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.1);
        border-left-color: #dc2626;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        color: #1e3a8a;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    /* Блок открытия */
    .finding-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.1);
    }
    
    .finding-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    
    .finding-value {
        font-size: 2rem;
        font-weight: 900;
        color: #dc2626;
        margin: 0.5rem 0;
    }
    
    .finding-description {
        color: #475569;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a8a 0%, #1e40af 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        font-weight: 600;
        font-size: 0.95rem;
    }
    
    /* Кнопки */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 0.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Графики */
    .stPlotlyChart {
        border-radius: 0.75rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        background: white;
        padding: 1rem;
    }
    
    /* Разделитель */
    hr {
        margin: 3rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
    }
    
    /* Заголовки секций */
    h2 {
        color: #1e3a8a;
        font-weight: 800;
        margin-top: 2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #f59e0b;
        display: inline-block;
    }
    
    h3 {
        color: #334155;
        font-weight: 700;
        margin-top: 1.5rem;
    }
    
    /* Статистика карточка */
    .stat-row {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-box {
        flex: 1;
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }
    
    /* Timeline */
    .timeline {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    
    .timeline-year {
        font-size: 1.5rem;
        font-weight: 900;
        color: #92400e;
        display: inline-block;
        background: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        margin: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ЗАГРУЗКА ДАННЫХ
# ============================================================================

@st.cache_data
def load_data():
    """Загрузка всех необходимых данных"""
    try:
        data_dir = Path('data')
        
        # Основные данные
        regional_stats = pd.read_csv(data_dir / 'regional_stats.csv')
        cluster_dist = pd.read_csv(data_dir / 'cluster_distribution.csv')
        cluster_profiles = pd.read_csv(data_dir / 'cluster_profiles.csv')
        correlation_data = pd.read_csv(data_dir / 'correlation_comparison.csv')
        
        # ВАЖНО: Конвертируем ter в строку для всех датафреймов
        for df in [regional_stats, cluster_dist]:
            if 'ter' in df.columns:
                df['ter'] = df['ter'].astype(str).str.strip()
        
        return {
            'stats': regional_stats,
            'clusters': cluster_dist,
            'profiles': cluster_profiles,
            'correlations': correlation_data
        }
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {e}")
        return None

data = load_data()

if data is None:
    st.stop()

# ============================================================================
# HERO SECTION
# ============================================================================

st.markdown("""
<div class="hero">
    <h1>🎯 ДЕМОЭКОНОМИЧЕСКИЙ АНАЛИЗ РЕСПУБЛИКИ ДАГЕСТАН</h1>
    <p>Машинное обучение × Региональное развитие</p>
    <div class="hero-meta">
        РНФ № 25-28-20473 | ДФИЦ РАН | 2016-2023
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# КЛЮЧЕВАЯ НАХОДКА (ГЛАВНАЯ)
# ============================================================================

st.markdown("""
<div class="key-finding">
    🔥 КЛЮЧЕВАЯ НАУЧНАЯ НАХОДКА
    <span class="key-finding-number">256%</span>
    Скрытый доход в Дагестане превышает официальный в 2.5 раза<br>
    <small style="font-size: 1.2rem; opacity: 0.9;">
    (125,651 руб официально → 447,308 руб реально, по данным ML-реконструкции)
    </small>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# ОСНОВНЫЕ МЕТРИКИ ПРОЕКТА
# ============================================================================

st.markdown("## 📊 Масштаб исследования")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">330,302</div>
        <div class="metric-label">Наблюдений</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">24</div>
        <div class="metric-label">Региона России</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">8</div>
        <div class="metric-label">Лет анализа</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">5</div>
        <div class="metric-label">Кластеров ML</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# TIMELINE ПРОЕКТА
# ============================================================================

st.markdown("---")

st.markdown("""
<div class="timeline">
    <h3 style="text-align: center; color: #92400e; margin-bottom: 1.5rem;">
        📅 Хронология исследования
    </h3>
    <div style="text-align: center; font-size: 1.1rem; color: #78350f;">
        <span class="timeline-year">2016</span>
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        <span class="timeline-year">2023</span>
        <br><br>
        <div style="margin-top: 1rem; font-size: 0.95rem;">
            ✓ Данные ОБДХ Росстат | ✓ K-means кластеризация | 
            ✓ ML реконструкция доходов | ✓ SHAP интерпретация
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# КЛЮЧЕВЫЕ НАУЧНЫЕ ОТКРЫТИЯ
# ============================================================================

st.markdown("## 🔬 Ключевые научные открытия")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">💰 Скрытая экономика</div>
        <div class="finding-value">256%</div>
        <div class="finding-description">
            Скрытый доход в Дагестане (vs 124% по России). 
            ML-модель реконструировала реальный доход: 
            447,308 руб против официальных 125,651 руб.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">👥 Кластер натурального хозяйства</div>
        <div class="finding-value">42% vs 1.6%</div>
        <div class="finding-description">
            Кластер K4 (молодые сельские семьи с низким денежным доходом 
            + натуральное хозяйство) доминирует в Дагестане, 
            но почти отсутствует в остальной России.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">♿ Адаптивные стратегии</div>
        <div class="finding-value">20.2% vs 6.4%</div>
        <div class="finding-description">
            Пенсионеры-инвалиды в Дагестане (vs Россия). 
            Уникальная адаптация: получение статуса инвалидности 
            для доступа к федеральным пособиям + работа в тени.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">💸 Барьеры накопления</div>
        <div class="finding-value">r = 0.113 vs 0.364</div>
        <div class="finding-description">
            Корреляция доход-сбережения в Дагестане значительно ниже, 
            чем по России. Структурные барьеры накопления богатства 
            препятствуют трансформации дохода в сбережения.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR НАВИГАЦИЯ
# ============================================================================

with st.sidebar:
    st.markdown("## 🗺️ Навигация")
    
    page = st.radio(
        "Выберите раздел:",
        [
            "🏠 Главная",
            "🗺️ Интерактивная карта",
            "📊 Сравнение регионов",
            "⏱️ Динамика 2016-2023",
            "🎯 Кластерный анализ",
            "🔗 Корреляции",
            "📥 Скачать данные",
            "📖 Документация"
        ],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📋 Информация о проекте")
    st.markdown("""
    **Грант:** РНФ № 25-28-20473  
    **Организация:** ДФИЦ РАН  
    **Период:** 2016-2023  
    **Наблюдений:** 330,302  
    **Регионов:** 24
    """)

# ============================================================================
# СТРАНИЦА: ГЛАВНАЯ
# ============================================================================

if page == "🏠 Главная":
    st.markdown("## 📈 Обзор ключевых показателей по Дагестану")
    
    # Получаем последние данные по Дагестану
    dag_latest = data['stats'][(data['stats']['ter'] == '82') & (data['stats']['year'] == 2023)]
    
    if len(dag_latest) == 0:
        st.warning("⚠️ Нет данных по Дагестану за 2023 год")
    else:
        dag_row = dag_latest.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="💰 Среднедушевой доход (2023)",
                value=f"{dag_row['doxodn']:,.0f} ₽",
                delta="Официальные данные"
            )
        
        with col2:
            st.metric(
                label="👤 Средний возраст",
                value=f"{dag_row['r1v2']:.1f} лет",
                delta=None
            )
        
        with col3:
            st.metric(
                label="🍞 Доля расходов на еду",
                value=f"{dag_row['food_share']:.1f}%",
                delta="Индикатор бедности"
            )
        
        # График динамики дохода
        st.markdown("### 📊 Динамика среднедушевого дохода (2016-2023)")
        
        dag_history = data['stats'][data['stats']['ter'] == '82'].sort_values('year')
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dag_history['year'],
            y=dag_history['doxodn'],
            mode='lines+markers',
            name='Дагестан',
            line=dict(color=COLORS['dagestan'], width=3),
            marker=dict(size=10),
            hovertemplate='<b>Год:</b> %{x}<br><b>Доход:</b> %{y:,.0f} ₽<extra></extra>'
        ))
        
        # Добавим среднее по России для сравнения
        russia_avg = data['stats'].groupby('year')['doxodn'].mean().reset_index()
        
        fig.add_trace(go.Scatter(
            x=russia_avg['year'],
            y=russia_avg['doxodn'],
            mode='lines+markers',
            name='Россия (среднее)',
            line=dict(color=COLORS['russia'], width=2, dash='dash'),
            marker=dict(size=8),
            hovertemplate='<b>Год:</b> %{x}<br><b>Доход:</b> %{y:,.0f} ₽<extra></extra>'
        ))
        
        fig.update_layout(
            title='Сравнение динамики доходов: Дагестан vs Россия',
            xaxis_title='Год',
            yaxis_title='Среднедушевой доход (руб)',
            hovermode='x unified',
            height=500,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# СТРАНИЦА: ИНТЕРАКТИВНАЯ КАРТА
# ============================================================================

elif page == "🗺️ Интерактивная карта":
    st.markdown("## 🗺️ Интерактивная карта регионов России")
    
    # Селекторы
    col1, col2 = st.columns(2)
    
    with col1:
        year = st.selectbox(
            "📅 Год:",
            sorted(data['stats']['year'].unique(), reverse=True),
            index=0
        )
    
    with col2:
        metric = st.selectbox(
            "📊 Показатель:",
            {
                'doxodn': 'Среднедушевой доход',
                'r1v2': 'Средний возраст',
                'food_share': 'Доля расходов на еду (%)',
                'savings_rate': 'Норма сбережений (%)',
                'mest_urban_pct': 'Урбанизация (%)',
                'pol_female_pct': 'Доля женщин (%)'
            }
        )
    
    # Данные за выбранный год
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    if len(df_year) == 0:
        st.warning(f"⚠️ Нет данных за {year} год")
    else:
        # Создаем scatter map (простая альтернатива choropleth)
        # Координаты центров регионов (упрощенные)
        region_coords = {
            '01': (51.7, 45.0),  # Адыгея
            '03': (54.7, 55.9),  # Башкортостан
            '07': (60.6, 56.8),  # Кабардино-Балкария
            '12': (55.8, 49.1),  # Марий Эл
            '18': (43.3, 45.0),  # Удмуртия
            '26': (55.0, 82.9),  # Ставропольский край
            '40': (44.0, 56.3),  # Калужская область
            '45': (38.0, 55.7),  # Курганская область
            '46': (42.0, 47.2),  # Курская область
            '60': (39.7, 47.2),  # Псковская область
            '82': (47.5, 42.5),  # Дагестан ⭐
            # Добавь остальные регионы по необходимости
        }
        
        # Создаем датафрейм с координатами
        df_year['lat'] = df_year['ter'].map(lambda x: region_coords.get(x, (55, 37))[1])
        df_year['lon'] = df_year['ter'].map(lambda x: region_coords.get(x, (55, 37))[0])
        
        # Названия регионов (упрощенные)
        region_names = {
            '82': 'Дагестан',
            '01': 'Адыгея',
            '03': 'Башкортостан',
            # Добавь остальные
        }
        df_year['region_name'] = df_year['ter'].map(lambda x: region_names.get(x, f'Регион {x}'))
        
        # Создаем scatter geo
        fig = px.scatter_geo(
            df_year,
            lat='lat',
            lon='lon',
            size=metric,
            color=metric,
            hover_name='region_name',
            hover_data={
                'lat': False,
                'lon': False,
                metric: ':.1f'
            },
            color_continuous_scale=[
                [0, COLORS['russia']],
                [0.5, COLORS['warning']],
                [1, COLORS['dagestan']]
            ],
            size_max=50,
            title=f'{list({metric: "..."}.keys())[0]} по регионам России ({year})'
        )
        
        fig.update_geos(
            scope='europe',
            showcountries=True,
            countrycolor='lightgray',
            showsubunits=True,
            subunitcolor='white',
            center=dict(lat=60, lon=60),
            projection_scale=2.5
        )
        
        fig.update_layout(height=600)
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ТОП и НИЗ регионов
        st.markdown("### 🏆 Рейтинг регионов")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⬆️ ТОП-5 регионов")
            top5 = df_year.nlargest(5, metric)[['region_name', metric]]
            for idx, row in top5.iterrows():
                st.markdown(f"**{row['region_name']}**: {row[metric]:.1f}")
        
        with col2:
            st.markdown("#### ⬇️ НИЗ-5 регионов")
            bottom5 = df_year.nsmallest(5, metric)[['region_name', metric]]
            for idx, row in bottom5.iterrows():
                st.markdown(f"**{row['region_name']}**: {row[metric]:.1f}")

# Продолжение следует...

# ============================================================================
# СТРАНИЦА: СРАВНЕНИЕ РЕГИОНОВ
# ============================================================================

elif page == "📊 Сравнение регионов":
    st.markdown("## 📊 Сравнительный анализ регионов")
    
    # Селектор года
    year = st.selectbox(
        "📅 Выберите год:",
        sorted(data['stats']['year'].unique(), reverse=True),
        key='comp_year'
    )
    
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    if len(df_year) == 0:
        st.warning(f"⚠️ Нет данных за {year} год")
    else:
        # Добавляем названия регионов
        df_year['region_name'] = df_year['ter'].apply(lambda x: f'Регион {x}')
        df_year.loc[df_year['ter'] == '82', 'region_name'] = 'Дагестан'
        
        # Мультивыбор показателей
        metrics_options = {
            'doxodn': 'Среднедушевой доход',
            'r1v2': 'Средний возраст',
            'chlico': 'Размер домохозяйства',
            'food_share': 'Доля расходов на еду (%)',
            'savings_rate': 'Норма сбережений (%)'
        }
        
        selected_metric = st.selectbox(
            "📊 Показатель для сравнения:",
            list(metrics_options.keys()),
            format_func=lambda x: metrics_options[x]
        )
        
        # Горизонтальный bar chart
        fig = px.bar(
            df_year.sort_values(selected_metric, ascending=True),
            x=selected_metric,
            y='region_name',
            orientation='h',
            color=selected_metric,
            color_continuous_scale=[
                [0, COLORS['russia']],
                [0.5, COLORS['warning']],
                [1, COLORS['dagestan']]
            ],
            title=f'{metrics_options[selected_metric]} по регионам ({year})',
            labels={selected_metric: metrics_options[selected_metric]}
        )
        
        # Highlight Дагестан
        dag_value = df_year[df_year['ter'] == '82'][selected_metric]
        if len(dag_value) > 0:
            fig.add_vline(
                x=dag_value.values[0],
                line_dash="dash",
                line_color=COLORS['dagestan'],
                line_width=2,
                annotation_text="Дагестан",
                annotation_position="top"
            )
        
        fig.update_layout(
            height=800,
            showlegend=False,
            template='plotly_white'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Статистика
        st.markdown("### 📈 Статистический анализ")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Среднее", f"{df_year[selected_metric].mean():.1f}")
        
        with col2:
            st.metric("Медиана", f"{df_year[selected_metric].median():.1f}")
        
        with col3:
            st.metric("Минимум", f"{df_year[selected_metric].min():.1f}")
        
        with col4:
            st.metric("Максимум", f"{df_year[selected_metric].max():.1f}")
        
        # Дагестан vs Россия
        if len(df_year[df_year['ter'] == '82']) > 0:
            dag_val = df_year[df_year['ter'] == '82'][selected_metric].values[0]
            russia_avg = df_year[selected_metric].mean()
            diff = ((dag_val - russia_avg) / russia_avg * 100)
            
            st.markdown("### 🎯 Дагестан vs Россия")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Дагестан",
                    f"{dag_val:.1f}"
                )
            
            with col2:
                st.metric(
                    "Россия (среднее)",
                    f"{russia_avg:.1f}"
                )
            
            with col3:
                st.metric(
                    "Разница",
                    f"{diff:+.1f}%",
                    delta=f"{'выше' if diff > 0 else 'ниже'} среднего"
                )

# ============================================================================
# СТРАНИЦА: ДИНАМИКА 2016-2023
# ============================================================================

elif page == "⏱️ Динамика 2016-2023":
    st.markdown("## ⏱️ Временная динамика 2016-2023")
    
    # Анимированный график
    st.markdown("### 🎬 Анимированная визуализация")
    
    st.info("💡 Нажмите ▶️ внизу графика для просмотра динамики по годам!")
    
    # Выбор показателей для осей
    col1, col2 = st.columns(2)
    
    with col1:
        x_metric = st.selectbox(
            "Ось X:",
            ['doxodn', 'r1v2', 'chlico', 'food_share', 'savings_rate'],
            format_func=lambda x: {
                'doxodn': 'Доход',
                'r1v2': 'Возраст',
                'chlico': 'Размер ДХ',
                'food_share': 'Доля еды (%)',
                'savings_rate': 'Сбережения (%)'
            }[x]
        )
    
    with col2:
        y_metric = st.selectbox(
            "Ось Y:",
            ['savings_rate', 'food_share', 'doxodn', 'r1v2', 'chlico'],
            format_func=lambda x: {
                'doxodn': 'Доход',
                'r1v2': 'Возраст',
                'chlico': 'Размер ДХ',
                'food_share': 'Доля еды (%)',
                'savings_rate': 'Сбережения (%)'
            }[x]
        )
    
    # Подготовка данных
    df_anim = data['stats'].copy()
    df_anim['region_name'] = df_anim['ter'].apply(lambda x: 'Дагестан' if x == '82' else f'Регион {x}')
    df_anim['is_dagestan'] = df_anim['ter'] == '82'
    
    # Анимированный scatter
    fig = px.scatter(
        df_anim,
        x=x_metric,
        y=y_metric,
        animation_frame='year',
        animation_group='ter',
        size='chlico',
        color='is_dagestan',
        hover_name='region_name',
        color_discrete_map={
            True: COLORS['dagestan'],
            False: COLORS['russia']
        },
        range_x=[df_anim[x_metric].min() * 0.9, df_anim[x_metric].max() * 1.1],
        range_y=[df_anim[y_metric].min() * 0.9, df_anim[y_metric].max() * 1.1],
        labels={
            x_metric: {
                'doxodn': 'Доход',
                'r1v2': 'Возраст',
                'chlico': 'Размер ДХ',
                'food_share': 'Доля еды (%)',
                'savings_rate': 'Сбережения (%)'
            }.get(x_metric, x_metric),
            y_metric: {
                'doxodn': 'Доход',
                'r1v2': 'Возраст',
                'chlico': 'Размер ДХ',
                'food_share': 'Доля еды (%)',
                'savings_rate': 'Сбережения (%)'
            }.get(y_metric, y_metric)
        }
    )
    
    fig.update_layout(
        title='Динамика по годам (нажмите Play)',
        height=600,
        showlegend=False,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Анализ роста
    st.markdown("### 📈 Анализ роста 2016 → 2023")
    
    metric_analysis = st.selectbox(
        "Показатель для анализа роста:",
        ['doxodn', 'r1v2', 'food_share', 'savings_rate'],
        format_func=lambda x: {
            'doxodn': 'Среднедушевой доход',
            'r1v2': 'Средний возраст',
            'food_share': 'Доля расходов на еду',
            'savings_rate': 'Норма сбережений'
        }[x],
        key='growth_metric'
    )
    
    dag_data = data['stats'][data['stats']['ter'] == '82']
    rus_data = data['stats'].groupby('year')[metric_analysis].mean().reset_index()
    rus_data = rus_data.rename(columns={metric_analysis: 'value'})
    
    dag_2016_data = dag_data[dag_data['year'] == 2016][metric_analysis]
    dag_2023_data = dag_data[dag_data['year'] == 2023][metric_analysis]
    rus_2016_data = rus_data[rus_data['year'] == 2016]['value']
    rus_2023_data = rus_data[rus_data['year'] == 2023]['value']
    
    if len(dag_2016_data) == 0 or len(dag_2023_data) == 0 or len(rus_2016_data) == 0 or len(rus_2023_data) == 0:
        st.warning("⚠️ Недостаточно данных для анализа роста")
    else:
        dag_2016 = dag_2016_data.values[0]
        dag_2023 = dag_2023_data.values[0]
        dag_growth_abs = dag_2023 - dag_2016
        dag_growth_pct = ((dag_2023 - dag_2016) / dag_2016 * 100)
        
        rus_2016 = rus_2016_data.values[0]
        rus_2023 = rus_2023_data.values[0]
        rus_growth_abs = rus_2023 - rus_2016
        rus_growth_pct = ((rus_2023 - rus_2016) / rus_2016 * 100)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Дагестан")
            st.metric(label="2016", value=f"{dag_2016:.1f}")
            st.metric(label="2023", value=f"{dag_2023:.1f}", delta=f"{dag_growth_pct:+.1f}%")
            st.metric(label="Абсолютный рост", value=f"{dag_growth_abs:+.1f}")
        
        with col2:
            st.markdown("### 🇷🇺 Россия (среднее)")
            st.metric(label="2016", value=f"{rus_2016:.1f}")
            st.metric(label="2023", value=f"{rus_2023:.1f}", delta=f"{rus_growth_pct:+.1f}%")
            st.metric(label="Абсолютный рост", value=f"{rus_growth_abs:+.1f}")
        
        with col3:
            st.markdown("### ⚖️ Разница темпов")
            diff_pct = dag_growth_pct - rus_growth_pct
            st.metric(
                label="Превышение темпа роста",
                value=f"{diff_pct:+.1f}%",
                delta="быстрее" if diff_pct > 0 else "медленнее"
            )

# ============================================================================
# СТРАНИЦА: КЛАСТЕРНЫЙ АНАЛИЗ
# ============================================================================

elif page == "🎯 Кластерный анализ":
    st.markdown("## 🎯 Кластерный анализ населения")
    
    st.info("💡 Население разделено на 5 кластеров по социально-экономическим характеристикам")
    
    # Распределение кластеров
    st.markdown("### 📊 Распределение населения по кластерам")
    
    # Группируем по кластерам
    cluster_summary = data['clusters'].groupby('cluster')['count'].sum().reset_index()
    cluster_summary['percentage'] = (cluster_summary['count'] / cluster_summary['count'].sum() * 100)
    
    # Названия кластеров
    cluster_names = {
        0: 'K0: Пожилые пенсионеры',
        1: 'K1: Средний класс',
        2: 'K2: Молодые городские',
        3: 'K3: Многодетные',
        4: 'K4: Сельские натуральное хозяйство'
    }
    
    cluster_summary['cluster_name'] = cluster_summary['cluster'].map(cluster_names)
    
    # Donut chart
    fig = px.pie(
        cluster_summary,
        values='count',
        names='cluster_name',
        hole=0.4,
        color='cluster',
        color_discrete_sequence=CLUSTER_COLORS,
        title='Общее распределение по кластерам (все регионы)'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Население: %{value:,}<br>Доля: %{percent}<extra></extra>'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Дагестан vs Россия
    st.markdown("### 🎯 Дагестан vs Россия по кластерам")
    
    dag_clusters = data['clusters'][data['clusters']['ter'] == '82'].groupby('cluster')['count'].sum()
    all_clusters = data['clusters'].groupby('cluster')['count'].sum()
    
    dag_pct = (dag_clusters / dag_clusters.sum() * 100)
    all_pct = (all_clusters / all_clusters.sum() * 100)
    
    comparison = pd.DataFrame({
        'Кластер': [cluster_names[i] for i in range(5)],
        'Дагестан (%)': [dag_pct.get(i, 0) for i in range(5)],
        'Россия (%)': [all_pct.get(i, 0) for i in range(5)]
    })
    
    # Grouped bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Дагестан',
        x=comparison['Кластер'],
        y=comparison['Дагестан (%)'],
        marker_color=COLORS['dagestan'],
        text=comparison['Дагестан (%)'].round(1),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Россия',
        x=comparison['Кластер'],
        y=comparison['Россия (%)'],
        marker_color=COLORS['russia'],
        text=comparison['Россия (%)'].round(1),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Сравнение распределения кластеров: Дагестан vs Россия',
        yaxis_title='Доля населения (%)',
        barmode='group',
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Ключевое наблюдение
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">🔥 Ключевое наблюдение</div>
        <div class="finding-description">
            <b>Кластер K4 (сельские с натуральным хозяйством)</b> составляет 
            <b style="color: #dc2626; font-size: 1.3rem;">42%</b> населения Дагестана,
            но только <b>1.6%</b> в остальной России. Это уникальная адаптивная 
            стратегия: низкий денежный доход компенсируется натуральным хозяйством.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Профили кластеров - Radar Chart
    st.markdown("### 🕸️ Профили кластеров (многомерное сравнение)")
    
    if 'profiles' in data and len(data['profiles']) > 0:
        # Нормализуем данные для radar chart
        profile_data = data['profiles'].copy()
        
        # Выбираем ключевые переменные
        key_vars = ['doxodn', 'r1v2', 'chlico', 'food_share', 'savings_rate']
        
        # Нормализация к [0, 1]
        for var in key_vars:
            if var in profile_data.columns:
                min_val = profile_data[var].min()
                max_val = profile_data[var].max()
                profile_data[f'{var}_norm'] = (profile_data[var] - min_val) / (max_val - min_val)
        
        # Radar chart
        fig = go.Figure()
        
        categories = ['Доход', 'Возраст', 'Размер ДХ', 'Доля еды', 'Сбережения']
        
        for cluster in range(5):
            cluster_data = profile_data[profile_data['cluster'] == cluster]
            if len(cluster_data) > 0:
                values = [
                    cluster_data['doxodn_norm'].values[0] if 'doxodn_norm' in cluster_data.columns else 0,
                    cluster_data['r1v2_norm'].values[0] if 'r1v2_norm' in cluster_data.columns else 0,
                    cluster_data['chlico_norm'].values[0] if 'chlico_norm' in cluster_data.columns else 0,
                    cluster_data['food_share_norm'].values[0] if 'food_share_norm' in cluster_data.columns else 0,
                    cluster_data['savings_rate_norm'].values[0] if 'savings_rate_norm' in cluster_data.columns else 0
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=cluster_names[cluster],
                    line_color=CLUSTER_COLORS[cluster]
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            title='Многомерные профили кластеров (нормализовано)',
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# СТРАНИЦА: КОРРЕЛЯЦИИ
# ============================================================================

elif page == "🔗 Корреляции":
    st.markdown("## 🔗 Корреляционный анализ")
    
    st.info("💡 Сравнение силы связей между переменными в Дагестане и России")
    
    if 'correlations' in data and len(data['correlations']) > 0:
        corr_data = data['correlations']
        
        # Heatmap корреляций
        st.markdown("### 🔥 Тепловая карта корреляций")
        
        # Фильтр: Дагестан или Россия
        region_choice = st.radio(
            "Выберите регион:",
            ["Дагестан", "Россия (среднее)"],
            horizontal=True
        )
        
        # Преобразуем данные в матрицу
        # (Предполагаем что correlation_comparison.csv содержит var1, var2, corr_dagestan, corr_russia)
        
        if region_choice == "Дагестан" and 'corr_dagestan' in corr_data.columns:
            pivot = corr_data.pivot(index='var1', columns='var2', values='corr_dagestan')
        elif 'corr_russia' in corr_data.columns:
            pivot = corr_data.pivot(index='var1', columns='var2', values='corr_russia')
        else:
            st.warning("⚠️ Данные корреляций не найдены")
            pivot = None
        
        if pivot is not None:
            # Heatmap с аннотациями
            fig = go.Figure(data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale='RdBu_r',
                zmid=0,
                text=pivot.values.round(2),
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Корреляция")
            ))
            
            fig.update_layout(
                title=f'Матрица корреляций: {region_choice}',
                height=600,
                xaxis_title='Переменная',
                yaxis_title='Переменная'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Ключевые различия
        st.markdown("### ⚖️ Ключевые различия в корреляциях")
        
        if 'corr_dagestan' in corr_data.columns and 'corr_russia' in corr_data.columns:
            corr_data['diff'] = abs(corr_data['corr_dagestan'] - corr_data['corr_russia'])
            top_diff = corr_data.nlargest(5, 'diff')[['var1', 'var2', 'corr_dagestan', 'corr_russia', 'diff']]
            
            st.markdown("**Топ-5 пар с наибольшими различиями:**")
            
            for idx, row in top_diff.iterrows():
                st.markdown(f"""
                <div class="finding-box">
                    <div class="finding-title">{row['var1']} ↔ {row['var2']}</div>
                    <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
                        <div>
                            <div style="font-size: 0.9rem; color: #64748b;">Дагестан</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #dc2626;">{row['corr_dagestan']:.3f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #64748b;">Россия</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #3b82f6;">{row['corr_russia']:.3f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9rem; color: #64748b;">Разница</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #f59e0b;">{row['diff']:.3f}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ============================================================================
# СТРАНИЦА: СКАЧАТЬ ДАННЫЕ
# ============================================================================

elif page == "📥 Скачать данные":
    st.markdown("## 📥 Экспорт данных")
    
    st.info("💡 Все данные доступны для скачивания в формате CSV")
    
    # Список файлов
    files = {
        'regional_stats.csv': 'Региональная статистика по годам',
        'cluster_distribution.csv': 'Распределение кластеров',
        'cluster_profiles.csv': 'Профили кластеров',
        'correlation_comparison.csv': 'Сравнение корреляций'
    }
    
    for filename, description in files.items():
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{filename}**")
            st.caption(description)
        
        with col2:
            try:
                file_path = Path('data') / filename
                if file_path.exists():
                    with open(file_path, 'rb') as f:
                        st.download_button(
                            label="⬇️ Скачать",
                            data=f,
                            file_name=filename,
                            mime='text/csv',
                            key=filename
                        )
            except:
                st.caption("Файл недоступен")
        
        st.markdown("---")
    
    # Полный dataset
    st.markdown("### 📦 Полный датасет")
    st.markdown("""
    Для доступа к полному датасету (330,302 наблюдений) обратитесь 
    к исследовательской группе ДФИЦ РАН.
    """)

# ============================================================================
# СТРАНИЦА: ДОКУМЕНТАЦИЯ
# ============================================================================

elif page == "📖 Документация":
    st.markdown("## 📖 Документация проекта")
    
    st.markdown("""
    ### 🎯 О проекте
    
    **Название:** Моделирование влияния демоэкономических процессов и самосохранительного 
    потенциала населения на региональное развитие с использованием методов машинного обучения
    
    **Грант:** РНФ № 25-28-20473  
    **Организация:** Дагестанский федеральный исследовательский центр РАН  
    **Период исследования:** 2016-2023  
    
    ---
    
    ### 📊 Данные
    
    **Источник:** Обследование бюджетов домашних хозяйств (ОБДХ) Росстата  
    **Наблюдений:** 330,302  
    **Регионов:** 24  
    **Лет:** 8 (2016-2023)  
    
    ---
    
    ### 🤖 Методы машинного обучения
    
    1. **K-means кластеризация** - разделение населения на 5 групп
    2. **Random Forest** - реконструкция реальных доходов
    3. **SHAP анализ** - интерпретация вкладов признаков
    4. **Ridge регрессия** - прогнозирование
    
    ---
    
    ### 🔬 Ключевые находки
    
    1. **Скрытая экономика:** 256% скрытого дохода в Дагестане (vs 124% по России)
    2. **Адаптивные стратегии:** 20.2% пенсионеров-инвалидов (vs 6.4%)
    3. **Натуральное хозяйство:** Кластер K4 составляет 42% (vs 1.6%)
    4. **Барьеры накопления:** Корреляция доход-сбережения r=0.113 (vs 0.364)
    
    ---
    
    ### 📚 Публикации
    
    Результаты исследования представлены в следующих публикациях:
    
    1. Статья в журнале "Народонаселение" (RSCI)
    2. Статья в журнале "Вестник Института экономики РАН" (RSCI)
    3. Препринт на arXiv.org
    
    ---
    
    ### 👥 Исследовательская группа
    
    **Руководитель проекта:** [Имя]  
    **Организация:** ДФИЦ РАН  
    **Контакты:** [email]  
    
    ---
    
    ### 📄 Цитирование
    
    ```
    [Авторы]. Моделирование влияния демоэкономических процессов 
    и самосохранительного потенциала населения на региональное 
    развитие с использованием методов машинного обучения. 
    РНФ № 25-28-20473, ДФИЦ РАН, 2025.
    ```
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p>🎯 Демоэкономический анализ Республики Дагестан</p>
    <p><b>РНФ № 25-28-20473</b> | ДФИЦ РАН | 2016-2023</p>
    <p style="font-size: 0.85rem;">
        Создано с использованием Streamlit | Python | Plotly<br>
        Машинное обучение × Региональное развитие
    </p>
</div>
""", unsafe_allow_html=True)
