"""
Tab 8: Workout Log / History
View past workouts, stats, streaks, and calorie burn history
"""
import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd


def render(app):
    """Render the Workout Log tab"""
    
    st.markdown("## 📓 Workout Log")
    st.caption("View your exercise history, streaks, and burn statistics")
    
    # Load exercise data
    exercises = app.load_json(app.DATA_DIR / "exercises.json", {})
    
    if not exercises:
        st.info("🏋️ No workouts logged yet! Head to the **Exercise Tracker** tab to log your first workout.")
        
        # Show motivational card
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
        ">
            <div style="font-size: 4rem;">🏃‍♂️</div>
            <div style="color: white; font-size: 1.3rem; font-weight: 600; margin-top: 1rem;">
                Start Your Fitness Journey Today!
            </div>
            <div style="color: white; opacity: 0.8; margin-top: 0.5rem;">
                Track exercises, see your progress, build streaks
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # ─── Overview Stats ───
    render_overview_stats(exercises)
    
    st.divider()
    
    # ─── Date Selector ───
    view_mode = st.radio(
        "View",
        ["📅 Today", "📆 This Week", "📊 All Time"],
        horizontal=True,
        key="log_view_mode"
    )
    
    if view_mode == "📅 Today":
        render_day_view(exercises, str(date.today()), app)
    elif view_mode == "📆 This Week":
        render_week_view(exercises, app)
    else:
        render_all_time_view(exercises, app)


def render_overview_stats(exercises):
    """Show overview stats cards"""
    
    today = str(date.today())
    
    # Calculate stats
    total_workouts = sum(len(day_exercises) for day_exercises in exercises.values())
    total_calories = sum(
        ex.get('calories_burned', 0) 
        for day_exercises in exercises.values() 
        for ex in day_exercises
    )
    total_minutes = sum(
        ex.get('duration_minutes', 0) 
        for day_exercises in exercises.values() 
        for ex in day_exercises
    )
    workout_days = len(exercises)
    
    # Today's stats
    today_exercises = exercises.get(today, [])
    today_calories = sum(ex.get('calories_burned', 0) for ex in today_exercises)
    today_minutes = sum(ex.get('duration_minutes', 0) for ex in today_exercises)
    
    # Calculate streak
    streak = calculate_streak(exercises)
    
    # Display stats in cards
    st.markdown("### 📊 Your Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
        ">
            <div style="color: white; font-size: 0.8rem; opacity: 0.9;">TODAY'S BURN</div>
            <div style="color: white; font-size: 2rem; font-weight: bold;">{int(today_calories)}</div>
            <div style="color: white; font-size: 0.75rem; opacity: 0.8;">kcal</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
        ">
            <div style="color: white; font-size: 0.8rem; opacity: 0.9;">🔥 STREAK</div>
            <div style="color: white; font-size: 2rem; font-weight: bold;">{streak}</div>
            <div style="color: white; font-size: 0.75rem; opacity: 0.8;">days</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
        ">
            <div style="color: white; font-size: 0.8rem; opacity: 0.9;">TOTAL BURNED</div>
            <div style="color: white; font-size: 2rem; font-weight: bold;">{int(total_calories)}</div>
            <div style="color: white; font-size: 0.75rem; opacity: 0.8;">kcal all time</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            padding: 1.2rem;
            border-radius: 12px;
            text-align: center;
        ">
            <div style="color: white; font-size: 0.8rem; opacity: 0.9;">WORKOUT DAYS</div>
            <div style="color: white; font-size: 2rem; font-weight: bold;">{workout_days}</div>
            <div style="color: white; font-size: 0.75rem; opacity: 0.8;">{total_workouts} exercises</div>
        </div>
        """, unsafe_allow_html=True)


def calculate_streak(exercises):
    """Calculate current workout streak (consecutive days)"""
    if not exercises:
        return 0
    
    today = date.today()
    streak = 0
    current_date = today
    
    # Check if today has exercises, if not start from yesterday
    if str(current_date) not in exercises:
        current_date = today - timedelta(days=1)
    
    while str(current_date) in exercises:
        streak += 1
        current_date -= timedelta(days=1)
    
    return streak


def render_day_view(exercises, day_str, app):
    """Show exercises for a specific day"""
    
    day_exercises = exercises.get(day_str, [])
    
    if not day_exercises:
        st.info(f"No exercises logged for {day_str}")
        return
    
    st.markdown(f"### 📅 {day_str}")
    
    total_cal = 0
    total_min = 0
    
    for idx, ex in enumerate(day_exercises):
        icon = ex.get('icon', '🏋️')
        name = ex.get('exercise', 'Unknown')
        duration = ex.get('duration_minutes', 0)
        calories = ex.get('calories_burned', 0)
        workout_name = ex.get('workout_name', '')
        notes = ex.get('notes', '')
        time_str = ex.get('time', '')
        
        total_cal += calories
        total_min += duration
        
        col_icon, col_name, col_dur, col_cal, col_del = st.columns([0.5, 3, 1, 1, 0.5])
        
        with col_icon:
            st.markdown(f"<div style='font-size: 1.5rem; text-align: center; padding-top: 0.5rem;'>{icon}</div>", unsafe_allow_html=True)
        with col_name:
            st.markdown(f"**{name}**")
            details = []
            if workout_name:
                details.append(f"🏷️ {workout_name}")
            if time_str:
                details.append(f"🕐 {time_str}")
            if notes:
                details.append(f"📝 {notes}")
            if details:
                st.caption(" · ".join(details))
        with col_dur:
            st.metric("⏱️", f"{duration} min", label_visibility="collapsed")
            st.caption(f"⏱️ {duration} min")
        with col_cal:
            st.caption(f"🔥 {int(calories)} cal")
        with col_del:
            if st.button("🗑️", key=f"del_ex_{day_str}_{idx}"):
                exercises[day_str].pop(idx)
                if not exercises[day_str]:
                    del exercises[day_str]
                app.save_json(app.DATA_DIR / "exercises.json", exercises)
                st.rerun()
    
    st.divider()
    
    # Day totals
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.metric("Total Exercises", len(day_exercises))
    with col_t2:
        st.metric("Total Duration", f"{total_min} min")
    with col_t3:
        st.metric("Total Burned", f"{int(total_cal)} cal")


def render_week_view(exercises, app):
    """Show this week's exercise summary"""
    
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday
    
    st.markdown("### 📆 This Week")
    
    week_total_cal = 0
    week_total_min = 0
    week_exercises = 0
    active_days = 0
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        day_str = str(day)
        day_name = day.strftime("%A")
        day_exercises_list = exercises.get(day_str, [])
        
        is_today = (day == today)
        is_future = (day > today)
        
        if day_exercises_list:
            active_days += 1
            day_cal = sum(ex.get('calories_burned', 0) for ex in day_exercises_list)
            day_min = sum(ex.get('duration_minutes', 0) for ex in day_exercises_list)
            week_total_cal += day_cal
            week_total_min += day_min
            week_exercises += len(day_exercises_list)
            
            with st.expander(f"{'✅' if not is_today else '📍'} **{day_name}** ({day_str}) — {len(day_exercises_list)} exercises, {int(day_cal)} cal", expanded=is_today):
                for ex in day_exercises_list:
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"{ex.get('icon', '🏋️')} {ex.get('exercise', 'Unknown')}")
                    with col2:
                        st.caption(f"⏱️ {ex.get('duration_minutes', 0)} min")
                    with col3:
                        st.caption(f"🔥 {int(ex.get('calories_burned', 0))} cal")
        elif not is_future:
            st.markdown(f"{'📍' if is_today else '⬜'} **{day_name}** ({day_str}) — Rest day")
        else:
            st.markdown(f"⏳ **{day_name}** ({day_str}) — Upcoming")
    
    st.divider()
    
    # Week summary
    st.markdown("### 📊 Week Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Days", f"{active_days}/7")
    with col2:
        st.metric("Exercises", week_exercises)
    with col3:
        st.metric("Total Time", f"{week_total_min} min")
    with col4:
        st.metric("Calories Burned", f"{int(week_total_cal)}")
    
    # Daily average
    if active_days > 0:
        st.caption(f"📈 Average: {int(week_total_cal / active_days)} cal/day · {int(week_total_min / active_days)} min/day")


def render_all_time_view(exercises, app):
    """Show all-time exercise history with charts"""
    
    st.markdown("### 📊 All-Time History")
    
    if not exercises:
        st.info("No exercise history yet")
        return
    
    # Build data for charts
    chart_data = []
    for day_str, day_exercises in sorted(exercises.items()):
        day_cal = sum(ex.get('calories_burned', 0) for ex in day_exercises)
        day_min = sum(ex.get('duration_minutes', 0) for ex in day_exercises)
        day_count = len(day_exercises)
        chart_data.append({
            'Date': day_str,
            'Calories Burned': int(day_cal),
            'Duration (min)': int(day_min),
            'Exercises': day_count
        })
    
    df = pd.DataFrame(chart_data)
    
    if not df.empty:
        # Calories burned over time
        st.markdown("#### 🔥 Calories Burned Over Time")
        st.bar_chart(df.set_index('Date')['Calories Burned'], color="#f5576c")
        
        # Duration over time
        st.markdown("#### ⏱️ Workout Duration Over Time")
        st.bar_chart(df.set_index('Date')['Duration (min)'], color="#667eea")
    
    st.divider()
    
    # ─── Most Frequent Exercises ───
    st.markdown("#### 🏆 Most Frequent Exercises")
    
    all_exercises = []
    for day_exercises in exercises.values():
        for ex in day_exercises:
            all_exercises.append(ex.get('exercise', 'Unknown'))
    
    if all_exercises:
        exercise_counts = {}
        for ex in all_exercises:
            exercise_counts[ex] = exercise_counts.get(ex, 0) + 1
        
        sorted_exercises = sorted(exercise_counts.items(), key=lambda x: x[1], reverse=True)
        
        for rank, (name, count) in enumerate(sorted_exercises[:10], 1):
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
            st.markdown(f"{medal} **{name}** — {count} times")
    
    st.divider()
    
    # ─── Exercise Log (Detailed) ───
    st.markdown("#### 📋 Detailed Log")
    
    # Show most recent first
    for day_str in sorted(exercises.keys(), reverse=True):
        day_exercises = exercises[day_str]
        day_cal = sum(ex.get('calories_burned', 0) for ex in day_exercises)
        
        with st.expander(f"📅 {day_str} — {len(day_exercises)} exercises, {int(day_cal)} cal burned"):
            for idx, ex in enumerate(day_exercises):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"{ex.get('icon', '🏋️')} **{ex.get('exercise', 'Unknown')}**")
                    if ex.get('workout_name'):
                        st.caption(f"🏷️ {ex['workout_name']}")
                    if ex.get('notes'):
                        st.caption(f"📝 {ex['notes']}")
                with col2:
                    st.caption(f"⏱️ {ex.get('duration_minutes', 0)} min")
                with col3:
                    st.caption(f"🔥 {int(ex.get('calories_burned', 0))} cal")
            
            # Delete entire day button
            if st.button(f"🗑️ Delete all exercises for {day_str}", key=f"del_day_{day_str}"):
                del exercises[day_str]
                app.save_json(app.DATA_DIR / "exercises.json", exercises)
                st.rerun()
