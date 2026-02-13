# 🍽️ Food Calorie Analyzer

An AI-powered nutrition & fitness tracking app that analyzes food images, searches nutrition databases, and tracks exercise — all with intelligent portion size detection and comprehensive logging.

## ✨ Features

### 🔍 Multi-Mode Food Analysis
- **📸 Photo Analysis**: Upload food images with AI-powered recognition (Google Vision API)
- **📷 Barcode Scanning**: Scan product barcodes for instant nutrition data (Open Food Facts)
- **🔍 Food Search**: Search 500,000+ foods from USDA FoodData Central
  - 12 popular food quick-tap buttons (Chicken, Rice, Egg, Banana, etc.)
  - Recent search history (last 10 searches, clickable)
  - Filter by source (All / Generic USDA / Branded)
  - Sort by Relevance, Calories, or Protein
- **🍽️ Multi-Item Detection**: Automatically detects multiple foods in one image
- **✅ Flexible Selection**: Choose single items or combine multiple foods into one meal

### 📊 Smart Nutrition Tracking
- **Detailed Macros**: Calories, protein, carbs/sugar, fat per 100g (USDA standard)
- **Intelligent Portions**: Category-based serving sizes (pieces, cups, grams, ml)
- **Quick Presets**: Category-specific portion shortcuts across all 3 food modes
- **Educational UI**: Learn about portion calculations with visual examples

### 📅 Comprehensive Meal Management
- **Daily Summary**: Track breakfast, lunch, dinner, and snacks with progress bars
- **Meal History**: View past meals with images, nutrition data, and CSV export
- **Goal Setting**: Mifflin-St Jeor BMR calculator with activity levels and pace selection
- **Progress Charts**: Weight tracking (kg/lbs toggle) and calorie trend charts
- **Water Tracking**: Monitor daily hydration with glass counter
- **Quick Add**: Manually log foods or re-add recent meals with one tap

### 🏋️ Exercise & Fitness Tracking
- **80+ Exercises**: 7 categories (Running, Cycling, Swimming, Walking, Gym/Weights, Sports, Other)
- **Dual Calorie Modes**:
  - **Simple (MET)**: Standard formula for cardio — `Calories = MET × weight(kg) × duration(hours)`
  - **Detailed (Volume-based)**: Strength exercises with mechanical work, rest metabolism, and EPOC afterburn
- **19 Strength Exercises with ROM Data**: Squat (0.65m), Bench Press (0.50m), Deadlift (0.60m), and more
- **Weight Unit Toggle**: kg/lbs support with automatic conversion
- **4 Educational Sections**: Estimation methods, accuracy margins, MET science, and tips
- **Workout Log**: Streaks, weekly summaries, all-time stats, bar charts, and delete confirmations

## 🛠️ Tech Stack

- **Framework:** Streamlit (Python web app)
- **AI Vision:** Google Cloud Vision API (label detection + object localization)
- **Nutrition APIs:** 
  - USDA FoodData Central (500,000+ foods, search + nutrient lookup)
  - Open Food Facts (barcode products)
- **Barcode:** pyzbar (QR & barcode reading)
- **Data Storage:** JSON-based local persistence
- **Language:** Python 3.13

## 🏗️ Architecture

**Modular Design:**
- **app.py** (~976 lines): Core utilities, API integrations, shared functions
- **tabs/** (8 modules): Separate UI components
  - `tab_analyze.py` (~2,194 lines) - Photo/barcode/search food analysis
  - `tab_summary.py` (~119 lines) - Daily nutrition overview
  - `tab_goals.py` (~306 lines) - Goal management with BMR calculator
  - `tab_history.py` (~240 lines) - Meal history browser with CSV export
  - `tab_progress.py` (~95 lines) - Weight (kg/lbs) and calorie trends
  - `tab_quick_add.py` (~234 lines) - Manual food entry & recent foods
  - `tab_exercise.py` (~908 lines) - Exercise tracker (MET + detailed mode)
  - `tab_workout_log.py` (~395 lines) - Workout log, streaks, stats

**Data Flow**: 
- Food: Image/Barcode/Search → API lookup → Smart serving detection → Multiplier → Save
- Exercise: Select exercise → MET or Volume calculation → Save to log

## ☁️ Deployment to Streamlit Community Cloud (FREE)

### Prerequisites
- GitHub account
- Google Cloud Vision API key
- USDA API key

### Steps to Deploy

1. **Go to Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Sign in with GitHub

2. **Deploy Your App**
   - Click "New app"
   - Select your repository: `KalvinVar/Calories-AI-App`
   - Main file: `app.py`
   - Click "Deploy"

3. **Configure Secrets** (in Streamlit Cloud dashboard)
   
   Go to App Settings → Secrets and add:
   
   ```toml
   # USDA API Key
   USDA_API_KEY = "your_usda_api_key_here"
   
   # Google Cloud Vision credentials (copy from vision-key.json)
   [google_credentials]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "your-private-key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
   client_email = "your-service-account@project.iam.gserviceaccount.com"
   client_id = "your-client-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your-cert-url"
   ```

4. **Update Code for Cloud Deployment** (Required changes)
   
   Replace `.env` loading with `st.secrets`:
   ```python
   # OLD: load_dotenv()
   # NEW: Use st.secrets directly
   
   # For USDA API
   USDA_API_KEY = st.secrets["USDA_API_KEY"]
   
   # For Google Vision
   credentials = service_account.Credentials.from_service_account_info(
       st.secrets["google_credentials"]
   )
   ```

5. **Access Your App**
   - URL: `https://your-app-name.streamlit.app`
   - Works on any device (phone, tablet, desktop)
   - Share the link with anyone!

### Benefits
✅ **100% FREE** - No hosting costs  
✅ **Mobile-friendly** - Works in any browser  
✅ **Auto-updates** - Pushes to GitHub update the site  
✅ **Global access** - Available anywhere with internet  
✅ **No maintenance** - Streamlit handles infrastructure  

### Future Enhancement: PWA (Progressive Web App)
To make the app installable on phones ("Add to Home Screen"):
- Add `manifest.json` with app metadata
- Users can install as if it's a native app
- Opens without browser UI
- Still free, just config files!

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
1. **Choose mode**: 🍕 Food Photo, 📷 Product Barcode, or 🔍 Search Foods
2. **Upload image / scan barcode / search by name**
3. **Select items**: 
   - Single item: Pick from dropdown (default)
   - Multiple items: Check "Combine multiple items" box
   - Search: Browse results, filter by source, sort by nutrition
4. **Adjust portions**: Use smart serving inputs or quick size buttons
5. **Save meal**: Add to breakfast, lunch, dinner, or snacks

### Tab 2: Daily Summary
- View today's meals grouped by meal type
- See total calories and macros vs goals
- Track water intake
- Visual progress bars

### Tab 3: Set Goals
- Mifflin-St Jeor BMR calculator with gender, age, height, weight
- 5 activity levels with detailed descriptions
- Goal type: Maintain, Lose, or Gain weight
- Adjustable pace slider (0.5–1.0 kg/week) with safety warnings
- Auto-calculated timeline to target weight
- Configure daily targets (calories, protein, carbs/sugar, fat)

### Tab 4: View History
- Browse meals by date with images
- Delete individual meals or entire days
- Bulk delete by date range
- Export to CSV with full nutrition data

### Tab 5: Progress
- Log daily weight with kg/lbs toggle
- Weight trend line chart
- Calorie trends bar chart (last 7 days)

### Tab 6: Quick Add
- Manually enter foods by name (USDA lookup)
- Barcode scanning shortcut
- Re-add recent foods with one tap

### Tab 7: Exercise Tracker
- Select from 80+ exercises across 7 categories
- Enter body weight, duration, and load weight
- Toggle between MET (simple) and detailed (volume-based) calorie estimation
- Quick preset buttons for duration, rest time, and weights
- Save exercises with notes

### Tab 8: Workout Log
- View exercise history by date
- Weekly calendar view with active days highlighted
- Streak tracking (current and longest)
- All-time stats with bar charts
- Delete exercises with confirmation

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
- `data/exercises.json` - Exercise history grouped by date
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
- [x] Daily calorie goals with BMR calculator
- [x] Barcode scanning
- [x] Multi-item detection
- [x] Smart portion presets (all 3 modes)
- [x] Food search (USDA, popular foods, recent searches, filter/sort)
- [x] Exercise tracker (MET + detailed volume-based)
- [x] Workout log with streaks and stats
- [x] Weight unit toggle (kg/lbs)
- [x] CSV export
- [x] Carbs/Sugar labeling throughout
- [ ] User accounts and cloud sync
- [ ] Recipe suggestions
- [ ] Export to fitness apps (MyFitnessPal, etc.)
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
