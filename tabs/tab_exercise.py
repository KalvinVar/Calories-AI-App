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


# ─── Range of motion database for detailed strength calculations ───
EXERCISE_ROM = {
    "Weight Lifting (light)": 0.45,
    "Weight Lifting (moderate)": 0.50,
    "Weight Lifting (vigorous)": 0.55,
    "Bodyweight Exercises": 0.40,
    "Circuit Training": 0.50,
    "CrossFit": 0.50,
    "Resistance Bands": 0.40,
    "Kettlebell Training": 0.60,
    "Push-ups / Pull-ups": 0.40,
    "Deadlifts / Squats (heavy)": 0.65,
}

DETAILED_MODE_CATEGORIES = ["🏋️ Strength Training"]


def calculate_calories_detailed(weight_kg, load_kg, sets, reps, rom_meters, rest_seconds_between_sets):
    """
    Volume-based calorie estimation for strength training.
    More accurate than MET for weight lifting because it accounts for actual load.
    Returns dict with breakdown of calorie components.
    """
    # 1. Lifting calories (mechanical work / efficiency)
    concentric_work = sets * reps * load_kg * 9.81 * rom_meters
    eccentric_work = concentric_work * 0.5
    total_mechanical = concentric_work + eccentric_work
    lifting_cal = total_mechanical / (0.20 * 4184)

    # 2. Rest & basal calories
    lifting_time_min = (sets * reps * 3) / 60  # ~3 seconds per rep
    rest_time_min = (sets - 1) * rest_seconds_between_sets / 60
    total_workout_min = lifting_time_min + rest_time_min
    rest_cal = 2.5 * weight_kg * (rest_time_min / 60)  # elevated metabolism during rest (~2.5 MET)
    basal_cal = 1.0 * weight_kg * (lifting_time_min / 60)  # basal rate during active lifting

    # 3. EPOC (Excess Post-exercise Oxygen Consumption) ~10% of workout total
    subtotal = lifting_cal + rest_cal + basal_cal
    epoc = subtotal * 0.10
    total = subtotal + epoc

    return {
        'total': total,
        'lifting': lifting_cal,
        'rest': rest_cal,
        'basal': basal_cal,
        'epoc': epoc,
        'total_duration_minutes': total_workout_min,
        'mechanical_work_joules': total_mechanical,
        'total_volume_kg': sets * reps * load_kg
    }


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
    """Single exercise logging interface with optional detailed mode for strength training"""

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

    # ─── Mode detection ───
    is_strength = category in DETAILED_MODE_CATEGORIES
    use_detailed = False
    detailed_result = None
    sets = reps = 0
    load_kg = 0.0
    rest_seconds = 0

    if is_strength:
        use_detailed = st.toggle(
            "📊 **Detailed Mode** — Enter sets, reps & weight for more accurate estimation",
            value=False,
            key="ex_detailed_mode",
            help="Uses volume-based calculation instead of simple MET. More accurate for weight training because it accounts for the actual weight you're lifting."
        )

    if use_detailed and is_strength:
        # ─── Detailed Mode Inputs ───
        col_sets, col_reps = st.columns(2)

        with col_sets:
            sets = st.number_input("Sets", min_value=1, max_value=20, value=3, step=1, key="ex_sets")

        with col_reps:
            reps = st.number_input("Reps per set", min_value=1, max_value=50, value=10, step=1, key="ex_reps")

        # Load weight with unit toggle
        col_load, col_load_unit = st.columns([2, 1])

        with col_load_unit:
            load_unit = st.radio("Load unit", ["kg", "lbs"], horizontal=True, key="ex_load_unit")

        with col_load:
            if load_unit == "lbs":
                load_lbs = st.number_input(
                    "Weight per rep (lbs)",
                    min_value=0.0, max_value=1100.0, value=44.0, step=5.0,
                    key="ex_load_lbs",
                    help="Total weight you're lifting per rep (include the bar if applicable)"
                )
                load_kg = load_lbs / 2.20462
            else:
                load_kg = st.number_input(
                    "Weight per rep (kg)",
                    min_value=0.0, max_value=500.0, value=20.0, step=2.5,
                    key="ex_load_kg",
                    help="Total weight you're lifting per rep (include the bar if applicable)"
                )

        # Rest between sets
        rest_seconds = st.number_input(
            "Rest between sets (seconds)",
            min_value=10, max_value=600, value=90, step=15,
            key="ex_rest",
            help="Average rest time between each set"
        )

        # Quick rest presets
        st.caption("**Quick rest presets:**")
        rest_cols = st.columns(4)
        rest_presets = [("30s", 30), ("60s", 60), ("90s", 90), ("2min", 120)]
        for i, (label, val) in enumerate(rest_presets):
            with rest_cols[i]:
                if st.button(label, use_container_width=True, key=f"rest_{val}"):
                    st.session_state['ex_rest'] = val
                    st.rerun()

        # Calculate detailed
        rom = EXERCISE_ROM.get(exercise_name, 0.50)
        detailed_result = calculate_calories_detailed(user_weight, load_kg, sets, reps, rom, rest_seconds)
        calories_burned = detailed_result['total']
        duration = detailed_result['total_duration_minutes']

        st.divider()

        # ─── Detailed Results Display ───
        st.markdown("### 🔥 Estimated Calorie Burn")

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
                {exercise_data['icon']} CALORIES BURNED (DETAILED)
            </div>
            <div style="color: white; font-size: 4rem; font-weight: bold; margin: 0.5rem 0;">
                {int(calories_burned)}
            </div>
            <div style="color: white; font-size: 0.9rem; opacity: 0.8;">
                kcal — {sets}×{reps} @ {load_kg:.1f}kg ({duration:.0f} min total)
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Detailed metrics
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("🏋️ Lifting", f"{detailed_result['lifting']:.0f} cal")
        with col_b:
            st.metric("😮\u200d💨 Rest Period", f"{detailed_result['rest']:.0f} cal")
        with col_c:
            st.metric("🔥 EPOC (Afterburn)", f"{detailed_result['epoc']:.0f} cal")
        with col_d:
            st.metric("📦 Total Volume", f"{detailed_result['total_volume_kg']:.0f} kg")

        # MET comparison
        met_calories = calculate_calories_burned(exercise_data['met'], user_weight, duration)
        st.caption(f"📊 **MET comparison:** Simple MET estimate for {duration:.0f} min = **{int(met_calories)} cal** vs Detailed = **{int(calories_burned)} cal**")

    else:
        # ─── Simple MET Mode ───
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

        if is_strength:
            st.caption("💡 **Tip:** Enable **Detailed Mode** above for more accurate strength training estimates using your actual sets, reps, and weight.")

    # ─── SHARED: Food Equivalency ───
    with st.expander("🍽️ What does this burn equal in food?"):
        st.markdown(f"""
**{int(calories_burned)} calories** is roughly equivalent to:

- 🍚 **{calories_burned / 130:.1f}** cups of white rice
- 🍞 **{calories_burned / 80:.1f}** slices of bread
- 🍌 **{calories_burned / 105:.1f}** bananas
- 🍕 **{calories_burned / 285:.1f}** slices of pizza
- 🍔 **{calories_burned / 250:.1f}** hamburgers
- 🍫 **{calories_burned / 230:.1f}** chocolate bars
- 🥤 **{calories_burned / 140:.1f}** cans of soda
        """)
        if detailed_result:
            st.markdown(f"""
---
**📦 Total Volume Lifted:** {detailed_result['total_volume_kg']:.0f} kg ({sets} sets × {reps} reps × {load_kg:.1f} kg)

**⚙️ Mechanical Work:** {detailed_result['mechanical_work_joules']:.0f} joules

The detailed calculation accounts for the actual weight moved through the range of motion,
rest period energy expenditure, and post-exercise oxygen consumption (EPOC).
            """)
        else:
            st.markdown(f"""
---
**⚡ MET Value:** {exercise_data['met']}

This means **{exercise_name}** burns **{exercise_data['met']}× more calories** than sitting at rest.
The MET (Metabolic Equivalent of Task) system estimates energy expenditure based on activity intensity
and your body weight. Formula: *Calories = MET × weight(kg) × hours*.
            """)

    # ─── SHARED: Educational Expanders ───
    with st.expander("ℹ️ How are exercise calories estimated?"):
        st.markdown("""#### Two Methods Available

**1. MET Method (Simple Mode)**

The MET (Metabolic Equivalent of Task) method is the standard approach used by most fitness apps and devices:

$$\\text{Calories} = \\text{MET} \\times \\text{Weight (kg)} \\times \\text{Duration (hours)}$$

**Example:** Running at 10 km/h (MET 9.8) for 30 minutes at 75 kg:
$$9.8 \\times 75 \\times 0.5 = 367.5 \\text{ cal}$$

✅ **Works well for:** Continuous cardio activities (running, cycling, swimming)

⚠️ **Less accurate for:** Strength training, interval workouts, activities with rest periods

---

**2. Volume-Based Method (Detailed Mode)**

Uses physics-based calculations with three components:

**a) Mechanical Work (Lifting Calories)**
$$W_{\\text{concentric}} = \\text{sets} \\times \\text{reps} \\times \\text{load (kg)} \\times 9.81 \\times \\text{ROM (m)}$$
$$W_{\\text{eccentric}} = W_{\\text{concentric}} \\times 0.5$$
$$\\text{Lifting cal} = \\frac{W_{\\text{concentric}} + W_{\\text{eccentric}}}{0.20 \\times 4184}$$

The human body is approximately **20% mechanically efficient** — for every calorie of energy used,
only ~20% becomes actual mechanical work. The rest dissipates as heat.

**b) Rest Period Calories**

During rest between sets, your body still burns calories at an elevated rate (~2.5 MET):
$$\\text{Rest cal} = 2.5 \\times \\text{weight (kg)} \\times \\frac{\\text{rest time (min)}}{60}$$

**c) EPOC (Excess Post-exercise Oxygen Consumption)**

After intense exercise, your metabolism stays elevated. We estimate this as ~10% of the workout total:
$$\\text{EPOC} = (\\text{Lifting} + \\text{Rest} + \\text{Basal}) \\times 0.10$$

---

**Worked Example:** 3 sets × 10 reps × 60 kg bench press, 90s rest, 75 kg person

| Component | Calculation | Calories |
|-----------|-------------|----------|
| Concentric work | 3 × 10 × 60 × 9.81 × 0.50 = 8,829 J | — |
| Eccentric work | 8,829 × 0.5 = 4,414 J | — |
| Lifting cal | 13,243 / (0.20 × 4184) | **15.8** |
| Rest cal | 2.5 × 75 × (3.0 / 60) | **9.4** |
| Basal cal | 1.0 × 75 × (1.5 / 60) | **1.9** |
| EPOC (10%) | 27.1 × 0.10 | **2.7** |
| **Total** | | **≈ 30 cal** |

This shows why strength training burns fewer calories *during* the workout than cardio —
but the muscle-building effects increase your resting metabolic rate long-term.
        """)

    with st.expander("⚠️ Accuracy & Error Margins — Read this!"):
        st.markdown("""#### How Accurate Are These Estimates?

| Method | Exercise Type | Error Margin | Reliability |
|--------|--------------|--------------|-------------|
| MET | Cardio (running, cycling) | ±10–15% | ⭐⭐⭐⭐ Good |
| MET | Sports (basketball, tennis) | ±15–20% | ⭐⭐⭐ Fair |
| MET | Strength training | ±30–50% | ⭐⭐ Poor |
| Detailed | Strength training | ±10–20% | ⭐⭐⭐⭐ Good |

---

**Why is MET bad for strength training?**

MET assigns the **same calorie estimate** regardless of how much weight you lift.
A 30-minute session lifting 20 kg dumbbells and a 30-minute session lifting 80 kg barbells
get the **exact same calorie number** — which is clearly wrong.

MET was designed for **continuous, steady-state activities** like walking or running.
Strength training involves short bursts of intense effort followed by rest periods,
which MET doesn't capture well.

---

**Why is the detailed method still an estimate?**

Even the volume-based calculation has uncertainties:

- **Mechanical efficiency** varies between 18–25% depending on the person, exercise, and fatigue level (we use 20%)
- **Range of motion** depends on your body proportions, flexibility, and movement quality
- **EPOC** varies significantly based on training status, intensity, and individual metabolism
- **Rep speed** affects time under tension but isn't captured (we assume 3 seconds per rep)
- **Stabilizer muscles** contribute additional energy expenditure not captured by the primary movement

---

**How does this compare to wearables?**

- **Apple Watch / Fitbit heart rate-based**: ±15–25% for most activities
- **Chest strap HR monitors**: ±10–15%
- **Our MET method**: Similar to wearable estimates for cardio
- **Our detailed method**: More accurate than wearables for strength training (wearables use HR, which doesn't correlate well with lifting effort)

---

**⚖️ Bottom Line:**

Use these estimates for **trends and relative comparisons**, not as exact calorie counts.
If you burned 200 cal on Monday and 300 cal on Wednesday doing the same exercise with more weight,
that relative difference is meaningful — even if the absolute numbers are off by 15%.
        """)

    with st.expander("📊 Understanding MET Values — The Science"):
        st.markdown(f"""#### What Are MET Values?

MET stands for **Metabolic Equivalent of Task**. 1 MET is the energy cost of sitting quietly,
which equals approximately **1 kcal/kg/hour** (or 3.5 ml O₂/kg/min).

| MET Range | Intensity | Examples |
|-----------|-----------|----------|
| 1.0 | Rest | Sitting, sleeping |
| 1.5–2.9 | Light | Standing, slow walking, stretching |
| 3.0–5.9 | Moderate | Brisk walking, yoga, light weights |
| 6.0–8.9 | Vigorous | Running, cycling, swimming laps |
| 9.0–11.9 | Very vigorous | Sprinting, HIIT, jump rope |
| 12.0+ | Maximum | All-out sprints, competitive racing |

---

#### Body Weight Makes a Big Difference

The same exercise burns very different amounts for different body weights:

| Exercise (30 min) | 60 kg person | 80 kg person | 100 kg person |
|-------------------|-------------|-------------|---------------|
| Walking (4 km/h, MET 3.0) | 90 cal | 120 cal | 150 cal |
| Running (10 km/h, MET 9.8) | 294 cal | 392 cal | 490 cal |
| Cycling (20 km/h, MET 8.0) | 240 cal | 320 cal | 400 cal |
| Weight Lifting (moderate, MET 5.0) | 150 cal | 200 cal | 250 cal |

This is why keeping your weight updated is important for accurate estimates.

---

#### Current Exercise: {exercise_name}

- **MET value:** {exercise_data['met']}
- **At your weight ({user_weight:.1f} kg):** {exercise_data['met'] * user_weight:.1f} cal/hour
- **Intensity level:** {"Light" if exercise_data['met'] < 3 else "Moderate" if exercise_data['met'] < 6 else "Vigorous" if exercise_data['met'] < 9 else "Very Vigorous"}

---

*Source: Compendium of Physical Activities (Ainsworth et al., 2011)*
        """)

    with st.expander("💡 Tips for Better Estimates"):
        st.markdown("""#### 8 Tips for More Accurate Calorie Tracking

1. **⚖️ Keep your weight updated** — A 10 kg difference means ~7% error in calorie estimates.
   Update your weight in the Goals tab regularly.

2. **📊 Use Detailed Mode for strength training** — The volume-based calculation accounts for
   the actual weight you're lifting, giving much more accurate results than simple MET.

3. **🎯 Pick the right intensity level** — "Weight Lifting (light)" vs "(vigorous)" makes a
   significant difference. Be honest about your effort level.

4. **🍽️ Don't eat back all exercise calories** — Exercise calorie estimates tend to be slightly
   high. A safe approach is to **eat back only 50–75%** of estimated exercise calories if you're
   trying to lose weight.

5. **📈 Track consistently for trends** — Even if individual estimates are off by 15%, tracking
   consistently over weeks reveals meaningful patterns in your activity levels.

6. **🏋️ Include the bar weight** — A standard Olympic barbell weighs 20 kg (45 lbs). Don't forget
   to include it when entering your load in Detailed Mode. For example, "135 lbs" on the bar
   means total load = 135 lbs, not just the plates.

7. **⏱️ Be accurate with rest periods** — In Detailed Mode, rest time significantly affects the
   total calorie estimate. Time your rests for a few sets to get a good average.

8. **🔢 Round numbers are fine** — Don't stress about exact seconds or grams. Entering "90 seconds
   rest" when it's actually 80–100 seconds makes minimal difference to the final estimate.

---

**Remember:** The goal is **awareness and consistency**, not laboratory precision.
Knowing that your workout burned roughly 200–250 calories is far more valuable than not tracking at all.
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
                'duration_minutes': round(duration, 1) if detailed_result else duration,
                'met': exercise_data['met'],
                'weight_kg': user_weight,
                'calories_burned': round(calories_burned, 1),
                'notes': notes,
                'estimation_mode': 'detailed' if detailed_result else 'met'
            }

            if detailed_result is not None:
                exercise_entry.update({
                    'sets': sets,
                    'reps': reps,
                    'load_kg': round(load_kg, 2),
                    'rest_seconds': rest_seconds,
                    'total_volume_kg': round(detailed_result['total_volume_kg'], 1),
                    'calories_breakdown': {
                        'lifting': round(detailed_result['lifting'], 1),
                        'rest': round(detailed_result['rest'], 1),
                        'epoc': round(detailed_result['epoc'], 1)
                    }
                })

            # Load and save
            exercises = app.load_json(app.DATA_DIR / "exercises.json", {})
            today = str(date.today())
            if today not in exercises:
                exercises[today] = []
            exercises[today].append(exercise_entry)
            app.save_json(app.DATA_DIR / "exercises.json", exercises)

            mode_label = " (Detailed)" if detailed_result else ""
            st.success(f"✅ Logged{mode_label}: {exercise_data['icon']} {exercise_name} — {int(calories_burned)} cal burned!")
            st.balloons()


def render_workout_planner(app, user_weight):
    """Multi-exercise workout planner"""
    
    st.markdown("### 📋 Workout Planner")
    st.caption("Build a workout with multiple exercises and see total burn")
    st.caption("💡 For detailed calorie tracking with sets/reps/weight for strength exercises, use **'Log an Exercise'** mode")

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
