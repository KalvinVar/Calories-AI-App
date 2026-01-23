# 🍽️ Food Calorie Analyzer

An AI-powered nutrition tracking app that analyzes food images and provides comprehensive calorie and nutritional information with intelligent portion size detection.

## ✨ Features

### 🔍 Multi-Mode Food Analysis
- **📸 Photo Analysis**: Upload food images with AI-powered recognition
- **📷 Barcode Scanning**: Scan product barcodes for instant nutrition data
- **🍽️ Multi-Item Detection**: Automatically detects multiple foods in one image
- **✅ Flexible Selection**: Choose single items or combine multiple foods into one meal

### 📊 Smart Nutrition Tracking
- **Detailed Macros**: Calories, protein, carbs, fat per 100g (USDA standard)
- **Intelligent Portions**: Category-based serving sizes (pieces, cups, grams, ml)
- **Quick Presets**: Small/Medium/Large/XL portion shortcuts
- **Educational UI**: Learn about portion calculations with visual examples

### 📅 Comprehensive Meal Management
- **Daily Summary**: Track breakfast, lunch, dinner, and snacks
- **Meal History**: View past meals with images and nutrition data
- **Goal Setting**: Set and track daily calorie & macro goals
- **Progress Charts**: Visualize weight trends and nutrition patterns
- **Water Tracking**: Monitor daily hydration (8 glasses goal)
- **Quick Add**: Manually log foods without photos

## 🛠️ Tech Stack

- **Framework:** Streamlit (Python web app)
- **AI Vision:** Google Cloud Vision API (label detection + object localization)
- **Nutrition APIs:** 
  - USDA FoodData Central (500,000+ foods)
  - Open Food Facts (barcode products)
- **Barcode:** pyzbar (QR & barcode reading)
- **Data Storage:** JSON-based local persistence
- **Language:** Python 3.13

## 🏗️ Architecture

- **Single-file monolith** (~2,200 lines): `app.py`
- **6-tab interface**: Analyze, Daily Summary, Set Goals, View History, Progress, Quick Add
- **Data Flow**: Image → Vision API → USDA lookup → Smart serving detection → Multiplier calculation
- **100g Standard**: All nutrition normalized to 100g, then scaled to user portions

## 🚀 Setup Instructions

### 1. Install Python
Make sure you have Python 3.13 or higher installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Google Cloud Vision API

**Step 1:** Create a Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Vision API:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

**Step 2:** Create Service Account & Get Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Give it a name and click "Create"
4. Grant it the "Cloud Vision API User" role
5. Click "Done"
6. Click on the service account you just created
7. Go to "Keys" tab > "Add Key" > "Create New Key"
8. Choose JSON format
9. Download the JSON key file and save as `vision-key.json`

### 4. Get USDA API Key
1. Go to https://fdc.nal.usda.gov/api-key-signup.html
2. Sign up for a free API key
3. Copy your API key (looks like: `abcd1234...`)

### 5. Configure Environment
Create a `.env` file in the project root:
```env
GOOGLE_APPLICATION_CREDENTIALS=E:\3rd qart\vision-key.json
USDA_API_KEY=your_actual_api_key_here
```
(Replace with your actual file path and API key)

### 6. Run the App
```bash
python -m streamlit run app.py
```

The app will open at `http://localhost:8501` (or your network IP like `http://10.0.0.246:8501`)

## 📱 Usage

### Tab 1: Analyze Food
1. **Choose mode**: 🍕 Food Photo or 📷 Product Barcode
2. **Upload image**: Click "Browse files" or drag & drop
3. **Select items**: 
   - Single item: Pick from dropdown (default)
   - Multiple items: Check "Combine multiple items" box
4. **Adjust portions**: Use smart serving inputs (pieces, cups, grams, etc.)
5. **Save meal**: Add to breakfast, lunch, dinner, or snacks

### Tab 2: Daily Summary
- View today's meals grouped by meal type
- See total calories and macros vs goals
- Track water intake (8 glasses/day)
- Visual progress bars

### Tab 3: Set Goals
- Configure daily targets (calories, protein, carbs, fat)
- Common presets: Maintenance, Cut, Bulk

### Tab 4: View History
- Browse meals by date
- See saved food images
- Review past nutrition data

### Tab 5: Progress
- Log daily weight
- View weight trend chart
- Track nutrition patterns over time

### Tab 6: Quick Add
- Manually enter foods without photos
- Direct calorie and macro input

## 💡 Tips for Best Results

### Food Photos
- Use clear, well-lit photos
- Capture the entire dish from above
- Separate items work better than mixed dishes
- Avoid blurry or dark images

### Barcode Scanning
- Straight-on, horizontal orientation
- Good lighting on the barcode
- Clear focus (not blurry)
- Works with UPC, EAN13, and most standard barcodes

### Portion Accuracy
- Use the smart serving presets (Small/Medium/Large/XL)
- Remember: USDA data is per 100g, app automatically scales
- For unrecognized foods, 100g ≈ palm-sized portion
- Multi-item meals: adjust each food individually

## 💰 Cost Estimates

**Google Cloud Vision API:**
- First 1,000 images/month: **FREE**
- After free tier: $1.50 per 1,000 images
- Object localization: Same pricing

**USDA FoodData Central API:**
- Completely **FREE** (no limits)

**Open Food Facts API:**
- Completely **FREE** (open database)

💚 **Perfect for personal use** - Most users stay within free tiers!

## 📂 Data Storage

All data stored locally in JSON files:
- `data/meals.json` - Meal history with nutrition
- `data/goals.json` - Daily calorie & macro targets
- `data/weight.json` - Weight tracking entries
- `data/water.json` - Daily water intake
- `data/meal_images/` - Saved food photos (JPEGs)

## ⚠️ Limitations

- **Estimates, not exact**: Nutrition data is approximate
- **Image quality matters**: Blurry/dark photos reduce accuracy
- **Generic categories**: Specific brands (e.g., "Big Mac") fall back to generic detection
- **100g standard**: USDA uses per-100g; app handles conversion automatically
- **Not medical advice**: Should not replace professional dietary guidance
- **Mixed dishes**: Complex meals (stir-fry, salads) harder to analyze than single items

## 🎯 Key Design Decisions

1. **No hardcoded brands**: Impossible to catch every product globally - generic categories + smart fallback UI
2. **100g normalization**: All USDA data per 100g → multiplier system scales to user portions
3. **Opt-in multi-item**: Default single-item selector; checkbox enables multi-food mode
4. **Educational fallback**: Unrecognized foods show presets with explanations (not errors)
5. **Local-first**: JSON persistence, no database, no user accounts needed

## 🔧 Development

Built with extensibility in mind. See `.github/copilot-instructions.md` for:
- Architecture patterns
- API integration details  
- Testing strategies
- Debugging workflows
- Code conventions

## 🐛 Common Issues

**"Empty label" warnings**: Harmless accessibility warnings from metrics without labels

**Vision API errors**: Check `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

**No USDA results**: Verify `USDA_API_KEY` is real key (not "DEMO_KEY")

**Barcode not detected**: Ensure straight-on, horizontal, well-lit photo

## 🚀 Future Enhancements

- [x] Meal tracking and history
- [x] Daily calorie goals
- [x] Barcode scanning
- [x] Multi-item detection
- [x] Smart portion presets
- [ ] User accounts and cloud sync
- [ ] Recipe suggestions
- [ ] Export to fitness apps (MyFitnessPal, etc.)
- [ ] Nutrition trends dashboard
- [ ] Meal planning features

## 📄 License

MIT License - Feel free to use and modify!

## 🤝 Contributing

Contributions welcome! This project uses:
- Generic food categories (no brand hardcoding)
- USDA 100g standard with multiplier conversions
- Session state for UI persistence
- Educational UI patterns for edge cases

## 📸 Screenshots

*(Upload images of your app to GitHub and link them here)*

## 🙏 Acknowledgments

- Google Cloud Vision API for image recognition
- USDA FoodData Central for comprehensive nutrition database
- Open Food Facts for barcode product data
- Streamlit for rapid app development

---

**Built with ❤️ for healthy living and AI-powered nutrition tracking**
