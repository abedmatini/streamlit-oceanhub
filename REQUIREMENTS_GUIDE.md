# 📦 Using requirements.txt - Quick Guide

## What is requirements.txt?

A `requirements.txt` file lists all Python packages needed for your project, making it easy to install everything with one command.

---

## 🚀 How to Use

### **Install All Packages**

```bash
pip install -r requirements.txt
```

This single command installs all required packages with the correct versions.

---

### **Create/Update requirements.txt**

If you add new packages to your project:

```bash
pip freeze > requirements.txt
```

**Warning:** This includes ALL packages in your environment. For cleaner requirements, manually edit to keep only the main packages (as we have done).

---

## 📋 What's Included

Our `requirements.txt` includes:

1. **streamlit** - Web app framework
2. **geopandas** - Geospatial data handling
3. **shapely** - Geometric operations
4. **pydeck** - Interactive map visualization
5. **google-generativeai** - Google Gemini AI
6. **python-dotenv** - Environment variables
7. **pandas** - Data manipulation

---

## 🔄 Different Ways to Install

### **Method 1: From requirements.txt (BEST)**
```bash
pip install -r requirements.txt
```
✅ Installs exact versions specified
✅ Reproducible across environments
✅ One command for everything

### **Method 2: Manual Installation**
```bash
pip install streamlit geopandas pydeck google-generativeai python-dotenv
```
⚠️ May install different versions
⚠️ Longer command
⚠️ Easy to miss a package

### **Method 3: Individual Packages**
```bash
pip install streamlit
pip install geopandas
pip install pydeck
pip install google-generativeai
pip install python-dotenv
```
❌ Very tedious
❌ Multiple commands
❌ Not recommended

---

## 💡 Pro Tips

### **Upgrade pip first:**
```bash
pip install --upgrade pip
```

### **Check what's installed:**
```bash
pip list
```

### **Verify a specific package:**
```bash
pip show streamlit
```

### **Uninstall everything (if needed):**
```bash
pip freeze > temp.txt
pip uninstall -r temp.txt -y
```

---

## 🐍 Virtual Environment Best Practice

**ALWAYS use requirements.txt with a virtual environment:**

```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate it
# Windows:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Install from requirements.txt
pip install -r requirements.txt

# 4. Run your app
streamlit run streamlit_map.py
```

---

## ❓ Troubleshooting

### **"No such file: requirements.txt"**
- Make sure you're in the project directory
- Run: `ls` (macOS/Linux) or `dir` (Windows)
- You should see `requirements.txt` in the list

### **"Could not find a version..."**
- Update pip: `pip install --upgrade pip`
- Check your Python version: `python --version` (need 3.8+)
- Try installing manually if one package fails

### **"Permission denied"**
- On Linux/Mac, try: `pip install --user -r requirements.txt`
- Or use: `sudo pip install -r requirements.txt` (not recommended)
- Better: Use a virtual environment!

### **Packages take forever to install**
- This is normal for `geopandas` (has many dependencies)
- Be patient, especially on first install
- Subsequent installs are faster (cached)

---

## 📊 Installation Time

Expected installation time:

- **Fast internet + SSD:** 2-5 minutes
- **Average setup:** 5-10 minutes
- **Slow connection:** 10-20 minutes

**GeoPandas** is the largest package and takes most of the time.

---

## ✅ Verify Installation Success

After running `pip install -r requirements.txt`, verify:

```bash
python -c "import streamlit; print('Streamlit:', streamlit.__version__)"
python -c "import geopandas; print('GeoPandas:', geopandas.__version__)"
python -c "import pydeck; print('PyDeck:', pydeck.__version__)"
python -c "import google.generativeai; print('Gemini: OK')"
```

All commands should print version numbers without errors.

---

## 🎯 Summary

**Use this command to install everything:**

```bash
pip install -r requirements.txt
```

**That's it! Simple and reliable! ✅**

---

## 📚 Learn More

- [pip documentation](https://pip.pypa.io/en/stable/)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [requirements.txt Best Practices](https://pip.pypa.io/en/stable/reference/requirements-file-format/)
