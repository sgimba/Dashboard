"""
🚀 ВАУ-ДАШБОРД ДЛЯ РНФ № 25-28-20473
Версия 5.1 (FINAL INTEGRATED) - Полный функционал + Понятные объяснения
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
    .metric-card:hover { transform: translateY(-5px); box-shadow: 0 12px 30px rgba(0,0,0,0.1); }
    
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
            "🔮 Симулятор 2030 (NEW)",
            "🕵️ Детектор скрытого (NEW)",
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

# --- НОВЫЙ СИМУЛЯТОР (С ПОЯСНЕНИЯМИ) ---
elif page == "🔮 Симулятор 2030 (NEW)":
    st.markdown("## 🔮 Сценарное моделирование развития")
    
    st.markdown("""
    <div class="finding-box" style="margin-top:0;">
        <div class="finding-title">ℹ️ Как работает эта модель?</div>
        <div style="color: #475569; margin-top: 0.5rem;">
        Мы моделируем влияние трех фундаментальных факторов на экономику Дагестана к 2030 году.
        Модель рассчитывает <b>"демографический дивиденд"</b> и эффект от <b>легализации теневого сектора</b>.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🎛️ Ввод параметров")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        st.markdown("**1. Урбанизация**")
        urban_delta = st.slider("Сдвиг город/село", -10, 20, 0, format="%+d%%")
        st.caption("Миграция из сел (низкая доходность) в города. +1% урбанизации дает прирост производительности.")
        
        st.markdown("---")
        st.markdown("**2. Обеление экономики**")
        shadow_delta = st.slider("Легализация тени", 0, 50, 0, format="%d%%")
        st.caption("Какую часть скрытого дохода (256%) удастся вывести в официальное поле.")
        
        st.markdown("---")
        st.markdown("**3. Демография**")
        family_delta = st.slider("Размер семьи", -20, 20, 0, format="%+d%%")
        st.caption("Снижение размера семьи увеличивает доход на душу населения.")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # Логика модели
        base_dag = data['stats'][(data['stats']['ter'] == '82') & (data['stats']['year'] == 2023)].iloc[0]
        base_income = base_dag['doxodn']
        
        # Коэффициенты (упрощенная эконометрическая модель)
        urb_factor = 1 + (urban_delta * 0.008) # Эластичность 0.8
        fam_factor = 1 - (family_delta * 0.01) # Обратная зависимость
        
        # Расчет "кусков" пирога
        hidden_income_pool = base_income * 2.56 # Из вашей находки 256%
        legalized_sum = hidden_income_pool * (shadow_delta / 100)
        
        # Итоговый прогноз
        organic_growth = base_income * urb_factor * fam_factor
        new_income = organic_growth + legalized_sum
        
        real_growth_pct = ((new_income - base_income) / base_income) * 100
        
        st.markdown("### 📊 Результаты моделирования")
        
        # Метрики
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("База 2023", format_metric(base_income, 'doxodn'))
        with m2:
            st.metric("Прогноз 2030", format_metric(new_income, 'doxodn'), 
                      delta=f"{real_growth_pct:.1f}%")
        with m3:
            st.metric("Эффект обеления", f"+{format_number_ru(legalized_sum)} руб",
                      help="Сумма, которая перейдет из 'конвертов' в официальную статистику")

        # График Waterfall
        fig = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["2023 (Факт)", "Эффект Урбанизации", "Демогр. эффект", "Вывод из тени", "2030 (Прогноз)"],
            textposition = "outside",
            text = [f"{int(x/1000)}k" for x in [base_income, base_income*(urb_factor-1), base_income*(fam_factor-1)*urb_factor, legalized_sum, new_income]],
            y = [base_income, 
                 base_income * (urb_factor - 1),
                 base_income * (fam_factor - 1) * urb_factor,
                 legalized_sum, 
                 new_income],
            connector = {"line":{"color":"#cbd5e1"}},
            decreasing = {"marker":{"color":COLORS['warning']}},
            increasing = {"marker":{"color":COLORS['success']}},
            totals = {"marker":{"color":COLORS['primary']}}
        ))
        
        fig.update_layout(
            title="За счет чего вырастет доход?", 
            height=450,
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='#e2e8f0')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Текстовый вывод
        if real_growth_pct > 0:
            st.success(f"💡 **Вывод:** При заданных параметрах, официальный доход вырастет на **{int(new_income - base_income):,} руб.** Основной драйвер роста: **{'Легализация тени' if legalized_sum > (new_income-organic_growth) else 'Структурные изменения'}**.")

# --- НОВЫЙ ДЕТЕКТОР (С ПОЯСНЕНИЯМИ) ---
elif page == "🕵️ Детектор скрытого (NEW)":
    st.markdown("## 🕵️ Микро-детектор скрытых доходов")
    
    st.markdown("""
    <div class="finding-box" style="margin-top:0;">
        <div class="finding-title">🔬 Методология: Обратная задача Энгеля</div>
        <div style="color: #475569; margin-top: 0.5rem;">
        Закон Эрнста Энгеля гласит: <i>«Чем беднее семья, тем выше доля расходов на питание»</i>. 
        Зная реальные траты на еду и заявленную долю в бюджете, мы можем восстановить <b>реальный доход</b> 
        и сравнить его с официальной зарплатой.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Шаг 1. Введите данные")
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        
        wage = st.number_input("1. Официальная зарплата (на руки)", value=25000, step=1000, help="То, что указано в справке 2-НДФЛ")
        food = st.number_input("2. Реальные траты на еду в месяц", value=18000, step=500, help="Мясо, овощи, хлеб, кафе")
        
        st.markdown("---")
        st.caption("Социологические параметры:")
        share = st.slider("3. Доля еды в бюджете семьи (%)", 10, 80, 45, help="Для бедных семей это 50-60%, для богатых <20%")
        savings = st.slider("4. Сколько удается откладывать (%)", 0, 50, 5)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 🧮 Шаг 2. Расчет модели")
        
        # Расчет
        real_spend_total = food / (share / 100)
        real_income_estimated = real_spend_total / ((100 - savings) / 100)
        gap = real_income_estimated - wage
        gap_percent = (gap / wage) * 100 if wage > 0 else 0
        
        # Визуализация логики (Explanation)
        st.markdown(f"""
        <div style="background: white; padding: 1.5rem; border-radius: 0.8rem; border: 1px solid #e2e8f0;">
            <p><b>Логика восстановления:</b></p>
            <ol>
                <li>Если на еду уходит <b>{format_number_ru(food)} руб.</b>...</li>
                <li>...и это <b>{share}%</b> бюджета, то полные расходы = <b>{format_number_ru(real_spend_total)} руб.</b></li>
                <li>С учетом сбережений ({savings}%), реальный доход = <b>{format_number_ru(real_income_estimated)} руб.</b></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🏁 Вердикт")
        
        if gap > 5000:
            st.markdown(f"""
            <div class="key-finding" style="padding: 1.5rem; margin: 1rem 0; background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);">
                <div style="font-size: 1.2rem;">⚠️ СКРЫТЫЙ ДОХОД</div>
                <div class="key-finding-number" style="font-size: 2.5rem;">{format_number_ru(gap)} руб.</div>
                <div style="opacity: 0.9">Это +{int(gap_percent)}% к официальной зарплате</div>
            </div>
            """, unsafe_allow_html=True)
        elif gap < -5000:
             st.warning(f"⚠️ **Странная аномалия:** Расчетный доход ниже официального. Возможно, доля расходов на еду указана неверно.")
        else:
            st.markdown("""
            <div class="finding-box" style="border-left: 5px solid #10b981; background: #ecfdf5;">
                <div class="finding-title" style="color: #047857;">✅ Все чисто</div>
                <div>Официальные доходы соответствуют уровню потребления.</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Бар-чарт
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Официально', x=['Доход'], y=[wage], 
            marker_color=COLORS['russia'], text=format_number_ru(wage), textposition='auto'
        ))
        fig.add_trace(go.Bar(
            name='Скрыто (Модель)', x=['Доход'], y=[gap if gap > 0 else 0], 
            marker_color=COLORS['dagestan'], text=format_number_ru(gap) if gap > 0 else "", textposition='auto'
        ))
        
        fig.update_layout(barmode='stack', title="Структура реального дохода", height=300, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

# --- КАРТА (КАК БЫЛО В 2.1) ---
elif page == "🗺️ Карта регионов":
    st.markdown("## 🗺️ Интерактивная карта России")
    col1, col2 = st.columns(2)
    with col1:
        year = st.selectbox("📅 Год:", sorted(data['stats']['year'].unique(), reverse=True), index=0)
    with col2:
        metric = st.selectbox("📊 Показатель:", list(VAR_NAMES.keys()), format_func=lambda x: VAR_NAMES.get(x, x))
    
    df_year = data['stats'][data['stats']['year'] == year].copy()
    
    # Координаты (Hardcoded from v2.1)
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
    st.plotly_chart(fig, use_container_width=True)

# --- СРАВНЕНИЕ (КАК БЫЛО В 2.1) ---
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
    st.plotly_chart(fig, use_container_width=True)

# --- ДИНАМИКА (КАК БЫЛО В 2.1) ---
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
    st.plotly_chart(fig, use_container_width=True)

# --- КЛАСТЕРЫ (ОБНОВЛЕННЫЕ) ---
elif page == "🎯 Кластеры":
    st.markdown("## 🎯 Кластерный анализ")
    
    # ТАБЫ: Старый обзор + Новый анализ
    tab1, tab2 = st.tabs(["📊 Общее распределение", "🧩 Глубокий анализ (Heatmap)"])
    
    with tab1:
        # Старый код v2.1
        cluster_summary = data['clusters'].groupby('cluster')['count'].sum().reset_index()
        cluster_summary['cluster_name'] = cluster_summary['cluster'].map(CLUSTER_NAMES)
        
        fig = px.pie(
            cluster_summary, values='count', names='cluster_name', hole=0.4,
            color='cluster', color_discrete_sequence=CLUSTER_COLORS,
            title='Распределение по кластерам'
        )
        st.plotly_chart(fig, use_container_width=True)
        
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
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # Новый Heatmap (Интерактивный)
        st.markdown("### 🌡️ Тепловая карта характеристик")
        st.caption("Показывает, чем каждый кластер отличается от среднего (Z-Score)")
        
        df_prof = data['profiles'].copy()
        if 'cluster' in df_prof.columns:
            df_prof = df_prof.set_index('cluster')
            
        # Фильтруем только числовые и известные нам колонки
        cols = [c for c in df_prof.columns if c in VAR_NAMES]
        heatmap_data = df_prof[cols].rename(columns=VAR_NAMES)
        
        # Нормализация
        heatmap_norm = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()
        
        fig_hm = px.imshow(
            heatmap_norm.T,
            labels=dict(x="Кластер", y="Показатель", color="Отклонение"),
            x=[CLUSTER_NAMES.get(i, str(i)) for i in heatmap_data.index],
            y=heatmap_data.columns,
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        st.plotly_chart(fig_hm, use_container_width=True)
        
        st.info("💡 **Инсайт:** K4 (Сельские) ярко выделяется синим цветом в доходах (ниже среднего), но красным в размере семьи (выше среднего).")

# --- ДАННЫЕ (КАК БЫЛО В 2.1) ---
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
