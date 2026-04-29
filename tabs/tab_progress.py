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
    
    # Unit toggle
    weight_unit = st.radio("Unit", ["lbs", "kg"], horizontal=True, key="progress_weight_unit")
    
    # Get last logged weight as default
    weight_log = app.load_weight_log()

    if weight_unit == "kg":
        min_val, max_val, step_val = 20.0, 250.0, 0.1
        fallback = 68.0
    else:
        min_val, max_val, step_val = 50.0, 500.0, 0.1
        fallback = 150.0

    if len(weight_log) > 0:
        last_weight = weight_log[-1].get('weight', fallback)
    else:
        last_weight = fallback

    # Clamp to the valid range for the selected unit without guessing conversions.
    # Weight entries don't store a unit, so we show the raw stored value and let
    # the user correct it if they previously logged in the other unit.
    default_weight = max(min_val, min(max_val, float(last_weight)))
    
    weight_col1, weight_col2, weight_col3 = st.columns([2, 2, 1])
    
    with weight_col1:
        weight_value = st.number_input(
            f"Weight ({weight_unit})",
            min_value=min_val,
            max_value=max_val,
            value=default_weight,
            step=step_val
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
    
    if len(weight_log) > 0:
        df_weight = pd.DataFrame(weight_log)
        df_weight['date'] = pd.to_datetime(df_weight['date'])
        df_weight = df_weight.sort_values('date')
        
        st.line_chart(df_weight.set_index('date')['weight'])
        
        # Show recent entries
        st.markdown("**Recent Entries:**")
        recent = df_weight.tail(5).sort_values('date', ascending=False)
        
        for _, row in recent.iterrows():
            st.caption(f"{row['date'].strftime('%Y-%m-%d')}: {row['weight']} {weight_unit}")
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
