"""
Tab 6: Quick Add
Manually add food via USDA search or barcode without photo
"""
import streamlit as st
from datetime import datetime


def render(app):
    """Render the Quick Add tab (Tab 6)
    
    Args:
        app: The main app module with all utility functions
    """
    
    st.markdown("## ⚙️ Quick Add Food")
    st.caption("Manually add food without uploading a photo")
    
    # Search USDA directly
    st.markdown("### 🔍 Search Food Database")
    
    search_term = st.text_input("Search for a food item", placeholder="e.g., chicken breast, apple, rice")
    
    if search_term and len(search_term) > 2:
        with st.spinner("Searching USDA database..."):
            usda_results = app.get_usda_nutrition(search_term)
            
            if usda_results:
                st.success(f"✅ Found: {usda_results.get('usda_match', search_term)}")
                
                # Show nutrition
                st.markdown("**Nutrition per 100g:**")
                quick_col1, quick_col2, quick_col3 = st.columns(3)
                
                with quick_col1:
                    st.metric("Calories", f"{usda_results['calories']} kcal")
                    st.metric("Protein", f"{usda_results['protein']}g")
                
                with quick_col2:
                    st.metric("Carbs/Sugar", f"{usda_results['carbs']}g")
                    st.metric("Fat", f"{usda_results['fat']}g")
                
                with quick_col3:
                    st.metric("Fiber", f"{usda_results['fiber']}g")
                    st.metric("Sugar", f"{usda_results['sugar']}g")
                
                st.divider()
                
                # Portion adjustment
                st.markdown("### 🍽️ Adjust Portion")
                
                portion_multiplier_quick = st.number_input(
                    "Multiplier (1.0 = 100g)",
                    min_value=0.1,
                    max_value=10.0,
                    value=1.0,
                    step=0.1,
                    key="quick_portion"
                )
                
                st.markdown(f"**Total: {int(usda_results['calories'] * portion_multiplier_quick)} calories**")
                
                # Save to log
                st.markdown("### 💾 Add to Log")
                
                quick_meal_col1, quick_meal_col2 = st.columns([2, 1])
                
                with quick_meal_col1:
                    quick_meal_type = st.selectbox(
                        "Meal type",
                        ["🌅 Breakfast", "🌞 Lunch", "🌆 Dinner", "🍿 Snack"],
                        key="quick_meal_type"
                    )
                
                with quick_meal_col2:
                    if st.button("💾 Add", type="primary", use_container_width=True, key="quick_save"):
                        meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                        
                        meal_data = {
                            'id': meal_id,
                            'food_name': usda_results.get('usda_match', search_term),
                            'meal_type': quick_meal_type,
                            'nutrition': usda_results,
                            'multiplier': portion_multiplier_quick,
                            'portion_text': f"{portion_multiplier_quick * 100}g",
                            'confidence': 'High',
                            'source': 'USDA'
                        }
                        
                        app.save_meal(meal_data)
                        st.success(f"✅ Added to your {quick_meal_type} log!")
                        st.balloons()
            else:
                st.warning("No results found. Try a different search term.")
    
    st.divider()
    
    # Barcode scanner
    st.markdown("### 📷 Barcode Scanner")
    st.caption("Upload a photo of a product barcode to get nutrition info")
    
    barcode_file = st.file_uploader(
        "Upload barcode image",
        type=["jpg", "jpeg", "png"],
        key="barcode_upload",
        help="Take a clear photo of the barcode on packaged food"
    )
    
    if barcode_file is not None:
        # Display uploaded image
        barcode_col1, barcode_col2 = st.columns([1, 2])
        
        with barcode_col1:
            st.image(barcode_file, caption="Barcode Image", use_container_width=True)
        
        with barcode_col2:
            with st.spinner("Scanning barcode..."):
                barcode_data, barcode_type = app.scan_barcode_from_image(barcode_file)
                
                if barcode_data:
                    st.success(f"✅ Barcode detected: {barcode_data}")
                    st.caption(f"Type: {barcode_type}")
                    
                    # Get product info
                    with st.spinner("Looking up product..."):
                        product_info = app.get_product_from_barcode(barcode_data)
                        
                        if product_info:
                            st.markdown(f"### {product_info['product_name']}")
                            st.caption(f"Brand: {product_info['brands']}")
                            
                            if product_info.get('image_url'):
                                st.image(product_info['image_url'], width=200)
                            
                            st.divider()
                            
                            # Show nutrition
                            st.markdown("**Nutrition per 100g:**")
                            bc_col1, bc_col2, bc_col3 = st.columns(3)
                            
                            with bc_col1:
                                st.metric("Calories", f"{product_info['calories']} kcal")
                                st.metric("Protein", f"{product_info['protein']}g")
                            
                            with bc_col2:
                                st.metric("Carbs/Sugar", f"{product_info['carbs']}g")
                                st.metric("Fat", f"{product_info['fat']}g")
                            
                            with bc_col3:
                                st.metric("Fiber", f"{product_info['fiber']}g")
                                st.metric("Sugar", f"{product_info['sugar']}g")
                            
                            st.divider()
                            
                            # Portion and save
                            st.markdown("### 🍽️ Add to Log")
                            
                            bc_portion_multiplier = st.number_input(
                                "Serving size multiplier (1.0 = 100g)",
                                min_value=0.1,
                                max_value=10.0,
                                value=1.0,
                                step=0.1,
                                key="bc_portion"
                            )
                            
                            st.markdown(f"**Total: {int(product_info['calories'] * bc_portion_multiplier)} calories**")
                            
                            bc_meal_col1, bc_meal_col2 = st.columns([2, 1])
                            
                            with bc_meal_col1:
                                bc_meal_type = st.selectbox(
                                    "Meal type",
                                    ["🌅 Breakfast", "🌞 Lunch", "🌆 Dinner", "🍿 Snack"],
                                    key="bc_meal_type"
                                )
                            
                            with bc_meal_col2:
                                if st.button("💾 Add", type="primary", use_container_width=True, key="bc_save"):
                                    meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    
                                    meal_data = {
                                        'id': meal_id,
                                        'food_name': f"{product_info['brands']} {product_info['product_name']}",
                                        'meal_type': bc_meal_type,
                                        'nutrition': product_info,
                                        'multiplier': bc_portion_multiplier,
                                        'portion_text': f"{bc_portion_multiplier * 100}g",
                                        'confidence': 'High',
                                        'source': 'Open Food Facts'
                                    }
                                    
                                    app.save_meal(meal_data)
                                    st.success(f"✅ Added to your {bc_meal_type} log!")
                                    st.balloons()
                        else:
                            st.error("❌ Product not found in database. Try the manual search above.")
                else:
                    st.error("❌ No barcode detected in image. Make sure the barcode is clear and well-lit.")
    
    # Recent foods
    st.divider()
    st.markdown("### 🕐 Recently Logged Foods")
    
    all_meals = app.load_meals()
    recent_foods = []
    
    for date_str in sorted(all_meals.keys(), reverse=True):
        for meal in all_meals[date_str]:
            food_name = meal['food_name']
            if food_name not in [f['name'] for f in recent_foods]:
                recent_foods.append({
                    'name': food_name,
                    'meal': meal
                })
            if len(recent_foods) >= 5:
                break
        if len(recent_foods) >= 5:
            break
    
    if recent_foods:
        for food in recent_foods:
            # Use the meal id if present; otherwise derive a stable key from the name
            # (avoid hash() — it's session-randomized in Python 3.3+ and causes
            # DuplicateWidgetID errors if the same food appears more than once)
            raw_key = food['meal'].get('id') or food['name']
            safe_key = "".join(c if c.isalnum() else "_" for c in raw_key)[:40]
            if st.button(f"➕ {food['name']}", key=f"recent_{safe_key}", use_container_width=True):
                # Quick add recent food
                meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                meal_data = food['meal'].copy()
                meal_data['id'] = meal_id
                meal_data['timestamp'] = datetime.now().isoformat()
                
                app.save_meal(meal_data)
                st.success(f"✅ Added {food['name']} to today's log!")
    else:
        st.caption("No recent foods. Add some meals first!")
