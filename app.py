"""
🚀 ДАШБОРД ДЛЯ РНФ № 25-28-20473
Версия 6.0 - Добавлен раздел "Аналитика подгрупп"
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np

# Импорты для расширенной аналитики
from scipy import stats
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
import io

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
    '01': 'Алтайский край', '03': 'Краснодарский край', '07': 'Ставропольский край',
    '12': 'Астраханская область', '18': 'Волгоградская область', '26': 'Республика Ингушетия',
    '40': 'Санкт-Петербург', '45': 'Москва', '46': 'Московская область',
    '60': 'Ростовская область', '76': 'Забайкальский край', '79': 'Республика Адыгея',
    '80': 'Республика Башкортостан', '81': 'Республика Бурятия', '82': 'Республика Дагестан',
    '83': 'Кабардино-Балкарская Республика', '84': 'Республика Алтай', '85': 'Республика Калмыкия',
    '90': 'Республика Северная Осетия - Алания', '91': 'Карачаево-Черкесская Республика',
    '92': 'Республика Татарстан', '93': 'Республика Тыва', '96': 'Чеченская Республика',
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
    'doxodn': 'руб', 'r1v2': 'лет', 'chlico': 'чел',
    'food_share': '%', 'savings_rate': '%', 'mest_urban_pct': '%',
    'pol_female_pct': '%', 'income_reconstructed': 'руб',
}

CLUSTER_NAMES = {
    0: 'K0: Пожилые пенсионеры',
    1: 'K1: Средний класс',
    2: 'K2: Молодые городские',
    3: 'K3: Многодетные',
    4: 'K4: Сельские с натуральным хозяйством'
}

# ============================================================================
# ФУНКЦИИ ФОРМАТИРОВАНИЯ
# ============================================================================

def format_number_ru(value, decimals=0):
    if pd.isna(value): return "—"
    value = round(value, decimals)
    integer_part = int(abs(value))
    decimal_part = abs(value) - integer_part
    integer_str = f"{integer_part:,}".replace(',', '\u00a0')
    if decimals > 0:
        decimal_str = f"{decimal_part:.{decimals}f}"[2:]
        result = f"{integer_str},{decimal_str}" if decimal_part > 0 else integer_str
    else:
        result = integer_str
    return f"-{result}" if value < 0 else result

def format_metric(value, var_name):
    if pd.isna(value): return "—"
    unit = VAR_UNITS.get(var_name, '')
    if var_name in ['doxodn', 'income_reconstructed']:
        return f"{format_number_ru(value, 0)}\u00a0{unit}"
    elif unit == '%':
        return f"{format_number_ru(value, 1)}%"
    else:
        return f"{format_number_ru(value, 1)}\u00a0{unit}"

def add_region_names(df):
    if 'ter' in df.columns:
        df = df.copy()
        df['region_name'] = df['ter'].map(REGION_NAMES).fillna('Регион ' + df['ter'].astype(str))
    return df

# ============================================================================
# КАСТОМНЫЙ CSS
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    .hero {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white; padding: 3rem 2rem; border-radius: 1rem;
        margin-bottom: 2rem; box-shadow: 0 20px 60px rgba(30, 58, 138, 0.3);
        text-align: center;
    }
    .hero h1 { font-size: 2.5rem; font-weight: 900; margin-bottom: 0.5rem; }
    
    .key-finding {
        background: linear-gradient(135deg, #dc2626 0%, #f59e0b 100%);
        color: white; padding: 2.5rem; border-radius: 1rem;
        font-size: 1.8rem; font-weight: 700; text-align: center;
        margin: 2rem 0; box-shadow: 0 20px 60px rgba(220, 38, 38, 0.3);
    }
    .key-finding-number { font-size: 3rem; font-weight: 900; display: block; margin: 0.5rem 0; }
    
    .metric-card {
        background: white; padding: 1.5rem; border-radius: 0.75rem;
        border-left: 4px solid #f59e0b; box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    
    .finding-box {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border-left: 5px solid #3b82f6; padding: 1.5rem; border-radius: 0.75rem; margin: 1rem 0;
    }
    .finding-title { font-size: 1.2rem; font-weight: 700; color: #1e3a8a; }
    .finding-value { font-size: 2rem; font-weight: 900; color: #dc2626; margin: 0.5rem 0; }
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
        
        for df in [regional_stats, cluster_dist]:
            if 'ter' in df.columns:
                df['ter'] = df['ter'].astype(str).str.strip()
        
        regional_stats = add_region_names(regional_stats)
        cluster_dist = add_region_names(cluster_dist)
        
        return {'stats': regional_stats, 'clusters': cluster_dist, 'profiles': cluster_profiles}
    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return None

@st.cache_data
def load_full_data():
    """Загрузка полной базы для детального анализа"""
    try:
        # Вариант 1: Локальный файл
        local_path = Path('data') / 'annual_24regions_2016_2023_WITH_CLUSTERS_FULL.pkl'
        if local_path.exists():
            df = pd.read_pickle(local_path)
            df['ter'] = df['ter'].astype(str).str.strip()
            df = add_region_names(df)
            return df
        
        # Вариант 2: Загрузка из Google Drive через gdown
        try:
            import gdown
        except ImportError:
            st.error("❌ Библиотека gdown не установлена. Установите: pip install gdown")
            st.info("💡 Альтернатива: Скачайте pkl вручную и положите в папку data/")
            return None
        
        # FILE_ID из твоей ссылки
        file_id = "14HMWkhVlIgNExyAv93koCd98fULe3sZN"
        url = f"https://drive.google.com/uc?id={file_id}"
        output_path = "temp_full_data.pkl"
        
        with st.spinner("⏳ Загрузка полной базы из Google Drive (245 МБ, ~2 минуты)..."):
            gdown.download(url, output_path, quiet=False)
            
            df = pd.read_pickle(output_path)
            df['ter'] = df['ter'].astype(str).str.strip()
            df = add_region_names(df)
            
            # Удаляем временный файл
            import os
            os.remove(output_path)
            
            st.success("✅ База загружена (330k записей)!")
            return df
        
    except Exception as e:
        st.warning(f"Полная база недоступна: {e}")
        st.info("💡 Решение: Скачайте pkl с Google Drive и загрузите в GitHub LFS или положите в папку data/")
        return None

data = load_data()
if data is None: st.stop()

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("## 🗺️ Навигация")
    page = st.radio(
        "Выберите раздел:",
        [
            "🏠 Главная",
            "🔍 Аналитика подгрупп (NEW)",
            "🔮 Симулятор 2030",
            "🕵️ Детектор скрытого",
            "🗺️ Карта регионов",
            "📊 Сравнение",
            "⏱️ Динамика",
            "🎯 Кластеры",
            "📥 Данные"
        ],
        index=0
    )
    st.info("РНФ № 25-28-20473\nРук. Гимбатов Ш.М.")

# ============================================================================
# РАЗДЕЛЫ
# ============================================================================

# --- ГЛАВНАЯ ---
if page == "🏠 Главная":
    st.markdown("""
    <div class="hero">
        <h1>🎯 ДЕМОЭКОНОМИЧЕСКИЙ АНАЛИЗ РЕСПУБЛИКИ ДАГЕСТАН</h1>
        <p>Машинное обучение × Региональное развитие</p>
        <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.7;">РНФ № 25-28-20473 | ДФИЦ РАН | 2016-2023</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="key-finding">
        🔥 КЛЮЧЕВАЯ НАУЧНАЯ НАХОДКА
        <span class="key-finding-number">256%</span>
        Скрытый доход в Дагестане превышает официальный в 2,5 раза<br>
        <small style="font-size: 1.2rem; opacity: 0.9;">(125\u00a0651 руб официально → 447\u00a0308 руб реально)</small>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## 📊 Масштаб исследования")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">330\u00a0302</div><div style="font-size: 0.9rem; color: #64748b;">НАБЛЮДЕНИЙ</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">24</div><div style="font-size: 0.9rem; color: #64748b;">РЕГИОНА</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">8</div><div style="font-size: 0.9rem; color: #64748b;">ЛЕТ</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div style="font-size: 2.5rem; font-weight: 900; color: #1e3a8a;">5</div><div style="font-size: 0.9rem; color: #64748b;">КЛАСТЕРОВ</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 🔬 Ключевые научные открытия")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="finding-box">
            <div class="finding-title">💰 Скрытая экономика</div>
            <div class="finding-value">256%</div>
            <div style="color: #475569;">Скрытый доход в Дагестане против 124% по России. ML-реконструкция выявила масштабную теневую занятость.</div>
        </div>
        <div class="finding-box">
            <div class="finding-title">👥 Натуральное хозяйство</div>
            <div class="finding-value">42% vs 1,6%</div>
            <div style="color: #475569;">Кластер K4 (молодые сельские семьи) доминирует в Дагестане, но почти отсутствует в России.</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="finding-box">
            <div class="finding-title">♿ Адаптивные стратегии</div>
            <div class="finding-value">20,2% vs 6,4%</div>
            <div style="color: #475569;">Пенсионеры-инвалиды. Использование статуса инвалидности как экономической стратегии выживания.</div>
        </div>
        <div class="finding-box">
            <div class="finding-title">💸 Барьеры накопления</div>
            <div class="finding-value">r = 0,113</div>
            <div style="color: #475569;">Низкая корреляция доход-сбережения. Структурные барьеры накопления богатства в регионе.</div>
        </div>
        """, unsafe_allow_html=True)

# --- НОВЫЙ: АНАЛИТИКА ПОДГРУПП ---
elif page == "🔍 Аналитика подгрупп (NEW)":
    st.markdown("## 🔍 Детальный анализ подгрупп населения")
    
    st.markdown("""
    <div class="finding-box" style="margin-top:0;">
        <div class="finding-title">📊 Сравнительный анализ</div>
        <div style="color: #475569; margin-top: 0.5rem;">
        Этот раздел работает с <b>полной базой (330k наблюдений)</b> и позволяет сравнивать подгруппы населения по любым характеристикам.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Загружаем полную базу
    df_full = load_full_data()
    
    if df_full is None:
        st.error("❌ Полная база данных не найдена. Загрузите файл `annual_24regions_2016_2023_WITH_CLUSTERS_FULL.pkl` в папку `data/`")
        st.stop()
    
    st.success(f"✅ Загружено: {len(df_full):,} наблюдений")
    
    # --- ФИЛЬТРЫ ---
    st.markdown("### 🎯 Шаг 1: Выберите подгруппы для сравнения")
    
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        st.markdown("#### 🔵 Группа A")
        with st.container(border=True):
            region_a = st.selectbox("Регион:", ['Все'] + sorted(df_full['region_name'].unique()), key='reg_a')
            year_a = st.selectbox("Год:", ['Все'] + sorted(df_full['year'].unique(), reverse=True), key='year_a')
            
            mest_a = st.radio("Местность:", ['Все', 'Город', 'Село'], key='mest_a', horizontal=True)
            pol_a = st.radio("Пол:", ['Все', 'Мужчины', 'Женщины'], key='pol_a', horizontal=True)
            
            cluster_a = st.multiselect("Кластер:", list(CLUSTER_NAMES.values()), key='cluster_a')
            
            age_min_a, age_max_a = st.slider("Возраст:", 0, 100, (0, 100), key='age_a')
    
    with col_filter2:
        st.markdown("#### 🔴 Группа B")
        with st.container(border=True):
            region_b = st.selectbox("Регион:", ['Все'] + sorted(df_full['region_name'].unique()), key='reg_b')
            year_b = st.selectbox("Год:", ['Все'] + sorted(df_full['year'].unique(), reverse=True), key='year_b')
            
            mest_b = st.radio("Местность:", ['Все', 'Город', 'Село'], key='mest_b', horizontal=True)
            pol_b = st.radio("Пол:", ['Все', 'Мужчины', 'Женщины'], key='pol_b', horizontal=True)
            
            cluster_b = st.multiselect("Кластер:", list(CLUSTER_NAMES.values()), key='cluster_b')
            
            age_min_b, age_max_b = st.slider("Возраст:", 0, 100, (0, 100), key='age_b')
    
    # --- ПРИМЕНЕНИЕ ФИЛЬТРОВ ---
    def apply_filters(df, region, year, mest, pol, cluster, age_min, age_max):
        df_filtered = df.copy()
        
        if region != 'Все':
            df_filtered = df_filtered[df_filtered['region_name'] == region]
        if year != 'Все':
            df_filtered = df_filtered[df_filtered['year'] == year]
        if mest == 'Город':
            df_filtered = df_filtered[df_filtered['mest'] == 1]
        elif mest == 'Село':
            df_filtered = df_filtered[df_filtered['mest'] == 2]
        if pol == 'Мужчины':
            df_filtered = df_filtered[df_filtered['pol'] == 1]
        elif pol == 'Женщины':
            df_filtered = df_filtered[df_filtered['pol'] == 2]
        if cluster:
            cluster_ids = [k for k, v in CLUSTER_NAMES.items() if v in cluster]
            df_filtered = df_filtered[df_filtered['cluster'].isin(cluster_ids)]
        
        df_filtered = df_filtered[(df_filtered['r1v2'] >= age_min) & (df_filtered['r1v2'] <= age_max)]
        
        return df_filtered
    
    df_a = apply_filters(df_full, region_a, year_a, mest_a, pol_a, cluster_a, age_min_a, age_max_a)
    df_b = apply_filters(df_full, region_b, year_b, mest_b, pol_b, cluster_b, age_min_b, age_max_b)
    
    # --- РЕЗУЛЬТАТЫ ---
    st.markdown("---")
    st.markdown("### 📈 Шаг 2: Результаты сравнения")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Группа A", f"{len(df_a):,} чел")
    with m2:
        st.metric("Группа B", f"{len(df_b):,} чел")
    with m3:
        ratio = len(df_a) / len(df_b) if len(df_b) > 0 else 0
        st.metric("Соотношение", f"{ratio:.2f}x")
    
    if len(df_a) == 0 or len(df_b) == 0:
        st.warning("⚠️ Одна из групп пуста. Измените фильтры.")
        st.stop()
    
    # Проверяем какие метрики есть в данных (ПЕРЕД ТАБАМИ!)
    available_metrics = []
    for var in ['doxodn', 'r1v2', 'chlico', 'food_share', 'savings_rate']:
        if var in df_a.columns and var in df_b.columns:
            available_metrics.append(var)
    
    if not available_metrics:
        st.error("❌ В данных отсутствуют нужные переменные для анализа")
        st.stop()
    
    # --- ТАБЫ ДЛЯ РАЗНЫХ ВИДОВ АНАЛИЗА ---
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Базовое сравнение", 
        "🔬 Статистические тесты", 
        "🤖 Регрессионный анализ",
        "📈 Динамика во времени"
    ])
    
    # ========================================================================
    # ТАБ 1: БАЗОВОЕ СРАВНЕНИЕ (существующий код)
    # ========================================================================
    with tab1:
        # --- СРАВНИТЕЛЬНАЯ ТАБЛИЦА ---
        st.markdown("#### 📊 Ключевые показатели")
        
        comparison_data = []
        for var in available_metrics:
            try:
                mean_a = df_a[var].mean()
                mean_b = df_b[var].mean()
                median_a = df_a[var].median()
                median_b = df_b[var].median()
                
                diff_mean = mean_a - mean_b
                diff_pct = (diff_mean / mean_b * 100) if mean_b != 0 else 0
                
                comparison_data.append({
                    'Показатель': VAR_NAMES.get(var, var),
                    'Группа A (среднее)': format_metric(mean_a, var),
                    'Группа B (среднее)': format_metric(mean_b, var),
                    'Разница': format_metric(diff_mean, var),
                    'Разница (%)': f"{diff_pct:+.1f}%"
                })
            except Exception as e:
                st.warning(f"⚠️ Ошибка обработки {var}: {e}")
                continue
        
        st.dataframe(pd.DataFrame(comparison_data), width='stretch', hide_index=True)
        
        # --- ГРАФИКИ РАСПРЕДЕЛЕНИЙ ---
        st.markdown("#### 📊 Распределения")
        
        var_to_plot = st.selectbox("Показатель для графика:", available_metrics, format_func=lambda x: VAR_NAMES.get(x, x))
        
        if var_to_plot not in df_a.columns or var_to_plot not in df_b.columns:
            st.error(f"❌ Переменная {var_to_plot} отсутствует в данных")
            st.stop()
        
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df_a[var_to_plot],
                name='Группа A',
                opacity=0.7,
                marker_color=COLORS['russia'],
                nbinsx=30
            ))
            
            fig.add_trace(go.Histogram(
                x=df_b[var_to_plot],
                name='Группа B',
                opacity=0.7,
                marker_color=COLORS['dagestan'],
                nbinsx=30
            ))
            
            fig.update_layout(
                barmode='overlay',
                title=f'Распределение: {VAR_NAMES.get(var_to_plot, var_to_plot)}',
                xaxis_title=VAR_NAMES.get(var_to_plot, var_to_plot),
                yaxis_title='Количество',
                height=400
            )
            
            st.plotly_chart(fig, width="stretch")
            
            # --- BOXPLOT ---
            st.markdown("#### 📦 Boxplot (медианы и квартили)")
            
            boxplot_data = pd.DataFrame({
                'Группа': ['A'] * len(df_a) + ['B'] * len(df_b),
                'Значение': list(df_a[var_to_plot]) + list(df_b[var_to_plot])
            })
            
            fig_box = px.box(
                boxplot_data,
                x='Группа',
                y='Значение',
                color='Группа',
                color_discrete_map={'A': COLORS['russia'], 'B': COLORS['dagestan']},
                title=f'{VAR_NAMES.get(var_to_plot, var_to_plot)} - медианы и квартили'
            )
            fig_box.update_layout(showlegend=False, height=400)
            
            st.plotly_chart(fig_box, width="stretch")
            
        except Exception as e:
            st.error(f"❌ Ошибка построения графиков: {e}")
            st.info("💡 Попробуйте выбрать другой показатель или изменить фильтры")
    
    # ========================================================================
    # ТАБ 2: СТАТИСТИЧЕСКИЕ ТЕСТЫ
    # ========================================================================
    with tab2:
        st.markdown("#### 🔬 Проверка статистической значимости различий")
        
        st.info("💡 Проверяем, являются ли различия между группами статистически значимыми (не случайными)")
        
        test_results = []
        
        for var in available_metrics:
            try:
                data_a = df_a[var].dropna()
                data_b = df_b[var].dropna()
                
                if len(data_a) < 2 or len(data_b) < 2:
                    continue
                
                # T-test (параметрический)
                t_stat, t_pval = stats.ttest_ind(data_a, data_b)
                
                # Mann-Whitney U (непараметрический)
                u_stat, u_pval = stats.mannwhitneyu(data_a, data_b, alternative='two-sided')
                
                # Доверительные интервалы (95%)
                ci_a = stats.t.interval(0.95, len(data_a)-1, 
                                       loc=data_a.mean(), 
                                       scale=stats.sem(data_a))
                ci_b = stats.t.interval(0.95, len(data_b)-1,
                                       loc=data_b.mean(),
                                       scale=stats.sem(data_b))
                
                # Определяем значимость
                is_significant_t = t_pval < 0.05
                is_significant_u = u_pval < 0.05
                
                test_results.append({
                    'Показатель': VAR_NAMES.get(var, var),
                    'Группа A (mean ± SE)': f"{data_a.mean():.2f} ± {stats.sem(data_a):.2f}",
                    'Группа B (mean ± SE)': f"{data_b.mean():.2f} ± {stats.sem(data_b):.2f}",
                    'T-test p-value': f"{t_pval:.4f}",
                    'Значимо (t-test)': "✅ Да" if is_significant_t else "❌ Нет",
                    'Mann-Whitney p-value': f"{u_pval:.4f}",
                    'Значимо (M-W)': "✅ Да" if is_significant_u else "❌ Нет"
                })
                
            except Exception as e:
                st.warning(f"⚠️ Ошибка теста для {var}: {e}")
                continue
        
        if test_results:
            results_df = pd.DataFrame(test_results)
            st.dataframe(results_df, width='stretch', hide_index=True)
            
            st.markdown("---")
            st.markdown("#### 📌 Интерпретация")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                **p-value < 0.05** → различия **статистически значимы**  
                **p-value ≥ 0.05** → различия могут быть случайными
                
                **T-test** - для нормально распределённых данных  
                **Mann-Whitney** - для любых распределений (робастнее)
                """)
            with col2:
                sig_count = sum(1 for r in test_results if "✅" in r['Значимо (t-test)'])
                total_count = len(test_results)
                st.metric("Значимых различий", f"{sig_count} из {total_count}")
            
            # --- ЭКСПОРТ ---
            st.markdown("---")
            st.markdown("#### 📥 Экспорт результатов")
            
            # Создаём Excel файл с несколькими листами
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Лист 1: Статтесты
                results_df.to_excel(writer, sheet_name='Статистические тесты', index=False)
                
                # Лист 2: Описательная статистика группы A
                desc_a = df_a[available_metrics].describe().T
                desc_a.to_excel(writer, sheet_name='Группа A - статистика')
                
                # Лист 3: Описательная статистика группы B
                desc_b = df_b[available_metrics].describe().T
                desc_b.to_excel(writer, sheet_name='Группа B - статистика')
            
            excel_data = output.getvalue()
            
            st.download_button(
                label="📊 Скачать результаты (Excel)",
                data=excel_data,
                file_name=f"subgroup_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        else:
            st.error("❌ Недостаточно данных для статистических тестов")
    
    # ========================================================================
    # ТАБ 3: РЕГРЕССИОННЫЙ АНАЛИЗ
    # ========================================================================
    with tab3:
        st.markdown("#### 🤖 ML-модели для анализа факторов")
        
        st.info("💡 Регрессия показывает, какие факторы влияют на целевую переменную и насколько сильно")
        
        # Выбор целевой переменной
        target_var = st.selectbox(
            "Целевая переменная (что предсказываем):",
            available_metrics,
            format_func=lambda x: VAR_NAMES.get(x, x),
            key='target_regression'
        )
        
        # Предикторы (всё кроме целевой)
        predictor_options = [v for v in available_metrics if v != target_var]
        
        if not predictor_options:
            st.warning("⚠️ Недостаточно переменных для регрессии")
        else:
            selected_predictors = st.multiselect(
                "Факторы (предикторы):",
                predictor_options,
                default=predictor_options[:min(3, len(predictor_options))],
                format_func=lambda x: VAR_NAMES.get(x, x)
            )
            
            if selected_predictors:
                group_choice = st.radio(
                    "Анализировать:",
                    ["Группу A", "Группу B", "Обе группы вместе"],
                    horizontal=True
                )
                
                # Выбираем данные
                if group_choice == "Группу A":
                    df_model = df_a
                elif group_choice == "Группу B":
                    df_model = df_b
                else:
                    df_model = pd.concat([df_a, df_b])
                
                try:
                    # Подготовка данных
                    X = df_model[selected_predictors].dropna()
                    y = df_model.loc[X.index, target_var]
                    
                    if len(X) < 10:
                        st.warning("⚠️ Слишком мало наблюдений (<10) для надёжной регрессии")
                    else:
                        # Нормализация
                        scaler = StandardScaler()
                        X_scaled = scaler.fit_transform(X)
                        
                        # Ridge регрессия
                        model = Ridge(alpha=1.0)
                        model.fit(X_scaled, y)
                        
                        # R² score
                        r2 = model.score(X_scaled, y)
                        
                        # Коэффициенты
                        coef_df = pd.DataFrame({
                            'Фактор': [VAR_NAMES.get(p, p) for p in selected_predictors],
                            'Коэффициент': model.coef_,
                            'Важность (abs)': np.abs(model.coef_)
                        }).sort_values('Важность (abs)', ascending=False)
                        
                        # Результаты
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**R² = {r2:.3f}** (качество модели)")
                            st.caption(f"Модель объясняет {r2*100:.1f}% вариации в '{VAR_NAMES.get(target_var, target_var)}'")
                        
                        with col2:
                            st.metric("Наблюдений", f"{len(X):,}")
                        
                        st.markdown("---")
                        st.markdown("#### 📊 Важность факторов")
                        
                        fig_coef = px.bar(
                            coef_df,
                            x='Важность (abs)',
                            y='Фактор',
                            orientation='h',
                            title=f'Влияние факторов на {VAR_NAMES.get(target_var, target_var)}',
                            color='Коэффициент',
                            color_continuous_scale='RdBu_r'
                        )
                        fig_coef.update_layout(height=400)
                        st.plotly_chart(fig_coef, width="stretch")
                        
                        st.markdown("#### 📋 Коэффициенты регрессии")
                        st.dataframe(
                            coef_df[['Фактор', 'Коэффициент']].reset_index(drop=True),
                            width='stretch',
                            hide_index=True
                        )
                        
                        st.markdown("---")
                        st.markdown("#### 💡 Интерпретация")
                        st.markdown(f"""
                        **Положительный коэффициент** → при росте фактора растёт {VAR_NAMES.get(target_var, target_var)}  
                        **Отрицательный коэффициент** → при росте фактора падает {VAR_NAMES.get(target_var, target_var)}  
                        **Чем больше |коэффициент|** → тем сильнее влияние
                        """)
                        
                except Exception as e:
                    st.error(f"❌ Ошибка построения модели: {e}")
            
            else:
                st.info("👆 Выберите хотя бы один предиктор")
    
    # ========================================================================
    # ТАБ 4: ДИНАМИКА ВО ВРЕМЕНИ
    # ========================================================================
    with tab4:
        st.markdown("#### 📈 Временные тренды 2016-2023")
        
        st.info("💡 Анализ изменения показателей во времени для выбранных подгрупп")
        
        # Проверяем наличие года
        if 'year' not in df_a.columns or 'year' not in df_b.columns:
            st.error("❌ В данных отсутствует переменная 'year'")
        else:
            metric_time = st.selectbox(
                "Показатель для анализа:",
                available_metrics,
                format_func=lambda x: VAR_NAMES.get(x, x),
                key='metric_time'
            )
            
            try:
                # Агрегируем по годам
                trend_a = df_a.groupby('year')[metric_time].agg(['mean', 'std', 'count']).reset_index()
                trend_b = df_b.groupby('year')[metric_time].agg(['mean', 'std', 'count']).reset_index()
                
                trend_a['group'] = 'Группа A'
                trend_b['group'] = 'Группа B'
                
                trend_combined = pd.concat([trend_a, trend_b])
                
                # График линий
                fig_trend = px.line(
                    trend_combined,
                    x='year',
                    y='mean',
                    color='group',
                    markers=True,
                    title=f'Динамика: {VAR_NAMES.get(metric_time, metric_time)}',
                    labels={'year': 'Год', 'mean': VAR_NAMES.get(metric_time, metric_time)},
                    color_discrete_map={'Группа A': COLORS['russia'], 'Группа B': COLORS['dagestan']}
                )
                
                # Добавляем доверительные интервалы
                for group_name, color in [('Группа A', COLORS['russia']), ('Группа B', COLORS['dagestan'])]:
                    group_data = trend_combined[trend_combined['group'] == group_name]
                    
                    # SE = std / sqrt(n)
                    group_data['se'] = group_data['std'] / np.sqrt(group_data['count'])
                    group_data['ci_lower'] = group_data['mean'] - 1.96 * group_data['se']
                    group_data['ci_upper'] = group_data['mean'] + 1.96 * group_data['se']
                    
                    fig_trend.add_scatter(
                        x=group_data['year'].tolist() + group_data['year'].tolist()[::-1],
                        y=group_data['ci_upper'].tolist() + group_data['ci_lower'].tolist()[::-1],
                        fill='toself',
                        fillcolor=color,
                        opacity=0.2,
                        line=dict(width=0),
                        showlegend=False,
                        hoverinfo='skip'
                    )
                
                fig_trend.update_layout(height=500)
                st.plotly_chart(fig_trend, width="stretch")
                
                # --- ЛИНЕЙНЫЙ ТРЕНД ---
                st.markdown("---")
                st.markdown("#### 📐 Линейный тренд и прогноз")
                
                col1, col2 = st.columns(2)
                
                for col, (df_group, group_name, color) in zip(
                    [col1, col2],
                    [(df_a, 'Группа A', COLORS['russia']), (df_b, 'Группа B', COLORS['dagestan'])]
                ):
                    with col:
                        st.markdown(f"**{group_name}**")
                        
                        # Линейная регрессия
                        years = df_group['year'].values.reshape(-1, 1)
                        values = df_group[metric_time].values
                        
                        lr = LinearRegression()
                        lr.fit(years, values)
                        
                        # Коэффициенты
                        slope = lr.coef_[0]
                        intercept = lr.intercept_
                        
                        # Прогноз на 2024-2025
                        future_years = np.array([[2024], [2025]])
                        predictions = lr.predict(future_years)
                        
                        # R²
                        r2 = r2_score(values, lr.predict(years))
                        
                        st.metric(
                            "Тренд (изменение/год)",
                            f"{slope:+.2f}",
                            delta=f"R² = {r2:.3f}"
                        )
                        
                        st.markdown(f"**Прогноз:**")
                        st.markdown(f"2024: **{predictions[0]:.1f}**")
                        st.markdown(f"2025: **{predictions[1]:.1f}**")
                        
                        if slope > 0:
                            st.success(f"📈 Рост на {abs(slope):.2f}/год")
                        elif slope < 0:
                            st.warning(f"📉 Падение на {abs(slope):.2f}/год")
                        else:
                            st.info("➡️ Стабильность")
                
                # --- ТАБЛИЦА ПО ГОДАМ ---
                st.markdown("---")
                st.markdown("#### 📋 Данные по годам")
                
                pivot_table = trend_combined.pivot(index='year', columns='group', values='mean').reset_index()
                pivot_table['Разница'] = pivot_table['Группа A'] - pivot_table['Группа B']
                
                st.dataframe(
                    pivot_table.style.format({
                        'Группа A': '{:.2f}',
                        'Группа B': '{:.2f}',
                        'Разница': '{:+.2f}'
                    }),
                    width='stretch'
                )
                
            except Exception as e:
                st.error(f"❌ Ошибка анализа динамики: {e}")
                st.info("💡 Убедитесь, что в подгруппах есть данные за несколько лет")

# --- СИМУЛЯТОР 2030 (твой код) ---
elif page == "🔮 Симулятор 2030":
    st.markdown("## 🔮 Сценарное моделирование развития")
    
    st.markdown("""
    <div class="finding-box" style="margin-top:0;">
        <div class="finding-title">ℹ️ Как работает эта модель?</div>
        <div style="color: #475569; margin-top: 0.5rem;">
        Мы моделируем влияние трех факторов на экономику к 2030 году.
        Поскольку базовый доход велик, малые изменения могут быть плохо видны на общем графике.
        Поэтому мы добавили <b>детальный график "Драйверы роста"</b>, чтобы вы видели вклад каждого рубля.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_params, col_charts = st.columns([1, 2])
    
    with col_params:
        st.markdown("### 🎛️ Ввод параметров")
        
        with st.container(border=True):
            st.markdown("**1. Урбанизация**")
            urban_delta = st.slider("Сдвиг город/село", -10, 20, 5, format="%+d%%")
            st.caption("Миграция в города повышает производительность труда.")
        
        with st.container(border=True):
            st.markdown("**2. Обеление экономики**")
            shadow_delta = st.slider("Легализация тени", 0, 50, 10, format="%d%%")
            st.caption("Вывод части скрытых доходов (256%) в официальное поле.")
        
        with st.container(border=True):
            st.markdown("**3. Демография**")
            family_delta = st.slider("Размер семьи", -20, 20, -5, format="%+d%%")
            st.caption("Уменьшение размера семьи увеличивает доход на душу.")
        
    with col_charts:
        base_dag = data['stats'][(data['stats']['ter'] == '82') & (data['stats']['year'] == 2023)].iloc[0]
        base_income = base_dag['doxodn']
        
        urb_factor = 1 + (urban_delta * 0.008)
        urb_rub = base_income * (urb_factor - 1)
        
        fam_factor = 1 - (family_delta * 0.01)
        base_plus_urb = base_income + urb_rub
        fam_rub = (base_plus_urb * fam_factor) - base_plus_urb
        
        hidden_income_pool = base_income * 2.56 
        shadow_rub = hidden_income_pool * (shadow_delta / 100)
        
        total_growth = urb_rub + fam_rub + shadow_rub
        new_income = base_income + total_growth
        real_growth_pct = (total_growth / base_income) * 100
        
        st.markdown("### 📊 Результаты")
        
        m1, m2, m3 = st.columns(3)
        with m1: st.metric("База 2023", format_metric(base_income, 'doxodn'))
        with m2: st.metric("Прогноз 2030", format_metric(new_income, 'doxodn'), delta=f"{real_growth_pct:.1f}%")
        with m3: st.metric("Чистый прирост", f"+{format_number_ru(total_growth)} руб")

        tab_drivers, tab_waterfall = st.tabs(["🔍 Драйверы роста (Детально)", "🌊 Общая картина (Waterfall)"])
        
        with tab_drivers:
            drivers_df = pd.DataFrame({
                'Фактор': ['Урбанизация', 'Демография', 'Обеление'],
                'Вклад (руб)': [urb_rub, fam_rub, shadow_rub],
                'Color': [COLORS['russia'], COLORS['warning'], COLORS['success']]
            })
            
            fig_bar = px.bar(
                drivers_df, 
                y='Фактор', 
                x='Вклад (руб)', 
                orientation='h',
                text_auto='.0f',
                title="Из чего складывается рост дохода?",
                color='Фактор',
                color_discrete_sequence=[COLORS['russia'], COLORS['warning'], COLORS['success']]
            )
            fig_bar.update_layout(showlegend=False, height=350)
            fig_bar.update_traces(texttemplate='%{x:,.0f} ₽', textposition='outside')
            st.plotly_chart(fig_bar, width="stretch")
            
            st.caption("На этом графике показан *только прирост*. Здесь хорошо видно, какой фактор вносит наибольший вклад.")

        with tab_waterfall:
            fig_wf = go.Figure(go.Waterfall(
                name = "20", orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "total"],
                x = ["2023", "Урбанизация", "Демография", "Обеление", "2030"],
                textposition = "outside",
                text = [f"{int(x/1000)}k" for x in [base_income, urb_rub, fam_rub, shadow_rub, new_income]],
                y = [base_income, urb_rub, fam_rub, shadow_rub, new_income],
                connector = {"line":{"color":"#cbd5e1"}},
                decreasing = {"marker":{"color":COLORS['warning']}},
                increasing = {"marker":{"color":COLORS['success']}},
                totals = {"marker":{"color":COLORS['primary']}}
            ))
            fig_wf.update_layout(title="Общая динамика дохода", height=350)
            st.plotly_chart(fig_wf, width="stretch")

# --- ДЕТЕКТОР СКРЫТОГО (твой код) ---
elif page == "🕵️ Детектор скрытого":
    st.markdown("## 🕵️ ML-Реконструкция доходов (Data-Driven)")
    
    st.markdown("""
    <div class="finding-box" style="margin-top:0;">
        <div class="finding-title">🔬 Алгоритм поиска аномалий</div>
        <div style="color: #475569; margin-top: 0.5rem;">
        Инструмент обращается к <b>загруженному датасету (330k наблюдений)</b>, 
        находит кластер людей, похожих на введенный профиль, и берет их реальные показатели потребления в качестве эталона.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_input, col_result = st.columns([1, 1.3])
    
    with col_input:
        st.markdown("### 1. Профиль субъекта")
        with st.container(border=True):
            loc_type = st.radio("Местность", ["Город", "Село"], horizontal=True)
            age_group = st.selectbox("Возрастная группа", ["Молодежь (18-35)", "Средний возраст (36-60)", "Пенсионеры (60+)"])
            family_size = st.slider("Размер семьи (чел)", 1, 10, 4)
            st.markdown("---")
            st.markdown("**Финансовые декларации**")
            official_income = st.number_input("Заявленный доход (семья/мес)", value=50000, step=1000)
            food_expense = st.number_input("Реальные траты на еду (мес)", value=25000, step=1000)

    predicted_cluster_id = 1
    cluster_desc = "K1: Средний класс"
    
    if age_group == "Пенсионеры (60+)":
        predicted_cluster_id = 0
        cluster_desc = "K0: Пенсионеры"
    elif loc_type == "Село" and family_size >= 4:
        predicted_cluster_id = 4
        cluster_desc = "K4: Сельские (Натуральное хоз-во)"
    elif loc_type == "Город" and age_group == "Молодежь (18-35)":
        predicted_cluster_id = 2
        cluster_desc = "K2: Городская молодежь"
    elif family_size >= 5:
        predicted_cluster_id = 3
        cluster_desc = "K3: Многодетные"
    
    df_prof = data['profiles']
    
    if df_prof is not None and not df_prof.empty:
        cluster_stats = df_prof[df_prof['cluster'] == predicted_cluster_id].iloc[0]
        ref_food_share = cluster_stats.get('food_share', 45.0) 
        ref_savings = cluster_stats.get('savings_rate', 5.0)
        
        reconstructed_income = food_expense / (ref_food_share / 100)
        reconstructed_income_full = reconstructed_income / ((100 - ref_savings)/100)
        hidden_income = reconstructed_income_full - official_income
        gap_pct = (hidden_income / official_income) * 100 if official_income > 0 else 0

        is_anomaly = hidden_income > 5000
        
        if is_anomaly:
            status_color = "#dc2626"
            status_label = "⚠️ СКРЫТЫЙ ДОХОД:"
            status_value = f"{format_number_ru(hidden_income)} руб."
            interpretation = f"Представители кластера *{cluster_desc}* при таких тратах обычно имеют доход не менее **{format_number_ru(reconstructed_income_full)}**. Разница указывает на теневые источники."
        else:
            status_color = "#10b981"
            status_label = "✅ СТАТУС:"
            status_value = "Норма"
            interpretation = "Расходы субъекта соответствуют модели потребления выбранного кластера. Данные выглядят достоверными."

        with col_result:
            st.markdown("### 2. Результат анализа")
            st.info(f"📊 Кластер субъекта: **{cluster_desc}**")
            
            c1, c2 = st.columns(2)
            c1.metric("Эталонная доля еды", f"{ref_food_share:.1f}%")
            c2.metric("Эталон сбережений", f"{ref_savings:.1f}%")
            st.markdown("---")
            
            html_card = f"""
<div style="background: white; padding: 1.5rem; border-radius: 0.8rem; border: 1px solid #e2e8f0; margin-bottom:1rem;">
<div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;">РАСЧЕТНАЯ МОДЕЛЬ (НА ОСНОВЕ ДАННЫХ):</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
    <span>Заявлено:</span>
    <span style="font-weight: bold;">{format_number_ru(official_income)} руб.</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom:10px; border-bottom:1px solid #eee;">
    <span>Реконструкция (ML):</span>
    <span style="font-weight: bold; color: #1e3a8a;">{format_number_ru(reconstructed_income_full)} руб.</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: center;">
    <span style="font-weight: bold; color: {status_color};">{status_label}</span>
    <span style="font-size: 1.5rem; font-weight: 900; color: {status_color};">{status_value}</span>
</div>
</div>
"""
            st.markdown(html_card, unsafe_allow_html=True)
            
            st.write(f"**Интерпретация:** {interpretation}")

    else:
        st.error("⚠️ Не удалось загрузить профили кластеров. Проверьте файл cluster_profiles.csv")

# --- КАРТА (твой код) ---
elif page == "🗺️ Карта регионов":
    st.markdown("## 🗺️ Интерактивная карта России")
    col1, col2 = st.columns(2)
    with col1: year = st.selectbox("📅 Год:", sorted(data['stats']['year'].unique(), reverse=True))
    with col2: metric = st.selectbox("📊 Показатель:", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES.get(x, x))
    
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    region_coords = {
        '01': (53.0, 83.0), '03': (45.0, 39.0), '07': (45.0, 43.0), '12': (46.3, 48.0),
        '18': (48.7, 44.5), '26': (43.3, 45.0), '40': (59.9, 30.3), '45': (55.75, 37.6),
        '46': (55.8, 38.0), '60': (47.2, 39.7), '76': (52.0, 114.0), '79': (44.6, 40.0),
        '80': (54.7, 56.0), '81': (52.0, 108.0), '82': (42.2, 47.1), '83': (43.5, 43.5),
        '84': (51.0, 86.0), '85': (46.0, 45.0), '90': (43.0, 44.0), '91': (43.5, 42.0),
        '92': (55.8, 49.1), '93': (51.7, 94.4), '96': (43.3, 45.7), '99': (48.5, 135.0),
    }
    
    df_year = df_year[df_year['ter'].isin(region_coords.keys())].copy()
    df_year['lat'] = df_year['ter'].map(lambda x: region_coords[x][0])
    df_year['lon'] = df_year['ter'].map(lambda x: region_coords[x][1])
    df_year['formatted_value'] = df_year[metric].apply(lambda x: format_metric(x, metric))
    
    fig = px.scatter_geo(
        df_year, lat='lat', lon='lon', size=metric, color=metric,
        hover_name='region_name',
        hover_data={'lat': False, 'lon': False, metric: False, 'formatted_value': True},
        color_continuous_scale=[[0, COLORS['russia']], [0.5, COLORS['warning']], [1, COLORS['dagestan']]],
        size_max=50, title=f'{VAR_NAMES.get(metric, metric)} ({year})',
        labels={'formatted_value': VAR_NAMES.get(metric, metric)}
    )
    fig.update_geos(
        showcountries=True, countrycolor='lightgray', showsubunits=False, showland=True,
        landcolor='white', lataxis_range=[40, 72], lonaxis_range=[30, 150],
        projection_type='mercator', bgcolor='#f8fafc', resolution=50, center=dict(lat=60, lon=90)
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=50, b=0))
    st.plotly_chart(fig, width="stretch")

# --- СРАВНЕНИЕ (твой код) ---
elif page == "📊 Сравнение":
    st.markdown("## 📊 Сравнение регионов")
    year = st.selectbox("📅 Год:", sorted(data['stats']['year'].unique(), reverse=True))
    df_year = data['stats'][data['stats']['year'] == year].copy()
    metric = st.selectbox("📊 Показатель:", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES.get(x, x))
    
    df_sorted = df_year.sort_values(metric, ascending=True)
    fig = px.bar(
        df_sorted, x=metric, y='region_name', orientation='h', color=metric,
        color_continuous_scale=[[0, COLORS['russia']], [0.5, COLORS['warning']], [1, COLORS['dagestan']]],
        title=f'{VAR_NAMES.get(metric, metric)} ({year})'
    )
    dag_val = df_year[df_year['ter'] == '82'][metric]
    if len(dag_val) > 0:
        fig.add_vline(x=dag_val.values[0], line_dash="dash", line_color=COLORS['dagestan'], annotation_text="Дагестан")
    fig.update_layout(height=800, showlegend=False)
    st.plotly_chart(fig, width="stretch")

# --- ДИНАМИКА (твой код) ---
elif page == "⏱️ Динамика":
    st.markdown("## ⏱️ Динамика 2016-2023")
    st.info("💡 Нажмите ▶️ для анимации")
    c1, c2 = st.columns(2)
    with c1: x_metric = st.selectbox("Ось X:", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES[x])
    with c2: y_metric = st.selectbox("Ось Y:", list(VAR_NAMES.keys()), index=4, format_func=lambda x: VAR_NAMES[x])
    
    df_anim = data['stats'].copy()
    df_anim['is_dagestan'] = df_anim['ter'] == '82'
    
    fig = px.scatter(
        df_anim, x=x_metric, y=y_metric, animation_frame='year', animation_group='ter',
        size='chlico', color='is_dagestan', hover_name='region_name',
        color_discrete_map={True: COLORS['dagestan'], False: COLORS['russia']},
        labels={x_metric: VAR_NAMES[x_metric], y_metric: VAR_NAMES[y_metric]}
    )
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, width="stretch")

# --- КЛАСТЕРЫ (твой код) ---
elif page == "🎯 Кластеры":
    st.markdown("## 🎯 Кластерный анализ")
    tab1, tab2, tab3 = st.tabs([
        "📊 Общее распределение", 
        "🧩 Глубокий анализ (Heatmap)",
        "🔬 Детальное сравнение"
    ])
    
    with tab1:
        cluster_summary = data['clusters'].groupby('cluster')['count'].sum().reset_index()
        cluster_summary['cluster_name'] = cluster_summary['cluster'].map(CLUSTER_NAMES)
        
        fig = px.pie(
            cluster_summary, values='count', names='cluster_name', hole=0.4,
            color='cluster', color_discrete_sequence=CLUSTER_COLORS,
            title='Распределение по кластерам'
        )
        st.plotly_chart(fig, width="stretch")
        
        st.markdown("### 🎯 Дагестан vs Россия")
        dag_clusters = data['clusters'][data['clusters']['ter'] == '82'].groupby('cluster')['count'].sum()
        all_clusters = data['clusters'].groupby('cluster')['count'].sum()
        dag_pct = (dag_clusters / dag_clusters.sum() * 100)
        all_pct = (all_clusters / all_clusters.sum() * 100)
        
        comparison = pd.DataFrame({
            'Кластер': [CLUSTER_NAMES[i] for i in range(5)],
            'Дагестан (%)': [dag_pct.get(i, 0) for i in range(5)],
            'Россия (%)': [all_pct.get(i, 0) for i in range(5)]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Дагестан', x=comparison['Кластер'], y=comparison['Дагестан (%)'], marker_color=COLORS['dagestan']))
        fig.add_trace(go.Bar(name='Россия', x=comparison['Кластер'], y=comparison['Россия (%)'], marker_color=COLORS['russia']))
        fig.update_layout(barmode='group', height=500)
        st.plotly_chart(fig, width="stretch")

    with tab2:
        st.markdown("### 🌡️ Тепловая карта характеристик")
        st.caption("Показывает, чем каждый кластер отличается от среднего (Z-Score)")
        
        df_prof = data['profiles'].copy()
        if 'cluster' in df_prof.columns:
            df_prof = df_prof.set_index('cluster')
            
        cols = [c for c in df_prof.columns if c in VAR_NAMES]
        heatmap_data = df_prof[cols].rename(columns=VAR_NAMES)
        heatmap_norm = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()
        
        fig_hm = px.imshow(
            heatmap_norm.T,
            labels=dict(x="Кластер", y="Показатель", color="Отклонение"),
            x=[CLUSTER_NAMES.get(i, str(i)) for i in heatmap_data.index],
            y=heatmap_data.columns,
            color_continuous_scale='RdBu_r', aspect="auto"
        )
        st.plotly_chart(fig_hm, width="stretch")
    
    with tab3:
        st.markdown("### 🔬 Интерактивное сравнение кластеров")
        st.info("💡 Выберите характеристики и кластеры для детального анализа")
        
        # Загружаем полную базу для анализа
        df_full = load_full_data()
        
        if df_full is None:
            st.warning("⚠️ Полная база недоступна. Показываю агрегированные данные.")
            # Используем profiles
            df_analysis = data['profiles'].copy()
        else:
            df_analysis = df_full.copy()
        
        # --- ФИЛЬТРЫ ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Выбор региональных групп (МУЛЬТИВЫБОР!)
            selected_region_groups = st.multiselect(
                "📍 Региональные группы для сравнения:",
                ["Дагестан", "Россия без Дагестана", "Северный Кавказ", 
                 "Развитые регионы", "Отсталые регионы"],
                default=["Дагестан", "Россия без Дагестана"],
                help="Выберите 2-5 групп регионов для сравнения"
            )
        
        with col2:
            # Выбор кластеров для сравнения
            selected_clusters = st.multiselect(
                "🎯 Кластеры для сравнения:",
                options=list(CLUSTER_NAMES.values()),
                default=[CLUSTER_NAMES[4]],  # K4 по умолчанию (натуральное хозяйство)
                help="Выберите 1-5 кластеров"
            )
        
        if not selected_region_groups:
            st.warning("⚠️ Выберите хотя бы одну региональную группу")
        elif not selected_clusters:
            st.warning("⚠️ Выберите хотя бы один кластер")
        else:
            # Конвертируем названия обратно в ID
            cluster_ids = [k for k, v in CLUSTER_NAMES.items() if v in selected_clusters]
            
            # Функция фильтрации по региону
            def filter_by_region(df, region_name):
                if 'ter' not in df.columns:
                    return df
                
                if region_name == "Дагестан":
                    return df[df['ter'] == '82']
                elif region_name == "Россия без Дагестана":
                    return df[df['ter'] != '82']
                elif region_name == "Северный Кавказ":
                    sk_codes = ['01', '07', '26', '91']
                    return df[df['ter'].isin(sk_codes)]
                elif region_name == "Развитые регионы":
                    dev_codes = ['45', '40', '78']
                    return df[df['ter'].isin(dev_codes)]
                elif region_name == "Отсталые регионы":
                    poor_codes = ['79', '81', '83']
                    return df[df['ter'].isin(poor_codes)]
                else:
                    return df
            
            st.markdown("---")
            
# --- ВЫБОР ХАРАКТЕРИСТИК ---
            st.markdown("#### 📊 Выберите характеристики для анализа")
            
            # Группируем характеристики по категориям
            char_categories = {
                "Демография": ['r1v2', 'pol', 'chlico'],
                "Социальный статус": ['r1v42', 'r1v45', 'r1v46', 'r1v47'],
                "Экономика": ['doxodn', 'raxodn', 'food_share', 'savings_rate'],
                "Натуральное хозяйство": ['natdoxod_total', 'natdoxod_share']
            }
            
            col_cat1, col_cat2 = st.columns(2)
            
            selected_chars = []
            
            with col_cat1:
                st.markdown("**Основные показатели:**")
                for var in ['doxodn', 'r1v2', 'chlico', 'food_share']:
                    # ИСПРАВЛЕНО: df_filtered -> df_analysis
                    if var in df_analysis.columns:
                        if st.checkbox(VAR_NAMES.get(var, var), value=(var=='doxodn'), key=f'char_{var}'):
                            selected_chars.append(var)
            
            with col_cat2:
                st.markdown("**Дополнительные показатели:**")
                additional_vars = ['raxodn', 'savings_rate', 'natdoxod_total', 'natdoxod_share']
                for var in additional_vars:
                    # ИСПРАВЛЕНО: df_filtered -> df_analysis
                    if var in df_analysis.columns:
                        if st.checkbox(VAR_NAMES.get(var, var), value=False, key=f'char_{var}'):
                            selected_chars.append(var)
            
            if not selected_chars:
                st.info("👆 Выберите хотя бы одну характеристику")
            else:
                st.markdown("---")
                
                # --- РАСЧЕТ СТАТИСТИКИ ПО РЕГИОНАМ × КЛАСТЕРАМ ---
                st.markdown(f"#### 📋 Сравнительная таблица: Регионы × Кластеры")
                
                cluster_stats = []
                
                # Двойной цикл: регионы × кластеры
                for region_name in selected_region_groups:
                    df_region = filter_by_region(df_analysis, region_name)
                    
                    for cluster_id in cluster_ids:
                        if 'cluster' not in df_region.columns:
                            continue
                        
                        cluster_data = df_region[df_region['cluster'] == cluster_id]
                        
                        if len(cluster_data) == 0:
                            continue
                        
                        stats_row = {
                            'Регион': region_name,
                            'Кластер': CLUSTER_NAMES[cluster_id],
                            'N': len(cluster_data),
                            'Доля в регионе (%)': len(cluster_data) / len(df_region) * 100 if len(df_region) > 0 else 0
                        }
                        
                        # Добавляем выбранные характеристики
                        for var in selected_chars:
                            if var in cluster_data.columns:
                                mean_val = cluster_data[var].mean()
                                stats_row[VAR_NAMES.get(var, var)] = mean_val
                        
                        cluster_stats.append(stats_row)
                
                if not cluster_stats:
                    st.error("❌ Нет данных для выбранных регионов и кластеров")
                    st.stop()
                
                df_table = pd.DataFrame(cluster_stats)
                
                # Форматирование
                format_dict = {
                    'N': '{:,.0f}',
                    'Доля в регионе (%)': '{:.1f}'
                }
                for var in selected_chars:
                    var_name = VAR_NAMES.get(var, var)
                    if var in ['doxodn', 'raxodn', 'natdoxod_total']:
                        format_dict[var_name] = '{:,.0f}'
                    elif var in ['food_share', 'savings_rate', 'natdoxod_share']:
                        format_dict[var_name] = '{:.1f}'
                    else:
                        format_dict[var_name] = '{:.2f}'
                
                st.dataframe(
                    df_table.style.format(format_dict),
                    width='stretch',
                    hide_index=True
                )
                
                # --- ВИЗУАЛИЗАЦИЯ ---
                st.markdown("---")
                st.markdown("#### 📊 Визуализация различий")
                
                viz_type = st.radio(
                    "Тип графика:",
                    ["Bar chart (столбцы)", "Grouped bar (группировка)", "Heatmap (тепловая карта)"],
                    horizontal=True
                )
                
                metric_to_plot = st.selectbox(
                    "Показатель для графика:",
                    selected_chars,
                    format_func=lambda x: VAR_NAMES.get(x, x)
                )
                
                plot_data = df_table.copy()
                
                # Создаём комбинированную метку для оси X
                plot_data['Регион-Кластер'] = plot_data['Регион'] + ' - ' + plot_data['Кластер']
                
                if viz_type == "Bar chart (столбцы)":
                    fig = px.bar(
                        plot_data,
                        x='Регион-Кластер',
                        y=VAR_NAMES.get(metric_to_plot, metric_to_plot),
                        color='Регион',
                        title=f'{VAR_NAMES.get(metric_to_plot, metric_to_plot)}: сравнение регионов и кластеров',
                        labels={'Регион-Кластер': ''}
                    )
                    fig.update_layout(height=500, xaxis_tickangle=-45)
                    st.plotly_chart(fig, width="stretch")
                
                elif viz_type == "Grouped bar (группировка)":
                    # Группировка: по регионам показать кластеры
                    fig = px.bar(
                        plot_data,
                        x='Кластер',
                        y=VAR_NAMES.get(metric_to_plot, metric_to_plot),
                        color='Регион',
                        barmode='group',
                        title=f'{VAR_NAMES.get(metric_to_plot, metric_to_plot)}: кластеры по регионам'
                    )
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, width="stretch")
                
                elif viz_type == "Heatmap (тепловая карта)":
                    # Pivot для heatmap: строки = регионы, столбцы = кластеры
                    pivot_data = plot_data.pivot(
                        index='Регион',
                        columns='Кластер',
                        values=VAR_NAMES.get(metric_to_plot, metric_to_plot)
                    )
                    
                    fig = px.imshow(
                        pivot_data,
                        labels=dict(x="Кластер", y="Регион", color=VAR_NAMES.get(metric_to_plot, metric_to_plot)),
                        aspect="auto",
                        color_continuous_scale='RdYlGn',
                        title=f'{VAR_NAMES.get(metric_to_plot, metric_to_plot)}: Heatmap'
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, width="stretch")
                
                # --- ЭКСПОРТ ---
                st.markdown("---")
                st.markdown("#### 📥 Экспорт результатов")
                
                # CSV
                csv = df_table.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📊 Скачать таблицу (CSV)",
                    data=csv,
                    file_name=f"cluster_comparison_{'_'.join(selected_region_groups)}_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

# --- ДАННЫЕ (твой код) ---
elif page == "📥 Данные":
    st.markdown("## 📥 Экспорт данных")
    
    files = {
        'regional_stats.csv': 'Статистика по регионам',
        'cluster_distribution.csv': 'Распределение кластеров',
        'cluster_profiles.csv': 'Профили кластеров'
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
                        st.download_button("⬇️ Скачать", data=f, file_name=filename, mime='text/csv', key=filename)
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
