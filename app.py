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
