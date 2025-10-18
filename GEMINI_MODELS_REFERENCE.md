# Google Gemini Models Reference

## 🚀 Recommended Models for This Project

### ✅ Currently Using: **gemini-2.5-flash**
- **Speed**: Very Fast ⚡
- **Quality**: High
- **Cost**: FREE (within limits)
- **Best For**: Chat applications, general Q&A
- **Supports**: `generateContent`, `countTokens`, `createCachedContent`

---

## 📋 Available Gemini Models (October 2025)

### 🔥 Latest & Greatest (Gemini 2.5 Series)

#### **gemini-2.5-flash** ⭐ RECOMMENDED
- Fastest and most efficient
- Perfect for chat applications
- FREE tier available

#### **gemini-2.5-pro**
- More powerful reasoning
- Better for complex tasks
- Slower but higher quality

#### **gemini-2.5-flash-lite**
- Even lighter/faster
- Good for simple tasks
- Ultra-low latency

---

### 🆕 Gemini 2.0 Series (Newer Features)

#### **gemini-2.0-flash**
- Newer generation
- Good balance of speed/quality
- Alternative to 2.5-flash

#### **gemini-2.0-flash-lite**
- Lightweight version
- Very fast responses
- Good for high-volume apps

#### **gemini-2.0-pro-exp**
- Experimental pro version
- Advanced capabilities
- May have limitations

---

### 🎯 Special Purpose Models

#### **gemini-flash-latest**
- Always points to latest flash model
- Auto-updates to newest version
- Good for staying current

#### **gemini-pro-latest**
- Always points to latest pro model
- Best quality available
- Auto-updates

---

## 🔄 How to Change Models

Edit `streamlit_map.py` line ~47:

```python
# Current:
model = genai.GenerativeModel('gemini-2.5-flash')

# Change to any of these:
model = genai.GenerativeModel('gemini-2.5-pro')          # More powerful
model = genai.GenerativeModel('gemini-2.5-flash-lite')   # Even faster
model = genai.GenerativeModel('gemini-2.0-flash')        # Alternative
model = genai.GenerativeModel('gemini-flash-latest')     # Always latest
```

---

## 📊 Model Comparison

| Model | Speed | Quality | Best For | Free Tier |
|-------|-------|---------|----------|-----------|
| **gemini-2.5-flash** ⭐ | ⚡⚡⚡ | ⭐⭐⭐⭐ | Chat, Q&A | ✅ Yes |
| gemini-2.5-pro | ⚡⚡ | ⭐⭐⭐⭐⭐ | Complex tasks | ✅ Yes |
| gemini-2.5-flash-lite | ⚡⚡⚡⚡ | ⭐⭐⭐ | Simple tasks | ✅ Yes |
| gemini-2.0-flash | ⚡⚡⚡ | ⭐⭐⭐⭐ | Alternative | ✅ Yes |
| gemini-flash-latest | ⚡⚡⚡ | ⭐⭐⭐⭐ | Auto-update | ✅ Yes |

---

## 🚫 Models NOT Recommended for Chat

These are for other purposes:
- `embedding-*` - For text embeddings, not chat
- `imagen-*` - For image generation
- `veo-*` - For video generation
- `aqa` - For Q&A with specific docs

---

## 💡 Rate Limits (Free Tier)

- **Requests**: 15 per minute
- **Tokens**: 1 million per month
- **Daily**: 1,500 requests

**If you hit limits:**
- Wait 60 seconds between batches
- Use lighter model (flash-lite)
- Consider paid tier for production

---

## 🔍 How We Got This List

Run this command to see current models:

```bash
python -c "import google.generativeai as genai; import os; from dotenv import load_dotenv; load_dotenv(); genai.configure(api_key=os.getenv('GEMINI_API_KEY')); [print(f'{m.name}') for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]"
```

---

## ✅ Updated in Project

- ✅ Changed from `gemini-1.5-flash` (deprecated)
- ✅ Now using `gemini-2.5-flash` (current)
- ✅ Error should be fixed!

---

**Last Updated**: October 18, 2025
**Source**: Google AI Studio / Gemini API
