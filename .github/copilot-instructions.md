# AI Agent Instructions for Food Calorie Analyzer

## Project Overview
Streamlit nutrition tracking app with AI-powered food image analysis. Uses Google Cloud Vision API (with Object Localization), USDA FoodData Central API, Open Food Facts (barcode), and Hugging Face classifiers. Single-file monolith (~2200 lines) with JSON-based local persistence and 6-tab interface for meal tracking, goals, progress, and history.

## Architecture & Data Flow
```
Image Upload → Vision API (labels + object localization) + HF classifier
           → analyze_food_image() combines predictions (up to 10 items)
           → User selects: single-item mode OR multi-item meal mode (checkbox)
           → get_nutrition_estimate() → USDA API (3 results) → fallback to local DB
           → detect_food_category() → smart serving UI (15 categories)
           → calculate_multiplier() converts to 100g base
           → Save to meals.json with meal_type, components, combined nutrition
```

**Key architectural decisions:**
- Single file for simplicity - all logic in `app.py`
- JSON file persistence (no database) - `data/{meals,goals,weight,water}.json`
- USDA per-100g standard requires multiplier system for user servings
- Optional multi-item mode: users can select multiple foods via checkbox → combine nutrition

## Critical Developer Workflows

### Running & Testing
```bash
python -m streamlit run app.py  # NOT 'streamlit run' - module form required
# Access at http://localhost:8501 or network IP (e.g., http://10.0.0.246:8501)
# Auto-reloads on file save
```

**Debug patterns:**
- Terminal logs show `[USDA]`, `[Object Detected]`, `[Barcode]` prefixes
- Vision API errors visible in Streamlit UI exception boxes
- Check `data/` directory for JSON structure issues

### Environment Setup
```
.env file (required):
  GOOGLE_APPLICATION_CREDENTIALS=E:\3rd qart\vision-key.json
  USDA_API_KEY=<real_key_not_DEMO_KEY>

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

### Multi-Item Meal Mode (New Feature)
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

# Philosophy: Let unrecognized specific items (Big Mac, Oreo) fall back to 
# the improved generic UI that educates users about 100g calculations
```

**Why this matters:**
- Users will upload thousands of different food brands globally
- The fallback UI (with presets: 100g/200g/300g/500g) is now excellent
- Generic categories remain maintainable and predictable
- Edge cases teach users the system rather than create false expectations

### Barcode Scanning Integration
```python
# Mode toggle: "🍕 Food Photo" vs "📷 Product Barcode"
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
```

### Data Persistence Pattern
```python
# Load: load_json(file_path, default=[]) → returns list/dict
# Save: save_json(file_path, data) → writes atomically
# Meals grouped by date: {date: {meal_type: [meal_objects]}}
# Components stored for multi-item meals: meal['components'] = [{name, portion, multiplier, nutrition}]
```

## Critical Files Structure
```
app.py (2200 lines):
  Lines 1-185: Imports, config, CSS, manifest
  Lines 187-305: Data persistence (JSON CRUD)
  Lines 308-385: Barcode scanning (pyzbar + Open Food Facts)
  Lines 389-435: Food name cleaning utilities
  Lines 437-505: Category detection & serving conversions
  Lines 507-645: USDA API + nutrition estimation
  Lines 650-730: Vision API integration (labels + object localization)
  Lines 747-1500: Tab 1 - Analyze Food (dual mode: photo/barcode)
  Lines 1502-2200: Tabs 2-6 (Daily Summary, Goals, History, Progress, Quick Add)

data/
  meals.json: {date: {meal_type: [meals]}}
  goals.json: {calories, protein, carbs, fat}
  weight.json: [{date, weight}]
  water.json: {date: glasses}
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

### Combine Mode Display Logic
```python
# Single item: Direct UI (no expanders)
# Multi-item: Expandable sections per food + combined total card
# Combined card: Purple gradient, large calories, ingredient list
```

### Info Expanders for Education
- "ℹ️ How are calories calculated?" - explains USDA 100g base
- "🔍 Debug: What was searched?" - shows USDA search terms
- Only shown in single-item mode to avoid clutter

## External API Patterns

**Google Vision API:**
- `label_detection()`: confidence >0.6
- `object_localization()`: confidence >0.5 (NEW - better multi-item detection)
- Free tier: 1000 images/month, then $1.50/1000

**USDA FoodData Central:**
- Search endpoint: try top 3 results per search term
- Nutrient IDs (not names): 1008=cal, 1003=protein, 1005=carbs, 1004=fat
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
4. Test multiplier calculation matches expected grams

**Improving fallback UI for unrecognized foods:**
- Update generic portion presets (currently: 100/200/300/500g)
- Modify educational text explaining 100g standard
- Adjust default multiplier (currently 2.0× = 200g)
- Add more real-world examples in markdown guide

## Testing Strategy

**Test Barcodes (known to work):**
- `0044000032319` - Nabisco Triscuit crackers (EAN13)
- Use any packaged food with clear horizontal barcode
- Check terminal for `[Barcode]` debug output

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
- Don't require migration - graceful degradation

## Debugging Workflow

**When user reports errors:**
1. **Ask for full error message** from terminal (not just Streamlit UI)
2. **Paste error into AI assistant** with context about what they were doing
3. **Common error patterns:**
   - `IndentationError` → Check recent edits for mixed tabs/spaces
   - `KeyError` → Missing session state initialization
   - `StreamlitMixedNumericTypesError` → Type mismatch in number_input
   - `Vision API error` → Check credentials path and API enabled
   - `NameError: name 'X' is not defined` → Variable used before definition in recent changes

**Quick fixes:**
- Clear session state: Refresh browser with Ctrl+F5
- Reset data: Delete files in `data/` directory
- API issues: Check terminal for `[USDA]`, `[Barcode]`, `[Object Detected]` logs
- UI broken: Check for unclosed `with` blocks or missing containers
