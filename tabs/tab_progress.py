"""
Tab 5: Progress
Weight tracking and calorie trends
"""
import streamlit as st
from datetime import date, timedelta
import pandas as pd


def render(app):
    """Render the Progress tab (Tab 5)
    
    Args:
        app: The main app module with all utility functions
    """
    
    st.markdown("## 📈 Weight & Progress Tracking")
    
    # Weight logging
    st.markdown("### ⚖️ Log Your Weight")
    
    weight_col1, weight_col2, weight_col3 = st.columns([2, 2, 1])
    
    with weight_col1:
        weight_value = st.number_input(
            "Weight (lbs)",
            min_value=50.0,
            max_value=500.0,
            value=150.0,
            step=0.1
        )
    
    with weight_col2:
        weight_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today(),
            key="weight_date"
        )
    
    with weight_col3:
        if st.button("💾 Log", key="save_weight"):
            app.save_weight_entry(weight_value, str(weight_date))
            st.success("✅ Logged!")
    
    st.divider()
    
    # Weight history chart
    st.markdown("### 📊 Weight History")
    
    weight_log = app.load_weight_log()
    
    if len(weight_log) > 0:
        df_weight = pd.DataFrame(weight_log)
        df_weight['date'] = pd.to_datetime(df_weight['date'])
        df_weight = df_weight.sort_values('date')
        
        st.line_chart(df_weight.set_index('date')['weight'])
        
        # Show recent entries
        st.markdown("**Recent Entries:**")
        recent = df_weight.tail(5).sort_values('date', ascending=False)
        
        for _, row in recent.iterrows():
            st.caption(f"{row['date'].strftime('%Y-%m-%d')}: {row['weight']} lbs")
    else:
        st.info("No weight entries yet. Start logging above!")
    
    st.divider()
    
    # Calorie trends
    st.markdown("### 📊 Calorie Trends (Last 7 Days)")
    
    trend_data = []
    for i in range(6, -1, -1):
        check_date = date.today() - timedelta(days=i)
        date_str = str(check_date)
        totals = app.get_daily_totals(date_str)
        trend_data.append({
            'Date': check_date.strftime('%m/%d'),
            'Calories': int(totals['calories'])
        })
    
    if any(d['Calories'] > 0 for d in trend_data):
        df_trend = pd.DataFrame(trend_data)
        st.bar_chart(df_trend.set_index('Date'))
    else:
        st.info("No calorie data in the last 7 days.")
