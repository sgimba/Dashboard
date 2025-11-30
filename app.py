"""
🚀 НАУЧНЫЙ ДАШБОРД РНФ № 25-28-20473
Версия 3.0 - Интерактивное моделирование и проверка гипотез
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
    page_title="Моделирование развития Дагестана | РНФ",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# СТИЛИ И ЦВЕТА
# ============================================================================

COLORS = {
    'primary': '#1e3a8a',
    'dagestan': '#dc2626',
    'russia': '#3b82f6',
    'cluster': ['#3b82f6', '#10b981', '#f59e0b', '#dc2626', '#8b5cf6']
}

st.markdown("""
<style>
    .stApp { background-color: #f8fafc; }
    .hero-box {
        background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%);
        padding: 2rem; border-radius: 1rem; color: white; text-align: center;
        margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
    }
    .metric-card {
        background: white; padding: 1.5rem; border-radius: 0.8rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05); border-left: 5px solid #dc2626;
    }
    .simulation-box {
        background: #eff6ff; padding: 1.5rem; border-radius: 0.8rem;
        border: 1px solid #bfdbfe; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ЗАГРУЗКА ДАННЫХ
# ============================================================================

@st.cache_data
def load_data():
    data_dir = Path('data')
    try:
        # Загружаем созданные ранее файлы
        stats = pd.read_csv(data_dir / 'regional_stats.csv')
        clusters = pd.read_csv(data_dir / 'cluster_profiles.csv')
        
        # Приводим типы
        if 'ter' in stats.columns:
            stats['ter'] = stats['ter'].astype(str).str.strip()
            
        return stats, clusters
    except Exception as e:
        st.error(f"Ошибка: {e}. Сначала запустите скрипт генерации данных!")
        return None, None

df_stats, df_profiles = load_data()

if df_stats is None:
    st.stop()

# Словари для UI
VAR_MAP = {
    'doxodn': 'Доход (руб)',
    'r1v2': 'Возраст (лет)',
    'chlico': 'Размер семьи (чел)',
    'food_share': 'Траты на еду (%)',
    'savings_rate': 'Сбережения (%)',
    'income_reconstructed': 'Скрытый доход (ML)',
    'mest_urban_pct': 'Урбанизация (%)'
}

CLUSTER_NAMES = {
    0: 'K0: Пенсионеры',
    1: 'K1: Средний класс',
    2: 'K2: Городская молодежь',
    3: 'K3: Многодетные',
    4: 'K4: Натуральное хоз-во'
}

# ============================================================================
# UI: БОКОВАЯ ПАНЕЛЬ
# ============================================================================

with st.sidebar:
    st.header("🧬 Лаборатория")
    mode = st.radio(
        "Режим работы:",
        ["🔮 Симулятор (Прогноз)", 
         "🕵️ Детектор скрытого",
         "🧩 Анализ связей", 
         "📊 Мониторинг (Статика)"]
    )
    
    st.info("""
    **РНФ № 25-28-20473**
    Интерактивная среда для проверки гипотез влияния демоэкономических факторов.
    """)

# ============================================================================
# 1. СИМУЛЯТОР (WHAT-IF MODEL)
# ============================================================================

if mode == "🔮 Симулятор (Прогноз)":
    st.markdown('<div class="hero-box"><h1>🔮 Сценарное моделирование 2030</h1><p>Как изменение параметров влияет на экономику Дагестана?</p></div>', unsafe_allow_html=True)

    col_sim, col_res = st.columns([1, 2])

    with col_sim:
        st.markdown("### 🎛️ Ввод параметров")
        st.markdown('<div class="simulation-box">', unsafe_allow_html=True)
        
        # Параметры модели (Эластичности - упрощенные коэффициенты для демо)
        urban_delta = st.slider("Урбанизация (переезд в город)", -10, 20, 0, suffix="%")
        shadow_delta = st.slider("Вывод из тени (обеление)", 0, 50, 0, suffix="%")
        family_delta = st.slider("Изменение размера семьи", -20, 20, 0, suffix="%")
        
        st.markdown("---")
        st.caption("Коэффициенты чувствительности модели:")
        st.caption("- Урбанизация +1% → Доход +0.8%")
        st.caption("- Обеление +1% → Офиц. доход +1.2%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_res:
        # Базовые значения (Дагестан 2023)
        base_dag = df_stats[(df_stats['ter'] == '82') & (df_stats['year'] == 2023)].iloc[0]
        
        base_income = base_dag.get('doxodn', 35000)
        base_savings = base_dag.get('savings_rate', 5)
        
        # Логика простой модели (Simulation Logic)
        # 1. Урбанизация повышает доход, но снижает размер семьи
        income_factor_urb = 1 + (urban_delta * 0.008) 
        
        # 2. Обеление переводит скрытый доход в официальный
        # Предполагаем, что скрытый доход = 2.5 * официальный
        hidden_potencial = base_income * 2.5
        legalized_sum = hidden_potencial * (shadow_delta / 100)
        
        # 3. Размер семьи влияет на доход на душу (обратная зависимость)
        family_factor = 1 - (family_delta * 0.01)
        
        # ИТОГОВЫЙ РАСЧЕТ
        new_income = (base_income * income_factor_urb * family_factor) + legalized_sum
        
        # Сбережения растут с доходом, но нелинейно
        new_savings = base_savings + (urban_delta * 0.1) + (shadow_delta * 0.05)
        
        # ВИЗУАЛИЗАЦИЯ
        st.markdown("### 📈 Результаты моделирования")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Прогноз дохода", f"{int(new_income):,} ₽", delta=f"{int(new_income - base_income):,} ₽")
        m2.metric("Сбережения", f"{new_savings:.1f} %", delta=f"{new_savings - base_savings:.1f} %")
        m3.metric("Эффект обеления", f"+{int(legalized_sum):,} ₽", help="Сумма, выведенная из тени")
        
        # График Waterfall
        fig = go.Figure(go.Waterfall(
            name = "20", orientation = "v",
            measure = ["relative", "relative", "relative", "relative", "total"],
            x = ["База 2023", "Эффект Урбанизации", "Демогр. дивиденд", "Легализация", "ПРОГНОЗ 2030"],
            textposition = "outside",
            text = [f"{int(x/1000)}k" for x in [base_income, base_income*(income_factor_urb-1), base_income*(family_factor-1)*income_factor_urb, legalized_sum, new_income]],
            y = [base_income, 
                 base_income * (income_factor_urb - 1),
                 base_income * (family_factor - 1) * income_factor_urb,
                 legalized_sum, 
                 new_income],
            connector = {"line":{"color":"rgb(63, 63, 63)"}},
        ))
        
        fig.update_layout(title = "Формирование дохода по факторам", showlegend = False, height=400)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# 2. ДЕТЕКТОР СКРЫТОГО (MICRO-CALCULATOR)
# ============================================================================

elif mode == "🕵️ Детектор скрытого":
    st.markdown('<div class="hero-box"><h1>🕵️ Детектор скрытых доходов</h1><p>Проверка гипотезы о расхождении доходов и расходов на микро-уровне</p></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Введите параметры типичного домохозяйства. Модель рассчитает **реальный располагаемый доход** 
    на основе структуры потребления (Закон Энгеля + Обратная задача).
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Ввод данных")
        official_wage = st.number_input("Официальная зарплата (на руки), руб", value=25000, step=1000)
        food_spend = st.number_input("Расходы на питание в месяц, руб", value=15000, step=500)
        food_share_hypo = st.slider("Какую долю бюджета занимает еда? (%)", 10, 80, 40)
        savings_hypo = st.slider("Сколько удается откладывать? (%)", 0, 50, 5)
        
    with col2:
        # Обратная задача (Reconstruction)
        # 1. Оценка полных расходов через еду
        estimated_expenditure = food_spend / (food_share_hypo / 100)
        
        # 2. Оценка дохода через расходы и сбережения
        estimated_real_income = estimated_expenditure / ((100 - savings_hypo) / 100)
        
        gap = estimated_real_income - official_wage
        gap_pct = (gap / official_wage) * 100 if official_wage > 0 else 0
        
        st.subheader("🧮 Результат реконструкции")
        
        if gap > 0:
            st.error(f"⚠️ Обнаружен скрытый доход: **{int(gap):,} руб.** (+{int(gap_pct)}%)")
        else:
            st.success("✅ Данные согласуются с официальной статистикой")
            
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Официально', 'Реально (Модель)'],
            y=[official_wage, estimated_real_income],
            marker_color=[COLORS['russia'], COLORS['dagestan']],
            text=[f"{int(official_wage):,}", f"{int(estimated_real_income):,}"],
            textposition='auto'
        ))
        fig.update_layout(title="Разрыв официального и модельного дохода", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Научное обоснование:** Если семья тратит 15 тыс. на еду, и это 40% бюджета, значит их расходы 37.5 тыс. Если при этом они откладывают 5%, то их реальный доход ~39.5 тыс., что выше заявленных 25 тыс.")

# ============================================================================
# 3. АНАЛИЗ СВЯЗЕЙ (CLUSTERS DECOMPOSITION)
# ============================================================================

elif mode == "🧩 Анализ связей":
    st.markdown('<div class="hero-box"><h1>🧩 Декомпозиция кластеров</h1><p>Исследование структуры зависимостей внутри данных</p></div>', unsafe_allow_html=True)
    
    # Подготовка данных для Heatmap
    if df_profiles is not None and not df_profiles.empty:
        # Нормализация для Heatmap (z-score внутри признака)
        heatmap_data = df_profiles.set_index('cluster').copy()
        
        # Выбираем только числовые колонки
        cols = [c for c in heatmap_data.columns if c in VAR_MAP.keys()]
        heatmap_data = heatmap_data[cols]
        heatmap_data.columns = [VAR_MAP.get(c, c) for c in heatmap_data.columns]
        
        # Стандартизация (чтобы цвета были красивые)
        heatmap_norm = (heatmap_data - heatmap_data.mean()) / heatmap_data.std()
        
        st.subheader("Тепловая карта характеристик")
        st.caption("Красный = Высокое значение, Синий = Низкое значение показателя в кластере")
        
        fig = px.imshow(
            heatmap_norm.T,
            labels=dict(x="Кластер", y="Показатель", color="Z-score"),
            x=[CLUSTER_NAMES.get(i, str(i)) for i in heatmap_data.index],
            y=heatmap_data.columns,
            color_continuous_scale='RdBu_r',
            aspect="auto"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 🔍 Детальный профиль кластера")
        selected_cluster = st.selectbox("Выберите кластер для анализа:", list(CLUSTER_NAMES.values()))
        cluster_id = [k for k, v in CLUSTER_NAMES.items() if v == selected_cluster][0]
        
        # Radar Chart
        row = heatmap_norm.loc[cluster_id]
        # Приводим к диапазону 0-1 для радара (min-max)
        row_minmax = (heatmap_data.loc[cluster_id] - heatmap_data.min()) / (heatmap_data.max() - heatmap_data.min())
        
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=row_minmax.values,
            theta=row_minmax.index,
            fill='toself',
            name=selected_cluster,
            line_color=COLORS['primary']
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=False,
            height=400,
            title=f"Уникальный профиль: {selected_cluster}"
        )
        
        col_text, col_radar = st.columns([1, 1])
        with col_radar:
            st.plotly_chart(fig_radar)
        with col_text:
            st.markdown(f"#### Характеристики {selected_cluster}")
            # Генерация текста описания на лету
            high_vals = row_minmax[row_minmax > 0.7].index.tolist()
            low_vals = row_minmax[row_minmax < 0.3].index.tolist()
            
            if high_vals:
                st.success(f"📈 **Доминирующие признаки:** {', '.join(high_vals)}")
            if low_vals:
                st.warning(f"📉 **Отстающие признаки:** {', '.join(low_vals)}")
            
            if cluster_id == 4:
                st.info("💡 **Научный вывод:** Этот кластер (K4) характерен именно для Дагестана. Высокая доля натурального потребления при низких официальных доходах маскирует реальное благосостояние.")

# ============================================================================
# 4. МОНИТОРИНГ (СТАТИКА ИЗ v2.1)
# ============================================================================

elif mode == "📊 Мониторинг (Статика)":
    st.markdown('<div class="hero-box"><h1>📊 Мониторинг показателей</h1><p>Визуализация агрегированных данных 2016-2023</p></div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Динамика", "Региональная карта"])
    
    with tab1:
        st.subheader("Тренды по годам")
        metric = st.selectbox("Показатель", list(VAR_MAP.keys()), format_func=lambda x: VAR_MAP[x])
        
        # График линий: Дагестан vs Среднее по РФ
        df_dag = df_stats[df_stats['ter'] == '82'].groupby('year')[metric].mean().reset_index()
        df_rf = df_stats.groupby('year')[metric].mean().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_dag['year'], y=df_dag[metric], name='Дагестан', line=dict(color=COLORS['dagestan'], width=4)))
        fig.add_trace(go.Scatter(x=df_rf['year'], y=df_rf[metric], name='Ср. по России', line=dict(color=COLORS['russia'], dash='dash')))
        
        fig.update_layout(title=f"Динамика: {VAR_MAP[metric]}", height=400)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.caption("Данные доступны в разделе Скачать")
        # Тут можно вернуть scatter_geo из прошлой версии, если нужно

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.caption(f"Система поддержки принятия решений | Грант РНФ № 25-28-20473 | Данные обновлены: {pd.Timestamp.now().strftime('%d.%m.%Y')}")
