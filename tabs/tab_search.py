import streamlit as st
from datetime import datetime, date
import requests

def render(app_module):
    """Render the Food Search tab with autocomplete"""
    
    st.header("🔍 Search Foods")
    st.markdown("Search for foods by name and get instant nutrition information")
    
    # Search input
    search_query = st.text_input(
        "Search for a food",
        placeholder="Type a food name (e.g., apple, chicken breast, pizza)...",
        help="Start typing and suggestions will appear"
    )
    
    if search_query and len(search_query) >= 2:
        # Show loading state
        with st.spinner("Searching..."):
            # Search USDA database
            results = search_usda_foods(search_query, app_module.USDA_API_KEY)
            
            if results:
                st.success(f"Found {len(results)} results")
                
                # Display results as expandable cards
                for idx, food in enumerate(results):
                    with st.expander(f"🍴 {food['name']}", expanded=(idx == 0)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Brand:** {food.get('brand', 'Generic')}")
                            st.markdown(f"**Data Source:** {food.get('dataType', 'USDA')}")
                        
                        with col2:
                            if st.button("Select This", key=f"select_{idx}"):
                                st.session_state['selected_food'] = food
                                st.rerun()
                        
                        # Nutrition info (per 100g)
                        if food.get('nutrition'):
                            st.markdown("### Nutrition Facts (per 100g)")
                            
                            nutrients = food['nutrition']
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Calories", f"{nutrients.get('calories', 0):.0f}")
                            with col2:
                                st.metric("Protein", f"{nutrients.get('protein', 0):.1f}g")
                            with col3:
                                st.metric("Carbs", f"{nutrients.get('carbs', 0):.1f}g")
                            with col4:
                                st.metric("Fat", f"{nutrients.get('fat', 0):.1f}g")
            else:
                st.info("No results found. Try a different search term.")
    
    # If a food is selected, show portion input and save option
    if 'selected_food' in st.session_state and st.session_state['selected_food']:
        st.divider()
        selected = st.session_state['selected_food']
        
        st.success(f"✅ Selected: **{selected['name']}**")
        
        # Portion input
        col1, col2 = st.columns(2)
        
        with col1:
            # Detect category for smart defaults
            category = app_module.detect_food_category(selected['name'])
            unit, grams_per_unit, label = app_module.get_serving_conversion(category)
            
            if unit == "pieces":
                default_amount = 1
                max_amount = 10
                step = 1
            elif unit == "ml":
                default_amount = 250
                max_amount = 2000
                step = 50
            elif unit == "cups":
                default_amount = 1.0
                max_amount = 5.0
                step = 0.5
            else:
                default_amount = 100
                max_amount = 500
                step = 25
            
            portion_amount = st.number_input(
                f"How many {label}?",
                min_value=float(step),
                max_value=float(max_amount),
                value=float(default_amount),
                step=float(step)
            )
        
        with col2:
            meal_type = st.selectbox(
                "Meal Type",
                ["Breakfast", "Lunch", "Dinner", "Snack"],
                index=0
            )
        
        # Calculate multiplier
        if unit == "pieces":
            multiplier = portion_amount * grams_per_unit / 100
        elif unit == "ml":
            multiplier = portion_amount / 100
        elif unit == "cups":
            multiplier = portion_amount * grams_per_unit / 100
        else:
            multiplier = portion_amount / 100
        
        # Calculate adjusted nutrition
        nutrition = selected['nutrition']
        adjusted = {
            'calories': nutrition.get('calories', 0) * multiplier,
            'protein': nutrition.get('protein', 0) * multiplier,
            'carbs': nutrition.get('carbs', 0) * multiplier,
            'fat': nutrition.get('fat', 0) * multiplier
        }
        
        # Show adjusted nutrition
        st.markdown(f"### Your Portion ({portion_amount} {label})")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Calories", f"{adjusted['calories']:.0f}", delta=None)
        with col2:
            st.metric("Protein", f"{adjusted['protein']:.1f}g")
        with col3:
            st.metric("Carbs", f"{adjusted['carbs']:.1f}g")
        with col4:
            st.metric("Fat", f"{adjusted['fat']:.1f}g")
        
        # Save button
        if st.button("💾 Save to Diary", type="primary", use_container_width=True):
            # Create meal entry
            meal = {
                'id': f"{datetime.now().timestamp()}",
                'date': str(date.today()),
                'time': datetime.now().strftime("%H:%M"),
                'food_name': selected['name'],
                'meal_type': meal_type,
                'portion_size': f"{portion_amount} {label}",
                'multiplier': multiplier,
                'nutrition': adjusted,
                'source': 'USDA Search',
                'has_image': False
            }
            
            # Save to meals
            meals = app_module.load_json(app_module.MEALS_FILE, default={})
            today = str(date.today())
            
            if today not in meals:
                meals[today] = {}
            if meal_type not in meals[today]:
                meals[today][meal_type] = []
            
            meals[today][meal_type].append(meal)
            app_module.save_json(app_module.MEALS_FILE, meals)
            
            st.success(f"✅ Added {selected['name']} to your {meal_type}!")
            
            # Clear selection
            st.session_state['selected_food'] = None
            st.rerun()


def search_usda_foods(query, api_key, max_results=10):
    """Search USDA FoodData Central and return formatted results"""
    
    try:
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "api_key": api_key,
            "query": query,
            "pageSize": max_results,
            "dataType": ["Survey (FNDDS)", "Branded", "Foundation", "SR Legacy"]
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"[USDA Search] Error: {response.status_code}")
            return []
        
        data = response.json()
        foods = data.get('foods', [])
        
        results = []
        for food in foods:
            # Extract nutrition per 100g
            nutrients_dict = {}
            for nutrient in food.get('foodNutrients', []):
                nutrient_id = nutrient.get('nutrientId')
                value = nutrient.get('value', 0)
                
                # Map nutrient IDs to our keys
                if nutrient_id == 1008:  # Energy
                    nutrients_dict['calories'] = value
                elif nutrient_id == 1003:  # Protein
                    nutrients_dict['protein'] = value
                elif nutrient_id == 1005:  # Carbohydrates
                    nutrients_dict['carbs'] = value
                elif nutrient_id == 1004:  # Fat
                    nutrients_dict['fat'] = value
            
            # Only include foods with calorie data
            if nutrients_dict.get('calories', 0) > 0:
                results.append({
                    'name': food.get('description', 'Unknown'),
                    'brand': food.get('brandOwner', food.get('brandName', 'Generic')),
                    'dataType': food.get('dataType', 'USDA'),
                    'fdcId': food.get('fdcId'),
                    'nutrition': nutrients_dict
                })
        
        return results
        
    except Exception as e:
        print(f"[USDA Search] Exception: {e}")
        return []
