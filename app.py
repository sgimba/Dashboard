"""
ИНТЕРАКТИВНЫЙ ДАШБОРД - ПОЛНАЯ ВЕРСИЯ
Проект РНФ № 25-28-20473: Дагестан - Демоэкономический Анализ

Моделирование влияния демоэкономических процессов и самосохранительного 
потенциала населения на региональное развитие с использованием методов 
машинного обучения
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import numpy as np

# ==================== НАСТРОЙКИ СТРАНИЦЫ ====================
st.set_page_config(
    page_title="Дагестан: Демоэкономический Анализ",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомный CSS для улучшения визуала
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ==================== СПРАВОЧНИКИ ====================
METRIC_NAMES = {
    'doxodn': 'Среднедушевой доход',
    'r1v2': 'Средний возраст',
    'chlico': 'Размер домохозяйства',
    'food_share': 'Доля расходов на продукты',
    'savings_rate': 'Норма сбережений',
    'avg_income': 'Среднедушевой доход',
    'avg_age': 'Средний возраст',
    'avg_hh_size': 'Размер домохозяйства',
    'food_share_pct': 'Доля расходов на продукты',
    'women_pct': 'Доля женщин',
    'urban_pct': 'Доля городского населения'
}

METRIC_UNITS = {
    'doxodn': 'руб/год',
    'r1v2': 'лет',
    'chlico': 'человек',
    'food_share': '%',
    'savings_rate': '%',
    'avg_income': 'руб/год',
    'avg_age': 'лет',
    'avg_hh_size': 'человек',
    'food_share_pct': '%',
    'women_pct': '%',
    'urban_pct': '%'
}

# ==================== ЗАГРУЗКА ДАННЫХ ====================
@st.cache_data
def load_data():
    """Загрузка всех данных"""
    try:
        regions = pd.read_csv('data/regions.csv')
        regional_stats = pd.read_csv('data/regional_stats.csv')
        time_series = pd.read_csv('data/time_series.csv')
        
        try:
            cluster_profiles = pd.read_csv('data/cluster_profiles.csv')
            cluster_dist = pd.read_csv('data/cluster_distribution.csv')
        except:
            cluster_profiles = None
            cluster_dist = None
        
        try:
            corr_dag = pd.read_csv('data/correlations_dagestan.csv', index_col=0)
            corr_all = pd.read_csv('data/correlations_all.csv', index_col=0)
        except:
            corr_dag = None
            corr_all = None
        
        with open('data/metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        return {
            'regions': regions,
            'stats': regional_stats,
            'time_series': time_series,
            'clusters': cluster_profiles,
            'cluster_dist': cluster_dist,
            'corr_dag': corr_dag,
            'corr_all': corr_all,
            'metadata': metadata
        }
    except Exception as e:
        st.error(f"❌ Ошибка загрузки данных: {e}")
        return None

data = load_data()

if data is None:
    st.stop()

# ==================== SIDEBAR ====================
st.sidebar.title("📊 Навигация")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Выберите раздел:",
    [
        "🏠 Главная",
        "🗺️ Карта регионов",
        "📈 Сравнение регионов",
        "⏱️ Динамика 2016-2023",
        "👥 Профили кластеров",
        "🔗 Корреляции",
        "💾 Скачать данные",
        "📖 Документация"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
**Проект:** РНФ № 25-28-20473  
**Организация:** ДФИЦ РАН  
**Период:** 2016-2023  
**Наблюдений:** {data['metadata']['n_observations']:,}  
**Регионов:** {data['metadata']['n_regions']}
""")

# ==================== ГЛАВНАЯ СТРАНИЦА ====================
if page == "🏠 Главная":
    st.markdown('<p class="main-header">📊 Дагестан: Демоэкономический Анализ</p>', unsafe_allow_html=True)
    st.markdown("### Интерактивная база данных")
    
    st.markdown(f"""
    **Проект РНФ № 25-28-20473**  
    *Моделирование влияния демоэкономических процессов и самосохранительного 
    потенциала населения на региональное развитие с использованием методов 
    машинного обучения*
    
    **Организация:** {data['metadata']['organization']}  
    **Источник данных:** {data['metadata']['data_source']}  
    **Период:** {data['metadata']['period']}
    """)
    
    st.markdown("---")
    
    # Ключевые цифры
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Наблюдений",
            value=f"{data['metadata']['n_observations']:,}"
        )
    
    with col2:
        st.metric(
            label="🗺️ Регионов",
            value=data['metadata']['n_regions']
        )
    
    with col3:
        st.metric(
            label="📅 Лет",
            value="8 (2016-2023)"
        )
    
    with col4:
        st.metric(
            label="📋 Переменных",
            value=data['metadata']['n_variables']
        )
    
    st.markdown("---")
    
    # Основные находки
    st.subheader("🎯 Ключевые находки")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Демографические особенности**
        - Дагестан моложе на 2.8 года
        - Размер домохозяйств на 39% больше
        - Высокая доля трудоспособных (+3.4 п.п.)
        
        **2. Экономическая уязвимость**
        - Доходы на 38.5% ниже среднероссийских
        - Отрицательная норма сбережений (-0.5%)
        - 62% расходов на продукты (vs 42% в РФ)
        - 31.5% домохозяйств живут в долг
        """)
    
    with col2:
        st.markdown("""
        **3. Институциональные провалы**
        - Региональная поддержка: 2.9% vs 32.1% в РФ
        - Транспортные льготы: 0% vs 8.1%
        - Медицинские льготы: <1% населения
        
        **4. Адаптивные стратегии**
        - Пенсии по инвалидности: 20.2% vs 6.4% (×3.2)
        - Концентрация в возрасте 40-49 лет
        - Компенсация через федеральные каналы
        - Признаки теневой экономики
        """)
    
    # Визуализация ключевых показателей
    st.markdown("---")
    st.subheader("📊 Ключевые показатели: Дагестан vs Россия")
    
    # Берём последний год (с защитой)
    latest_year = data['stats']['year'].max()
    
    dag_latest = data['stats'][(data['stats']['ter'] == '82') & (data['stats']['year'] == latest_year)]
    if len(dag_latest) == 0:
        st.warning("⚠️ Нет данных по Дагестану за последний год")
        st.stop()
    dag_2023 = dag_latest.iloc[0]
    
    rus_latest = data['stats'][(data['stats']['ter'] != '82') & (data['stats']['year'] == latest_year)]
    if len(rus_latest) == 0:
        st.warning("⚠️ Нет данных по России за последний год")
        st.stop()
    rus_2023 = rus_latest.groupby('year').mean().iloc[0]
    
    # Создаём данные для сравнения
    comparison_data = pd.DataFrame({
        'Показатель': [
            'Среднедушевой доход\n(руб/год)',
            'Средний возраст\n(лет)',
            'Размер ДХ\n(человек)',
            'Доля продуктов\n(%)',
            'Норма сбережений\n(%)',
            'Доля города\n(%)'
        ],
        'Дагестан': [
            dag_2023['avg_income'],
            dag_2023['avg_age'],
            dag_2023['avg_hh_size'],
            dag_2023['food_share_pct'],
            dag_2023['savings_rate'],
            dag_2023['urban_pct']
        ],
        'Россия': [
            rus_2023['avg_income'],
            rus_2023['avg_age'],
            rus_2023['avg_hh_size'],
            rus_2023['food_share_pct'],
            rus_2023['savings_rate'],
            rus_2023['urban_pct']
        ]
    })
    
    # График сравнения
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Дагестан',
        x=comparison_data['Показатель'],
        y=comparison_data['Дагестан'],
        marker_color='#e74c3c'
    ))
    
    fig.add_trace(go.Bar(
        name='Россия (среднее)',
        x=comparison_data['Показатель'],
        y=comparison_data['Россия'],
        marker_color='#3498db'
    ))
    
    fig.update_layout(
        title='Сравнение ключевых показателей (2023)',
        barmode='group',
        height=400,
        xaxis_title='',
        yaxis_title='Значение'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Регионы в базе
    st.markdown("---")
    st.subheader("🗺️ Регионы в базе данных")
    
    regions_by_group = data['regions'].groupby('region_group')['region_name'].apply(list).to_dict()
    
    cols = st.columns(3)
    for idx, (group, regions) in enumerate(regions_by_group.items()):
        with cols[idx % 3]:
            st.markdown(f"**{group}** ({len(regions)})")
            for region in sorted(regions):
                is_dag = '🎯 ' if 'Дагестан' in region else '• '
                st.markdown(f"{is_dag}{region}")

# ==================== КАРТА РЕГИОНОВ ====================
elif page == "🗺️ Карта регионов":
    st.title("🗺️ Карта регионов")
    
    # Выбор года и показателя
    col1, col2 = st.columns([1, 2])
    
    with col1:
        year = st.selectbox(
            "📅 Год:",
            sorted(data['stats']['year'].unique(), reverse=True)
        )
    
    with col2:
        metric = st.selectbox(
            "📊 Показатель:",
            ['avg_income', 'avg_age', 'avg_hh_size', 'food_share_pct', 'savings_rate', 'women_pct', 'urban_pct'],
            format_func=lambda x: f"{METRIC_NAMES[x]} ({METRIC_UNITS[x]})"
        )
    
    # Фильтруем данные
    df_year = data['stats'][data['stats']['year'] == year].copy()
    df_year = df_year.sort_values(metric, ascending=False)
    
    # Статистика по топ и низ регионам
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏆 ТОП-3 региона")
        top3 = df_year.nlargest(3, metric)[['region_name', metric]]
        for idx, row in top3.iterrows():
            st.metric(
                label=row['region_name'],
                value=f"{row[metric]:.1f} {METRIC_UNITS[metric]}"
            )
    
    with col2:
        st.markdown("### 🎯 Дагестан")
        dag_data = df_year[df_year['ter'] == '82']
        
        if len(dag_data) == 0:
            st.warning("⚠️ Нет данных по Дагестану за выбранный год")
        else:
            dag_row = dag_data.iloc[0]
            dag_value = dag_row[metric]
            rus_mean = df_year[df_year['ter'] != '82'][metric].mean()
            diff_pct = ((dag_value - rus_mean) / rus_mean * 100)
            
            st.metric(
                label="Значение",
                value=f"{dag_value:.1f} {METRIC_UNITS[metric]}",
                delta=f"{diff_pct:+.1f}% от среднего по РФ"
            )
            
            dag_rank = (df_year[metric] > dag_value).sum() + 1
            st.metric(
                label="Место в рейтинге",
                value=f"{dag_rank} из {len(df_year)}"
            )
    
    with col3:
        st.markdown("### 📉 НИЗ-3 региона")
        bottom3 = df_year.nsmallest(3, metric)[['region_name', metric]]
        for idx, row in bottom3.iterrows():
            st.metric(
                label=row['region_name'],
                value=f"{row[metric]:.1f} {METRIC_UNITS[metric]}"
            )
    
    # Полная таблица с рейтингом
    st.markdown("---")
    st.subheader(f"📊 Полный рейтинг по показателю: {METRIC_NAMES[metric]}")
    
    # Добавляем место в рейтинге
    df_display = df_year[['region_name', 'region_group', metric, 'n_observations']].copy()
    df_display.insert(0, 'Место', range(1, len(df_display) + 1))
    df_display.columns = ['Место', 'Регион', 'Группа', METRIC_NAMES[metric], 'Наблюдений']
    
    # Подсвечиваем Дагестан
    def highlight_dagestan(row):
        if 'Дагестан' in row['Регион']:
            return ['background-color: #ffe6e6'] * len(row)
        return [''] * len(row)
    
    st.dataframe(
        df_display.style.apply(highlight_dagestan, axis=1),
        use_container_width=True,
        height=600
    )
    
    # График распределения
    st.markdown("---")
    st.subheader("📈 Распределение по группам регионов")
    
    fig = px.box(
        df_year,
        x='region_group',
        y=metric,
        color='region_group',
        points='all',
        hover_data=['region_name'],
        title=f'Распределение: {METRIC_NAMES[metric]}',
        labels={
            'region_group': 'Группа регионов',
            metric: f'{METRIC_NAMES[metric]} ({METRIC_UNITS[metric]})'
        }
    )
    
    # Добавляем линию Дагестана (с защитой)
    dag_data_for_line = df_year[df_year['ter'] == '82'][metric]
    if len(dag_data_for_line) > 0:
        dag_value = dag_data_for_line.values[0]
        fig.add_hline(
            y=dag_value,
            line_dash="dash",
            line_color="red",
            annotation_text="Дагестан",
            annotation_position="right"
        )
    
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ==================== СРАВНЕНИЕ РЕГИОНОВ ====================
elif page == "📈 Сравнение регионов":
    st.title("📈 Сравнение регионов")
    
    st.markdown("""
    Сравните показатели различных регионов с возможностью фильтрации по годам,
    группам регионов и типам визуализации.
    """)
    
    # Фильтры
    col1, col2, col3 = st.columns(3)
    
    with col1:
        years = st.multiselect(
            "📅 Годы:",
            sorted(data['stats']['year'].unique()),
            default=[2023, 2022, 2021]
        )
    
    with col2:
        groups = st.multiselect(
            "🗺️ Группы регионов:",
            data['regions']['region_group'].unique().tolist(),
            default=data['regions']['region_group'].unique().tolist()
        )
    
    with col3:
        chart_type = st.selectbox(
            "📊 Тип графика:",
            ['Столбчатая диаграмма', 'Точечная диаграмма', 'Ящик с усами', 'Линейный график']
        )
    
    # Фильтруем данные
    df_filtered = data['stats'][
        (data['stats']['year'].isin(years)) &
        (data['stats']['region_group'].isin(groups))
    ].copy()
    
    if len(df_filtered) == 0:
        st.warning("⚠️ Нет данных для выбранных фильтров")
        st.stop()
    
    # Выбор показателей
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        y_metric = st.selectbox(
            "📊 Показатель (ось Y):",
            ['avg_income', 'avg_age', 'avg_hh_size', 'food_share_pct', 'savings_rate', 'women_pct', 'urban_pct'],
            format_func=lambda x: f"{METRIC_NAMES[x]} ({METRIC_UNITS[x]})"
        )
    
    with col2:
        if chart_type == 'Точечная диаграмма':
            x_metric = st.selectbox(
                "📊 Показатель (ось X):",
                ['avg_income', 'avg_age', 'avg_hh_size', 'food_share_pct', 'savings_rate', 'women_pct', 'urban_pct'],
                index=0,
                format_func=lambda x: f"{METRIC_NAMES[x]} ({METRIC_UNITS[x]})"
            )
    
    # Строим график
    st.markdown("---")
    
    if chart_type == 'Столбчатая диаграмма':
        # Агрегируем по регионам (среднее по годам)
        df_agg = df_filtered.groupby(['region_name', 'region_group'])[y_metric].mean().reset_index()
        df_agg = df_agg.sort_values(y_metric, ascending=True)
        
        fig = px.bar(
            df_agg,
            x=y_metric,
            y='region_name',
            color='region_group',
            orientation='h',
            title=f'{METRIC_NAMES[y_metric]} по регионам (среднее за выбранные годы)',
            labels={
                'region_name': 'Регион',
                y_metric: f'{METRIC_NAMES[y_metric]} ({METRIC_UNITS[y_metric]})',
                'region_group': 'Группа'
            },
            height=800
        )
        
        # Выделяем Дагестан
        colors = ['#e74c3c' if 'Дагестан' in x else '#3498db' 
                 for x in df_agg['region_name']]
        fig.update_traces(marker_color=colors)
    
    elif chart_type == 'Точечная диаграмма':
        fig = px.scatter(
            df_filtered,
            x=x_metric,
            y=y_metric,
            size='n_observations',
            color='region_group',
            hover_data=['region_name', 'year'],
            title=f'{METRIC_NAMES[y_metric]} vs {METRIC_NAMES[x_metric]}',
            labels={
                x_metric: f'{METRIC_NAMES[x_metric]} ({METRIC_UNITS[x_metric]})',
                y_metric: f'{METRIC_NAMES[y_metric]} ({METRIC_UNITS[y_metric]})',
                'region_group': 'Группа',
                'n_observations': 'Наблюдений'
            },
            height=600
        )
        
        # Выделяем Дагестан
        dag_points = df_filtered[df_filtered['ter'] == '82']
        fig.add_trace(go.Scatter(
            x=dag_points[x_metric],
            y=dag_points[y_metric],
            mode='markers',
            marker=dict(size=15, color='red', symbol='star'),
            name='Дагестан',
            hovertemplate='Дагестан<br>' +
                         f'{METRIC_NAMES[x_metric]}: %{{x}}<br>' +
                         f'{METRIC_NAMES[y_metric]}: %{{y}}'
        ))
    
    elif chart_type == 'Ящик с усами':
        fig = px.box(
            df_filtered,
            x='region_group',
            y=y_metric,
            color='region_group',
            points='all',
            hover_data=['region_name', 'year'],
            title=f'Распределение: {METRIC_NAMES[y_metric]}',
            labels={
                'region_group': 'Группа регионов',
                y_metric: f'{METRIC_NAMES[y_metric]} ({METRIC_UNITS[y_metric]})'
            },
            height=600
        )
    
    else:  # Линейный график
        # Группируем по годам и группам
        df_line = df_filtered.groupby(['year', 'region_group'])[y_metric].mean().reset_index()
        
        fig = px.line(
            df_line,
            x='year',
            y=y_metric,
            color='region_group',
            markers=True,
            title=f'Динамика: {METRIC_NAMES[y_metric]}',
            labels={
                'year': 'Год',
                y_metric: f'{METRIC_NAMES[y_metric]} ({METRIC_UNITS[y_metric]})',
                'region_group': 'Группа'
            },
            height=500
        )
        
        # Добавляем Дагестан отдельной линией
        dag_line = df_filtered[df_filtered['ter'] == '82'].groupby('year')[y_metric].mean().reset_index()
        fig.add_trace(go.Scatter(
            x=dag_line['year'],
            y=dag_line[y_metric],
            mode='lines+markers',
            name='Дагестан',
            line=dict(color='red', width=3),
            marker=dict(size=10)
        ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Статистика
    st.markdown("---")
    st.subheader("📊 Статистика по группам")
    
    summary = df_filtered.groupby('region_group')[y_metric].agg([
        ('Среднее', 'mean'),
        ('Медиана', 'median'),
        ('Ст. откл.', 'std'),
        ('Минимум', 'min'),
        ('Максимум', 'max'),
        ('Регионов', 'count')
    ]).round(2)
    
    # Добавляем Дагестан
    dag_stats = df_filtered[df_filtered['ter'] == '82'][y_metric]
    if len(dag_stats) > 0:
        summary.loc['🎯 Дагестан'] = [
            dag_stats.mean(),
            dag_stats.median(),
            dag_stats.std(),
            dag_stats.min(),
            dag_stats.max(),
            len(dag_stats)
        ]
    
    st.dataframe(
        summary,
        use_container_width=True
    )

# ==================== ДИНАМИКА ====================
elif page == "⏱️ Динамика 2016-2023":
    st.title("⏱️ Динамика 2016-2023")
    
    st.markdown("""
    Анализ временных трендов ключевых показателей. Сравнение Дагестана 
    со среднероссийским уровнем.
    """)
    
    # Выбор показателя
    metric = st.selectbox(
        "📊 Выберите показатель:",
        ['doxodn', 'r1v2', 'chlico', 'food_share', 'savings_rate'],
        format_func=lambda x: f"{METRIC_NAMES[x]} ({METRIC_UNITS[x]})"
    )
    
    # График динамики
    fig = go.Figure()
    
    # Дагестан
    dag_data = data['time_series'][data['time_series']['region'] == 'Дагестан']
    fig.add_trace(go.Scatter(
        x=dag_data['year'],
        y=dag_data[metric],
        mode='lines+markers',
        name='🎯 Дагестан',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10)
    ))
    
    # Россия
    rus_data = data['time_series'][data['time_series']['region'] == 'Россия (без Дагестана)']
    fig.add_trace(go.Scatter(
        x=rus_data['year'],
        y=rus_data[metric],
        mode='lines+markers',
        name='🇷🇺 Россия (среднее)',
        line=dict(color='#3498db', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title=f'Динамика: {METRIC_NAMES[metric]}',
        xaxis_title='Год',
        yaxis_title=f'{METRIC_NAMES[metric]} ({METRIC_UNITS[metric]})',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Темпы роста
    st.markdown("---")
    st.subheader("📈 Анализ роста (2016 → 2023)")
    
    # Получаем данные с защитой
    dag_2016_data = dag_data[dag_data['year'] == 2016][metric]
    dag_2023_data = dag_data[dag_data['year'] == 2023][metric]
    rus_2016_data = rus_data[rus_data['year'] == 2016][metric]
    rus_2023_data = rus_data[rus_data['year'] == 2023][metric]
    
    # Проверяем наличие данных
    if len(dag_2016_data) == 0 or len(dag_2023_data) == 0 or len(rus_2016_data) == 0 or len(rus_2023_data) == 0:
        st.warning("⚠️ Недостаточно данных для анализа роста (нужны данные за 2016 и 2023)")
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
            st.metric(
                label="2016",
                value=f"{dag_2016:.1f}"
            )
            st.metric(
                label="2023",
                value=f"{dag_2023:.1f}",
                delta=f"{dag_growth_pct:+.1f}%"
            )
            st.metric(
                label="Абсолютный рост",
                value=f"{dag_growth_abs:+.1f}"
            )
        
        with col2:
            st.markdown("### 🇷🇺 Россия")
            st.metric(
                label="2016",
                value=f"{rus_2016:.1f}"
            )
            st.metric(
                label="2023",
                value=f"{rus_2023:.1f}",
                delta=f"{rus_growth_pct:+.1f}%"
            )
            st.metric(
                label="Абсолютный рост",
                value=f"{rus_growth_abs:+.1f}"
            )
        
        with col3:
            st.markdown("### 📊 Сравнение")
            diff_growth_pct = dag_growth_pct - rus_growth_pct
            st.metric(
                label="Разница темпов роста",
                value=f"{diff_growth_pct:+.1f} п.п.",
                delta="быстрее" if diff_growth_pct > 0 else "медленнее"
            )
            
            gap_2016 = ((dag_2016 - rus_2016) / rus_2016 * 100)
            gap_2023 = ((dag_2023 - rus_2023) / rus_2023 * 100)
            gap_change = gap_2023 - gap_2016
            
            st.metric(
                label="Разрыв в 2016",
                value=f"{gap_2016:+.1f}%"
            )
            st.metric(
                label="Разрыв в 2023",
                value=f"{gap_2023:+.1f}%",
                delta=f"{gap_change:+.1f} п.п."
            )
    
    # Таблица по годам
    st.markdown("---")
    st.subheader("📊 Детальные данные по годам")
    
    pivot = data['time_series'].pivot(
        index='year',
        columns='region',
        values=metric
    ).round(2)
    
    # Добавляем разницу
    pivot['Разница (абс.)'] = (pivot['Дагестан'] - pivot['Россия (без Дагестана)']).round(2)
    pivot['Разница (%)'] = (
        (pivot['Дагестан'] / pivot['Россия (без Дагестана)'] - 1) * 100
    ).round(2)
    
    st.dataframe(
        pivot,
        use_container_width=True
    )

# ==================== ПРОФИЛИ КЛАСТЕРОВ ====================
elif page == "👥 Профили кластеров":
    st.title("👥 Профили кластеров")
    
    if data['clusters'] is None:
        st.warning("⚠️ Данные по кластерам не найдены в базе")
        st.stop()
    
    st.markdown("""
    Кластеризация населения по самосохранительному поведению, демографическим 
    и экономическим характеристикам. Использован метод **K-Means** с k=5.
    """)
    
    # Названия кластеров (можно настроить)
    cluster_names = {
        0: "Кластер 0: Описание",
        1: "Кластер 1: Описание",
        2: "Кластер 2: Описание",
        3: "Кластер 3: Описание",
        4: "Кластер 4: Описание"
    }
    
    # Профили кластеров
    st.markdown("---")
    st.subheader("📊 Характеристики кластеров")
    
    # Преобразуем MultiIndex в нормальный формат
    cluster_df = data['clusters'].copy()
    
    # Если есть MultiIndex колонки, упрощаем
    if isinstance(cluster_df.columns, pd.MultiIndex):
        cluster_df.columns = ['_'.join(col).strip() for col in cluster_df.columns.values]
    
    st.dataframe(
        cluster_df,
        use_container_width=True
    )
    
    # Распределение по регионам
    if data['cluster_dist'] is not None:
        st.markdown("---")
        st.subheader("🗺️ Распределение кластеров по регионам")
        
        # Объединяем с названиями
        dist_with_names = data['cluster_dist'].merge(
            data['regions'][['ter', 'region_name', 'region_group']],
            on='ter'
        )
        
        # Тепловая карта
        st.markdown("#### Тепловая карта (количество наблюдений)")
        
        pivot = dist_with_names.pivot(
            index='region_name',
            columns='cluster',
            values='count'
        ).fillna(0)
        
        fig = px.imshow(
            pivot,
            labels=dict(x="Кластер", y="Регион", color="Количество"),
            aspect="auto",
            height=800,
            color_continuous_scale='YlOrRd',
            text_auto=True
        )
        
        fig.update_xaxes(side="top")
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Доли кластеров по группам регионов
        st.markdown("---")
        st.markdown("#### 📊 Распределение кластеров по группам регионов")
        
        # Считаем доли
        group_cluster = dist_with_names.groupby(['region_group', 'cluster'])['count'].sum().reset_index()
        group_totals = group_cluster.groupby('region_group')['count'].sum().reset_index()
        group_totals.columns = ['region_group', 'total']
        
        group_cluster = group_cluster.merge(group_totals, on='region_group')
        group_cluster['percentage'] = (group_cluster['count'] / group_cluster['total'] * 100).round(1)
        
        fig = px.bar(
            group_cluster,
            x='region_group',
            y='percentage',
            color='cluster',
            title='Доля каждого кластера по группам регионов (%)',
            labels={
                'region_group': 'Группа регионов',
                'percentage': 'Доля (%)',
                'cluster': 'Кластер'
            },
            height=500,
            text='percentage'
        )
        
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='inside')
        fig.update_layout(barmode='stack')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Выделяем Дагестан
        st.markdown("---")
        st.markdown("#### 🎯 Дагестан: Распределение кластеров")
        
        dag_dist = dist_with_names[dist_with_names['ter'] == '82'][['cluster', 'count']].copy()
        dag_dist['percentage'] = (dag_dist['count'] / dag_dist['count'].sum() * 100).round(1)
        
        fig = px.pie(
            dag_dist,
            values='count',
            names='cluster',
            title='Распределение кластеров в Дагестане',
            hole=0.4,
            labels={'cluster': 'Кластер', 'count': 'Количество'}
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)

# ==================== КОРРЕЛЯЦИИ ====================
elif page == "🔗 Корреляции":
    st.title("🔗 Корреляционный анализ")
    
    if data['corr_dag'] is None or data['corr_all'] is None:
        st.warning("⚠️ Данные по корреляциям не найдены")
        st.stop()
    
    st.markdown("""
    Анализ взаимосвязей между переменными. Сравнение корреляций 
    в Дагестане и в среднем по России.
    """)
    
    # Выбор региона
    region_choice = st.radio(
        "Выберите регион:",
        ['🎯 Дагестан', '🇷🇺 Вся Россия', '🔀 Сравнение']
    )
    
    st.markdown("---")
    
    if region_choice == '🎯 Дагестан':
        st.subheader("Корреляционная матрица: Дагестан")
        
        fig = px.imshow(
            data['corr_dag'],
            labels=dict(color="Корреляция"),
            x=data['corr_dag'].columns,
            y=data['corr_dag'].index,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            aspect="auto",
            height=800
        )
        
        fig.update_xaxes(side="bottom")
        fig.update_layout(title="Тепловая карта корреляций (Дагестан)")
        
        st.plotly_chart(fig, use_container_width=True)
    
    elif region_choice == '🇷🇺 Вся Россия':
        st.subheader("Корреляционная матрица: Вся Россия")
        
        fig = px.imshow(
            data['corr_all'],
            labels=dict(color="Корреляция"),
            x=data['corr_all'].columns,
            y=data['corr_all'].index,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            aspect="auto",
            height=800
        )
        
        fig.update_xaxes(side="bottom")
        fig.update_layout(title="Тепловая карта корреляций (Россия)")
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:  # Сравнение
        st.subheader("🔀 Сравнение корреляций: Дагестан vs Россия")
        
        # Находим самые большие различия
        common_vars = data['corr_dag'].columns.intersection(data['corr_all'].columns)
        diff_matrix = data['corr_dag'][common_vars].loc[common_vars] - data['corr_all'][common_vars].loc[common_vars]
        
        # Топ различий
        diff_values = []
        for i in range(len(common_vars)):
            for j in range(i+1, len(common_vars)):
                var1 = common_vars[i]
                var2 = common_vars[j]
                diff = diff_matrix.loc[var1, var2]
                dag_corr = data['corr_dag'].loc[var1, var2]
                rus_corr = data['corr_all'].loc[var1, var2]
                
                diff_values.append({
                    'Переменная 1': var1,
                    'Переменная 2': var2,
                    'Корр. Дагестан': dag_corr,
                    'Корр. Россия': rus_corr,
                    'Разница': diff,
                    'Разница (абс.)': abs(diff)
                })
        
        diff_df = pd.DataFrame(diff_values).sort_values('Разница (абс.)', ascending=False).head(15)
        
        st.markdown("#### 📊 ТОП-15 наибольших различий в корреляциях")
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Дагестан',
            y=[f"{row['Переменная 1']} × {row['Переменная 2']}" for _, row in diff_df.iterrows()],
            x=diff_df['Корр. Дагестан'],
            orientation='h',
            marker_color='#e74c3c'
        ))
        
        fig.add_trace(go.Bar(
            name='Россия',
            y=[f"{row['Переменная 1']} × {row['Переменная 2']}" for _, row in diff_df.iterrows()],
            x=diff_df['Корр. Россия'],
            orientation='h',
            marker_color='#3498db'
        ))
        
        fig.update_layout(
            barmode='group',
            height=600,
            xaxis_title='Коэффициент корреляции',
            yaxis_title='Пара переменных',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Таблица с различиями
        st.markdown("#### 📋 Детальная таблица")
        st.dataframe(
            diff_df[['Переменная 1', 'Переменная 2', 'Корр. Дагестан', 'Корр. Россия', 'Разница']],
            use_container_width=True
        )

# ==================== СКАЧАТЬ ====================
elif page == "💾 Скачать данные":
    st.title("💾 Скачать данные")
    
    st.markdown("""
    Вы можете скачать агрегированные данные в формате CSV для 
    дальнейшего анализа в Excel, R, Python и других инструментах.
    """)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Региональная статистика")
        st.markdown("Показатели по 24 регионам за 2016-2023")
        csv = data['stats'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Скачать regional_statistics.csv",
            data=csv,
            file_name="regional_statistics.csv",
            mime="text/csv"
        )
        st.info(f"📦 Размер: {len(csv)/1024:.1f} KB")
    
    with col2:
        st.markdown("### ⏱️ Временные ряды")
        st.markdown("Дагестан vs Россия по годам")
        csv = data['time_series'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Скачать time_series.csv",
            data=csv,
            file_name="time_series.csv",
            mime="text/csv"
        )
        st.info(f"📦 Размер: {len(csv)/1024:.1f} KB")
    
    if data['clusters'] is not None:
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 👥 Профили кластеров")
            st.markdown("Характеристики 5 кластеров")
            csv = data['clusters'].to_csv(encoding='utf-8').encode('utf-8')
            st.download_button(
                label="⬇️ Скачать cluster_profiles.csv",
                data=csv,
                file_name="cluster_profiles.csv",
                mime="text/csv"
            )
            st.info(f"📦 Размер: {len(csv)/1024:.1f} KB")
        
        with col2:
            st.markdown("### 🗺️ Распределение кластеров")
            st.markdown("По регионам")
            csv = data['cluster_dist'].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Скачать cluster_distribution.csv",
                data=csv,
                file_name="cluster_distribution.csv",
                mime="text/csv"
            )
            st.info(f"📦 Размер: {len(csv)/1024:.1f} KB")
    
    # Справочник регионов
    st.markdown("---")
    st.markdown("### 🗺️ Справочник регионов")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        csv = data['regions'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Скачать regions.csv",
            data=csv,
            file_name="regions.csv",
            mime="text/csv"
        )
        st.info(f"📦 Размер: {len(csv)/1024:.1f} KB")
    
    with col2:
        st.dataframe(data['regions'], use_container_width=True)

# ==================== ДОКУМЕНТАЦИЯ ====================
elif page == "📖 Документация":
    st.title("📖 Документация")
    
    tab1, tab2, tab3, tab4 = st.tabs(["О проекте", "Методология", "Переменные", "Цитирование"])
    
    with tab1:
        st.markdown(f"""
        ## О проекте
        
        **Название:** {data['metadata']['title']}
        
        **Грант:** {data['metadata']['project']}
        
        **Организация:** {data['metadata']['organization']}
        
        **Источник данных:** {data['metadata']['data_source']}
        
        **Период:** {data['metadata']['period']}
        
        **Дата создания:** {data['metadata']['created']}
        
        ---
        
        ### 🎯 Цели проекта:
        
        1. Создание интегрированной базы данных по демоэкономическим процессам
        2. Прогнозные модели демографических изменений и их влияния на экономику
        3. Оценка влияния старения населения на валовой региональный продукт
        4. Исследование самосохранительного поведения населения
        5. Выявление демографических трендов Республики Дагестан
        6. Оценка "демографического дивиденда"
        7. Публикация открытой базы данных для научного сообщества
        
        ---
        
        ### 📊 Основные результаты:
        
        - **Демографический парадокс:** При более молодом населении (+2.8 года) и большем 
          размере домохозяйств (+39%) Дагестан имеет доходы на 38.5% ниже среднероссийских
        
        - **Институциональные провалы:** Региональная система социальной поддержки 
          практически отсутствует (2.9% vs 32.1% в среднем по РФ)
        
        - **Адаптивные стратегии:** Трехкратное превышение доли пенсий по инвалидности 
          (20.2% vs 6.4%) как механизм компенсации институциональных провалов
        
        - **Структура бедности:** 62% расходов на продукты (vs 42% в РФ), отрицательная 
          норма сбережений (-0.5%), признаки теневой экономики
        """)
    
    with tab2:
        st.markdown("""
        ## Методология
        
        ### 📁 Источник данных
        
        Исследование основано на данных **Обследования бюджетов домашних хозяйств (ОБДХ)** 
        Росстата за период 2016-2023 годов. ОБДХ - крупнейшее представительное обследование 
        доходов, расходов и потребления российских домохозяйств.
        
        **Итоговая база:**
        - Наблюдений: 330,302
        - Регионов: 24
        - Период: 2016-2023 (8 лет)
        - Переменных: 90+
        
        ---
        
        ### 📊 Структура данных
        
        **Тип данных:** Repeated cross-sections (повторяющиеся поперечные срезы)
        - 11.4% наблюдений - истинные панели (один и тот же индивид несколько лет)
        - 88.6% - независимые наблюдения
        
        **Уровни анализа:**
        - Индивидуальный (возраст, пол, образование, занятость)
        - Домохозяйство (доходы, расходы, состав)
        - Региональный (24 субъекта РФ)
        
        **Агрегация:**
        - Квартальные данные → годовые (суммирование/усреднение)
        - Экономические переменные: суммирование по 4 кварталам
        - Демографические: значение на конец года (4-й квартал)
        
        ---
        
        ### 🔬 Методы анализа
        
        **1. Кластерный анализ (K-Means, k=5)**
        - Группировка населения по самосохранительному поведению
        - Переменные: демография, экономика, льготы, здоровье
        - Цель: выявление типов поведения
        
        **2. Регрессионный анализ**
        - Оценка влияния демографических факторов на экономику
        - Pooled OLS с робастными стандартными ошибками
        - Кластеризация на уровне региона×год
        
        **3. Временной анализ**
        - Тренды 2016-2023
        - Темпы роста
        - Структурные сдвиги
        
        **4. Сравнительный анализ**
        - Дагестан vs среднероссийский уровень
        - Сравнение по группам регионов
        - Выявление региональных особенностей
        
        ---
        
        ### ✅ Качество данных
        
        - **Математическая консистентность:** 100% (doxodn = doxodsn/chlico)
        - **Полнота ключевых переменных:** >95%
        - **Валидация:** Многоуровневая (структурная, логическая, статистическая)
        - **Общая оценка качества:** 95/100
        
        ---
        
        ### ⚠️ Ограничения
        
        1. **Структура данных:** Не полноценная панель, ограничены панельные методы
        2. **Репрезентативность:** ОБДХ репрезентативно на уровне регионов, но могут быть 
           смещения на уровне отдельных групп
        3. **Отсутствующие данные:** Некоторые важные переменные (например, этничность) 
           отсутствуют в ОБДХ
        4. **Теневая экономика:** Неформальные доходы занижены по определению
        """)
    
    with tab3:
        st.markdown("""
        ## Основные переменные
        
        ### 👥 Демографические
        
        | Переменная | Описание | Единицы |
        |------------|----------|---------|
        | **r1v2** | Возраст | лет |
        | **pol** | Пол | 1=мужчина, 2=женщина |
        | **chlico** | Число лиц в домохозяйстве | человек |
        | **chdet** | Число детей до 16 лет | человек |
        | **mest** | Тип населенного пункта | 1=город, 2=село |
        
        ---
        
        ### 💰 Экономические
        
        | Переменная | Описание | Единицы |
        |------------|----------|---------|
        | **doxodn** | Среднедушевой денежный доход | руб/год |
        | **doxodsn** | Денежный доход домохозяйства | руб/год |
        | **potras** | Потребительские расходы | руб/год |
        | **rasres** | Располагаемые ресурсы | руб/год |
        | **food_share** | Доля расходов на продукты | % |
        | **savings_rate** | Норма сбережений | % |
        | **natdox** | Натуральные поступления | руб/год |
        
        ---
        
        ### 🎓 Занятость и образование
        
        | Переменная | Описание | Коды |
        |------------|----------|------|
        | **r1v73** | Статус занятости | см. кодировку ОБДХ |
        | **r1v8** | Уровень образования | см. кодировку ОБДХ |
        | **chrab** | Число работающих в ДХ | человек |
        
        ---
        
        ### 🏥 Самосохранительное поведение
        
        | Переменная | Описание | Тип |
        |------------|----------|-----|
        | **has_pension** | Получает пенсию | 0/1 |
        | **is_disabled** | Пенсия по инвалидности | 0/1 |
        | **has_federal_benefit** | Федеральные льготы | 0/1 |
        | **has_regional_benefit** | Региональные льготы | 0/1 |
        | **r2v74_unified** | Льготные лекарства | 0/1 |
        | **r2v76_unified** | Санаторно-курортное лечение | 0/1 |
        
        ---
        
        ### 👥 Кластеры
        
        | Кластер | Описание (примерное) |
        |---------|----------------------|
        | **0** | Группа с определёнными характеристиками |
        | **1** | Группа с определёнными характеристиками |
        | **2** | Группа с определёнными характеристиками |
        | **3** | Группа с определёнными характеристиками |
        | **4** | Группа с определёнными характеристиками |
        
        *Примечание: Детальное описание кластеров см. в разделе "Профили кластеров"*
        
        ---
        
        ### 📍 Географические
        
        | Код | Регион | Группа |
        |-----|--------|--------|
        | **82** | Республика Дагестан | Северный Кавказ |
        | **45** | г. Москва | Богатые регионы |
        | **40** | г. Санкт-Петербург | Богатые регионы |
        | ... | ... | ... |
        
        *Полный список см. в разделе "Скачать данные → Справочник регионов"*
        """)
    
    with tab4:
        st.markdown("""
        ## Как цитировать
        
        ### 📝 Формат цитирования базы данных:
        
        ```
        Интерактивная база данных "Дагестан: Демоэкономический анализ" 
        (2016-2023) / Проект РНФ № 25-28-20473. 
        Дагестанский федеральный исследовательский центр РАН. 2025.
        URL: [ссылка на дашборд]
        ```
        
        ---
        
        ### 📚 Формат цитирования для статей:
        
        **На русском:**
        ```
        Автор(ы). Моделирование влияния демоэкономических процессов и 
        самосохранительного потенциала населения на региональное развитие 
        с использованием методов машинного обучения // Название журнала. 
        2025. № X. С. Y-Z. DOI: ...
        ```
        
        **На английском:**
        ```
        Author(s). Modeling the Impact of Demo-Economic Processes and 
        Self-Preservation Potential of the Population on Regional Development 
        Using Machine Learning Methods // Journal Name. 2025. Vol. X. 
        No. Y. Pp. Z-W. DOI: ...
        ```
        
        ---
        
        ### 📄 Лицензия
        
        Данные предоставляются для научных и образовательных целей.
        
        **Условия использования:**
        - ✅ Научные исследования
        - ✅ Образовательные цели
        - ✅ Воспроизведение анализа
        - ✅ Цитирование с указанием источника
        - ❌ Коммерческое использование без согласования
        
        ---
        
        ### 📧 Контакты
        
        По вопросам использования данных и сотрудничества:
        
        **Организация:** Дагестанский федеральный исследовательский центр РАН  
        **Проект:** РНФ № 25-28-20473  
        **Сайт:** [укажите URL]  
        **Email:** [укажите контактный email]
        
        ---
        
        ### 🙏 Благодарности
        
        Исследование выполнено при финансовой поддержке **Российского научного фонда** 
        (грант № **25-28-20473**).
        
        Данные предоставлены **Федеральной службой государственной статистики 
        (Росстат)** в рамках программы Обследования бюджетов домашних хозяйств (ОБДХ).
        
        ---
        
        ### 📊 Техническая информация
        
        **Дашборд создан с использованием:**
        - Python 3.9+
        - Streamlit 1.28
        - Plotly 5.17
        - Pandas 2.1
        
        **Хостинг:** Streamlit Cloud  
        **Исходный код:** [укажите GitHub репозиторий если открыт]  
        
        **Версия дашборда:** 1.0  
        **Дата последнего обновления:** {data['metadata']['created']}
        """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    📊 Интерактивный дашборд проекта РНФ № 25-28-20473<br>
    Дагестанский федеральный исследовательский центр РАН, 2025<br>
    Данные: ОБДХ Росстат, 2016-2023<br>
    <br>
    💡 Для обратной связи и предложений используйте раздел Issues на GitHub
</div>
""", unsafe_allow_html=True)
