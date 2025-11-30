"""
🚀 ВАУ-ДАШБОРД ДЛЯ РНФ № 25-28-20473
Версия 2.1 FINAL - Все исправления
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
    'primary': '#1e3a8a',
    'secondary': '#f59e0b',
    'dagestan': '#dc2626',
    'russia': '#3b82f6',
    'success': '#10b981',
    'warning': '#f59e0b',
    'background': '#f8fafc',
    'text': '#1e293b',
}

CLUSTER_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6']

# ============================================================================
# СЛОВАРИ НАЗВАНИЙ
# ============================================================================

REGION_NAMES = {
    '01': 'Алтайский край',
    '03': 'Краснодарский край',
    '07': 'Ставропольский край',
    '12': 'Астраханская область',
    '18': 'Волгоградская область',
    '26': 'Республика Ингушетия',
    '40': 'Санкт-Петербург',
    '45': 'Москва',
    '46': 'Московская область',
    '60': 'Ростовская область',
    '76': 'Забайкальский край',
    '79': 'Республика Адыгея',
    '80': 'Республика Башкортостан',
    '81': 'Республика Бурятия',
    '82': 'Республика Дагестан',
    '83': 'Кабардино-Балкарская Республика',
    '84': 'Республика Алтай',
    '85': 'Республика Калмыкия',
    '90': 'Республика Северная Осетия - Алания',
    '91': 'Карачаево-Черкесская Республика',
    '92': 'Республика Татарстан',
    '93': 'Республика Тыва',
    '96': 'Чеченская Республика',
    '99': 'Еврейская автономная область',
}

VAR_NAMES = {
    'doxodn': 'Среднедушевой доход',
    'r1v2': 'Средний возраст',
    'chlico': 'Размер домохозяйства',
    'food_share': 'Доля расходов на продукты',
    'savings_rate': 'Норма сбережений',
    'mest_urban_pct': 'Доля городского населения',
    'pol_female_pct': 'Доля женщин',
    'income_reconstructed': 'Доход (ML-реконструкция)',
}

VAR_UNITS = {
    'doxodn': 'руб',
    'r1v2': 'лет',
    'chlico': 'чел',
    'food_share': '%',
    'savings_rate': '%',
    'mest_urban_pct': '%',
    'pol_female_pct': '%',
    'income_reconstructed': 'руб',
}

# ============================================================================
# ФУНКЦИИ ФОРМАТИРОВАНИЯ (РОССИЙСКИЙ ФОРМАТ!)
# ============================================================================

def format_number_ru(value, decimals=0):
    """
    Российский формат чисел:
    125651 → "125 651"
    36.5 → "36,5"
    """
    if pd.isna(value):
        return "—"
    
    value = round(value, decimals)
    
    if decimals > 0:
        # Форматируем с десятичными знаками
        integer_part = int(abs(value))
        decimal_part = abs(value) - integer_part
        
        # Разделяем тысячи пробелами (неразрывный пробел)
        integer_str = f"{integer_part:,}".replace(',', '\u00a0')
        
        if decimal_part > 0:
            decimal_str = f"{decimal_part:.{decimals}f}"[2:]
            result = f"{integer_str},{decimal_str}"
        else:
            result = integer_str
        
        return f"-{result}" if value < 0 else result
    else:
        # Только целое число
        integer_str = f"{int(abs(value)):,}".replace(',', '\u00a0')
        return f"-{integer_str}" if value < 0 else integer_str

def format_metric(value, var_name):
    """Форматирование с единицами измерения"""
    if pd.isna(value):
        return "—"
    
    if var_name in ['doxodn', 'income_reconstructed']:
        return f"{format_number_ru(value, decimals=0)}\u00a0{VAR_UNITS.get(var_name, '')}"
    elif var_name in ['food_share', 'savings_rate', 'mest_urban_pct', 'pol_female_pct']:
        return f"{format_number_ru(value, decimals=1)}%"
    elif var_name == 'r1v2':
        return f"{format_number_ru(value, decimals=1)}\u00a0{VAR_UNITS.get(var_name, '')}"
    elif var_name == 'chlico':
        return f"{format_number_ru(value, decimals=1)}\u00a0{VAR_UNITS.get(var_name, '')}"
    else:
        return format_number_ru(value, decimals=1)

def add_region_names(df):
    """Добавляет названия регионов"""
    if 'ter' in df.columns:
        df = df.copy()
        df['region_name'] = df['ter'].map(REGION_NAMES)
        df['region_name'] = df['region_name'].fillna('Регион ' + df['ter'].astype(str))
    return df

# ============================================================================
# КАСТОМНЫЙ CSS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
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
    }
    
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
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .key-finding-number {
        font-size: 3rem;
        font-weight: 900;
        display: block;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        border-left: 4px solid #f59e0b;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.1);
    }
    
    .finding-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin: 1rem 0;
    }
    
    .finding-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .finding-value {
        font-size: 2rem;
        font-weight: 900;
        color: #dc2626;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ЗАГРУЗКА ДАННЫХ
# ============================================================================

@st.cache_data
def load_data():
    try:
        data_dir = Path('data')
        
        regional_stats = pd.read_csv(data_dir / 'regional_stats.csv')
        cluster_dist = pd.read_csv(data_dir / 'cluster_distribution.csv')
        cluster_profiles = pd.read_csv(data_dir / 'cluster_profiles.csv')
        correlation_data = pd.read_csv(data_dir / 'correlation_comparison.csv')
        
        # Конвертируем ter в строку
        for df in [regional_stats, cluster_dist]:
            if 'ter' in df.columns:
                df['ter'] = df['ter'].astype(str).str.strip()
        
        # КРИТИЧНО: Добавляем названия регионов!
        regional_stats = add_region_names(regional_stats)
        cluster_dist = add_region_names(cluster_dist)
        
        return {
            'stats': regional_stats,
            'clusters': cluster_dist,
            'profiles': cluster_profiles,
            'correlations': correlation_data
        }
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
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
    <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">
        РНФ № 25-28-20473 | ДФИЦ РАН | 2016-2023
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# КЛЮЧЕВАЯ НАХОДКА
# ============================================================================

st.markdown("""
<div class="key-finding">
    🔥 КЛЮЧЕВАЯ НАУЧНАЯ НАХОДКА
    <span class="key-finding-number">256%</span>
    Скрытый доход в Дагестане превышает официальный в 2,5 раза<br>
    <small style="font-size: 1.2rem; opacity: 0.9;">
    (125\u00a0651 руб официально → 447\u00a0308 руб реально)
    </small>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# МЕТРИКИ ПРОЕКТА
# ============================================================================

st.markdown("## 📊 Масштаб исследования")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">330\u00a0302</div>
        <div style="font-size: 0.9rem; color: #64748b; text-transform: uppercase;">Наблюдений</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">24</div>
        <div style="font-size: 0.9rem; color: #64748b; text-transform: uppercase;">Региона</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">8</div>
        <div style="font-size: 0.9rem; color: #64748b; text-transform: uppercase;">Лет</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">5</div>
        <div style="font-size: 0.9rem; color: #64748b; text-transform: uppercase;">Кластеров</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# КЛЮЧЕВЫЕ ОТКРЫТИЯ
# ============================================================================

st.markdown("## 🔬 Ключевые научные открытия")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">💰 Скрытая экономика</div>
        <div class="finding-value">256%</div>
        <div style="color: #475569; font-size: 0.95rem;">
            Скрытый доход в Дагестане против 124% по России.
            ML-реконструкция: 447\u00a0308 руб vs 125\u00a0651 руб официально.
        </div>
    </div>
    
    <div class="finding-box">
        <div class="finding-title">👥 Натуральное хозяйство</div>
        <div class="finding-value">42% vs 1,6%</div>
        <div style="color: #475569; font-size: 0.95rem;">
            Кластер K4 (молодые сельские семьи) доминирует в Дагестане,
            но почти отсутствует в России.
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="finding-box">
        <div class="finding-title">♿ Адаптивные стратегии</div>
        <div class="finding-value">20,2% vs 6,4%</div>
        <div style="color: #475569; font-size: 0.95rem;">
            Пенсионеры-инвалиды. Адаптация: статус инвалидности
            для пособий + работа в тени.
        </div>
    </div>
    
    <div class="finding-box">
        <div class="finding-title">💸 Барьеры накопления</div>
        <div class="finding-value">r = 0,113 vs 0,364</div>
        <div style="color: #475569; font-size: 0.95rem;">
            Корреляция доход-сбережения. Структурные барьеры
            накопления богатства в Дагестане.
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🗺️ Навигация")
    
    page = st.radio(
        "Выберите раздел:",
        [
            "🏠 Главная",
            "🗺️ Карта регионов",
            "📊 Сравнение",
            "⏱️ Динамика",
            "🎯 Кластеры",
            "📥 Данные"
        ],
        index=0
    )

# Продолжение следует в части 2...

# ============================================================================
# ГЛАВНАЯ
# ============================================================================

if page == "🏠 Главная":
    st.markdown("## 📈 Обзор по Дагестану")
    
    dag_latest = data['stats'][(data['stats']['ter'] == '82') & (data['stats']['year'] == 2023)]
    
    if len(dag_latest) > 0:
        dag_row = dag_latest.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Доход (2023)",
                format_metric(dag_row['doxodn'], 'doxodn')
            )
        
        with col2:
            st.metric(
                "👤 Средний возраст",
                format_metric(dag_row['r1v2'], 'r1v2')
            )
        
        with col3:
            st.metric(
                "🍞 Доля на еду",
                format_metric(dag_row['food_share'], 'food_share')
            )

# ============================================================================
# КАРТА РЕГИОНОВ (ИСПРАВЛЕННАЯ!)
# ============================================================================

elif page == "🗺️ Карта регионов":
    st.markdown("## 🗺️ Интерактивная карта России")
    
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
            list(VAR_NAMES.keys()),
            format_func=lambda x: VAR_NAMES.get(x, x)
        )
    
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    if len(df_year) == 0:
        st.warning(f"⚠️ Нет данных за {year}")
    else:
        # Координаты ТОЛЬКО 24 регионов из базы
        region_coords = {
            '01': (45.0, 40.0),    # Алтайский край
            '03': (45.0, 39.0),    # Краснодарский край
            '07': (45.0, 43.0),    # Ставропольский край
            '12': (56.6, 47.9),    # Астраханская область
            '18': (48.7, 44.5),    # Волгоградская область
            '26': (43.3, 46.0),    # Республика Ингушетия
            '40': (59.9, 30.3),    # Санкт-Петербург
            '45': (55.75, 37.6),   # Москва
            '46': (55.8, 37.6),    # Московская область
            '60': (47.2, 39.7),    # Ростовская область
            '76': (52.0, 113.5),   # Забайкальский край
            '79': (44.6, 39.0),    # Республика Адыгея
            '80': (55.0, 54.7),    # Республика Башкортостан
            '81': (51.8, 107.6),   # Республика Бурятия
            '82': (42.2, 47.1),    # Республика Дагестан ⭐
            '83': (43.5, 43.4),    # Кабардино-Балкарская Республика
            '84': (50.7, 86.2),    # Республика Алтай
            '85': (46.3, 44.3),    # Республика Калмыкия
            '90': (43.0, 44.7),    # Республика Северная Осетия
            '91': (43.7, 41.9),    # Карачаево-Черкесская Республика
            '92': (55.8, 49.1),    # Республика Татарстан
            '93': (51.7, 94.4),    # Республика Тыва
            '96': (43.3, 45.7),    # Чеченская Республика
            '99': (48.5, 135.1),   # Еврейская автономная область
        }
        
        # Фильтруем только те регионы что ЕСТЬ в region_coords
        df_year = df_year[df_year['ter'].isin(region_coords.keys())].copy()
        
        # Добавляем координаты
        df_year['lat'] = df_year['ter'].map(lambda x: region_coords[x][0])
        df_year['lon'] = df_year['ter'].map(lambda x: region_coords[x][1])
        
        # РОССИЙСКИЙ ФОРМАТ для hover!
        df_year['formatted_value'] = df_year[metric].apply(
            lambda x: format_metric(x, metric)
        )
        
        # Scatter geo с правильными настройками
        fig = px.scatter_geo(
            df_year,
            lat='lat',
            lon='lon',
            size=metric,
            color=metric,
            hover_name='region_name',  # ← Названия регионов!
            hover_data={
                'lat': False,
                'lon': False,
                metric: False,
                'formatted_value': True  # ← Российский формат!
            },
            color_continuous_scale=[
                [0, COLORS['russia']],
                [0.5, COLORS['warning']],
                [1, COLORS['dagestan']]
            ],
            size_max=50,
            title=f'{VAR_NAMES.get(metric, metric)} ({year})',
            labels={'formatted_value': VAR_NAMES.get(metric, metric)}
        )
        
        # ИСПРАВЛЕНИЕ: Только Россия, правильные границы!
        fig.update_geos(
            scope='asia',
            showcountries=True,
            countrycolor='lightgray',
            showsubunits=False,
            lataxis_range=[40, 72],      # Широта: от Кавказа до севера
            lonaxis_range=[30, 150],     # Долгота: от Петербурга до Забайкалья
            projection_type='mercator',
            bgcolor='#f8fafc',
            resolution=50
        )
        
        # ПРЯМОУГОЛЬНАЯ карта!
        fig.update_layout(
            height=600,
            margin=dict(l=0, r=0, t=50, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ТОП и НИЗ с РОССИЙСКИМ ФОРМАТОМ
        st.markdown("### 🏆 Рейтинг")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⬆️ ТОП-5")
            top5 = df_year.nlargest(5, metric)[['region_name', metric]]
            for idx, row in top5.iterrows():
                st.markdown(f"**{row['region_name']}**: {format_metric(row[metric], metric)}")
        
        with col2:
            st.markdown("#### ⬇️ НИЗ-5")
            bottom5 = df_year.nsmallest(5, metric)[['region_name', metric]]
            for idx, row in bottom5.iterrows():
                st.markdown(f"**{row['region_name']}**: {format_metric(row[metric], metric)}")

# ============================================================================
# СРАВНЕНИЕ
# ============================================================================

elif page == "📊 Сравнение":
    st.markdown("## 📊 Сравнение регионов")
    
    year = st.selectbox("📅 Год:", sorted(data['stats']['year'].unique(), reverse=True))
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    if len(df_year) > 0:
        metric = st.selectbox(
            "📊 Показатель:",
            list(VAR_NAMES.keys()),
            format_func=lambda x: VAR_NAMES.get(x, x)
        )
        
        df_sorted = df_year.sort_values(metric, ascending=True)
        
        fig = px.bar(
            df_sorted,
            x=metric,
            y='region_name',
            orientation='h',
            color=metric,
            color_continuous_scale=[
                [0, COLORS['russia']],
                [0.5, COLORS['warning']],
                [1, COLORS['dagestan']]
            ],
            title=f'{VAR_NAMES.get(metric, metric)} ({year})',
            labels={metric: VAR_NAMES.get(metric, metric)}
        )
        
        # Highlight Дагестан
        dag_val = df_year[df_year['ter'] == '82'][metric]
        if len(dag_val) > 0:
            fig.add_vline(
                x=dag_val.values[0],
                line_dash="dash",
                line_color=COLORS['dagestan'],
                line_width=2,
                annotation_text="Дагестан"
            )
        
        fig.update_layout(height=800, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Статистика с РОССИЙСКИМ ФОРМАТОМ
        st.markdown("### 📈 Статистика")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Среднее", format_metric(df_year[metric].mean(), metric))
        with col2:
            st.metric("Медиана", format_metric(df_year[metric].median(), metric))
        with col3:
            st.metric("Минимум", format_metric(df_year[metric].min(), metric))
        with col4:
            st.metric("Максимум", format_metric(df_year[metric].max(), metric))

# ============================================================================
# ДИНАМИКА
# ============================================================================

elif page == "⏱️ Динамика":
    st.markdown("## ⏱️ Динамика 2016-2023")
    
    st.info("💡 Нажмите ▶️ для анимации")
    
    col1, col2 = st.columns(2)
    
    with col1:
        x_metric = st.selectbox(
            "Ось X:",
            list(VAR_NAMES.keys()),
            format_func=lambda x: VAR_NAMES[x].split()[0]
        )
    
    with col2:
        y_metric = st.selectbox(
            "Ось Y:",
            list(VAR_NAMES.keys()),
            index=4,
            format_func=lambda x: VAR_NAMES[x].split()[0]
        )
    
    df_anim = data['stats'].copy()
    df_anim['is_dagestan'] = df_anim['ter'] == '82'
    
    fig = px.scatter(
        df_anim,
        x=x_metric,
        y=y_metric,
        animation_frame='year',
        animation_group='ter',
        size='chlico',
        color='is_dagestan',
        hover_name='region_name',  # ← Названия!
        color_discrete_map={
            True: COLORS['dagestan'],
            False: COLORS['russia']
        },
        range_x=[df_anim[x_metric].min() * 0.9, df_anim[x_metric].max() * 1.1],
        range_y=[df_anim[y_metric].min() * 0.9, df_anim[y_metric].max() * 1.1],
        labels={
            x_metric: VAR_NAMES[x_metric],
            y_metric: VAR_NAMES[y_metric]
        }
    )
    
    fig.update_layout(
        title='Динамика (нажмите Play)',
        height=600,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# КЛАСТЕРЫ
# ============================================================================

elif page == "🎯 Кластеры":
    st.markdown("## 🎯 Кластерный анализ")
    
    cluster_names = {
        0: 'K0: Пожилые пенсионеры',
        1: 'K1: Средний класс',
        2: 'K2: Молодые городские',
        3: 'K3: Многодетные',
        4: 'K4: Сельские с натуральным хозяйством'
    }
    
    # Распределение
    cluster_summary = data['clusters'].groupby('cluster')['count'].sum().reset_index()
    cluster_summary['percentage'] = (cluster_summary['count'] / cluster_summary['count'].sum() * 100)
    cluster_summary['cluster_name'] = cluster_summary['cluster'].map(cluster_names)
    
    fig = px.pie(
        cluster_summary,
        values='count',
        names='cluster_name',
        hole=0.4,
        color='cluster',
        color_discrete_sequence=CLUSTER_COLORS,
        title='Распределение по кластерам'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Дагестан vs Россия
    st.markdown("### 🎯 Дагестан vs Россия")
    
    dag_clusters = data['clusters'][data['clusters']['ter'] == '82'].groupby('cluster')['count'].sum()
    all_clusters = data['clusters'].groupby('cluster')['count'].sum()
    
    dag_pct = (dag_clusters / dag_clusters.sum() * 100)
    all_pct = (all_clusters / all_clusters.sum() * 100)
    
    comparison = pd.DataFrame({
        'Кластер': [cluster_names[i] for i in range(5)],
        'Дагестан (%)': [dag_pct.get(i, 0) for i in range(5)],
        'Россия (%)': [all_pct.get(i, 0) for i in range(5)]
    })
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Дагестан',
        x=comparison['Кластер'],
        y=comparison['Дагестан (%)'],
        marker_color=COLORS['dagestan'],
        text=comparison['Дагестан (%)'].apply(lambda x: format_number_ru(x, 1) + '%'),
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Россия',
        x=comparison['Кластер'],
        y=comparison['Россия (%)'],
        marker_color=COLORS['russia'],
        text=comparison['Россия (%)'].apply(lambda x: format_number_ru(x, 1) + '%'),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Сравнение кластеров',
        yaxis_title='Доля (%)',
        barmode='group',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# ДАННЫЕ
# ============================================================================

elif page == "📥 Данные":
    st.markdown("## 📥 Экспорт данных")
    
    files = {
        'regional_stats.csv': 'Статистика по регионам',
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
                            "⬇️ Скачать",
                            data=f,
                            file_name=filename,
                            mime='text/csv',
                            key=filename
                        )
            except:
                st.caption("Недоступен")
        
        st.markdown("---")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 2rem;">
    <p>🎯 Демоэкономический анализ Республики Дагестан</p>
    <p><b>РНФ № 25-28-20473</b> | ДФИЦ РАН | 2016-2023</p>
</div>
""", unsafe_allow_html=True)
