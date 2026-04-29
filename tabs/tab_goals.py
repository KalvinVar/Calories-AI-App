"""
Tab 3: Goals
Set daily nutrition targets with built-in calorie calculator
"""
import streamlit as st
from datetime import date, timedelta


def render(app):
    """Render the Goals tab (Tab 3)
    
    Args:
        app: The main app module with all utility functions
    """
    
    st.markdown("## 🎯 Set Your Daily Goals")
    st.caption("Customize your daily nutrition targets")
    
    current_goals = app.load_goals()
    
    # Add calorie calculator
    with st.expander("🧮 Calculate Recommended Goals", expanded=False):
        st.markdown("**Use this calculator to estimate your daily calorie and macro needs**")
        
        calc_col1, calc_col2 = st.columns(2)
        
        with calc_col1:
            age = st.number_input("Age (years)", min_value=15, max_value=100, value=30, step=1)
            
            # Weight input with unit selector
            weight_unit = st.radio("Weight unit:", ["kg", "lbs"], horizontal=True, key="weight_unit")
            if weight_unit == "kg":
                weight_input = st.number_input("Current Weight (kg)", min_value=40.0, max_value=200.0, value=70.0, step=0.5)
                weight_kg = weight_input
            else:
                weight_input = st.number_input("Current Weight (lbs)", min_value=88.0, max_value=440.0, value=154.0, step=1.0)
                weight_kg = weight_input * 0.453592
            
            # Height input with unit selector
            height_unit = st.radio("Height unit:", ["cm", "ft/in"], horizontal=True, key="height_unit")
            if height_unit == "cm":
                height_input = st.number_input("Height (cm)", min_value=140.0, max_value=220.0, value=170.0, step=0.1)
                height_cm = height_input
            else:
                col_ft, col_in = st.columns(2)
                with col_ft:
                    feet = st.number_input("Feet", min_value=4, max_value=7, value=5, step=1)
                with col_in:
                    inches = st.number_input("Inches", min_value=0, max_value=11, value=7, step=1)
                height_cm = (feet * 12 + inches) * 2.54
            
            gender = st.selectbox("Gender", ["Male", "Female"])
        
        with calc_col2:
            activity_level = st.selectbox(
                "Activity Level",
                [
                    "Sedentary (little/no exercise)",
                    "Lightly Active (1-3 days/week)",
                    "Moderately Active (3-5 days/week)",
                    "Very Active (6-7 days/week)",
                    "Extremely Active (athlete/physical job)"
                ]
            )
            
            # Show detailed examples based on selection
            activity_examples = {
                "Sedentary (little/no exercise)": "🪑 **Examples:** Desk job, minimal walking, mostly sitting/lying down. <8,000 steps/day.",
                "Lightly Active (1-3 days/week)": "🚶 **Examples:** Office work + occasional gym, light walks, standing job with sitting breaks. 8,000-10,000 steps/day.",
                "Moderately Active (3-5 days/week)": "🏃 **Examples:** Regular exercise 30-60 min, active commute, server/retail work. 10,000-12,000 steps/day.",
                "Very Active (6-7 days/week)": "💪 **Examples:** Daily gym, physically demanding job, athletic training. 12,000-15,000 steps/day.",
                "Extremely Active (athlete/physical job)": "🏋️ **Examples:** Professional athlete, construction/labor work, training 2x/day. 15,000+ steps/day."
            }
            st.caption(activity_examples[activity_level])
            
            goal_type = st.selectbox(
                "Goal",
                ["Maintain Weight", "Lose Weight", "Gain Weight"]
            )
            
            # Target weight input (only show if losing/gaining)
            if goal_type != "Maintain Weight":
                target_weight_label = f"Target Weight ({weight_unit})"
                if weight_unit == "kg":
                    default_target = weight_input - 5 if goal_type == "Lose Weight" else weight_input + 5
                    default_target = max(40.0, min(200.0, default_target))  # Clamp within bounds
                    target_weight_input = st.number_input(
                        target_weight_label, 
                        min_value=40.0, 
                        max_value=200.0, 
                        value=default_target,
                        step=0.5
                    )
                    target_weight_kg = target_weight_input
                else:
                    default_target = weight_input - 11 if goal_type == "Lose Weight" else weight_input + 11
                    default_target = max(88.0, min(440.0, default_target))  # Clamp within bounds
                    target_weight_input = st.number_input(
                        target_weight_label,
                        min_value=88.0,
                        max_value=440.0,
                        value=default_target,
                        step=1.0
                    )
                    target_weight_kg = target_weight_input * 0.453592
                
                # Let user choose their pace
                st.markdown("**How fast do you want to progress?**")
                pace = st.select_slider(
                    "Weekly rate",
                    options=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                    value=0.5,
                    format_func=lambda x: f"{x} kg/week (~{x*2.2:.1f} lbs/week)",
                    help="Choose your preferred rate of progress. Slower is easier to maintain."
                )
                
                # Dynamic feedback based on pace
                if pace <= 0.5:
                    st.info("✅ **Moderate pace** - Most sustainable and easiest to stick with. Great for long-term success with minimal hunger.")
                elif pace <= 0.6:
                    st.info("💪 **Steady pace** - Good balance between speed and sustainability. Manageable for most people.")
                elif pace <= 0.7:
                    st.warning("⚡ **Balanced pace** - Noticeable progress with moderate effort. May feel hungry at times.")
                elif pace <= 0.8:
                    st.warning("🔥 **Ambitious pace** - Requires strong discipline. Expect significant hunger and lower energy levels.")
                elif pace <= 0.9:
                    st.warning("⚠️ **Aggressive pace** - Very challenging to maintain. Risk of muscle loss if protein intake isn't adequate. Consider tracking carefully.")
                else:  # 1.0
                    st.error("🚨 **Maximum safe pace** - Extremely difficult to sustain. High risk of fatigue, muscle loss, and rebound weight gain. Only recommended for short periods with medical supervision.")
        
        if st.button("Calculate", type="primary"):
            # Mifflin-St Jeor Equation for BMR
            if gender == "Male":
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
            else:
                bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

            # Activity multipliers
            activity_multipliers = {
                "Sedentary (little/no exercise)": 1.2,
                "Lightly Active (1-3 days/week)": 1.375,
                "Moderately Active (3-5 days/week)": 1.55,
                "Very Active (6-7 days/week)": 1.725,
                "Extremely Active (athlete/physical job)": 1.9
            }

            tdee = bmr * activity_multipliers[activity_level]

            # Calculate based on goal and target weight
            _already_at_target = False
            if goal_type == "Maintain Weight":
                target_calories = tdee
                timeline_text = ""
            else:
                # Calculate weight difference
                weight_diff_kg = abs(target_weight_kg - weight_kg)

                # Handle already at target weight
                if weight_diff_kg < 0.1:
                    st.info("✅ You're already at your target weight! Consider switching to **Maintain Weight** mode.")
                    _already_at_target = True

            if not _already_at_target:
                # Use user-selected pace (0.5-1.0 kg/week)
                # 1kg fat = ~7700 calories, so daily adjustment = (weekly_rate * 7700) / 7
                weekly_rate = pace
                daily_cal_adjustment = int((weekly_rate * 7700) / 7)

                if goal_type == "Lose Weight":
                    target_calories = tdee - daily_cal_adjustment
                    # Don't go below 1200 cal for women, 1500 for men
                    min_calories = 1500 if gender == "Male" else 1200
                    if target_calories < min_calories:
                        target_calories = min_calories
                        actual_daily_deficit = tdee - min_calories
                        weekly_rate = max(0.01, (actual_daily_deficit * 7) / 7700)
                        st.warning(f"⚠️ Adjusted to safe minimum ({min_calories} cal/day). Actual rate: ~{weekly_rate:.2f} kg/week")
                elif goal_type != "Maintain Weight":  # Gain Weight
                    target_calories = tdee + daily_cal_adjustment

                # Calculate timeline
                if goal_type != "Maintain Weight":
                    weeks_needed = weight_diff_kg / weekly_rate if weekly_rate > 0 else 0
                    estimated_date = date.today() + timedelta(weeks=int(weeks_needed))

                    if weight_unit == "lbs":
                        weight_diff_display = weight_diff_kg * 2.20462
                        rate_display = weekly_rate * 2.20462
                        timeline_text = f"📅 **Timeline:** {int(weeks_needed)} weeks (~{weight_diff_display:.1f} lbs at {rate_display:.1f} lbs/week) → **{estimated_date.strftime('%B %d, %Y')}**"
                    else:
                        timeline_text = f"📅 **Timeline:** {int(weeks_needed)} weeks (~{weight_diff_kg:.1f} kg at {weekly_rate:.1f} kg/week) → **{estimated_date.strftime('%B %d, %Y')}**"

                # Calculate macros (40% carbs, 30% protein, 30% fat)
                protein_grams = int((target_calories * 0.30) / 4)
                carbs_grams = int((target_calories * 0.40) / 4)
                fat_grams = int((target_calories * 0.30) / 9)

                st.success("📊 **Recommended Daily Targets:**")

                rec_col1, rec_col2, rec_col3, rec_col4 = st.columns(4)
                with rec_col1:
                    st.metric("Calories", f"{int(target_calories)} kcal")
                with rec_col2:
                    st.metric("Protein", f"{protein_grams}g")
                with rec_col3:
                    st.metric("Carbs/Sugar", f"{carbs_grams}g")
                with rec_col4:
                    st.metric("Fat", f"{fat_grams}g")

                st.info(f"💡 **Your BMR:** {int(bmr)} kcal/day | **TDEE:** {int(tdee)} kcal/day")

                if timeline_text:
                    st.warning(timeline_text)

                st.caption("📝 **Note:** These are estimates based on scientific formulas. Adjust based on your progress and how you feel. Consult a healthcare professional for personalized advice.")
                st.caption("⚠️ **Safe weight loss/gain:** 0.5-1kg (1-2 lbs) per week is recommended. Faster changes may not be sustainable or healthy.")

                # Store calculated values in session state
                st.session_state['calculated_goals'] = {
                    'calories': int(target_calories),
                    'protein': protein_grams,
                    'carbs': carbs_grams,
                    'fat': fat_grams
                }
        
        # Show apply button if calculations exist (outside the Calculate button block)
        if 'calculated_goals' in st.session_state and st.session_state['calculated_goals']:
            if st.button("✅ Apply These Goals", key="apply_calc", type="primary"):
                new_goals = {
                    'calories': st.session_state['calculated_goals']['calories'],
                    'protein': st.session_state['calculated_goals']['protein'],
                    'carbs': st.session_state['calculated_goals']['carbs'],
                    'fat': st.session_state['calculated_goals']['fat'],
                    'water_glasses': current_goals.get('water_glasses', 8)
                }
                app.save_goals(new_goals)
                st.success("✅ Goals saved! They are now active in your Daily Summary.")
                st.balloons()
                # Clear calculated goals after applying
                st.session_state['calculated_goals'] = None
                st.rerun()
    
    st.divider()
    st.markdown("### Manual Goal Setting")
    st.caption("Or set your own custom targets below")
    
    st.markdown("#### Calorie Goal")
    calories_goal = st.number_input(
        "Daily calorie target (kcal)",
        min_value=1000,
        max_value=5000,
        value=max(1000, min(5000, int(current_goals['calories']))),
        step=50
    )

    st.markdown("### Macronutrient Goals")
    col1, col2, col3 = st.columns(3)

    with col1:
        protein_goal = st.number_input(
            "💪 Protein (g)",
            min_value=30,
            max_value=500,
            value=max(30, min(500, int(current_goals['protein']))),
            step=5
        )

    with col2:
        carbs_goal = st.number_input(
            "🍞 Carbs/Sugar (g)",
            min_value=50,
            max_value=700,
            value=max(50, min(700, int(current_goals['carbs']))),
            step=10
        )

    with col3:
        fat_goal = st.number_input(
            "🥑 Fat (g)",
            min_value=20,
            max_value=300,
            value=max(20, min(300, int(current_goals['fat']))),
            step=5
        )

    st.markdown("### Hydration Goal")
    water_goal = st.number_input(
        "💧 Water glasses per day",
        min_value=4,
        max_value=25,
        value=max(4, min(25, int(current_goals['water_glasses']))),
        step=1
    )
    
    st.markdown("")
    
    if st.button("💾 Save Goals", type="primary", use_container_width=True):
        new_goals = {
            'calories': calories_goal,
            'protein': protein_goal,
            'carbs': carbs_goal,
            'fat': fat_goal,
            'water_glasses': water_goal
        }
        app.save_goals(new_goals)
        st.success("✅ Goals saved successfully!")
        st.balloons()
