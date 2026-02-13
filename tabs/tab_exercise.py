"""
Tab 7: Exercise Tracker / Planner & Calorie Burn Estimator
Track exercises with MET-based calorie burn calculations
"""
import streamlit as st
from datetime import datetime, date


# ─── Exercise database with MET values ───
# MET = Metabolic Equivalent of Task (calories burned per kg per hour)
# Source: Compendium of Physical Activities
EXERCISE_DATABASE = {
    "🏃 Cardio": {
        "Running (slow, 8 km/h)": {"met": 8.3, "icon": "🏃"},
        "Running (moderate, 10 km/h)": {"met": 9.8, "icon": "🏃"},
        "Running (fast, 12 km/h)": {"met": 11.5, "icon": "🏃‍♂️"},
        "Running (sprint, 14+ km/h)": {"met": 13.5, "icon": "🏃‍♂️"},
        "Walking (casual, 4 km/h)": {"met": 3.0, "icon": "🚶"},
        "Walking (brisk, 6 km/h)": {"met": 4.3, "icon": "🚶‍♂️"},
        "Walking (power, 7+ km/h)": {"met": 5.0, "icon": "🚶‍♂️"},
        "Cycling (leisure, 16 km/h)": {"met": 6.8, "icon": "🚴"},
        "Cycling (moderate, 20 km/h)": {"met": 8.0, "icon": "🚴"},
        "Cycling (vigorous, 25+ km/h)": {"met": 10.0, "icon": "🚴‍♂️"},
        "Stationary Bike (light)": {"met": 5.5, "icon": "🚲"},
        "Stationary Bike (moderate)": {"met": 7.0, "icon": "🚲"},
        "Stationary Bike (vigorous)": {"met": 10.5, "icon": "🚲"},
        "Jump Rope (slow)": {"met": 8.8, "icon": "⏫"},
        "Jump Rope (moderate)": {"met": 11.8, "icon": "⏫"},
        "Jump Rope (fast)": {"met": 14.0, "icon": "⏫"},
        "Elliptical Trainer": {"met": 5.0, "icon": "🏋️"},
        "Rowing Machine (moderate)": {"met": 7.0, "icon": "🚣"},
        "Rowing Machine (vigorous)": {"met": 8.5, "icon": "🚣"},
        "Stair Climbing": {"met": 9.0, "icon": "🪜"},
    },
    "🏋️ Strength Training": {
        "Weight Lifting (light)": {"met": 3.5, "icon": "🏋️"},
        "Weight Lifting (moderate)": {"met": 5.0, "icon": "🏋️"},
        "Weight Lifting (vigorous)": {"met": 6.0, "icon": "🏋️‍♂️"},
        "Bodyweight Exercises": {"met": 3.8, "icon": "💪"},
        "Circuit Training": {"met": 8.0, "icon": "🔄"},
        "CrossFit": {"met": 8.0, "icon": "🏋️‍♂️"},
        "Resistance Bands": {"met": 3.5, "icon": "🔗"},
        "Kettlebell Training": {"met": 6.0, "icon": "🏋️"},
        "Push-ups / Pull-ups": {"met": 3.8, "icon": "💪"},
        "Deadlifts / Squats (heavy)": {"met": 6.0, "icon": "🏋️‍♂️"},
    },
    "🏊 Water Sports": {
        "Swimming (leisure)": {"met": 6.0, "icon": "🏊"},
        "Swimming (laps, moderate)": {"met": 7.0, "icon": "🏊"},
        "Swimming (laps, vigorous)": {"met": 9.8, "icon": "🏊‍♂️"},
        "Water Aerobics": {"met": 5.3, "icon": "💧"},
        "Surfing": {"met": 3.0, "icon": "🏄"},
        "Kayaking": {"met": 5.0, "icon": "🛶"},
    },
    "⚽ Sports": {
        "Basketball": {"met": 6.5, "icon": "🏀"},
        "Soccer / Football": {"met": 7.0, "icon": "⚽"},
        "Tennis (singles)": {"met": 7.3, "icon": "🎾"},
        "Tennis (doubles)": {"met": 5.0, "icon": "🎾"},
        "Badminton": {"met": 5.5, "icon": "🏸"},
        "Table Tennis": {"met": 4.0, "icon": "🏓"},
        "Volleyball": {"met": 4.0, "icon": "🏐"},
        "Baseball / Softball": {"met": 5.0, "icon": "⚾"},
        "Golf (walking + carrying)": {"met": 4.3, "icon": "⛳"},
        "Boxing (bag work)": {"met": 5.5, "icon": "🥊"},
        "Boxing (sparring)": {"met": 7.8, "icon": "🥊"},
        "Martial Arts": {"met": 5.3, "icon": "🥋"},
        "Wrestling": {"met": 6.0, "icon": "🤼"},
        "Rock Climbing": {"met": 8.0, "icon": "🧗"},
    },
    "🧘 Flexibility & Mind-Body": {
        "Yoga (hatha)": {"met": 2.5, "icon": "🧘"},
        "Yoga (power/vinyasa)": {"met": 4.0, "icon": "🧘‍♂️"},
        "Pilates": {"met": 3.0, "icon": "🧘‍♀️"},
        "Stretching": {"met": 2.3, "icon": "🤸"},
        "Tai Chi": {"met": 3.0, "icon": "🧘"},
        "Meditation (active)": {"met": 1.5, "icon": "🧘"},
    },
    "🏠 Daily Activities": {
        "Housework (general)": {"met": 3.3, "icon": "🏠"},
        "Gardening": {"met": 3.8, "icon": "🌱"},
        "Mowing Lawn": {"met": 5.5, "icon": "🌿"},
        "Shoveling Snow": {"met": 6.0, "icon": "❄️"},
        "Moving Furniture": {"met": 5.8, "icon": "📦"},
        "Playing with Kids (active)": {"met": 5.0, "icon": "👶"},
        "Dancing (casual)": {"met": 4.5, "icon": "💃"},
        "Dancing (intense)": {"met": 7.0, "icon": "💃"},
    },
    "🏃‍♂️ HIIT & Functional": {
        "HIIT Workout": {"met": 9.0, "icon": "🔥"},
        "Tabata": {"met": 10.0, "icon": "🔥"},
        "Burpees": {"met": 8.0, "icon": "💥"},
        "Mountain Climbers": {"met": 8.0, "icon": "⛰️"},
        "Battle Ropes": {"met": 10.3, "icon": "🪢"},
        "Box Jumps": {"met": 8.0, "icon": "📦"},
        "Plank Hold": {"met": 3.0, "icon": "🧱"},
        "Sprints / Intervals": {"met": 12.0, "icon": "⚡"},
    },
}


def calculate_calories_burned(met, weight_kg, duration_minutes):
    """
    Calculate calories burned using MET formula:
    Calories = MET × weight(kg) × duration(hours)
    """
    duration_hours = duration_minutes / 60
    return met * weight_kg * duration_hours


def render(app):
    """Render the Exercise Tracker tab"""
    
    st.markdown("## 🏃 Exercise Tracker & Calorie Burn Estimator")
    st.caption("Plan workouts, estimate calories burned, and log your exercises")
    
    # ─── User weight for calorie calculation ───
    weight_log = app.load_weight_log()
    if weight_log:
        latest_weight = weight_log[-1]['weight']
    else:
        latest_weight = 70  # default kg
    
    # Weight input at the top
    col_weight, col_info = st.columns([1, 2])
    
    with col_weight:
        # Unit toggle
        weight_unit = st.radio("Unit", ["kg", "lbs"], horizontal=True, key="exercise_weight_unit")
        
        if weight_unit == "lbs":
            default_lbs = round(latest_weight * 2.20462, 1)
            user_weight_input = st.number_input(
                "Your weight (lbs)",
                min_value=66.0,
                max_value=660.0,
                value=float(default_lbs),
                step=1.0,
                key="exercise_weight",
                help="Used for accurate calorie burn estimation"
            )
            user_weight = user_weight_input / 2.20462  # convert to kg for calculations
        else:
            user_weight = st.number_input(
                "Your weight (kg)",
                min_value=30.0,
                max_value=300.0,
                value=float(latest_weight),
                step=0.5,
                key="exercise_weight",
                help="Used for accurate calorie burn estimation"
            )
    with col_info:
        st.info("💡 Calorie burn is estimated using **MET values** (Metabolic Equivalent of Task). More accurate with your current weight.")
    
    st.divider()
    
    # ─── Two modes: Quick Log vs Workout Planner ───
    mode = st.radio(
        "What would you like to do?",
        ["🏋️ Log an Exercise", "📋 Plan a Workout"],
        horizontal=True,
        key="exercise_mode"
    )
    
    if mode == "🏋️ Log an Exercise":
        render_exercise_logger(app, user_weight)
    else:
        render_workout_planner(app, user_weight)


def render_exercise_logger(app, user_weight):
    """Single exercise logging interface"""
    
    st.markdown("### 🏋️ Log an Exercise")
    
    # Category selection
    category = st.selectbox(
        "Exercise Category",
        list(EXERCISE_DATABASE.keys()),
        key="ex_category"
    )
    
    # Exercise selection within category
    exercises_in_category = EXERCISE_DATABASE[category]
    exercise_name = st.selectbox(
        "Exercise",
        list(exercises_in_category.keys()),
        key="ex_name"
    )
    
    exercise_data = exercises_in_category[exercise_name]
    
    # Duration and intensity
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=300,
            value=30,
            step=5,
            key="ex_duration"
        )
    
    with col2:
        # Quick duration presets
        st.caption("**Quick durations:**")
        d_cols = st.columns(4)
        durations = [15, 30, 45, 60]
        for i, d in enumerate(durations):
            with d_cols[i]:
                if st.button(f"{d} min", use_container_width=True, key=f"dur_{d}"):
                    st.session_state['ex_duration'] = d
                    st.rerun()
    
    # Calculate calories burned
    calories_burned = calculate_calories_burned(exercise_data['met'], user_weight, duration)
    
    st.divider()
    
    # ─── Results Display ───
    st.markdown("### 🔥 Estimated Calorie Burn")
    
    # Big calorie display
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    ">
        <div style="color: white; font-size: 1rem; opacity: 0.9; font-weight: 600;">
            {exercise_data['icon']} CALORIES BURNED
        </div>
        <div style="color: white; font-size: 4rem; font-weight: bold; margin: 0.5rem 0;">
            {int(calories_burned)}
        </div>
        <div style="color: white; font-size: 0.9rem; opacity: 0.8;">
            kcal in {duration} minutes
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Details
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("⏱️ Duration", f"{duration} min")
    with col_b:
        st.metric("⚡ MET Value", f"{exercise_data['met']}")
    with col_c:
        cal_per_min = calories_burned / duration if duration > 0 else 0
        st.metric("🔥 Cal/min", f"{cal_per_min:.1f}")
    
    # Comparison context
    with st.expander("ℹ️ What does this burn mean?"):
        st.markdown(f"""
**{int(calories_burned)} calories** is roughly equivalent to:

- 🍚 {calories_burned / 130:.1f} cups of white rice
- 🍞 {calories_burned / 80:.1f} slices of bread
- 🍌 {calories_burned / 105:.1f} bananas
- 🍕 {calories_burned / 285:.1f} slices of pizza
- 🍔 {calories_burned / 250:.1f} hamburgers

**MET {exercise_data['met']}** means this activity burns **{exercise_data['met']}× more calories** than sitting at rest.
        """)
    
    st.divider()
    
    # ─── Save to Log ───
    st.markdown("### 💾 Save Exercise")
    
    col_notes, col_save = st.columns([2, 1])
    
    with col_notes:
        notes = st.text_input("Notes (optional)", placeholder="e.g., felt great, increased weight", key="ex_notes")
    
    with col_save:
        if st.button("💾 Log Exercise", type="primary", use_container_width=True, key="ex_save"):
            exercise_entry = {
                'id': datetime.now().strftime("%Y%m%d_%H%M%S"),
                'date': str(date.today()),
                'time': datetime.now().strftime("%H:%M"),
                'exercise': exercise_name,
                'category': category,
                'icon': exercise_data['icon'],
                'duration_minutes': duration,
                'met': exercise_data['met'],
                'weight_kg': user_weight,
                'calories_burned': round(calories_burned, 1),
                'notes': notes
            }
            
            # Load and save
            exercises = app.load_json(app.DATA_DIR / "exercises.json", {})
            today = str(date.today())
            if today not in exercises:
                exercises[today] = []
            exercises[today].append(exercise_entry)
            app.save_json(app.DATA_DIR / "exercises.json", exercises)
            
            st.success(f"✅ Logged: {exercise_data['icon']} {exercise_name} — {int(calories_burned)} cal burned!")
            st.balloons()


def render_workout_planner(app, user_weight):
    """Multi-exercise workout planner"""
    
    st.markdown("### 📋 Workout Planner")
    st.caption("Build a workout with multiple exercises and see total burn")
    
    # Initialize workout plan in session state
    if 'workout_plan' not in st.session_state:
        st.session_state['workout_plan'] = []
    
    # ─── Add exercises to plan ───
    with st.expander("➕ Add Exercise to Workout", expanded=len(st.session_state['workout_plan']) == 0):
        col1, col2 = st.columns(2)
        
        with col1:
            plan_category = st.selectbox(
                "Category",
                list(EXERCISE_DATABASE.keys()),
                key="plan_category"
            )
        
        with col2:
            exercises_in_cat = EXERCISE_DATABASE[plan_category]
            plan_exercise = st.selectbox(
                "Exercise",
                list(exercises_in_cat.keys()),
                key="plan_exercise"
            )
        
        plan_duration = st.number_input(
            "Duration (minutes)",
            min_value=1,
            max_value=180,
            value=15,
            step=5,
            key="plan_duration"
        )
        
        if st.button("➕ Add to Workout", type="primary", use_container_width=True, key="plan_add"):
            ex_data = exercises_in_cat[plan_exercise]
            cals = calculate_calories_burned(ex_data['met'], user_weight, plan_duration)
            
            st.session_state['workout_plan'].append({
                'exercise': plan_exercise,
                'category': plan_category,
                'icon': ex_data['icon'],
                'duration': plan_duration,
                'met': ex_data['met'],
                'calories': round(cals, 1)
            })
            st.rerun()
    
    # ─── Display workout plan ───
    if st.session_state['workout_plan']:
        st.markdown("---")
        st.markdown("### 📝 Your Workout")
        
        total_duration = 0
        total_calories = 0
        
        for idx, item in enumerate(st.session_state['workout_plan']):
            col_ex, col_dur, col_cal, col_del = st.columns([3, 1, 1, 0.5])
            
            with col_ex:
                st.markdown(f"**{item['icon']} {item['exercise']}**")
            with col_dur:
                st.caption(f"⏱️ {item['duration']} min")
            with col_cal:
                st.caption(f"🔥 {int(item['calories'])} cal")
            with col_del:
                if st.button("❌", key=f"del_plan_{idx}"):
                    st.session_state['workout_plan'].pop(idx)
                    st.rerun()
            
            total_duration += item['duration']
            total_calories += item['calories']
        
        st.divider()
        
        # ─── Workout Summary ───
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        ">
            <div style="color: white; font-size: 1rem; opacity: 0.9; font-weight: 600;">
                WORKOUT SUMMARY
            </div>
            <div style="display: flex; justify-content: center; gap: 3rem; margin-top: 1rem;">
                <div>
                    <div style="color: white; font-size: 2.5rem; font-weight: bold;">{len(st.session_state['workout_plan'])}</div>
                    <div style="color: white; opacity: 0.8;">exercises</div>
                </div>
                <div>
                    <div style="color: white; font-size: 2.5rem; font-weight: bold;">{total_duration}</div>
                    <div style="color: white; opacity: 0.8;">minutes</div>
                </div>
                <div>
                    <div style="color: white; font-size: 2.5rem; font-weight: bold;">{int(total_calories)}</div>
                    <div style="color: white; opacity: 0.8;">cal burned</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ─── Save entire workout ───
        col_name, col_save = st.columns([2, 1])
        
        with col_name:
            workout_name = st.text_input("Workout Name (optional)", 
                                         placeholder="e.g., Morning Cardio, Leg Day",
                                         key="workout_name")
        
        with col_save:
            if st.button("💾 Log Entire Workout", type="primary", use_container_width=True, key="save_workout"):
                # Save each exercise individually
                exercises = app.load_json(app.DATA_DIR / "exercises.json", {})
                today = str(date.today())
                if today not in exercises:
                    exercises[today] = []
                
                workout_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                for item in st.session_state['workout_plan']:
                    exercise_entry = {
                        'id': f"{workout_id}_{item['exercise'][:10]}",
                        'date': today,
                        'time': datetime.now().strftime("%H:%M"),
                        'exercise': item['exercise'],
                        'category': item['category'],
                        'icon': item['icon'],
                        'duration_minutes': item['duration'],
                        'met': item['met'],
                        'weight_kg': user_weight,
                        'calories_burned': item['calories'],
                        'workout_name': workout_name or "Unnamed Workout",
                        'workout_id': workout_id,
                        'notes': ''
                    }
                    exercises[today].append(exercise_entry)
                
                app.save_json(app.DATA_DIR / "exercises.json", exercises)
                
                st.success(f"✅ Workout logged! {len(st.session_state['workout_plan'])} exercises — {int(total_calories)} cal burned!")
                st.balloons()
                st.session_state['workout_plan'] = []
                st.rerun()
        
        # Clear workout button
        if st.button("🗑️ Clear Workout", use_container_width=True, key="clear_workout"):
            st.session_state['workout_plan'] = []
            st.rerun()
    
    else:
        st.info("👆 Add exercises above to start building your workout plan")
