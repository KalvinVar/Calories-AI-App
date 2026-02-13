"""
Tab 1: Analyze Food
Food photo analysis and barcode scanning
"""
import streamlit as st
from datetime import datetime
from PIL import Image


def render(app):
    """Render the Analyze Food tab (Tab 1)
    
    Args:
        app: The main app module with all utility functions
    """
    
    # Initialize scan mode in session state
    if 'scan_mode' not in st.session_state:
        st.session_state['scan_mode'] = "🍕 Food Photo"
    
    # Eye-catching mode selector with large buttons
    st.markdown("### 🔍 How do you want to track your food?")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(
            "🍕 Food Photo",
            use_container_width=True,
            type="primary" if st.session_state['scan_mode'] == "🍕 Food Photo" else "secondary",
            key="btn_food_photo"
        ):
            st.session_state['scan_mode'] = "🍕 Food Photo"
            st.rerun()
    
    with col2:
        if st.button(
            "📷 Product Barcode",
            use_container_width=True,
            type="primary" if st.session_state['scan_mode'] == "📷 Product Barcode" else "secondary",
            key="btn_barcode"
        ):
            st.session_state['scan_mode'] = "📷 Product Barcode"
            st.rerun()
    
    with col3:
        if st.button(
            "🔍 Search Foods",
            use_container_width=True,
            type="primary" if st.session_state['scan_mode'] == "🔍 Search Foods" else "secondary",
            key="btn_search"
        ):
            st.session_state['scan_mode'] = "🔍 Search Foods"
            st.rerun()
    
    scan_mode = st.session_state['scan_mode']
    
    st.divider()
    
    if scan_mode == "🔍 Search Foods":
        # FOOD SEARCH MODE
        render_search_mode(app)
        return  # Exit early - search mode handles everything
        
    elif scan_mode == "🍕 Food Photo":
        st.markdown("### 📤 Upload Your Food Image")
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG | Max size: 200MB",
            label_visibility="collapsed",
            key="food_upload"
        )
        
        # Clear old analysis/custom foods when new file is uploaded
        if uploaded_file is not None:
            if 'last_uploaded_file' not in st.session_state or st.session_state['last_uploaded_file'] != uploaded_file.name:
                st.session_state['last_uploaded_file'] = uploaded_file.name
                st.session_state['analysis'] = None
                st.session_state['custom_foods'] = []
                st.session_state['selected_items'] = {}
                
    else:  # Barcode mode
        st.markdown("### 📷 Upload Barcode Image")
        st.caption("Take a clear photo of the product barcode")
        uploaded_file = st.file_uploader(
            "Upload barcode image",
            type=["jpg", "jpeg", "png"],
            help="Make sure the barcode is clear and well-lit",
            label_visibility="collapsed",
            key="barcode_upload_main"
        )
    
    # Process based on mode
    if uploaded_file is not None and scan_mode == "📷 Product Barcode":
        # BARCODE SCANNING MODE
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Product Image")
            st.image(uploaded_file, use_container_width=True)
        
        with col2:
            st.subheader("Nutrition Analysis")
            
            # Auto-scan from uploaded image
            with st.spinner("Scanning barcode..."):
                barcode_data, barcode_type = app.scan_barcode_from_image(uploaded_file)
            
            if barcode_data:
                st.success(f"✅ Barcode detected: {barcode_data}")
                st.caption(f"Type: {barcode_type}")
                
                # Get product info
                with st.spinner("Looking up product..."):
                    product_info = app.get_product_from_barcode(barcode_data)
                    
                    if product_info:
                            st.divider()
                            st.markdown("### ✏️ Detected Product")
                            st.markdown(f"**{product_info['brands']} - {product_info['product_name']}**")
                            
                            # Show product image directly (not in expander)
                            if product_info.get('image_url'):
                                st.image(product_info['image_url'], caption="Product Photo", use_container_width=True)
                            
                            st.divider()
                            
                            # Portion adjustment - USE SMART SERVING DETECTION
                            st.markdown("### 🍴 Adjust Your Portion Size")
                            
                            # Detect food category from product name
                            product_full_name = f"{product_info['product_name']} {product_info['brands']}"
                            food_category = app.detect_food_category(product_full_name)
                            
                            if food_category != 'other':
                                st.info(f"✨ Smart serving detected: {product_info['product_name']} ({food_category})")
                            else:
                                st.info("ℹ️ Using standard portion multiplier")
                            
                            # Get category-specific conversion
                            conversion = app.get_serving_conversion(food_category)
                            
                            # Category-specific input or fallback to multiplier
                            if food_category != 'other':
                                # Set defaults based on category
                                if food_category in ['cookies', 'candy', 'bread']:
                                    default_amount = 3
                                    max_amount = 20
                                    step = 1
                                elif food_category in ['pizza']:
                                    default_amount = 2
                                    max_amount = 8
                                    step = 1
                                elif food_category in ['burger']:
                                    default_amount = 1
                                    max_amount = 5
                                    step = 1
                                elif food_category in ['meat']:
                                    default_amount = 100
                                    max_amount = 500
                                    step = 25
                                elif food_category in ['beverage']:
                                    default_amount = 250
                                    max_amount = 2000
                                    step = 50
                                elif food_category in ['rice', 'pasta', 'soup', 'vegetables']:
                                    default_amount = 1
                                    max_amount = 5
                                    step = 0.5
                                elif food_category in ['fries', 'snacks']:
                                    default_amount = 1
                                    max_amount = 5
                                    step = 0.5
                                else:
                                    default_amount = 1
                                    max_amount = 5
                                    step = 0.5
                                
                                # Serving amount input
                                if isinstance(step, int):
                                    serving_amount = st.number_input(
                                        conversion['label'],
                                        min_value=int(step),
                                        max_value=int(max_amount),
                                        value=int(default_amount),
                                        step=int(step),
                                        help=f"Enter the amount in {conversion['unit']}",
                                        key="bc_serving_amount"
                                    )
                                    
                                    # Add quick size buttons for beverages
                                    if food_category == 'beverage':
                                        st.caption("**Quick sizes:**")
                                        bc_bev_col1, bc_bev_col2, bc_bev_col3, bc_bev_col4 = st.columns(4)
                                        with bc_bev_col1:
                                            if st.button("🥤 Can (355ml)", use_container_width=True, key="bc_can"):
                                                st.session_state['bc_bev_amount'] = 355
                                        with bc_bev_col2:
                                            if st.button("🧃 Small (250ml)", use_container_width=True, key="bc_small"):
                                                st.session_state['bc_bev_amount'] = 250
                                        with bc_bev_col3:
                                            if st.button("🥤 Medium (500ml)", use_container_width=True, key="bc_med"):
                                                st.session_state['bc_bev_amount'] = 500
                                        with bc_bev_col4:
                                            if st.button("🥤 Large (750ml)", use_container_width=True, key="bc_large"):
                                                st.session_state['bc_bev_amount'] = 750
                                        
                                        if 'bc_bev_amount' in st.session_state:
                                            serving_amount = st.session_state['bc_bev_amount']
                                            st.info(f"Selected: {serving_amount}ml")
                                else:
                                    serving_amount = st.number_input(
                                        conversion['label'],
                                        min_value=float(step),
                                        max_value=float(max_amount),
                                        value=float(default_amount),
                                        step=float(step),
                                        help=f"Enter the amount in {conversion['unit']}",
                                        key="bc_serving_amount"
                                    )
                                
                                # Calculate multiplier
                                bc_portion_multiplier = app.calculate_multiplier(food_category, serving_amount)
                                
                                # Show conversion info
                                total_grams = serving_amount * conversion['grams_per_unit']
                                st.caption(f"≈ {total_grams:.0f}g total ({serving_amount} {conversion['unit']} × {conversion['grams_per_unit']}g per {conversion['unit']})")
                                
                                # Display portion text for saving
                                portion_text = f"{serving_amount} {conversion['unit']}"
                            else:
                                # Fallback to multiplier for unrecognized products
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    if st.button("0.5x (Half)", use_container_width=True, key="bc_half"):
                                        st.session_state['bc_portion'] = 0.5
                                with col2:
                                    if st.button("1x (Standard)", use_container_width=True, key="bc_1x"):
                                        st.session_state['bc_portion'] = 1.0
                                with col3:
                                    if st.button("1.5x (Large)", use_container_width=True, key="bc_15x"):
                                        st.session_state['bc_portion'] = 1.5
                                with col4:
                                    if st.button("2x (Double)", use_container_width=True, key="bc_2x"):
                                        st.session_state['bc_portion'] = 2.0
                                
                                if 'bc_portion' not in st.session_state:
                                    st.session_state['bc_portion'] = 1.0
                                
                                bc_portion_multiplier = st.slider(
                                    "Portion size:",
                                    min_value=0.25,
                                    max_value=3.0,
                                    value=st.session_state['bc_portion'],
                                    step=0.25,
                                    help="Adjust the portion size relative to 100g",
                                    key="bc_slider"
                                )
                                portion_text = f"{bc_portion_multiplier:.2f}x"
                            
                            # Advanced multiplier override
                            with st.expander("⚙️ Advanced: Manual multiplier"):
                                manual_multiplier = st.number_input(
                                    "Override with custom multiplier",
                                    min_value=0.1,
                                    max_value=10.0,
                                    value=bc_portion_multiplier,
                                    step=0.1,
                                    help="Manually override the calculated multiplier if needed",
                                    key="bc_manual"
                                )
                                if st.checkbox("Use manual multiplier", key="bc_use_manual"):
                                    bc_portion_multiplier = manual_multiplier
                                    portion_text = f"{bc_portion_multiplier:.2f}x"
                            
                            # Display product name
                            st.markdown(f"### **{product_info['brands']} {product_info['product_name']}**")
                            st.success("✓ Data from Open Food Facts")
                            st.markdown(f"**Base Data:** 100g")
                            if food_category != 'other':
                                display_amount = bc_portion_multiplier * 100 / conversion['grams_per_unit']
                                st.markdown(f"**Your Portion:** {display_amount:.1f} {conversion['unit']} ({bc_portion_multiplier:.2f}x of 100g)")
                            else:
                                st.markdown(f"**Your Portion:** {bc_portion_multiplier:.2f}x")
                                st.markdown(f"**Confidence:** High")
                            
                            st.divider()
                            
                            # Calculate adjusted nutrition values - MATCH FOOD PHOTO LAYOUT
                            st.markdown("### 📊 Nutritional Facts")
                            st.markdown("**For your selected portion:**")
                            st.markdown("")
                            
                            # Highlight calories in larger display
                            st.markdown(f"""
                            <div style="text-align: center; padding: 1.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                        border-radius: 15px; margin-bottom: 1.5rem; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                                <h1 style="color: white; margin: 0; font-size: 3rem;">{int(product_info['calories'] * bc_portion_multiplier)}</h1>
                                <p style="color: white; margin: 0; font-size: 1.2rem; opacity: 0.9;">Calories (kcal)</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Macronutrients in columns
                            st.markdown("**Macronutrients:**")
                            col_a, col_b, col_c = st.columns(3)
                            
                            with col_a:
                                st.metric("💪 Protein", f"{round(product_info['protein'] * bc_portion_multiplier, 1)}g", 
                                         help="Essential for muscle growth and repair")
                            
                            with col_b:
                                st.metric("🍞 Carbs", f"{round(product_info['carbs'] * bc_portion_multiplier, 1)}g",
                                         help="Primary energy source")
                            
                            with col_c:
                                st.metric("🥑 Fat", f"{round(product_info['fat'] * bc_portion_multiplier, 1)}g",
                                         help="Essential for hormone production")
                            
                            st.markdown("")
                            st.markdown("**Additional Info:**")
                            col_d, col_e = st.columns(2)
                            
                            with col_d:
                                st.metric("🌾 Fiber", f"{round(product_info['fiber'] * bc_portion_multiplier, 1)}g",
                                         help="Good for digestion")
                            
                            with col_e:
                                st.metric("🍯 Sugar", f"{round(product_info['sugar'] * bc_portion_multiplier, 1)}g",
                                         help="Natural and added sugars")
                            
                            st.divider()
                            st.caption("⚠️ Values are estimates and may vary based on preparation method and ingredients.")
                            
                            # Save meal to log
                            st.markdown("### 💾 Save This Meal")
                            
                            bc_meal_col1, bc_meal_col2 = st.columns([2, 1])
                            with bc_meal_col1:
                                bc_meal_type = st.selectbox(
                                    "Meal type",
                                    ["🌅 Breakfast", "🌞 Lunch", "🌆 Dinner", "🍿 Snack"],
                                    key="bc_meal_type_main",
                                    label_visibility="collapsed"
                                )
                            
                            with bc_meal_col2:
                                if st.button("💾 Save to Log", type="primary", use_container_width=True, key="bc_save_main"):
                                    meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    
                                    meal_data = {
                                        'id': meal_id,
                                        'food_name': f"{product_info['brands']} {product_info['product_name']}",
                                        'meal_type': bc_meal_type,
                                        'nutrition': product_info,
                                        'multiplier': bc_portion_multiplier,
                                        'portion_text': portion_text,
                                        'confidence': 'High',
                                        'source': 'Open Food Facts'
                                    }
                                    
                                    app.save_meal(meal_data)
                                    st.success(f"✅ Meal saved to your {bc_meal_type} log!")
                                    st.balloons()
                            
                            st.divider()
                            
                            # Download report
                            report = f"""Product Nutrition Report

Product: {product_info['brands']} {product_info['product_name']}
Barcode: {barcode_data}
Portion: {portion_text} of 100g
Data Source: Open Food Facts

Nutritional Facts:
- Calories: {int(product_info['calories'] * bc_portion_multiplier)} kcal
- Protein: {round(product_info['protein'] * bc_portion_multiplier, 1)}g
- Carbohydrates: {round(product_info['carbs'] * bc_portion_multiplier, 1)}g
- Fat: {round(product_info['fat'] * bc_portion_multiplier, 1)}g
- Fiber: {round(product_info['fiber'] * bc_portion_multiplier, 1)}g
- Sugar: {round(product_info['sugar'] * bc_portion_multiplier, 1)}g
"""
                            
                            st.download_button(
                                label="📥 Download Report",
                                data=report,
                                file_name="barcode_nutrition_analysis.txt",
                                mime="text/plain"
                            )
                    else:
                        st.error("❌ Product not found in Open Food Facts database.")
                        st.info("💡 Try searching manually in the 'Quick Add' tab, or the barcode may have been misread.")
                        st.caption("**Scanning tips:** Image quality, resolution, lighting, and camera angle (take photo straight-on, not tilted) can affect barcode accuracy. Try retaking with better conditions.")
            else:
                st.error("❌ No barcode detected in image.")
                st.info("💡 **Scanning tips:**")
                st.markdown("""
                - Ensure barcode is **clear and in focus**
                - Use **good lighting** (avoid shadows/glare)
                - Take photo **straight-on, not at an angle** (camera parallel to barcode surface)
                - Get **close enough** so barcode fills frame
                - Keep barcode lines **horizontal or vertical**
                - Try a **higher resolution** image if possible
                
                **Alternative:** Use the 'Quick Add' tab to search by product name.
                """)

    elif uploaded_file is not None and scan_mode == "🍕 Food Photo":
        # Display the image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Your Food")
            try:
                image = Image.open(uploaded_file)
                st.image(image, use_container_width=True)
            except Exception as e:
                st.error(f"Error loading image: {e}")
                st.stop()
        
        with col2:
            st.subheader("Nutrition Analysis")
            
            # Analyze button
            if st.button("🔍 Analyze Nutrition", type="primary", use_container_width=True):
                with st.spinner("Analyzing your food..."):
                    # Reset file pointer before sending
                    uploaded_file.seek(0)
                    result = app.analyze_food_image(uploaded_file)
                    
                    # Store in session state
                    if isinstance(result, dict):
                        st.session_state['analysis'] = result
                    else:
                        st.session_state['error'] = result
            
            # Display error if any
            if 'error' in st.session_state and st.session_state['error']:
                st.error(st.session_state['error'])
                st.session_state['error'] = None
            
            # Display results if available
            if 'analysis' in st.session_state and st.session_state['analysis'] is not None:
                data = st.session_state['analysis']
                
                # User confirmation - let them edit the food name
                st.divider()
                st.markdown("### ✏️ Detected Food")
                
                # Check if multiple items detected
                if data['other_items'] and len(data['other_items']) > 0:
                    # Show option to combine multiple items
                    st.markdown(f"**{len(data['other_items']) + 1} items detected**")
                    
                    # Checkbox to enable multi-item meal mode
                    combine_mode = st.checkbox(
                        "🍽️ Combine multiple items into one meal",
                        value=False,
                        help="Check this to select and combine multiple detected foods into a single meal entry"
                    )
                    
                    if combine_mode:
                        # MULTI-ITEM MODE: Show checkboxes for each item
                        st.caption("**Select all items on your plate:**")
                        
                        # Initialize custom foods list in session state
                        if 'custom_foods' not in st.session_state:
                            st.session_state['custom_foods'] = []
                        
                        # Create list with primary food + alternatives + custom foods
                        all_detected_foods = [data['food_name']] + data['other_items'] + st.session_state['custom_foods']
                        
                        # Initialize selected items in session state
                        if 'selected_items' not in st.session_state:
                            st.session_state['selected_items'] = {all_detected_foods[0]: True}
                        
                        # Display checkboxes for each detected item
                        selected_foods = []
                        for i, food in enumerate(all_detected_foods):
                            if food not in st.session_state['selected_items']:
                                st.session_state['selected_items'][food] = (i == 0)
                            
                            is_checked = st.checkbox(
                                food,
                                value=st.session_state['selected_items'][food],
                                key=f"food_check_{i}"
                            )
                            st.session_state['selected_items'][food] = is_checked
                            
                            if is_checked:
                                selected_foods.append(food)
                        
                        st.caption(f"*{len(selected_foods)} item{'s' if len(selected_foods) != 1 else ''} selected*")
                        
                        # Option to add custom item
                        with st.expander("➕ Add custom food item"):
                            custom_food = st.text_input("Enter food name:", placeholder="e.g., Ketchup")
                            if st.button("Add to meal") and custom_food:
                                if custom_food not in all_detected_foods:
                                    st.session_state['custom_foods'].append(custom_food)
                                    st.session_state['selected_items'][custom_food] = True
                                    st.success(f"✓ Added {custom_food}")
                                    st.rerun()
                    else:
                        # SINGLE-ITEM MODE (DEFAULT): Show dropdown selector
                        st.markdown("**Select or edit the detected food:**")
                        
                        all_detected_foods = [data['food_name']] + data['other_items']
                        
                        col_select1, col_select2 = st.columns([3, 1])
                        
                        with col_select1:
                            selected_food = st.selectbox(
                                "Choose detected food:",
                                options=all_detected_foods,
                                index=0,
                                help="Switch between detected foods",
                                label_visibility="collapsed"
                            )
                        
                        with col_select2:
                            # Manual edit option
                            if st.button("✏️ Edit", use_container_width=True, help="Manually edit food name"):
                                st.session_state['manual_edit'] = True
                                st.rerun()
                        
                        # If user wants to manually edit
                        if st.session_state.get('manual_edit', False):
                            corrected_food = st.text_input(
                                "Enter custom food name:",
                                value=selected_food,
                                help="Type a custom food name if detection was incorrect"
                            )
                            
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button("🔄 Update", use_container_width=True, type="primary"):
                                    remaining_alternatives = [f for f in all_detected_foods if f != corrected_food]
                                    new_nutrition = app.get_nutrition_estimate(corrected_food, remaining_alternatives)
                                    data['food_name'] = corrected_food
                                    data['other_items'] = remaining_alternatives
                                    data['nutrition'] = new_nutrition
                                    st.session_state['analysis'] = data
                                    st.session_state['manual_edit'] = False
                                    st.rerun()
                            with col_btn2:
                                if st.button("❌ Cancel", use_container_width=True):
                                    st.session_state['manual_edit'] = False
                                    st.rerun()
                        
                        # If user selects a different food from dropdown
                        elif selected_food != data['food_name']:
                            remaining_alternatives = [f for f in all_detected_foods if f != selected_food]
                            new_nutrition = app.get_nutrition_estimate(selected_food, remaining_alternatives)
                            data['food_name'] = selected_food
                            data['other_items'] = remaining_alternatives
                            data['nutrition'] = new_nutrition
                            st.session_state['analysis'] = data
                            st.rerun()
                        
                        selected_foods = [data['food_name']]
                    
                else:
                    # Only one item detected - simple interface
                    st.markdown("**Confirm or edit the detected food name:**")
                    
                    col_edit1, col_edit2 = st.columns([3, 1])
                    
                    with col_edit1:
                        corrected_food = st.text_input(
                            "Food name:",
                            value=data['food_name'],
                            help="Edit if the detection was incorrect",
                            label_visibility="collapsed"
                        )
                    
                    with col_edit2:
                        if corrected_food != data['food_name']:
                            if st.button("🔄 Refresh", type="primary", use_container_width=True):
                                new_nutrition = app.get_nutrition_estimate(corrected_food, [])
                                data['food_name'] = corrected_food
                                data['nutrition'] = new_nutrition
                                st.session_state['analysis'] = data
                                st.rerun()
                        else:
                            st.button("✓ Confirmed", disabled=True, use_container_width=True)
                    
                    selected_foods = [data['food_name']]
                    combine_mode = False
                
                # Show uploaded food image in expandable section
                with st.expander("📷 View Food Photo"):
                    st.image(uploaded_file, use_container_width=True)
                
                # Check if any foods are selected before proceeding
                if len(selected_foods) == 0:
                    st.warning("⚠️ Please select at least one food item from the list above.")
                    st.stop()
                
                # Portion size adjuster - Different UI for single vs multi-item mode
                st.divider()
                
                if combine_mode and len(selected_foods) > 1:
                    # MULTI-ITEM MODE: Show expandable portions for each selected item
                    st.markdown(f"### 🍴 Adjust Portions ({len(selected_foods)} items)")
                else:
                    # SINGLE-ITEM MODE: Traditional portion UI
                    st.markdown("### 🍴 Adjust Your Portion Size")
                
                # Initialize combined nutrition storage
                combined_nutrition = {
                    'calories': 0, 'protein': 0, 'carbs': 0, 
                    'fat': 0, 'fiber': 0, 'sugar': 0
                }
                meal_components = []
                
                # Process each selected food
                for idx, food_item in enumerate(selected_foods):
                    # Show in expander only for multi-item mode
                    if combine_mode and len(selected_foods) > 1:
                        expander_label = f"🍽️ {food_item}"
                        is_expanded = (idx == 0)  # First item expanded by default
                        container = st.expander(expander_label, expanded=is_expanded)
                    else:
                        # Single item mode - no expander, direct display
                        container = st.container()
                    
                    with container:
                        # Get nutrition for this item
                        item_alternatives = [f for f in selected_foods if f != food_item]
                        item_nutrition = app.get_nutrition_estimate(food_item, item_alternatives)
                        
                        # Detect category for smart serving
                        food_category = app.detect_food_category(food_item)
                        conversion = app.get_serving_conversion(food_category)
                        
                        # Show smart serving input based on category
                        if food_category != 'other':
                            st.caption(f"✨ **{food_category.title()}** ({conversion['unit']})")
                            
                            # Show helpful explanation for USDA data
                            if not (combine_mode and len(selected_foods) > 1):
                                # Only show in single-item mode to avoid clutter
                                with st.expander("ℹ️ How are calories calculated?"):
                                    st.markdown(f"""
**USDA provides nutrition per 100g (standard reference amount)**

**How it works:**
1. USDA data: **{item_nutrition.get('calories', 0)} calories per 100g** of {food_item}
2. Your portion: **{conversion['label'].lower()}**
3. Conversion: 1 {conversion['unit'][:-1] if conversion['unit'].endswith('s') else conversion['unit']} ≈ **{conversion['grams_per_unit']}g**
4. Final calculation: Your portions × grams per unit ÷ 100 = multiplier

**Example:** 1 Big Mac (215g) = 2.15× the 100g base = {int(item_nutrition.get('calories', 0) * 2.15)} calories
                                    """)
                            
                            # Get defaults
                            if food_category in ['cookies', 'bread']:
                                default_amount, max_amount, step = 3, 20, 1
                            elif food_category in ['pizza', 'fruit', 'salad']:
                                default_amount, max_amount, step = 2, 8, 1
                            elif food_category in ['burger', 'candy']:
                                default_amount, max_amount, step = 1, 5, 1
                            elif food_category in ['meat']:
                                default_amount, max_amount, step = 100, 500, 25
                            elif food_category in ['beverage']:
                                default_amount, max_amount, step = 250, 2000, 50
                            elif food_category in ['rice', 'pasta', 'soup', 'vegetables']:
                                default_amount, max_amount, step = 1, 5, 0.5
                            elif food_category in ['fries', 'snacks']:
                                default_amount, max_amount, step = 1, 5, 0.5
                            else:
                                default_amount, max_amount, step = 1, 5, 0.5
                            
                            # Unique key for each food item
                            food_key = food_item.replace(" ", "_")[:30] + str(hash(food_item))[:8]
                            
                            if isinstance(step, int):
                                serving_amount = st.number_input(
                                    conversion['label'],
                                    min_value=int(step),
                                    max_value=int(max_amount),
                                    value=int(default_amount),
                                    step=int(step),
                                    key=f"amt_{food_key}"
                                )
                            else:
                                serving_amount = st.number_input(
                                    conversion['label'],
                                    min_value=float(step),
                                    max_value=float(max_amount),
                                    value=float(default_amount),
                                    step=float(step),
                                    key=f"amt_{food_key}"
                                )
                            
                            # Calculate multiplier
                            portion_multiplier = app.calculate_multiplier(food_category, serving_amount)
                            portion_text = f"{serving_amount:.1f} {conversion['unit']}"
                            
                            st.caption(f"**≈ {int(portion_multiplier * 100)}g total** (USDA data is per 100g, your portion is {portion_multiplier:.2f}× that base)")
                        else:
                            # Generic portion size - explain clearly how it works
                            st.info("ℹ️ **Smart serving not available** - Using weight-based calculation")
                            
                            st.markdown("""
**How to calculate your portion:**

USDA nutrition data is standardized per **100 grams** (about 3.5 oz).

**Choose your multiplier:**
- **0.5× = 50g** (small portion, like 2 chicken nuggets)
- **1.0× = 100g** (standard reference, about palm-sized)
- **2.0× = 200g** (typical restaurant burger/meal)
- **3.0× = 300g** (large meal or combo)

**Not sure?** Most single burgers/sandwiches are 200-250g (2.0-2.5×)
                            """)
                            
                            # Show quick preset buttons with gram equivalents
                            st.caption("**Quick presets:**")
                            preset_col1, preset_col2, preset_col3, preset_col4 = st.columns(4)
                            
                            food_key = food_item.replace(" ", "_")[:30] + str(hash(food_item))[:8]
                            
                            # Initialize session state for this item
                            if f'portion_{food_key}' not in st.session_state:
                                st.session_state[f'portion_{food_key}'] = 2.0  # Default to 200g (typical meal)
                            
                            with preset_col1:
                                if st.button("Small\n(100g)", use_container_width=True, key=f"sm_{food_key}"):
                                    st.session_state[f'portion_{food_key}'] = 1.0
                            with preset_col2:
                                if st.button("Medium\n(200g)", use_container_width=True, key=f"md_{food_key}"):
                                    st.session_state[f'portion_{food_key}'] = 2.0
                            with preset_col3:
                                if st.button("Large\n(300g)", use_container_width=True, key=f"lg_{food_key}"):
                                    st.session_state[f'portion_{food_key}'] = 3.0
                            with preset_col4:
                                if st.button("XL\n(500g)", use_container_width=True, key=f"xl_{food_key}"):
                                    st.session_state[f'portion_{food_key}'] = 5.0
                            
                            # Fine-tune with number input (more precise than slider)
                            col_input1, col_input2 = st.columns([2, 1])
                            
                            with col_input1:
                                portion_multiplier = st.number_input(
                                    "Portion multiplier (× 100g):",
                                    min_value=0.1,
                                    max_value=10.0,
                                    value=st.session_state[f'portion_{food_key}'],
                                    step=0.1,
                                    key=f"mult_{food_key}",
                                    help="How many times larger than 100g is your portion?"
                                )
                                st.session_state[f'portion_{food_key}'] = portion_multiplier
                            
                            with col_input2:
                                st.metric("Weight", f"{int(portion_multiplier * 100)}g")
                            
                            portion_text = f"{portion_multiplier:.1f}× (≈{int(portion_multiplier * 100)}g)"
                        
                        # Calculate nutrition for this item
                        item_cal = int(item_nutrition['calories'] * portion_multiplier)
                        item_prot = round(item_nutrition['protein'] * portion_multiplier, 1)
                        item_carb = round(item_nutrition['carbs'] * portion_multiplier, 1)
                        item_fat = round(item_nutrition['fat'] * portion_multiplier, 1)
                        item_fiber = round(item_nutrition['fiber'] * portion_multiplier, 1)
                        item_sugar = round(item_nutrition['sugar'] * portion_multiplier, 1)
                        
                        # Show individual nutrition (compact for multi-item, detailed for single)
                        if combine_mode and len(selected_foods) > 1:
                            # Compact view in expander
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Calories", f"{item_cal} kcal")
                            with col2:
                                st.metric("Protein", f"{item_prot}g")
                            with col3:
                                st.metric("Carbs", f"{item_carb}g")
                        
                        # Add to combined totals
                        combined_nutrition['calories'] += item_cal
                        combined_nutrition['protein'] += item_prot
                        combined_nutrition['carbs'] += item_carb
                        combined_nutrition['fat'] += item_fat
                        combined_nutrition['fiber'] += item_fiber
                        combined_nutrition['sugar'] += item_sugar
                        
                        # Store component for meal saving
                        meal_components.append({
                            'name': food_item,
                            'portion': portion_text,
                            'multiplier': portion_multiplier,
                            'nutrition': item_nutrition,
                            'source': item_nutrition.get('source', 'Estimate')
                        })
                
                # Show combined nutrition total
                st.divider()
                
                # Only show nutrition if items are selected
                if len(meal_components) == 0:
                    st.warning("⚠️ Please select at least one food item to see nutritional information.")
                else:
                    if combine_mode and len(selected_foods) > 1:
                        # MULTI-ITEM MODE: Show combined totals prominently
                        st.markdown("### 📊 Combined Nutritional Facts")
                        st.info(f"**Total for {len(selected_foods)} items:** {', '.join([c['name'] for c in meal_components])}")
                    else:
                        # SINGLE-ITEM MODE: Standard nutrition display
                        st.markdown("### 📊 Nutritional Facts")
                        
                        # Show data source badge for single item
                        source = meal_components[0]['source']
                        if source == 'USDA':
                            usda_match = meal_components[0]['nutrition'].get('usda_match', '')
                            st.success(f"✓ Real USDA data: {usda_match}")
                            st.caption(f"💡 **Note:** USDA provides nutrition per 100g. Your portion is {int(combined_nutrition['calories'] / meal_components[0]['nutrition']['calories'] * 100)}g = {meal_components[0]['portion']}")
                        else:
                            st.info("ℹ️ Estimated nutrition data")
                    
                    # Display combined totals in prominent card
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 2rem; border-radius: 15px; text-align: center; margin: 1rem 0;">
                        <h1 style="color: white; font-size: 3rem; margin: 0;">{int(combined_nutrition['calories'])}</h1>
                        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin: 0;">Calories (kcal)</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Macros
                    st.markdown("**Macronutrients:**")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("💪 Protein", f"{round(combined_nutrition['protein'], 1)}g")
                    with col_b:
                        st.metric("🍞 Carbs", f"{round(combined_nutrition['carbs'], 1)}g")
                    with col_c:
                        st.metric("🥑 Fat", f"{round(combined_nutrition['fat'], 1)}g")
                    
                    st.markdown("**Additional Info:**")
                    col_d, col_e = st.columns(2)
                    with col_d:
                        st.metric("🌾 Fiber", f"{round(combined_nutrition['fiber'], 1)}g")
                    with col_e:
                        st.metric("🍯 Sugar", f"{round(combined_nutrition['sugar'], 1)}g")
                    
                    st.caption("⚠️ Values are estimates and may vary based on preparation method and ingredients.")
                    
                    # Save meal to log
                    st.divider()
                    st.markdown("### 💾 Save This Meal")
                    
                    meal_col1, meal_col2 = st.columns([2, 1])
                    with meal_col1:
                        meal_type = st.selectbox(
                            "Meal type",
                            ["🌅 Breakfast", "🌞 Lunch", "🌆 Dinner", "🍿 Snack"],
                            label_visibility="collapsed"
                        )
                    
                    with meal_col2:
                        if st.button("💾 Save to Log", use_container_width=True, type="primary"):
                            # Save meal image
                            meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                            image_path = app.save_meal_image(uploaded_file, meal_id)
                            
                            # Create combined food name
                            if len(selected_foods) > 1:
                                combined_food_name = " + ".join([c['name'] for c in meal_components])
                                portion_display = f"{len(selected_foods)} items"
                            else:
                                combined_food_name = meal_components[0]['name']
                                portion_display = meal_components[0]['portion']
                            
                            # Prepare meal data with combined nutrition
                            meal_data = {
                                'id': meal_id,
                                'food_name': combined_food_name,
                                'meal_type': meal_type,
                                'nutrition': combined_nutrition,  # Using combined totals
                                'multiplier': 1.0,  # Already calculated in combined_nutrition
                                'portion_text': portion_display,
                                'image_path': image_path,
                                'confidence': data['confidence'],
                                'source': 'Combined' if len(selected_foods) > 1 else meal_components[0]['source'],
                                'components': meal_components  # Store individual items
                            }
                            
                            app.save_meal(meal_data)
                            st.success(f"✅ Meal saved to {meal_type} log!")
                            st.balloons()
                            
                            # Clear selection for next meal
                            st.session_state['selected_items'] = {}
                            st.session_state['custom_foods'] = []
                    
                    # Download report
                    if len(selected_foods) > 1:
                        items_list = "\n".join([f"  - {c['name']}: {c['portion']}" for c in meal_components])
                        report = f"""Food Nutrition Report

Combined Meal: {len(selected_foods)} items
{items_list}

Total Nutritional Facts:
- Calories: {int(combined_nutrition['calories'])} kcal
- Protein: {round(combined_nutrition['protein'], 1)}g
- Carbohydrates: {round(combined_nutrition['carbs'], 1)}g
- Fat: {round(combined_nutrition['fat'], 1)}g
- Fiber: {round(combined_nutrition['fiber'], 1)}g
- Sugar: {round(combined_nutrition['sugar'], 1)}g
"""
                    else:
                        component = meal_components[0]
                        report = f"""Food Nutrition Report

Food: {component['name']}
Portion: {component['portion']}
Confidence: {data['confidence']}
Data Source: {component['source']}

Nutritional Facts:
- Calories: {int(combined_nutrition['calories'])} kcal
- Protein: {round(combined_nutrition['protein'], 1)}g
- Carbohydrates: {round(combined_nutrition['carbs'], 1)}g
- Fat: {round(combined_nutrition['fat'], 1)}g
- Fiber: {round(combined_nutrition['fiber'], 1)}g
- Sugar: {round(combined_nutrition['sugar'], 1)}g
"""
                    
                    st.download_button(
                        label="📥 Download Report",
                        data=report,
                        file_name="nutrition_analysis.txt",
                        mime="text/plain"
                    )

    else:
        # No file uploaded - show welcome message
        st.info("👆 Upload a food image above to get started!")
        st.markdown("")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown("""
        **🍕 Fast Food**
        - Pizza
        - Burgers
        - Fries
        - Sandwiches
        """)
        with col2:
            st.markdown("""
        **🥗 Healthy Options**
        - Salads
        - Fruits
        - Vegetables
        - Grilled meats
        """)
        with col3:
            st.markdown("""
        **🍝 Meals**
        - Pasta
        - Rice bowls
        - Soups
        - Stir-fries
        """)
        with col4:
            st.markdown("""
        **🍪 Snacks**
        - Cookies
        - Candy bars
        - Chips
        - Desserts
        """)


def render_search_mode(app):
    """Render the food search interface"""
    import requests
    from datetime import date
    
    st.markdown("### 🔍 Search for Foods")
    st.caption("Type a food name to search the USDA database")
    
    # Search input
    search_query = st.text_input(
        "Search for a food",
        placeholder="e.g., chicken breast, apple, pizza, rice...",
        help="Start typing to search USDA FoodData Central",
        key="search_input"
    )
    
    if search_query and len(search_query) >= 2:
        # Show loading state
        with st.spinner("Searching USDA database..."):
            # Search USDA database
            results = search_usda_foods(search_query, app.USDA_API_KEY)
            
            if results:
                st.success(f"✅ Found {len(results)} matching foods")
                
                # Display results as expandable cards
                for idx, food in enumerate(results):
                    with st.expander(f"🍴 {food['name']}", expanded=(idx == 0)):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Brand:** {food.get('brand', 'Generic')}")
                            st.markdown(f"**Source:** {food.get('dataType', 'USDA')}")
                        
                        with col2:
                            if st.button("✅ Select This", key=f"select_{idx}", type="primary", use_container_width=True):
                                st.session_state['selected_food'] = food
                                st.rerun()
                        
                        # Nutrition info (per 100g)
                        if food.get('nutrition'):
                            st.markdown("#### 📊 Nutrition Facts (per 100g)")
                            
                            nutrients = food['nutrition']
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("🔥 Calories", f"{nutrients.get('calories', 0):.0f}")
                            with col2:
                                st.metric("💪 Protein", f"{nutrients.get('protein', 0):.1f}g")
                            with col3:
                                st.metric("🍞 Carbs", f"{nutrients.get('carbs', 0):.1f}g")
                            with col4:
                                st.metric("🥑 Fat", f"{nutrients.get('fat', 0):.1f}g")
            else:
                st.info("💡 No results found. Try a different search term or check spelling.")
    elif search_query:
        st.info("👆 Type at least 2 characters to search")
    
    # If a food is selected, show portion input and save option
    if 'selected_food' in st.session_state and st.session_state.get('selected_food'):
        st.divider()
        selected = st.session_state['selected_food']
        
        # Header
        st.markdown("### ✏️ Selected Product")
        st.markdown(f"**{selected.get('brand', 'Generic')}** - {selected['name']}")
        
        # Product display section
        col_img, col_info = st.columns([1, 2])
        
        with col_img:
            st.markdown("**Product Photo**")
            
            # Show a food emoji based on category
            category = app.detect_food_category(selected['name'])
            emoji_map = {
                'beverage': '🥤', 'meat': '🥩', 'pizza': '🍕', 'burger': '🍔',
                'fries': '🍟', 'fruit': '🍎', 'salad': '🥗', 'pasta': '🍝',
                'rice': '🍚', 'soup': '🍲', 'bread': '🍞', 'cookies': '🍪',
                'candy': '🍬', 'snacks': '🍿', 'vegetables': '🥦', 'other': '🍽️'
            }
            food_emoji = emoji_map.get(category, '🍽️')
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 3rem;
                border-radius: 15px;
                text-align: center;
                font-size: 5rem;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            ">
                {food_emoji}
            </div>
            """, unsafe_allow_html=True)
        
        with col_info:
            # Show nutrition per 100g
            st.markdown("**Nutrition Facts (per 100g)**")
            nutrition = selected['nutrition']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔥 Cal", f"{nutrition.get('calories', 0):.0f}")
            with col2:
                st.metric("💪 Pro", f"{nutrition.get('protein', 0):.1f}g")
            with col3:
                st.metric("🍞 Carbs", f"{nutrition.get('carbs', 0):.1f}g")
            with col4:
                st.metric("🥑 Fat", f"{nutrition.get('fat', 0):.1f}g")
        
        st.divider()
        
        # Portion adjustment section
        st.markdown("### 🍴 Adjust Your Portion Size")
        
        # Detect category for smart defaults
        conversion = app.get_serving_conversion(category)
        
        # Show category info
        if category != 'other':
            st.caption(f"✨ Smart serving detected: {selected['name']} ({category})")
        
        # Main portion input
        st.markdown(f"**{conversion['label']}**")
        
        # Get defaults based on category
        if category in ['cookies', 'bread']:
            default_amount, max_amount, step = 3, 20, 1
            quick_sizes = [1, 2, 3, 5, 10]
        elif category in ['pizza', 'fruit', 'salad']:
            default_amount, max_amount, step = 2, 8, 1
            quick_sizes = [1, 2, 3, 4]
        elif category in ['burger', 'candy']:
            default_amount, max_amount, step = 1, 5, 1
            quick_sizes = [1, 2, 3]
        elif category in ['meat']:
            default_amount, max_amount, step = 100, 500, 25
            quick_sizes = [100, 150, 200, 300]
        elif category in ['beverage']:
            default_amount, max_amount, step = 250, 2000, 50
            quick_sizes = [250, 330, 500, 750, 1000]
        elif category in ['rice', 'pasta', 'soup', 'vegetables']:
            default_amount, max_amount, step = 1.0, 5.0, 0.5
            quick_sizes = [0.5, 1, 1.5, 2, 3]
        elif category in ['fries', 'snacks']:
            default_amount, max_amount, step = 1.0, 5.0, 0.5
            quick_sizes = [0.5, 1, 1.5, 2]
        else:
            default_amount, max_amount, step = 2.0, 5.0, 0.5
            quick_sizes = [1, 2, 3, 4]
        
        # Initialize portion amount in session state
        if 'search_portion_value' not in st.session_state:
            st.session_state['search_portion_value'] = default_amount
        
        # Type-safe number input
        if isinstance(step, int):
            portion_amount = st.number_input(
                f"{conversion['label']}",
                min_value=int(step),
                max_value=int(max_amount),
                value=int(st.session_state['search_portion_value']),
                step=int(step),
                key="search_portion",
                label_visibility="collapsed"
            )
        else:
            portion_amount = st.number_input(
                f"{conversion['label']}",
                min_value=float(step),
                max_value=float(max_amount),
                value=float(st.session_state['search_portion_value']),
                step=float(step),
                key="search_portion",
                label_visibility="collapsed"
            )
        
        # Quick size buttons
        st.markdown("**Quick sizes:**")
        quick_cols = st.columns(len(quick_sizes))
        for idx, size in enumerate(quick_sizes):
            with quick_cols[idx]:
                if isinstance(size, float):
                    btn_label = f"{size:.1f}"
                else:
                    btn_label = str(size)
                if st.button(btn_label, key=f"quick_{idx}", use_container_width=True):
                    st.session_state['search_portion_value'] = size
                    st.rerun()
        
        # Calculate multiplier using the app's function
        multiplier = app.calculate_multiplier(category, portion_amount)
        
        # Show calculation
        total_grams = int(multiplier * 100)
        st.caption(f"≈ {total_grams}g total ({portion_amount} {conversion['unit']} × {conversion['grams_per_unit']}g per {conversion['unit'][:-1] if conversion['unit'].endswith('s') else conversion['unit']})")
        
        # Advanced manual multiplier
        with st.expander("⚙️ Advanced: Manual multiplier"):
            st.caption("Override with custom multiplier")
            manual_multiplier = st.number_input(
                "Multiplier",
                min_value=0.1,
                max_value=10.0,
                value=float(multiplier),
                step=0.1,
                key="search_manual_mult",
                label_visibility="collapsed"
            )
            if abs(manual_multiplier - multiplier) > 0.01:
                multiplier = manual_multiplier
                st.info(f"Using manual multiplier: {multiplier:.2f}×")
        
        st.divider()
        
        # Product name display
        st.markdown(f"### {selected.get('brand', 'Generic')} {selected['name']}")
        
        # Calculate adjusted nutrition
        nutrition = selected['nutrition']
        adjusted = {
            'calories': nutrition.get('calories', 0) * multiplier,
            'protein': nutrition.get('protein', 0) * multiplier,
            'carbs': nutrition.get('carbs', 0) * multiplier,
            'fat': nutrition.get('fat', 0) * multiplier
        }
        
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
            <div style="color: white; font-size: 1rem; opacity: 0.9; font-weight: 600;">CALORIES</div>
            <div style="color: white; font-size: 4rem; font-weight: bold; margin: 0.5rem 0;">{int(adjusted['calories'])}</div>
            <div style="color: white; font-size: 0.9rem; opacity: 0.8;">kcal</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Macronutrients in columns
        st.markdown("**Macronutrients:**")
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.metric("💪 Protein", f"{adjusted['protein']:.1f}g", 
                     help="Essential for muscle growth and repair")
        
        with col_b:
            st.metric("🍞 Carbs", f"{adjusted['carbs']:.1f}g",
                     help="Primary energy source")
        
        with col_c:
            st.metric("🥑 Fat", f"{adjusted['fat']:.1f}g",
                     help="Essential for hormone production")
        
        st.divider()
        st.caption("⚠️ Values are estimates from USDA FoodData Central and may vary.")
        
        # Save button
        st.markdown("### 💾 Save This Meal")
        
        col_meal_select, col_save = st.columns([2, 1])
        
        with col_meal_select:
            meal_type = st.selectbox(
                "Meal type",
                ["🌅 Breakfast", "🌞 Lunch", "🌆 Dinner", "🍿 Snack"],
                key="search_meal_type",
                label_visibility="collapsed"
            )
        
        with col_save:
            if st.button("💾 Save to Log", type="primary", use_container_width=True, key="search_save"):
                # Create meal entry
                meal = {
                    'id': f"{datetime.now().timestamp()}",
                    'date': str(date.today()),
                    'time': datetime.now().strftime("%H:%M"),
                    'food_name': selected['name'],
                    'meal_type': meal_type,
                    'portion_size': f"{portion_amount} {conversion['unit']}",
                    'multiplier': multiplier,
                    'nutrition': adjusted,
                    'source': 'USDA Search',
                    'has_image': False
                }
                
                # Save to meals
                meals = app.load_json(app.MEALS_FILE, default={})
                today = str(date.today())
                
                if today not in meals:
                    meals[today] = {}
                if meal_type not in meals[today]:
                    meals[today][meal_type] = []
                
                meals[today][meal_type].append(meal)
                app.save_json(app.MEALS_FILE, meals)
                
                st.success(f"✅ Meal saved to your {meal_type} log!")
                st.balloons()
                
                # Clear selection and portion state
                st.session_state['selected_food'] = None
                if 'search_portion_value' in st.session_state:
                    del st.session_state['search_portion_value']
                st.rerun()


def search_usda_foods(query, api_key, max_results=10):
    """Search USDA FoodData Central and return formatted results"""
    import requests
    
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
