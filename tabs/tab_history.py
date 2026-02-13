"""
Tab 4: History
View past meals, delete entries, export data
"""
import streamlit as st
from datetime import date, timedelta
from pathlib import Path
import pandas as pd


def render(app):
    """Render the History tab (Tab 4)
    
    Args:
        app: The main app module with all utility functions
    """
    
    st.markdown("## 📅 Meal History")
    
    # Date picker
    selected_date = st.date_input(
        "Select date",
        value=date.today(),
        max_value=date.today()
    )
    
    date_str = str(selected_date)
    st.markdown(f"### {selected_date.strftime('%A, %B %d, %Y')}")
    
    # Get meals for selected date
    meals_on_date = app.load_meals(date_str)
    
    if meals_on_date:
        # Show daily totals
        daily_totals = app.get_daily_totals(date_str)
        
        st.markdown("**Daily Totals:**")
        tot_col1, tot_col2, tot_col3, tot_col4 = st.columns(4)
        with tot_col1:
            st.metric("Calories", f"{int(daily_totals['calories'])} kcal")
        with tot_col2:
            st.metric("Protein", f"{round(daily_totals['protein'], 1)}g")
        with tot_col3:
            st.metric("Carbs", f"{round(daily_totals['carbs'], 1)}g")
        with tot_col4:
            st.metric("Fat", f"{round(daily_totals['fat'], 1)}g")
        
        st.divider()
        
        # Group meals by type
        breakfast_meals = [m for m in meals_on_date if '🌅' in m.get('meal_type', '')]
        lunch_meals = [m for m in meals_on_date if '🌞' in m.get('meal_type', '')]
        dinner_meals = [m for m in meals_on_date if '🌆' in m.get('meal_type', '')]
        snack_meals = [m for m in meals_on_date if '🍿' in m.get('meal_type', '')]
        
        for meal_type_name, meal_list in [
            ("🌅 Breakfast", breakfast_meals),
            ("🌞 Lunch", lunch_meals),
            ("🌆 Dinner", dinner_meals),
            ("🍿 Snacks", snack_meals)
        ]:
            if meal_list:
                st.markdown(f"### {meal_type_name}")
                for idx, meal in enumerate(meal_list):
                    with st.container():
                        meal_col1, meal_col2 = st.columns([1, 4])
                        
                        with meal_col1:
                            if 'image_path' in meal and Path(meal['image_path']).exists():
                                st.image(meal['image_path'], use_container_width=True)
                        
                        with meal_col2:
                            # Meal name and delete button in same row
                            name_del_col1, name_del_col2 = st.columns([3, 1])
                            with name_del_col1:
                                st.markdown(f"**{meal['food_name']}**")
                            with name_del_col2:
                                # Delete button with meal name - more prominent and clear
                                if st.button(f"🗑️ Delete", key=f"delete_meal_{date_str}_{meal_type_name}_{idx}", type="secondary", use_container_width=True):
                                    # Load all meals
                                    all_meals = app.load_meals()
                                    # Remove this specific meal by index match
                                    if date_str in all_meals:
                                        meals_list = all_meals[date_str]
                                        # Find by id if available, otherwise by index
                                        meal_id = meal.get('id', None)
                                        removed = False
                                        if meal_id:
                                            for i, m in enumerate(meals_list):
                                                if m.get('id') == meal_id:
                                                    meals_list.pop(i)
                                                    removed = True
                                                    break
                                        if not removed:
                                            # Fallback: remove by matching food_name and timestamp
                                            for i, m in enumerate(meals_list):
                                                if m.get('food_name') == meal.get('food_name') and m.get('timestamp') == meal.get('timestamp'):
                                                    meals_list.pop(i)
                                                    removed = True
                                                    break
                                        if not removed and idx < len(meals_list):
                                            meals_list.pop(idx)
                                        # If no meals left for this date, remove the date entry
                                        if len(meals_list) == 0:
                                            del all_meals[date_str]
                                        app.save_json(app.MEALS_FILE, all_meals)
                                        st.success(f"✅ Deleted: {meal['food_name']}")
                                        st.rerun()
                            
                            st.caption(f"Portion: {meal.get('portion_text', 'N/A')}")
                            
                            nutrition = meal['nutrition']
                            multiplier = meal.get('multiplier', 1.0)
                            
                            info_col1, info_col2, info_col3, info_col4 = st.columns(4)
                            with info_col1:
                                st.metric("Cal", f"{int(nutrition['calories'] * multiplier)}")
                            with info_col2:
                                st.metric("Protein", f"{round(nutrition['protein'] * multiplier, 1)}g")
                            with info_col3:
                                st.metric("Carbs", f"{round(nutrition['carbs'] * multiplier, 1)}g")
                            with info_col4:
                                st.metric("Fat", f"{round(nutrition['fat'] * multiplier, 1)}g")
                        
                        st.markdown("")
        
        # Delete entire day button - make it prominent and red
        st.divider()
        st.markdown("#### Delete This Day's Meals")
        del_day_col1, del_day_col2 = st.columns([2, 1])
        with del_day_col1:
            st.caption(f"Remove all {len(meals_on_date)} meal(s) from {selected_date.strftime('%B %d, %Y')}")
        with del_day_col2:
            if st.button(f"🗑️ Delete {len(meals_on_date)} Meal(s)", key=f"delete_day_{date_str}", type="primary", use_container_width=True):
                all_meals = app.load_meals()
                if date_str in all_meals:
                    del all_meals[date_str]
                    app.save_json(app.MEALS_FILE, all_meals)
                    st.success(f"✅ All meals from {selected_date.strftime('%B %d, %Y')} deleted!")
                    st.rerun()
    else:
        st.info("No meals logged on this date.")
    
    st.divider()
    
    # Bulk Data Management
    st.markdown("### 🗂️ Data Management")
    
    with st.expander("⚠️ Bulk Delete Options", expanded=False):
        st.warning("**Warning:** These actions cannot be undone!")
        
        st.markdown("#### Delete Date Range")
        bulk_col1, bulk_col2 = st.columns(2)
        with bulk_col1:
            del_start_date = st.date_input("From date", value=date.today() - timedelta(days=7), key="del_start")
        with bulk_col2:
            del_end_date = st.date_input("To date", value=date.today(), key="del_end")
        
        if st.button("🗑️ Delete Date Range", key="delete_range"):
            all_meals = app.load_meals()
            deleted_count = 0
            current = del_start_date
            while current <= del_end_date:
                date_str_loop = str(current)
                if date_str_loop in all_meals:
                    del all_meals[date_str_loop]
                    deleted_count += 1
                current += timedelta(days=1)
            
            if deleted_count > 0:
                app.save_json(app.MEALS_FILE, all_meals)
                st.success(f"✅ Deleted meals from {deleted_count} day(s)!")
                st.rerun()
            else:
                st.info("No meals found in selected date range.")
        
        st.divider()
        
        st.markdown("#### Clear All Data")
        st.error("⚠️ This will permanently delete ALL your meal history!")
        
        confirm_clear = st.checkbox("I understand this cannot be undone", key="confirm_clear")
        clear_weight = st.checkbox("Also clear weight tracking history", key="clear_weight")
        
        if confirm_clear:
            if st.button("💣 Delete Everything", key="delete_all", type="primary"):
                # Clear all data files
                app.save_json(app.MEALS_FILE, {})
                app.save_json(app.WATER_FILE, {})
                # Optionally clear weight log
                if clear_weight:
                    app.save_json(app.WEIGHT_FILE, [])
                st.success("✅ All data cleared!")
                st.rerun()
    
    st.divider()
    
    # Export options
    st.markdown("### 📥 Export History")
    
    # Date range for export
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        start_date = st.date_input("From", value=date.today() - timedelta(days=7))
    with export_col2:
        end_date = st.date_input("To", value=date.today())
    
    if st.button("📥 Export to CSV", use_container_width=True):
        # Collect all meals in date range
        all_meals = app.load_meals()
        export_data = []
        
        current = start_date
        while current <= end_date:
            date_str_export = str(current)
            if date_str_export in all_meals:
                for meal in all_meals[date_str_export]:
                    nutrition = meal['nutrition']
                    multiplier = meal.get('multiplier', 1.0)
                    
                    export_data.append({
                        'Date': date_str_export,
                        'Meal Type': meal.get('meal_type', 'N/A'),
                        'Food': meal['food_name'],
                        'Portion': meal.get('portion_text', 'N/A'),
                        'Calories': int(nutrition['calories'] * multiplier),
                        'Protein (g)': round(nutrition['protein'] * multiplier, 1),
                        'Carbs (g)': round(nutrition['carbs'] * multiplier, 1),
                        'Fat (g)': round(nutrition['fat'] * multiplier, 1),
                        'Fiber (g)': round(nutrition.get('fiber', 0) * multiplier, 1),
                        'Sugar (g)': round(nutrition.get('sugar', 0) * multiplier, 1)
                    })
            
            current += timedelta(days=1)
        
        if export_data:
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name=f"nutrition_log_{start_date}_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No data in selected date range")
