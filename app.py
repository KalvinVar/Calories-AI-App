import streamlit as st
from google.cloud import vision
from PIL import Image
import io
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime, date, timedelta
import base64
from pathlib import Path
import pandas as pd
from pyzbar.pyzbar import decode as decode_barcode

# Load environment variables
load_dotenv()

# Data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MEALS_FILE = DATA_DIR / "meals.json"
GOALS_FILE = DATA_DIR / "goals.json"
WEIGHT_FILE = DATA_DIR / "weight.json"
WATER_FILE = DATA_DIR / "water.json"
IMAGES_DIR = DATA_DIR / "meal_images"
IMAGES_DIR.mkdir(exist_ok=True)

# Page config
st.set_page_config(
    page_title="Food Calorie Analyzer",
    page_icon="🍽️",
    layout="centered"
)

# PWA Setup with embedded manifest
st.markdown("""
    <meta name="theme-color" content="#FF6B6B">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="CalorieApp">
    <meta name="description" content="Analyze food calories and nutrition from photos using AI">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogIkZvb2QgQ2Fsb3JpZSBBbmFseXplciIsCiAgInNob3J0X25hbWUiOiAiQ2Fsb3JpZUFwcCIsCiAgImRlc2NyaXB0aW9uIjogIkFuYWx5emUgZm9vZCBjYWxvcmllcyBhbmQgbnV0cml0aW9uIGZyb20gcGhvdG9zIHVzaW5nIEFJIiwKICAic3RhcnRfdXJsIjogIi8iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiNmZmZmZmYiLAogICJ0aGVtZV9jb2xvciI6ICIjRkY2QjZCIiwKICAib3JpZW50YXRpb24iOiAicG9ydHJhaXQiLAogICJpY29ucyI6IFsKICAgIHsKICAgICAgInNyYyI6ICJkYXRhOmltYWdlL3N2Zyt4bWwsPHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAxMDAgMTAwJz48dGV4dCB5PSc3NScgZm9udC1zaXplPSc3NSc+8J+NvO+4jzwvdGV4dD48L3N2Zz4iLAogICAgICAic2l6ZXMiOiAiMTkyeDE5MiIsCiAgICAgICJ0eXBlIjogImltYWdlL3N2Zyt4bWwiLAogICAgICAicHVycG9zZSI6ICJhbnkgbWFza2FibGUiCiAgICB9LAogICAgewogICAgICAic3JjIjogImRhdGE6aW1hZ2Uvc3ZnK3htbCw8c3ZnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zycgdmlld0JveD0nMCAwIDEwMCAxMDAnPjx0ZXh0IHk9Jzc1JyBmb250LXNpemU9Jzc1Jz7wn42877iPPC90ZXh0Pjwvc3ZnPiIsCiAgICAgICJzaXplcyI6ICI1MTJ4NTEyIiwKICAgICAgInR5cGUiOiAiaW1hZ2Uvc3ZnK3htbCIsCiAgICAgICJwdXJwb3NlIjogImFueSBtYXNrYWJsZSIKICAgIH0KICBdCn0=">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75'>🍽️</text></svg>">
    """, unsafe_allow_html=True)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main title styling */
    h1 {
        color: #FF6B6B;
        text-align: center;
        padding: 1rem 0;
        font-size: 2.5rem !important;
    }
    
    /* Subtitle styling */
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers */
    .stAlert {
        border-radius: 10px;
        border-left: 5px solid;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: bold;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border: 2px dashed #FF6B6B;
        border-radius: 10px;
        padding: 2rem;
        background: linear-gradient(135deg, #FFF5F5 0%, #FFE3E3 100%);
    }
    
    /* File uploader uploaded file text - dark background for readability */
    [data-testid="stFileUploader"] section[data-testid="stFileUploaderFileData"] {
        background-color: #4A4A4A !important;
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    /* File name text styling */
    [data-testid="stFileUploader"] section[data-testid="stFileUploaderFileData"] * {
        color: #FFFFFF !important;
    }
    
    /* Delete button in file uploader */
    [data-testid="stFileUploader"] button[kind="icon"] {
        color: #FF6B6B !important;
    }
    
    /* Additional selectors for uploaded file display */
    [data-testid="stFileUploader"] section {
        background-color: #4A4A4A !important;
    }
    
    /* Target the uploaded file container */
    .stFileUploaderFile {
        background-color: #4A4A4A !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
    }
    
    /* File name and size text */
    .stFileUploaderFileName,
    .stFileUploaderFileData,
    .stFileUploaderFileData small {
        color: #FFFFFF !important;
    }
    
    /* File icon color */
    .stFileUploaderFile svg {
        color: #FFFFFF !important;
    }
    
    /* Make sure the dropzone area stays light */
    [data-testid="stFileUploaderDropzone"] {
        background: transparent !important;
    }
    
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] div {
        color: #666 !important;
    }
    
    /* Divider styling */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(to right, transparent, #FF6B6B, transparent);
    }
    
    /* Success/Info boxes */
    .element-container:has(> .stSuccess) {
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Number input styling */
    .stNumberInput input {
        font-size: 1.2rem;
        font-weight: 600;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# DATA PERSISTENCE FUNCTIONS
# =============================================================================

def load_json(file_path, default=None):
    """Load JSON data from file"""
    if default is None:
        default = []
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file_path, data):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_meals(date_str=None):
    """Load meals for a specific date or all meals"""
    meals = load_json(MEALS_FILE, {})
    if date_str:
        return meals.get(date_str, [])
    return meals

def save_meal(meal_data, meal_date=None):
    """Save a meal entry"""
    if meal_date is None:
        meal_date = str(date.today())
    
    meals = load_meals()
    if meal_date not in meals:
        meals[meal_date] = []
    
    meal_data['timestamp'] = datetime.now().isoformat()
    meals[meal_date].append(meal_data)
    save_json(MEALS_FILE, meals)

def load_goals():
    """Load user goals"""
    default_goals = {
        'calories': 2000,
        'protein': 150,
        'carbs': 250,
        'fat': 65,
        'water_glasses': 8
    }
    return load_json(GOALS_FILE, default_goals)

def save_goals(goals):
    """Save user goals"""
    save_json(GOALS_FILE, goals)

def load_weight_log():
    """Load weight tracking log"""
    return load_json(WEIGHT_FILE, [])

def save_weight_entry(weight, log_date=None):
    """Save a weight entry"""
    if log_date is None:
        log_date = str(date.today())
    
    weight_log = load_weight_log()
    # Remove existing entry for same date
    weight_log = [w for w in weight_log if w['date'] != log_date]
    # Add new entry
    weight_log.append({'date': log_date, 'weight': weight})
    # Sort by date
    weight_log.sort(key=lambda x: x['date'])
    save_json(WEIGHT_FILE, weight_log)

def load_water_log():
    """Load water intake log"""
    return load_json(WATER_FILE, {})

def save_water_intake(glasses, log_date=None):
    """Save water intake for a date"""
    if log_date is None:
        log_date = str(date.today())
    
    water_log = load_water_log()
    water_log[log_date] = glasses
    save_json(WATER_FILE, water_log)

def get_daily_totals(date_str):
    """Calculate total nutrition for a specific date"""
    meals = load_meals(date_str)
    totals = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0
    }
    
    for meal in meals:
        nutrition = meal.get('nutrition', {})
        multiplier = meal.get('multiplier', 1.0)
        
        for key in totals:
            totals[key] += nutrition.get(key, 0) * multiplier
    
    return totals

def save_meal_image(image_file, meal_id):
    """Save meal image to disk and return path"""
    image_path = IMAGES_DIR / f"{meal_id}.jpg"
    
    # Reset file pointer
    image_file.seek(0)
    img = Image.open(image_file)
    
    # Resize to save space (max 800px wide)
    max_size = (800, 800)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save as JPEG
    img.save(image_path, "JPEG", quality=85)
    
    return str(image_path)

def scan_barcode_from_image(image_file):
    """Scan barcode from uploaded image"""
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        
        # Decode barcodes
        barcodes = decode_barcode(img)
        
        if barcodes:
            # Return first barcode found
            barcode_data = barcodes[0].data.decode('utf-8')
            barcode_type = barcodes[0].type
            return barcode_data, barcode_type
        
        return None, None
    except Exception as e:
        print(f"Barcode scan error: {e}")
        return None, None

def get_product_from_barcode(barcode):
    """Get product info from Open Food Facts API"""
    try:
        url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 1:
                product = data.get('product', {})
                
                # Extract nutrition data (per 100g)
                nutriments = product.get('nutriments', {})
                
                nutrition_data = {
                    'calories': int(nutriments.get('energy-kcal_100g', 0)),
                    'protein': round(nutriments.get('proteins_100g', 0), 1),
                    'carbs': round(nutriments.get('carbohydrates_100g', 0), 1),
                    'fat': round(nutriments.get('fat_100g', 0), 1),
                    'fiber': round(nutriments.get('fiber_100g', 0), 1),
                    'sugar': round(nutriments.get('sugars_100g', 0), 1),
                    'serving': '100g',
                    'source': 'Open Food Facts',
                    'product_name': product.get('product_name', 'Unknown Product'),
                    'brands': product.get('brands', 'Unknown Brand'),
                    'image_url': product.get('image_url', '')
                }
                
                return nutrition_data
        
        return None
    except Exception as e:
        print(f"Open Food Facts API error: {e}")
        return None

# USDA API configuration
USDA_API_KEY = os.getenv("USDA_API_KEY", "DEMO_KEY")  # Free API, no key required with rate limits
USDA_SEARCH_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Hugging Face Food Classifier
HF_FOOD_API = "https://api-inference.huggingface.co/models/nateraw/food"

# Nutrition database - common foods (fallback)
NUTRITION_DB = {
    "pizza": {"calories": 266, "protein": 11, "carbs": 33, "fat": 10, "fiber": 2, "sugar": 4, "serving": "1 slice (100g)"},
    "burger": {"calories": 295, "protein": 17, "carbs": 28, "fat": 13, "fiber": 1, "sugar": 6, "serving": "1 burger (150g)"},
    "hamburger": {"calories": 295, "protein": 17, "carbs": 28, "fat": 13, "fiber": 1, "sugar": 6, "serving": "1 burger (150g)"},
    "cheeseburger": {"calories": 330, "protein": 19, "carbs": 29, "fat": 16, "fiber": 1, "sugar": 6, "serving": "1 burger (160g)"},
    "salad": {"calories": 150, "protein": 3, "carbs": 12, "fat": 10, "fiber": 4, "sugar": 5, "serving": "1 bowl (200g)"},
    "pasta": {"calories": 220, "protein": 8, "carbs": 43, "fat": 1, "fiber": 3, "sugar": 2, "serving": "1 cup (140g)"},
    "rice": {"calories": 205, "protein": 4, "carbs": 45, "fat": 0, "fiber": 1, "sugar": 0, "serving": "1 cup (158g)"},
    "chicken": {"calories": 165, "protein": 31, "carbs": 0, "fat": 4, "fiber": 0, "sugar": 0, "serving": "100g"},
    "sandwich": {"calories": 250, "protein": 12, "carbs": 35, "fat": 8, "fiber": 3, "sugar": 4, "serving": "1 sandwich"},
    "fruit": {"calories": 52, "protein": 1, "carbs": 14, "fat": 0, "fiber": 2, "sugar": 10, "serving": "1 medium piece"},
    "fries": {"calories": 312, "protein": 4, "carbs": 41, "fat": 15, "fiber": 4, "sugar": 0, "serving": "1 serving (100g)"},
    "sushi": {"calories": 145, "protein": 6, "carbs": 24, "fat": 3, "fiber": 1, "sugar": 4, "serving": "6 pieces"},
    "taco": {"calories": 226, "protein": 9, "carbs": 21, "fat": 13, "fiber": 3, "sugar": 1, "serving": "1 taco"},
    "soup": {"calories": 120, "protein": 6, "carbs": 15, "fat": 4, "fiber": 2, "sugar": 3, "serving": "1 cup (240ml)"},
}

def clean_food_name(food_name):
    """Clean and generate smart search terms from detected food name"""
    # Generic words to remove
    generic_words = ['food', 'dish', 'cuisine', 'meal', 'ingredient', 'recipe', 'plate']
    
    food_lower = food_name.lower()
    
    # Remove generic words
    for word in generic_words:
        food_lower = food_lower.replace(word, '').strip()
    
    # Remove common adjectives
    adjectives = ['fresh', 'raw', 'cooked', 'grilled', 'fried', 'baked', 'steamed', 'organic']
    for adj in adjectives:
        food_lower = food_lower.replace(adj, '').strip()
    
    # Clean up extra spaces
    food_lower = ' '.join(food_lower.split())
    
    return food_lower if food_lower else food_name

def get_category_terms(food_name, alternatives):
    """Generate category-based search terms from detected items"""
    category_map = {
        'snickers': ['chocolate bar', 'candy bar'],
        'chocolate': ['chocolate bar', 'candy'],
        'candy': ['candy bar', 'chocolate'],
    }
    
    terms = []
    food_lower = food_name.lower()
    
    # Check if we have category mapping
    for key, categories in category_map.items():
        if key in food_lower:
            terms.extend(categories)
    
    # Use alternatives as category hints
    for alt in alternatives:
        alt_lower = alt.lower()
        if 'bar' in alt_lower or 'chocolate' in alt_lower or 'candy' in alt_lower:
            if 'chocolate' in alt_lower:
                terms.append('chocolate bar')
            if 'candy' in alt_lower:
                terms.append('candy bar')
    
    return list(set(terms))  # Remove duplicates

def detect_food_category(food_name):
    """Detect the category of food to show appropriate serving size input"""
    food_lower = food_name.lower()
    
    # Define categories with their keywords (order matters - check more specific first)
    categories = {
        'cookies': ['cookie', 'oreo', 'biscuit', 'macaroon', 'wafer', 'sandwich cookie'],
        'pizza': ['pizza', 'flatbread'],
        'meat': ['steak', 'beef', 'pork', 'lamb', 'chicken breast', 'fish fillet', 'salmon', 'tuna'],
        'rice': ['rice', 'fried rice', 'rice bowl'],
        'bread': ['bread', 'toast', 'baguette', 'roll'],
        'candy': ['candy bar', 'chocolate bar', 'snickers', 'kitkat', 'mars', 'twix'],
        'burger': ['burger', 'hamburger', 'cheeseburger'],
        'fries': ['fries', 'french fries', 'chips'],
        'soup': ['soup', 'broth', 'stew', 'chowder'],
        'beverage': ['juice', 'soda', 'cola', 'drink', 'smoothie', 'shake', 'milk', 'coffee', 'tea'],
        'snacks': ['chips', 'crisps', 'popcorn', 'pretzels', 'crackers'],
        'fruit': ['apple', 'banana', 'orange', 'pear', 'peach', 'plum', 'fruit'],
        'salad': ['salad', 'coleslaw'],
        'pasta': ['pasta', 'spaghetti', 'noodles', 'macaroni', 'linguine'],
        'vegetables': ['broccoli', 'carrots', 'beans', 'peas', 'corn', 'vegetable'],
    }
    
    # Check for matches
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in food_lower:
                return category
    
    return 'other'  # Default fallback

def get_serving_conversion(category):
    """Get serving size conversion info for a food category"""
    # Approximate conversions to 100g (USDA standard)
    conversions = {
        'cookies': {'unit': 'cookies', 'grams_per_unit': 12, 'label': 'Number of cookies'},  # Standard Oreo ~11g
        'pizza': {'unit': 'slices', 'grams_per_unit': 120, 'label': 'Number of slices'},
        'meat': {'unit': 'grams', 'grams_per_unit': 1, 'label': 'Weight in grams'},
        'rice': {'unit': 'cups', 'grams_per_unit': 158, 'label': 'Cups of cooked rice'},
        'bread': {'unit': 'slices', 'grams_per_unit': 30, 'label': 'Number of slices'},
        'candy': {'unit': 'bars', 'grams_per_unit': 50, 'label': 'Number of bars/pieces'},
        'burger': {'unit': 'burgers', 'grams_per_unit': 215, 'label': 'Number of burgers (avg 215g each)'},
        'fries': {'unit': 'servings', 'grams_per_unit': 100, 'label': 'Servings (small/medium/large)'},
        'soup': {'unit': 'cups', 'grams_per_unit': 240, 'label': 'Cups (240ml each)'},
        'beverage': {'unit': 'ml', 'grams_per_unit': 1, 'label': 'Volume in mL'},
        'snacks': {'unit': 'servings', 'grams_per_unit': 28, 'label': 'Servings (about 1 oz)'},
        'fruit': {'unit': 'pieces', 'grams_per_unit': 150, 'label': 'Number of pieces'},
        'salad': {'unit': 'bowls', 'grams_per_unit': 200, 'label': 'Number of bowls'},
        'pasta': {'unit': 'cups', 'grams_per_unit': 140, 'label': 'Cups of cooked pasta'},
        'vegetables': {'unit': 'cups', 'grams_per_unit': 150, 'label': 'Cups of vegetables'},
        'other': {'unit': 'multiplier', 'grams_per_unit': 100, 'label': 'Portion multiplier'},
    }
    
    return conversions.get(category, conversions['other'])

def calculate_multiplier(category, amount):
    """Calculate multiplier from serving amount and category"""
    conversion = get_serving_conversion(category)
    
    if category == 'other':
        return amount  # Already a multiplier
    
    # Calculate grams from servings
    total_grams = amount * conversion['grams_per_unit']
    
    # Convert to multiplier (USDA data is per 100g)
    multiplier = total_grams / 100.0
    
    return multiplier

def get_usda_nutrition(food_name):
    """Fetch nutrition data from USDA FoodData Central API"""
    # Generate smart search terms
    search_terms = []
    
    # Original name
    search_terms.append(food_name)
    
    # Cleaned name
    cleaned = clean_food_name(food_name)
    if cleaned != food_name.lower() and cleaned:
        search_terms.append(cleaned)
    
    # Try singular/plural variations
    if cleaned.endswith('s'):
        search_terms.append(cleaned[:-1])
    else:
        search_terms.append(cleaned + 's')
    
    for search_term in search_terms:
        try:
            params = {
                "api_key": USDA_API_KEY,
                "query": search_term,
                "pageSize": 3  # Try top 3 results
            }
            
            response = requests.get(USDA_SEARCH_URL, params=params, timeout=5)
            
            if response.status_code == 429:
                print(f"[USDA] Rate limit hit for '{search_term}'")
                continue
            elif response.status_code != 200:
                print(f"[USDA] Error {response.status_code} for '{search_term}'")
                continue
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('foods') and len(data['foods']) > 0:
                    # Try each result until we find one with nutrition data
                    for idx, food in enumerate(data['foods'][:3]):
                        food_nutrients = food.get('foodNutrients', [])
                        
                        # Debug logging - what USDA found
                        print(f"[USDA] Search: '{search_term}' → {food.get('description', 'N/A')[:60]} ({food.get('dataType', 'N/A')}) - {len(food_nutrients)} nutrients")
                        
                        # Build nutrient lookup by ID (more reliable than names)
                        nutrients = {}
                        for n in food_nutrients:
                            nutrient_id = n.get('nutrientId')
                            nutrient_name = n.get('nutrientName', '')
                            nutrient_number = n.get('nutrientNumber', '')
                            value = n.get('value', 0)
                            
                            # Map by common nutrient IDs and numbers
                            if nutrient_id == 1008 or nutrient_number == '208' or 'Energy' in nutrient_name or 'Calories' in nutrient_name:
                                nutrients['calories'] = value
                            elif nutrient_id == 1003 or nutrient_number == '203' or 'Protein' in nutrient_name:
                                nutrients['protein'] = value
                            elif nutrient_id == 1005 or nutrient_number == '205' or 'Carbohydrate' in nutrient_name:
                                nutrients['carbs'] = value
                            elif nutrient_id == 1004 or nutrient_number == '204' or 'Total lipid' in nutrient_name or nutrient_name == 'Fat':
                                nutrients['fat'] = value
                            elif nutrient_id == 1079 or nutrient_number == '291' or 'Fiber' in nutrient_name:
                                nutrients['fiber'] = value
                            elif nutrient_id == 2000 or nutrient_number == '269' or 'Sugars, total' in nutrient_name or 'Total Sugars' in nutrient_name:
                                nutrients['sugar'] = value
                        
                        # If we got at least calories, return the data
                        if nutrients.get('calories', 0) > 0:
                            result = {
                                "calories": int(nutrients.get('calories', 200)),
                                "protein": round(nutrients.get('protein', 0), 1),
                                "carbs": round(nutrients.get('carbs', 0), 1),
                                "fat": round(nutrients.get('fat', 0), 1),
                                "fiber": round(nutrients.get('fiber', 0), 1),
                                "sugar": round(nutrients.get('sugar', 0), 1),
                                "serving": "100g (USDA data)",
                                "source": "USDA",
                                "usda_match": food.get('description', search_term)
                            }
                            return result
        except Exception as e:
            print(f"USDA API error for '{search_term}': {e}")
            continue
    
    return None

def get_nutrition_estimate(food_name, alternative_names=[]):
    """Get nutrition estimate from USDA API first, then fallback to local database"""
    # Build list of search terms to try
    search_terms = [food_name] + alternative_names
    
    # Add category-based terms
    category_terms = get_category_terms(food_name, alternative_names)
    search_terms.extend(category_terms)
    
    # Try USDA API for each term
    for term in search_terms:
        usda_data = get_usda_nutrition(term)
        if usda_data:
            return usda_data
    
    # Fallback to local database
    food_lower = food_name.lower()
    for key in NUTRITION_DB:
        if key in food_lower or food_lower in key:
            result = NUTRITION_DB[key].copy()
            result["source"] = "Estimate"
            return result
    
    # Check alternatives in local database
    for alt_name in alternative_names:
        alt_lower = alt_name.lower()
        for key in NUTRITION_DB:
            if key in alt_lower or alt_lower in key:
                result = NUTRITION_DB[key].copy()
                result["source"] = "Estimate"
                return result
    
    # Default values if not found
    return {
        "calories": 200, "protein": 8, "carbs": 25, "fat": 8, 
        "fiber": 2, "sugar": 4, "serving": "1 portion (estimated)",
        "source": "Estimate"
    }

def classify_food_with_ai(image_bytes):
    """Use specialized food classifier for more accurate food identification"""
    try:
        response = requests.post(HF_FOOD_API, data=image_bytes, timeout=10)
        
        if response.status_code == 200:
            predictions = response.json()
            if predictions and len(predictions) > 0:
                # Return top 3 predictions
                return [p['label'].replace('_', ' ') for p in predictions[:3]]
    except Exception as e:
        print(f"Food classifier error: {e}")
    
    return []

def analyze_food_image(image_file):
    """Send image to Google Cloud Vision API and get nutrition analysis"""
    
    try:
        # Initialize Google Cloud Vision client
        client = vision.ImageAnnotatorClient()
        
        # Reset file pointer and read image
        image_file.seek(0)
        content = image_file.read()
        
        # Try specialized food classifier first
        ai_predictions = classify_food_with_ai(content)
        
        image = vision.Image(content=content)
        
        # Detect labels (objects/food items)
        response = client.label_detection(image=image)
        labels = response.label_annotations
        
        # NEW: Detect objects with localization for better multi-item detection
        objects_response = client.object_localization(image=image)
        objects = objects_response.localized_object_annotations
        
        # Detect web entities for more context
        web_response = client.web_detection(image=image)
        web_entities = web_response.web_detection.web_entities
        
        if response.error.message:
            raise Exception(response.error.message)
        
        # Combine all detection sources, prioritizing AI food classifier
        food_items = []
        
        # Add AI predictions first (most accurate for food)
        food_items.extend(ai_predictions)
        
        # NEW: Add localized objects (great for multi-food detection)
        for obj in objects:
            if obj.score > 0.5:  # Decent confidence for objects
                obj_name = obj.name
                if obj_name not in food_items:
                    food_items.append(obj_name)
                    print(f"[Object Detected] {obj_name} (confidence: {obj.score:.2f})")
        
        # Add Vision API labels
        for label in labels[:5]:
            if label.score > 0.6:  # Slightly lower threshold to catch more items
                if label.description not in food_items:
                    food_items.append(label.description)
        
        # Add web entities
        for entity in web_entities[:3]:
            if entity.score > 0.5:
                if entity.description not in food_items:
                    food_items.append(entity.description)
        
        # Filter out generic terms for primary food selection
        generic_terms = ['food', 'dish', 'cuisine', 'meal', 'ingredient', 'recipe', 'plate', 'tableware']
        specific_foods = [item for item in food_items if item.lower() not in generic_terms]
        
        # Primary food identified - use specific food if available, fallback to first item
        primary_food = specific_foods[0] if specific_foods else (food_items[0] if food_items else "Unknown food")
        
        # Keep MORE alternatives for multi-food detection (up to 10 items)
        alternative_names = food_items[1:10] if len(food_items) > 1 else []
        
        # Get nutrition data (try primary and alternatives)
        nutrition = get_nutrition_estimate(primary_food, alternative_names)
        
        # Format response (stored in session state for portion adjustment)
        result = {
            "food_name": primary_food,
            "other_items": alternative_names,  # Now contains up to 10 items
            "nutrition": nutrition,
            "confidence": "High" if labels and labels[0].score > 0.85 else "Medium" if labels else "Low"
        }
        
        return result
    
    except Exception as e:
        return f"""**Error analyzing image:** {str(e)}

**Troubleshooting:**
- Make sure you've set up Google Cloud credentials correctly
- Check that the Vision API is enabled in your Google Cloud Console
- Verify your GOOGLE_APPLICATION_CREDENTIALS path is correct
- Ensure the image is clear and shows food items"""

# Initialize session state
if 'analysis' not in st.session_state:
    st.session_state['analysis'] = None
if 'error' not in st.session_state:
    st.session_state['error'] = None
if 'current_date' not in st.session_state:
    st.session_state['current_date'] = str(date.today())

# App UI
st.title("🍽️ Food Calorie Analyzer")
st.markdown('<p class="subtitle">📸 Track your nutrition with AI-powered food analysis!</p>', unsafe_allow_html=True)

# Create tabs for different features
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📸 Analyze Food", 
    "📊 Daily Summary", 
    "🎯 Goals", 
    "📅 History",
    "📈 Progress",
    "⚙️ Quick Add"
])

# ==================== TAB 1: ANALYZE FOOD ====================
with tab1:
    # Mode selector
    scan_mode = st.radio(
        "What do you want to scan?",
        ["🍕 Food Photo", "📷 Product Barcode"],
        horizontal=True
    )
    
    st.divider()
    
    if scan_mode == "🍕 Food Photo":
        st.markdown("### 📤 Upload Your Food Image")
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type=["jpg", "jpeg", "png"],
            help="Supported formats: JPG, JPEG, PNG | Max size: 200MB",
            label_visibility="collapsed",
            key="food_upload"
        )
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
    # BARCODE SCANNING MODE - Auto-scan on upload
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Product Image")
        st.image(uploaded_file, use_container_width=True)
    
    with col2:
        st.subheader("Nutrition Analysis")
        
        # Auto-scan immediately on upload
        with st.spinner("Scanning barcode..."):
            barcode_data, barcode_type = scan_barcode_from_image(uploaded_file)
            
            if barcode_data:
                st.success(f"✅ Barcode detected: {barcode_data}")
                st.caption(f"Type: {barcode_type}")
                
                # Get product info
                with st.spinner("Looking up product..."):
                    product_info = get_product_from_barcode(barcode_data)
                    
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
                        food_category = detect_food_category(product_full_name)
                        
                        if food_category != 'other':
                            st.info(f"✨ Smart serving detected: {product_info['product_name']} ({food_category})")
                        else:
                            st.info("ℹ️ Using standard portion multiplier")
                        
                        # Get category-specific conversion
                        conversion = get_serving_conversion(food_category)
                        
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
                            bc_portion_multiplier = calculate_multiplier(food_category, serving_amount)
                            
                            # Show conversion info
                            total_grams = serving_amount * conversion['grams_per_unit']
                            st.caption(f"≈ {total_grams:.0f}g total ({serving_amount} {conversion['unit']} × {conversion['grams_per_unit']}g per {conversion['unit']})")
                            
                            # Display portion text for saving
                            portion_text = f"{serving_amount} {conversion['unit']}"
                        else:
                            # Fallback to multiplier for unrecognized products
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                if st.button("0.5x (Half)", width='stretch', key="bc_half"):
                                    st.session_state['bc_portion'] = 0.5
                            with col2:
                                if st.button("1x (Standard)", width='stretch', key="bc_1x"):
                                    st.session_state['bc_portion'] = 1.0
                            with col3:
                                if st.button("1.5x (Large)", width='stretch', key="bc_15x"):
                                    st.session_state['bc_portion'] = 1.5
                            with col4:
                                if st.button("2x (Double)", width='stretch', key="bc_2x"):
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
                                
                                save_meal(meal_data)
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
                        st.info("💡 Try searching manually in the 'Quick Add' tab.")
            else:
                st.error("❌ No barcode detected in image.")
                st.info("💡 Make sure the barcode is clear, well-lit, and the lines are horizontal.")

elif uploaded_file is not None and scan_mode == "🍕 Food Photo":
    # Display the image
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Your Food")
        try:
            image = Image.open(uploaded_file)
            st.image(image, width='stretch')
        except Exception as e:
            st.error(f"Error loading image: {e}")
            st.stop()
    
    with col2:
        st.subheader("Nutrition Analysis")
        
        # Analyze button
        if st.button("🔍 Analyze Nutrition", type="primary", width='stretch'):
            with st.spinner("Analyzing your food..."):
                # Reset file pointer before sending
                uploaded_file.seek(0)
                result = analyze_food_image(uploaded_file)
                
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
                    
                    # Create list with primary food + alternatives
                    all_detected_foods = [data['food_name']] + data['other_items']
                    
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
                                all_detected_foods.append(custom_food)
                                st.session_state['selected_items'][custom_food] = True
                                selected_foods.append(custom_food)
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
                                new_nutrition = get_nutrition_estimate(corrected_food, remaining_alternatives)
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
                        new_nutrition = get_nutrition_estimate(selected_food, remaining_alternatives)
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
                            new_nutrition = get_nutrition_estimate(corrected_food, [])
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
                    item_nutrition = get_nutrition_estimate(food_item, item_alternatives)
                    
                    # Detect category for smart serving
                    food_category = detect_food_category(food_item)
                    conversion = get_serving_conversion(food_category)
                    
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
                        portion_multiplier = calculate_multiplier(food_category, serving_amount)
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
                    image_path = save_meal_image(uploaded_file, meal_id)
                    
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
                    
                    save_meal(meal_data)
                    st.success(f"✅ Meal saved to {meal_type} log!")
                    st.balloons()
                    
                    # Clear selection for next meal
                    if 'selected_items' in st.session_state:
                        st.session_state['selected_items'] = {}
            
            st.divider()
            
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
    st.info("👆 Upload a food image above to get started!")
    
    # Example section with better design
    st.markdown("")
    st.markdown("")
    st.markdown("### 🎯 What Can You Analyze?")
    st.markdown("This app works great with all types of food! Here are some examples:")
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

# ==================== TAB 2: DAILY SUMMARY ====================
with tab2:
    st.markdown("## 📊 Today's Nutrition Summary")
    
    today = str(date.today())
    st.markdown(f"**{date.today().strftime('%A, %B %d, %Y')}**")
    
    # Get today's totals
    totals = get_daily_totals(today)
    goals = load_goals()
    
    # Progress display
    st.markdown("### 🎯 Daily Goals Progress")
    
    # Calories
    cal_progress = min(totals['calories'] / goals['calories'], 1.0) if goals['calories'] > 0 else 0
    st.markdown(f"**Calories:** {int(totals['calories'])} / {goals['calories']} kcal")
    st.progress(cal_progress)
    remaining_cal = goals['calories'] - totals['calories']
    if remaining_cal > 0:
        st.caption(f"✅ {int(remaining_cal)} kcal remaining")
    else:
        st.caption(f"⚠️ {int(-remaining_cal)} kcal over target")
    
    st.markdown("")
    
    # Macros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        protein_progress = min(totals['protein'] / goals['protein'], 1.0) if goals['protein'] > 0 else 0
        st.markdown(f"**💪 Protein**")
        st.metric("", f"{round(totals['protein'], 1)}g")
        st.progress(protein_progress)
        st.caption(f"Goal: {goals['protein']}g")
    
    with col2:
        carbs_progress = min(totals['carbs'] / goals['carbs'], 1.0) if goals['carbs'] > 0 else 0
        st.markdown(f"**🍞 Carbs**")
        st.metric("", f"{round(totals['carbs'], 1)}g")
        st.progress(carbs_progress)
        st.caption(f"Goal: {goals['carbs']}g")
    
    with col3:
        fat_progress = min(totals['fat'] / goals['fat'], 1.0) if goals['fat'] > 0 else 0
        st.markdown(f"**🥑 Fat**")
        st.metric("", f"{round(totals['fat'], 1)}g")
        st.progress(fat_progress)
        st.caption(f"Goal: {goals['fat']}g")
    
    st.divider()
    
    # Water intake
    st.markdown("### 💧 Water Intake")
    water_log = load_water_log()
    current_water = water_log.get(today, 0)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        water_glasses = st.number_input(
            f"Glasses today ({current_water}/{goals['water_glasses']})",
            min_value=0,
            max_value=20,
            value=current_water,
            step=1,
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("💾 Save", key="save_water"):
            save_water_intake(water_glasses, today)
            st.success("✅ Saved!")
    
    water_progress = min(water_glasses / goals['water_glasses'], 1.0) if goals['water_glasses'] > 0 else 0
    st.progress(water_progress)
    
    st.divider()
    
    # Today's meals
    st.markdown("### 🍽️ Today's Meals")
    
    meals_today = load_meals(today)
    
    if meals_today:
        for meal in meals_today:
            with st.expander(f"{meal['meal_type']} - {meal['food_name']}"):
                meal_col1, meal_col2 = st.columns([1, 2])
                
                with meal_col1:
                    # Display meal image if exists
                    if 'image_path' in meal and Path(meal['image_path']).exists():
                        st.image(meal['image_path'], use_container_width=True)
                
                with meal_col2:
                    nutrition = meal['nutrition']
                    multiplier = meal.get('multiplier', 1.0)
                    
                    st.markdown(f"**Portion:** {meal.get('portion_text', 'N/A')}")
                    st.markdown(f"**Calories:** {int(nutrition['calories'] * multiplier)} kcal")
                    st.markdown(f"**Protein:** {round(nutrition['protein'] * multiplier, 1)}g")
                    st.markdown(f"**Carbs:** {round(nutrition['carbs'] * multiplier, 1)}g")
                    st.markdown(f"**Fat:** {round(nutrition['fat'] * multiplier, 1)}g")
    else:
        st.info("No meals logged today. Add a meal from the 'Analyze Food' tab!")

# ==================== TAB 3: GOALS ====================
with tab3:
    st.markdown("## 🎯 Set Your Daily Goals")
    st.caption("Customize your daily nutrition targets")
    
    current_goals = load_goals()
    
    st.markdown("### Calorie Goal")
    calories_goal = st.number_input(
        "Daily calorie target (kcal)",
        min_value=1000,
        max_value=5000,
        value=current_goals['calories'],
        step=50
    )
    
    st.markdown("### Macronutrient Goals")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        protein_goal = st.number_input(
            "💪 Protein (g)",
            min_value=30,
            max_value=300,
            value=current_goals['protein'],
            step=5
        )
    
    with col2:
        carbs_goal = st.number_input(
            "🍞 Carbs (g)",
            min_value=50,
            max_value=500,
            value=current_goals['carbs'],
            step=10
        )
    
    with col3:
        fat_goal = st.number_input(
            "🥑 Fat (g)",
            min_value=20,
            max_value=200,
            value=current_goals['fat'],
            step=5
        )
    
    st.markdown("### Hydration Goal")
    water_goal = st.number_input(
        "💧 Water glasses per day",
        min_value=4,
        max_value=15,
        value=current_goals['water_glasses'],
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
        save_goals(new_goals)
        st.success("✅ Goals saved successfully!")
        st.balloons()

# ==================== TAB 4: HISTORY ====================
with tab4:
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
    meals_on_date = load_meals(date_str)
    
    if meals_on_date:
        # Show daily totals
        daily_totals = get_daily_totals(date_str)
        
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
                for meal in meal_list:
                    with st.container():
                        meal_col1, meal_col2 = st.columns([1, 3])
                        
                        with meal_col1:
                            if 'image_path' in meal and Path(meal['image_path']).exists():
                                st.image(meal['image_path'], use_container_width=True)
                        
                        with meal_col2:
                            st.markdown(f"**{meal['food_name']}**")
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
    else:
        st.info("No meals logged on this date.")
    
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
        all_meals = load_meals()
        export_data = []
        
        current = start_date
        while current <= end_date:
            date_str = str(current)
            if date_str in all_meals:
                for meal in all_meals[date_str]:
                    nutrition = meal['nutrition']
                    multiplier = meal.get('multiplier', 1.0)
                    
                    export_data.append({
                        'Date': date_str,
                        'Meal Type': meal.get('meal_type', 'N/A'),
                        'Food': meal['food_name'],
                        'Portion': meal.get('portion_text', 'N/A'),
                        'Calories': int(nutrition['calories'] * multiplier),
                        'Protein (g)': round(nutrition['protein'] * multiplier, 1),
                        'Carbs (g)': round(nutrition['carbs'] * multiplier, 1),
                        'Fat (g)': round(nutrition['fat'] * multiplier, 1),
                        'Fiber (g)': round(nutrition['fiber'] * multiplier, 1),
                        'Sugar (g)': round(nutrition['sugar'] * multiplier, 1)
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

# ==================== TAB 5: PROGRESS ====================
with tab5:
    st.markdown("## 📈 Weight & Progress Tracking")
    
    # Weight logging
    st.markdown("### ⚖️ Log Your Weight")
    
    weight_col1, weight_col2, weight_col3 = st.columns([2, 2, 1])
    
    with weight_col1:
        weight_value = st.number_input(
            "Weight (lbs)",
            min_value=50.0,
            max_value=500.0,
            value=150.0,
            step=0.1
        )
    
    with weight_col2:
        weight_date = st.date_input(
            "Date",
            value=date.today(),
            max_value=date.today(),
            key="weight_date"
        )
    
    with weight_col3:
        if st.button("💾 Log", key="save_weight"):
            save_weight_entry(weight_value, str(weight_date))
            st.success("✅ Logged!")
    
    st.divider()
    
    # Weight history chart
    st.markdown("### 📊 Weight History")
    
    weight_log = load_weight_log()
    
    if len(weight_log) > 0:
        df_weight = pd.DataFrame(weight_log)
        df_weight['date'] = pd.to_datetime(df_weight['date'])
        df_weight = df_weight.sort_values('date')
        
        st.line_chart(df_weight.set_index('date')['weight'])
        
        # Show recent entries
        st.markdown("**Recent Entries:**")
        recent = df_weight.tail(5).sort_values('date', ascending=False)
        
        for _, row in recent.iterrows():
            st.caption(f"{row['date'].strftime('%Y-%m-%d')}: {row['weight']} lbs")
    else:
        st.info("No weight entries yet. Start logging above!")
    
    st.divider()
    
    # Calorie trends
    st.markdown("### 📊 Calorie Trends (Last 7 Days)")
    
    trend_data = []
    for i in range(6, -1, -1):
        check_date = date.today() - timedelta(days=i)
        date_str = str(check_date)
        totals = get_daily_totals(date_str)
        trend_data.append({
            'Date': check_date.strftime('%m/%d'),
            'Calories': int(totals['calories'])
        })
    
    if any(d['Calories'] > 0 for d in trend_data):
        df_trend = pd.DataFrame(trend_data)
        st.bar_chart(df_trend.set_index('Date'))
    else:
        st.info("No calorie data in the last 7 days.")

# ==================== TAB 6: QUICK ADD ====================
with tab6:
    st.markdown("## ⚙️ Quick Add Food")
    st.caption("Manually add food without uploading a photo")
    
    # Search USDA directly
    st.markdown("### 🔍 Search Food Database")
    
    search_term = st.text_input("Search for a food item", placeholder="e.g., chicken breast, apple, rice")
    
    if search_term and len(search_term) > 2:
        with st.spinner("Searching USDA database..."):
            usda_results = get_usda_nutrition(search_term)
            
            if usda_results:
                st.success(f"✅ Found: {usda_results.get('usda_match', search_term)}")
                
                # Show nutrition
                st.markdown("**Nutrition per 100g:**")
                quick_col1, quick_col2, quick_col3 = st.columns(3)
                
                with quick_col1:
                    st.metric("Calories", f"{usda_results['calories']} kcal")
                    st.metric("Protein", f"{usda_results['protein']}g")
                
                with quick_col2:
                    st.metric("Carbs", f"{usda_results['carbs']}g")
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
                        
                        save_meal(meal_data)
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
                barcode_data, barcode_type = scan_barcode_from_image(barcode_file)
                
                if barcode_data:
                    st.success(f"✅ Barcode detected: {barcode_data}")
                    st.caption(f"Type: {barcode_type}")
                    
                    # Get product info
                    with st.spinner("Looking up product..."):
                        product_info = get_product_from_barcode(barcode_data)
                        
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
                                st.metric("Carbs", f"{product_info['carbs']}g")
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
                                    
                                    save_meal(meal_data)
                                    st.success(f"✅ Added to your {bc_meal_type} log!")
                                    st.balloons()
                        else:
                            st.error("❌ Product not found in database. Try the manual search above.")
                else:
                    st.error("❌ No barcode detected in image. Make sure the barcode is clear and well-lit.")
    
    # Recent foods
    st.divider()
    st.markdown("### 🕐 Recently Logged Foods")
    
    all_meals = load_meals()
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
            if st.button(f"➕ {food['name']}", key=f"recent_{food['meal']['id']}", use_container_width=True):
                # Quick add recent food
                meal_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                meal_data = food['meal'].copy()
                meal_data['id'] = meal_id
                meal_data['timestamp'] = datetime.now().isoformat()
                
                save_meal(meal_data)
                st.success(f"✅ Added {food['name']} to today's log!")
    else:
        st.caption("No recent foods. Add some meals first!")

# Footer
st.markdown("")
st.markdown("")
st.divider()
st.markdown("""
<div style="text-align: center; padding: 1rem; color: #666;">
    <p style="margin: 0;">⚠️ <strong>Disclaimer:</strong> Nutritional estimates are approximate and may vary.</p>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.9rem;">This tool should not replace professional dietary or medical advice.</p>
</div>
""", unsafe_allow_html=True)
