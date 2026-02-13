# AI Agent Instructions for Food Calorie Analyzer

## Project Overview
Streamlit nutrition & fitness tracking app with AI-powered food image analysis. Uses Google Cloud Vision API (with Object Localization), USDA FoodData Central API (search + nutrition), Open Food Facts (barcode), and Hugging Face classifiers. Multi-file architecture with tab-based modules, JSON-based local persistence, and 8-tab interface for meal tracking, food search, goals, progress, history, quick add, exercise tracking, and workout log.

## Architecture & Data Flow
```
Food Analysis (3 modes):
  1. Food Photo → Vision API (labels + object localization) + HF classifier
              → analyze_food_image() combines predictions (up to 10 items)
              → User selects: single-item OR multi-item meal mode (checkbox)
  2. Product Barcode → pyzbar decode → Open Food Facts API → nutrition per 100g
  3. Food Search → USDA FoodData Central search API (15 results, deduped)
              → Popular foods grid (12 one-tap buttons) + recent searches
              → Filter by source (All/Generic/Branded) + sort (Relevance/Calories/Protein)

All modes → get_nutrition_estimate() → USDA API (3 results) → fallback to local DB
         → detect_food_category() → smart serving UI (15 categories)
         → Quick size buttons (consistent across all 3 modes)
         → calculate_multiplier() converts to 100g base
         → Save to meals.json with meal_type, components, combined nutrition

Exercise Tracking:
  Exercise Logger → EXERCISE_DATABASE (80+ exercises, 7 categories)
                 → MET-based calorie formula (cardio/general)
                 → Volume-based detailed mode (strength exercises with ROM data)
                 → Save to exercises.json grouped by date
```

**Key architectural decisions:**
- Multi-file tab architecture: `app.py` (shared utilities) + `tabs/tab_*.py` (8 tab modules)
- JSON file persistence (no database) - `data/{meals,goals,weight,water,exercises}.json`
- USDA per-100g standard requires multiplier system for user servings
- Optional multi-item mode: users can select multiple foods via checkbox → combine nutrition
- Exercise calories: MET formula for cardio, volume-based (mechanical work / efficiency) for strength
- UI labels use "Carbs/Sugar" (not just "Carbs") throughout all tabs

## Critical Developer Workflows

### Running & Testing
```bash
python -m streamlit run app.py  # NOT 'streamlit run' - module form required
# Access at http://localhost:8501 or network IP (e.g., http://10.0.0.246:8501)
# Auto-reloads on file save
# Streamlit Cloud: auto-deploys from GitHub main branch
# After push: "Manage app" → "Reboot app" + Ctrl+Shift+R for hard refresh
```

**Debug patterns:**
- Terminal logs show `[USDA]`, `[Object Detected]`, `[Barcode]`, `[USDA Search]` prefixes
- Vision API errors visible in Streamlit UI exception boxes
- Check `data/` directory for JSON structure issues

### Environment Setup
```
.env file (local development):
  GOOGLE_APPLICATION_CREDENTIALS=E:\3rd qart\vision-key.json
  USDA_API_KEY=<real_key_not_DEMO_KEY>

Streamlit Cloud: st.secrets with USDA_API_KEY and google_credentials dict

vision-key.json: Google Cloud service account with Vision API enabled
Python 3.13 on Windows (WindowsApps path)
```

## Project-Specific Conventions

### USDA 100g Calculation Pattern (CRITICAL)
**All USDA data is per 100g** - users think in servings. The app bridges this:
```python
# Example: Big Mac (215g) showing 261 cal per 100g
# User sees: "1 burger" → multiplier 2.15 → displays 561 calories
# DON'T hardcode food-specific multipliers - use generic explanations

# For unrecognized foods, show educational UI:
# - Explain "100g = palm-sized"
# - Provide presets: Small (100g), Medium (200g), Large (300g), XL (500g)
# - Default to 2.0× (200g) - realistic for most meals
```

### Food Search Mode
```python
# 3-column grid of 12 popular food buttons (one-tap search):
#   Chicken Breast, White Rice, Egg, Banana, Bread, Milk,
#   Apple, Beef, Salmon, Avocado, Pasta, Cheese
# Recent searches stored in session state (last 10, clickable)
# Explicit "🔍 Search" button + Enter key both trigger search
# Filter: All / Generic (USDA) / Branded
# Sort: Relevance / Calories ↑ / Calories ↓ / Protein ↓
# Results shown as expandable cards (first auto-expanded)
# Deduplication of similar food names, generic USDA data prioritized
# Session state pattern: search_input (widget key), search_query_text (tracking),
#   last_search_query (cache key), _search_prefill_pending (popular button flag)
# CRITICAL: Never set both key= and value= on text_input (causes state conflicts)
```

### Multi-Item Meal Mode
```python
# DEFAULT: Single-item dropdown selector (old behavior)
# OPTIONAL: Check "Combine multiple items into one meal"
#   → Checkboxes appear for all detected foods
#   → Each gets expandable portion adjuster
#   → Combined nutrition displayed
#   → Saves as "Hamburger + French fries" with components array
```

### Food Category Detection Strategy (CRITICAL)
**NEVER hardcode specific brands or products** - it's impossible to catch everything:
```python
# ❌ BAD - Too specific, unsustainable:
'burger': ['burger', 'big mac', 'whopper', 'quarter pounder', 'baconator']
'cookies': ['oreo', 'chips ahoy', 'nutter butter', 'milano']

# ✅ GOOD - Generic keywords only:
'burger': ['burger', 'hamburger', 'cheeseburger']
'cookies': ['cookie', 'biscuit']

# Philosophy: Let unrecognized specific items fall back to the improved
# generic UI that educates users about 100g calculations
```

### Exercise Tracking
```python
# EXERCISE_DATABASE: 80+ exercises across 7 categories
#   (Running, Cycling, Swimming, Walking, Gym/Weights, Sports, Other)
# Each exercise has: name, MET value, icon, description (for strength)
# Two calorie modes:
#   Simple (MET): Calories = MET × weight(kg) × duration(hours)
#   Detailed (Volume-based, strength only):
#     Lifting cal = (sets × reps × weight × ROM) / 0.20 efficiency / 4184
#     Rest cal = 2.5 MET × body_weight × rest_time
#     EPOC = 10% afterburn
# EXERCISE_ROM: 19 strength exercises with range-of-motion in meters
#   e.g., Squat=0.65m, Bench Press=0.50m, Calf Raises=0.15m
# Detailed mode enabled by default (toggle available)
# Weight unit toggle: kg/lbs (key: "exercise_weight_unit")
# Load weight uses separate keys per unit: exercise_weight_kg / exercise_weight_lbs
# 4 educational expanders: estimation methods, accuracy, MET science, tips
```

### Barcode Scanning Integration
```python
# Mode toggle: "🍕 Food Photo" vs "📷 Product Barcode" vs "🔍 Search Foods"
# Auto-scans on upload (no button needed)
# pyzbar → Open Food Facts API → nutrition per 100g
# Same smart serving detection applies to barcode products
```

### Streamlit Session State Rules
```python
# ALWAYS initialize before use:
if 'key' not in st.session_state:
    st.session_state['key'] = default_value

# Check existence AND value:
if st.session_state.get('key', None) is not None:
    # use value

# Per-item state needs unique keys (use food name hash):
food_key = food_item.replace(" ", "_")[:30] + str(hash(food_item))[:8]

# Widget key pattern for quick buttons: render buttons BEFORE number_input
# to avoid StreamlitAPIException when setting session state
# Use _pending flags for deferred state updates (e.g., _search_prefill_pending)

# CRITICAL: Never use both key= and value= on st.text_input simultaneously
# Use key-based state only, set st.session_state[key] before the widget renders
```

### Data Persistence Pattern
```python
# Load: load_json(file_path, default=[]) → returns list/dict
#   Uses except (json.JSONDecodeError, IOError, OSError) — NOT bare except
# Save: save_json(file_path, data) → writes with json.dump
# Meals grouped by date: {date: [meal_objects]}  (flat list per date)
# Exercises grouped by date: {date: [exercise_objects]}
# Components stored for multi-item meals: meal['components'] = [{name, portion, multiplier, nutrition}]
# Old meals may lack 'id' field — always use .get('id', fallback)
```

## Critical Files Structure
```
app.py (~976 lines):
  Lines 1-60: Imports, API config (secrets + .env fallback), data dir
  Lines 60-300: CSS, manifest, PWA config
  Lines 297-315: load_json / save_json (with proper exception handling)
  Lines 315-385: Data CRUD (load/save meals, goals, weight, water, exercises)
  Lines 385-510: Barcode scanning (pyzbar + Open Food Facts)
  Lines 510-650: Food name cleaning, category detection, serving conversions
  Lines 650-790: USDA API (get_nutrition_estimate) + Vision API integration
  Lines 790-976: Tab orchestration (8 tabs), shared utilities

tabs/tab_analyze.py (~2194 lines):
  Tab 1 - Analyze Food (3 modes: photo, barcode, search)
  Lines 1-60: Mode selector (Food Photo / Product Barcode / Search Foods)
  Lines 60-560: Barcode mode (scan, portion, nutrition, save)
  Lines 560-1370: Food photo mode (upload, Vision API, single/multi-item, save)
  Lines 1370-1900: Search mode - selected food view (portion, nutrition, save)
  Lines 1900-2090: Search mode - search interface (popular foods, input, results)
  Lines 2090-2194: search_usda_foods() API function

tabs/tab_summary.py (~119 lines): Tab 2 - Daily nutrition summary, water intake
tabs/tab_goals.py (~306 lines): Tab 3 - Goal setting with Mifflin-St Jeor BMR calculator
tabs/tab_history.py (~240 lines): Tab 4 - Meal history, deletion, CSV export
tabs/tab_progress.py (~95 lines): Tab 5 - Weight tracking (kg/lbs toggle), calorie trends
tabs/tab_quick_add.py (~234 lines): Tab 6 - Quick meal adding, barcode, recent foods
tabs/tab_exercise.py (~908 lines): Tab 7 - Exercise tracker (MET + detailed volume mode)
tabs/tab_workout_log.py (~395 lines): Tab 8 - Workout log, streaks, weekly/all-time stats

data/
  meals.json: {date: [meal_objects]}
  goals.json: {calories, protein, carbs, fat, water_glasses}
  weight.json: [{date, weight}]
  water.json: {date: glasses}
  exercises.json: {date: [exercise_objects]}
  meal_images/: auto-saved JPEGs named by meal_id

requirements.txt: streamlit, google-cloud-vision, pillow, python-dotenv, requests, pandas, pyzbar
```

## Common Pitfalls & Solutions

1. **Low calorie readings**: User expects full meal calories but sees 100g base
   - **Fix**: Explain "USDA is per 100g, your portion is 2.15× = 561 cal"
   - Show calculation in UI: "215g = 1 burger"

2. **"McDonald's Big Mac" not detected as burger**: Brand names in food name
   - **Don't**: Add "big mac" to category keywords
   - **Do**: Show fallback UI explaining multiplier with helpful presets

3. **Number input type errors**: `StreamlitMixedNumericTypesError`
   - **Fix**: Match step type to min/max/value: `int()` or `float()` consistently

4. **Barcode not reading**: Image quality, angle, or format issues
   - pyzbar requires clear horizontal barcode
   - Check terminal for `[Barcode]` debug logs

5. **Vision API Object Localization not finding items**: 
   - Lowers confidence threshold to 0.5 (from 0.7 for labels)
   - Returns up to 10 items (increased from 4)
   - Falls back to labels + web entities

6. **Search not working after page refresh**: 
   - Don't use both `key=` and `value=` on `st.text_input` (state conflict)
   - Use `_search_prefill_pending` flag for popular food button prefills
   - Provide explicit "🔍 Search" button as backup to Enter key

7. **Widget key crashes with quick buttons**:
   - Quick size/duration/rest buttons must render BEFORE the `number_input` widget
   - Use `_pending` flag pattern: button sets flag + value → rerun → pending check sets widget key → widget renders

8. **Duplicate widget keys across tabs**:
   - Use tab-specific prefixes: `exercise_weight_unit`, `progress_weight_unit`
   - Never share keys like `weight_unit` between tabs

9. **Exercise weight unit not converting**:
   - Split into separate keys per unit: `exercise_weight_kg` / `exercise_weight_lbs`

10. **Old meal data missing 'id' field**:
    - Always use `meal.get('id', fallback)` not `meal['id']`

11. **CSV export KeyError on fiber/sugar**:
    - Always use `nutrition.get('fiber', 0)` and `nutrition.get('sugar', 0)`

12. **Delete by list.remove() is fragile**:
    - Prefer ID-based matching, then timestamp matching, then index fallback

## UI/UX Patterns

### Portion Size Defaults by Category
```python
cookies/bread: 3 pieces, step=1, max=20
pizza/fruit: 2 pieces, step=1, max=8
burger/candy: 1 piece, step=1, max=5
meat: 100g, step=25, max=500
beverage: 250ml, step=50, max=2000
rice/pasta/vegetables: 1 cup, step=0.5, max=5
```

### Quick Size Buttons (consistent across all 3 food modes)
```python
# Rendered BEFORE the number_input widget
# Category-specific: beverage (250/355/500/750ml), cookies (1/2/3/5 pcs),
#   pizza (1/2/3/4 slices), burger (1/2/3), meat (100/150/200/300g),
#   rice/pasta (½/1/1½/2 cups), generic (Small/Medium/Large/XL)
# Uses _pending flag pattern to avoid widget state conflicts
```

### Combine Mode Display Logic
```python
# Single item: Direct UI (no expanders)
# Multi-item: Expandable sections per food + combined total card
# Combined card: Purple gradient, large calories, ingredient list
```

### Nutrition Labels
- Use "Carbs/Sugar" (not "Carbs") in all UI labels, metrics, and exports
- Emoji convention: 🔥 Calories, 💪 Protein, 🍞 Carbs/Sugar, 🥑 Fat

### Delete Confirmations
- Individual meal: single button click
- Full day of meals: single button click
- Full day of exercises: two-step confirmation (button → confirm/cancel)
- Clear all data: checkbox confirmation + button

## External API Patterns

**Google Vision API:**
- `label_detection()`: confidence >0.6
- `object_localization()`: confidence >0.5 (better multi-item detection)
- Free tier: 1000 images/month, then $1.50/1000

**USDA FoodData Central:**
- Search endpoint: `GET /fdc/v1/foods/search` with pageSize=15
- Nutrient IDs: 1008=cal, 1003=protein, 1005=carbs, 1004=fat, 1079=fiber, 2000=sugar
- dataType filter: Survey (FNDDS), Branded, Foundation, SR Legacy
- Results deduped by name, sorted: generic first then branded
- Return on first result with calories > 0

**Open Food Facts:**
- GET `/api/v2/product/{barcode}.json`
- Nutrient keys: `energy-kcal_100g`, `proteins_100g`, `carbohydrates_100g`, `fat_100g`
- May have incomplete data (check for null/0 values)

## Code Modification Patterns

**Adding new food categories:**
1. `detect_food_category()`: Add keywords to categories dict
2. `get_serving_conversion()`: Define unit, grams_per_unit, label
3. Portion UI defaults: Add to if/elif chain (default_amount, max_amount, step)
4. Quick size buttons: Add to category-specific button section in all 3 modes
5. Test multiplier calculation matches expected grams

**Adding new exercises:**
1. Add to `EXERCISE_DATABASE` in appropriate category with name, MET, icon
2. For strength: add description and ROM value to `EXERCISE_ROM` dict
3. Test both simple (MET) and detailed (volume) calorie calculations

**Adding new tabs:**
1. Create `tabs/tab_newtab.py` with `render(app)` function
2. Import in `app.py` and add to tab list
3. Use `app` parameter to access shared utilities

## Testing Strategy

**Test Barcodes (known to work):**
- `0044000032319` - Nabisco Triscuit crackers (EAN13)
- Use any packaged food with clear horizontal barcode
- Check terminal for `[Barcode]` debug output

**Test Food Search:**
- Popular food buttons should trigger immediate search
- Recent searches should persist within session
- Filter/sort should work without re-fetching
- Works immediately after page refresh (no delay needed)

**Test Images (realistic scenarios):**
- Single clear items: burger on plate, pizza slice, cookie close-up
- Multi-item meals: burger + fries combo, breakfast plate (eggs/bacon/toast)
- Edge cases: mixed salad, stir-fry (complex/overlapping items)
- Barcode photos: straight-on, well-lit, horizontal orientation

**Expected behaviors:**
- Single item → dropdown selector (default mode)
- Multi-item → "8 items detected" with optional checkbox to combine
- Unrecognized → fallback UI with 100g explanation + presets
- Barcode → auto-scan on upload, nutrition displayed immediately
- Search → type + Enter or click Search button, results in expander cards

## Data Migration & Backward Compatibility

**Meal data structure evolution:**
```python
# Old format (single food):
meal = {
    'food_name': 'Hamburger',
    'nutrition': {calories: 250, ...},
    'multiplier': 1.5
}

# New format (supports multi-item):
meal = {
    'food_name': 'Hamburger + French fries',  # Combined name
    'nutrition': {calories: 750, ...},        # Combined totals
    'multiplier': 1.0,                        # Already calculated
    'components': [                           # NEW - optional field
        {
            'name': 'Hamburger',
            'portion': '1.0 burgers',
            'multiplier': 2.15,
            'nutrition': {...},
            'source': 'USDA'
        },
        {...}
    ]
}
```

**When reading meals:**
- Check `if 'components' in meal` before accessing
- Old meals without 'components' still work (display as single item)
- Old meals without 'id' use `.get('id', fallback)` 
- Old meals without 'fiber'/'sugar' use `.get('fiber', 0)`
- Don't require migration - graceful degradation

## Debugging Workflow

**When user reports errors:**
1. **Ask for full error message** from terminal (not just Streamlit UI)
2. **Paste error into AI assistant** with context about what they were doing
3. **Common error patterns:**
   - `IndentationError` → Check recent edits for mixed tabs/spaces
   - `KeyError` → Missing session state initialization or old data format
   - `StreamlitMixedNumericTypesError` → Type mismatch in number_input
   - `Vision API error` → Check credentials path and API enabled
   - `NameError: name 'X' is not defined` → Variable used before definition in recent changes
   - `StreamlitAPIException` → Widget key conflict (quick button after number_input)

**Quick fixes:**
- Clear session state: Refresh browser with Ctrl+F5
- Reset data: Delete files in `data/` directory
- API issues: Check terminal for `[USDA]`, `[Barcode]`, `[Object Detected]`, `[USDA Search]` logs
- UI broken: Check for unclosed `with` blocks or missing containers
- Streamlit Cloud not updating: "Manage app" → "Reboot app" + Ctrl+Shift+R
