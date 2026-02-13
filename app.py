import streamlit as st
from google.cloud import vision
from google.oauth2 import service_account
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

# Load environment variables (for local development)
load_dotenv()

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Food Calorie Analyzer",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# API Keys - Support both local (.env) and cloud (st.secrets)
vision_client = None
USDA_API_KEY = None

# Try Streamlit Cloud secrets first
try:
    # This will fail if secrets aren't configured or if running locally
    USDA_API_KEY = st.secrets["USDA_API_KEY"]
    # If we get here, we're on Streamlit Cloud with secrets configured
    google_creds = dict(st.secrets["google_credentials"])
    credentials = service_account.Credentials.from_service_account_info(google_creds)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
    print("[DEBUG] Successfully loaded Streamlit Cloud secrets")
    st.toast("✅ Using Cloud Secrets", icon="☁️")
except Exception as e:
    print(f"[DEBUG] Secrets failed, trying local: {e}")
    # Running locally or secrets not configured - use .env
    USDA_API_KEY = os.getenv("USDA_API_KEY")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_path and os.path.exists(credentials_path):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        vision_client = vision.ImageAnnotatorClient()
        print("[DEBUG] Using local credentials file")
        st.toast("📁 Using Local Credentials", icon="💻")
    else:
        st.error(f"❌ No credentials found! Please configure secrets in Streamlit Cloud.\n\nError: {str(e)}")
        st.stop()

if vision_client is None or USDA_API_KEY is None:
    st.error("❌ Failed to initialize API clients. Check your secrets configuration.")
    st.stop()

# Data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
MEALS_FILE = DATA_DIR / "meals.json"
GOALS_FILE = DATA_DIR / "goals.json"
WEIGHT_FILE = DATA_DIR / "weight.json"
WATER_FILE = DATA_DIR / "water.json"
IMAGES_DIR = DATA_DIR / "meal_images"
IMAGES_DIR.mkdir(exist_ok=True)

# PWA Setup with embedded manifest
st.markdown("""
    <meta name="theme-color" content="#FF6B6B">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="CalorieApp">
    <meta name="description" content="Analyze food calories and nutrition from photos using AI">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, user-scalable=yes">
    <link rel="manifest" href="data:application/json;base64,ewogICJuYW1lIjogIkZvb2QgQ2Fsb3JpZSBBbmFseXplciIsCiAgInNob3J0X25hbWUiOiAiQ2Fsb3JpZUFwcCIsCiAgImRlc2NyaXB0aW9uIjogIkFuYWx5emUgZm9vZCBjYWxvcmllcyBhbmQgbnV0cml0aW9uIGZyb20gcGhvdG9zIHVzaW5nIEFJIiwKICAic3RhcnRfdXJsIjogIi8iLAogICJkaXNwbGF5IjogInN0YW5kYWxvbmUiLAogICJiYWNrZ3JvdW5kX2NvbG9yIjogIiNmZmZmZmYiLAogICJ0aGVtZV9jb2xvciI6ICIjRkY2QjZCIiwKICAib3JpZW50YXRpb24iOiAicG9ydHJhaXQiLAogICJpY29ucyI6IFsKICAgIHsKICAgICAgInNyYyI6ICJkYXRhOmltYWdlL3N2Zyt4bWwsPHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAxMDAgMTAwJz48dGV4dCB5PSc3NScgZm9udC1zaXplPSc3NSc+8J+NvO+4jzwvdGV4dD48L3N2Zz4iLAogICAgICAic2l6ZXMiOiAiMTkyeDE5MiIsCiAgICAgICJ0eXBlIjogImltYWdlL3N2Zyt4bWwiLAogICAgICAicHVycG9zZSI6ICJhbnkgbWFza2FibGUiCiAgICB9LAogICAgewogICAgICAic3JjIjogImRhdGE6aW1hZ2Uvc3ZnK3htbCw8c3ZnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zycgdmlld0JveD0nMCAwIDEwMCAxMDAnPjx0ZXh0IHk9Jzc1JyBmb250LXNpemU9Jzc1Jz7wn42877iPPC90ZXh0Pjwvc3ZnPiIsCiAgICAgICJzaXplcyI6ICI1MTJ4NTEyIiwKICAgICAgInR5cGUiOiAiaW1hZ2Uvc3ZnK3htbCIsCiAgICAgICJwdXJwb3NlIjogImFueSBtYXNrYWJsZSIKICAgIH0KICBdCn0=">
    <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='75' font-size='75'>🍽️</text></svg>">
    """, unsafe_allow_html=True)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Desktop: Tabs spread evenly across */
    .stTabs [data-baseweb="tab-list"] {
        display: flex !important;
        flex-wrap: nowrap !important;
        justify-content: space-evenly !important;
        gap: 0.5rem;
        width: 100%;
    }
    
    [data-baseweb="tab"] {
        flex: 1 1 auto !important;
        text-align: center !important;
    }
    
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        /* Allow tabs to wrap to multiple rows on mobile */
        .stTabs [data-baseweb="tab-list"] {
            display: flex !important;
            flex-wrap: wrap !important;
            gap: 0.5rem;
            justify-content: center !important;
        }
        
        /* Compact tab styling for mobile */
        [data-baseweb="tab"] {
            flex: 0 1 auto !important;
            min-width: 80px !important;
            max-width: 110px !important;
            padding: 0.6rem 0.5rem !important;
            font-size: 0.85rem !important;
            text-align: center;
            white-space: nowrap;
        }
        
        /* Increase button sizes for mobile */
        .stButton button {
            min-height: 48px !important;
            font-size: 1.1rem !important;
            padding: 0.75rem 1.5rem !important;
        }
        
        /* Larger input fields */
        input, select, textarea {
            min-height: 48px !important;
            font-size: 1rem !important;
        }
        
        /* Better spacing for mobile */
        .element-container {
            padding: 0.5rem 0 !important;
        }
        
        /* Larger title on mobile */
        h1 {
            font-size: 2rem !important;
        }
        
        /* Larger metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
        }
        
        /* Better file uploader on mobile */
        [data-testid="stFileUploader"] {
            padding: 1.5rem 1rem !important;
        }
        
        /* Wider content on mobile */
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
    }
    
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

def validate_ean13_checksum(barcode):
    """Validate EAN13 barcode checksum to ensure it's correctly read"""
    if len(barcode) != 13 or not barcode.isdigit():
        return False
    
    # EAN13 checksum: alternating multiply by 1 and 3, sum, then check last digit
    odd_sum = sum(int(barcode[i]) for i in range(0, 12, 2))
    even_sum = sum(int(barcode[i]) for i in range(1, 12, 2))
    total = odd_sum + (even_sum * 3)
    checksum = (10 - (total % 10)) % 10
    
    return checksum == int(barcode[12])

def scan_barcode_from_image(image_file):
    """Scan barcode from uploaded image - tries multiple rotations and flips with validation"""
    try:
        image_file.seek(0)
        img = Image.open(image_file)
        
        # Try multiple rotations (0°, 90°, 180°, 270°) and horizontal flip
        rotations = [0, 90, 180, 270]
        candidates = []  # Store all detected barcodes with their confidence
        
        for angle in rotations:
            # Rotate image if needed
            if angle == 0:
                rotated_img = img
            else:
                rotated_img = img.rotate(-angle, expand=True)
            
            # Try normal orientation
            barcodes = decode_barcode(rotated_img)
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                barcode_type = barcodes[0].type
                candidates.append((barcode_data, barcode_type, angle, False))
            
            # Try horizontally flipped (mirror image)
            flipped_img = rotated_img.transpose(Image.FLIP_LEFT_RIGHT)
            barcodes = decode_barcode(flipped_img)
            if barcodes:
                barcode_data = barcodes[0].data.decode('utf-8')
                barcode_type = barcodes[0].type
                candidates.append((barcode_data, barcode_type, angle, True))
        
        # Validate candidates - prioritize those with valid checksums
        for barcode_data, barcode_type, angle, flipped in candidates:
            if barcode_type == 'EAN13' and validate_ean13_checksum(barcode_data):
                orientation = f"{angle}° rotation" + (" (flipped)" if flipped else "")
                print(f"[Barcode] Valid checksum at {orientation}: {barcode_data}")
                return barcode_data, barcode_type
        
        # If no valid EAN13 found, return first candidate (for other barcode types)
        if candidates:
            barcode_data, barcode_type, angle, flipped = candidates[0]
            orientation = f"{angle}° rotation" + (" (flipped)" if flipped else "")
            print(f"[Barcode] Found at {orientation} (no checksum validation): {barcode_data}")
            return barcode_data, barcode_type
        
        print("[Barcode] No barcode detected at any rotation/flip")
        return None, None
    except Exception as e:
        print(f"[Barcode] Scan error: {e}")
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

@st.cache_data(ttl=3600, show_spinner="Getting nutrition data...")  # Cache for 1 hour
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

@st.cache_data(ttl=3600, show_spinner="Getting Nutrition Estimate")  # Cache for 1 hour
def get_nutrition_estimate(food_name, alternative_names=None):
    """Get nutrition estimate from USDA API first, then fallback to local database"""
    # Handle mutable default argument
    if alternative_names is None:
        alternative_names = []
    
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
        # Use the global vision_client that has proper credentials
        global vision_client
        
        # Reset file pointer and read image
        image_file.seek(0)
        content = image_file.read()
        
        # Try specialized food classifier first
        ai_predictions = classify_food_with_ai(content)
        
        image = vision.Image(content=content)
        
        # Detect labels (objects/food items)
        response = vision_client.label_detection(image=image)
        labels = response.label_annotations
        
        # NEW: Detect objects with localization for better multi-item detection
        objects_response = vision_client.object_localization(image=image)
        objects = objects_response.localized_object_annotations
        
        # Detect web entities for more context
        web_response = vision_client.web_detection(image=image)
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
# Import tab modules
import sys
import tabs.tab_analyze as tab_analyze
import tabs.tab_summary as tab_summary
import tabs.tab_goals as tab_goals
import tabs.tab_history as tab_history
import tabs.tab_progress as tab_progress
import tabs.tab_quick_add as tab_quick_add

with tab1:
    tab_analyze.render(sys.modules[__name__])

# ==================== TAB 2: DAILY SUMMARY ====================
with tab2:
    tab_summary.render(sys.modules[__name__])

# ==================== TAB 3: GOALS ====================
with tab3:
    tab_goals.render(sys.modules[__name__])

# ==================== TAB 4: HISTORY ====================
with tab4:
    tab_history.render(sys.modules[__name__])

# ==================== TAB 5: PROGRESS ====================
with tab5:
    tab_progress.render(sys.modules[__name__])

# ==================== TAB 6: QUICK ADD ====================
with tab6:
    tab_quick_add.render(sys.modules[__name__])

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
