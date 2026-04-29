"""
Tab 2: Daily Summary
Shows today's nutrition totals, goal progress, water intake, and meal list
"""
import streamlit as st
from datetime import date
from pathlib import Path


def render(app):
    """Render the Daily Summary tab (Tab 2)
    
    Args:
        app: The main app module with all utility functions
    """
    
    st.markdown("## 📊 Today's Nutrition Summary")
    
    today = str(date.today())
    st.markdown(f"**{date.today().strftime('%A, %B %d, %Y')}**")
    
    # Get today's totals
    totals = app.get_daily_totals(today)
    goals = app.load_goals()
    
    # Progress display
    st.markdown("### 🎯 Daily Goals Progress")
    
    # Calories
    cal_progress = min(totals['calories'] / goals['calories'], 1.0) if goals['calories'] > 0 else 0
    st.markdown(f"**Calories:** {int(totals['calories'])} / {goals['calories']} kcal")
    st.progress(cal_progress)
    remaining_cal = goals['calories'] - totals['calories']
    if remaining_cal > 0:
        st.caption(f"✅ {int(remaining_cal)} kcal remaining")
    else:
        st.caption(f"⚠️ {int(-remaining_cal)} kcal over target")
    
    st.markdown("")
    
    # Macros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        protein_progress = min(totals['protein'] / goals['protein'], 1.0) if goals['protein'] > 0 else 0
        st.markdown(f"**💪 Protein**")
        st.metric("", f"{round(totals['protein'], 1)}g")
        st.progress(protein_progress)
        st.caption(f"Goal: {goals['protein']}g")
    
    with col2:
        carbs_progress = min(totals['carbs'] / goals['carbs'], 1.0) if goals['carbs'] > 0 else 0
        st.markdown(f"**🍞 Carbs/Sugar**")
        st.metric("", f"{round(totals['carbs'], 1)}g")
        st.progress(carbs_progress)
        st.caption(f"Goal: {goals['carbs']}g")
    
    with col3:
        fat_progress = min(totals['fat'] / goals['fat'], 1.0) if goals['fat'] > 0 else 0
        st.markdown(f"**🥑 Fat**")
        st.metric("", f"{round(totals['fat'], 1)}g")
        st.progress(fat_progress)
        st.caption(f"Goal: {goals['fat']}g")
    
    st.divider()
    
    # Water intake
    st.markdown("### 💧 Water Intake")
    water_log = app.load_water_log()
    current_water = water_log.get(today, 0)
    current_water = int(max(0, min(25, current_water)))  # Clamp to valid range and ensure int
    
    col1, col2 = st.columns([3, 1])
    with col1:
        water_glasses = st.number_input(
            f"Glasses today ({current_water}/{goals['water_glasses']})",
            min_value=0,
            max_value=25,
            value=current_water,
            step=1,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("💾 Save", key="save_water"):
            app.save_water_intake(water_glasses, today)
            st.success("✅ Saved!")
    
    water_progress = min(water_glasses / goals['water_glasses'], 1.0) if goals['water_glasses'] > 0 else 0
    st.progress(water_progress)
    
    st.divider()
    
    # Today's meals
    st.markdown("### 🍽️ Today's Meals")
    
    meals_today = app.load_meals(today)
    
    if meals_today:
        for meal in meals_today:
            with st.expander(f"{meal['meal_type']} - {meal['food_name']}"):
                meal_col1, meal_col2 = st.columns([1, 2])
                
                with meal_col1:
                    # Display meal image if exists
                    if 'image_path' in meal and Path(meal['image_path']).exists():
                        st.image(meal['image_path'], use_container_width=True)
                
                with meal_col2:
                    nutrition = meal['nutrition']
                    multiplier = meal.get('multiplier', 1.0)
                    
                    st.markdown(f"**Portion:** {meal.get('portion_text', 'N/A')}")
                    st.markdown(f"**Calories:** {int(nutrition['calories'] * multiplier)} kcal")
                    st.markdown(f"**Protein:** {round(nutrition['protein'] * multiplier, 1)}g")
                    st.markdown(f"**Carbs/Sugar:** {round(nutrition['carbs'] * multiplier, 1)}g")
                    st.markdown(f"**Fat:** {round(nutrition['fat'] * multiplier, 1)}g")
    else:
        st.info("No meals logged today. Add a meal from the 'Analyze Food' tab!")
