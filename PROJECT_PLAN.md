# WIO LMMA IOC Map with Gemini Chat - Project Plan

## 📋 Project Overview

Adding a Google Gemini AI chatbot alongside the interactive map in a 2-column layout.

---

## 🔑 API Keys Setup

### Google Gemini API Key

#### How to Get Your Gemini API Key:

1. **Visit Google AI Studio**

   - Go to: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Create API Key**

   - Click "Get API Key" or "Create API Key"
   - Select "Create API key in new project" (or use existing project)
   - Copy the generated key (starts with `AIza...`)

3. **Add to .env file**
   ```
   GEMINI_API_KEY=AIza...your-key-here
   ```

#### API Key Features:

- ✅ Free tier: 15 requests per minute
- ✅ 1 million tokens per month (free)
- ✅ No credit card required for testing
- ✅ Works with Gemini 1.5 Flash (fast & free)

---

## 🎯 Implementation Steps

### ✅ Step 1: Clean Up & Create 2-Column Layout

**Goal**: Restructure the page with map on left (60%) and placeholder on right (40%)

**Tasks**:

- [x] Move debug logs to expandable section
- [x] Create two columns using `st.columns([6, 4])`
- [x] Place map in left column
- [x] Add placeholder in right column
- [x] Add Gemini API key to .env

**Validation**:

- Both columns display correctly
- Map still works
- Layout is responsive

---

### ⏳ Step 2: Add Basic Chat UI

**Goal**: Create chat interface without AI (echo bot for testing)

**Tasks**:

- [ ] Add chat message container (scrollable)
- [ ] Add chat input box at bottom
- [ ] Display user messages
- [ ] Echo back messages (simple response)
- [ ] Use `st.session_state` for message history

**Validation**:

- Can type and see messages
- Messages stay in history
- UI is clean and usable

---

### ⏳ Step 3: Integrate Google Gemini API

**Goal**: Connect real Gemini AI responses

**Tasks**:

- [ ] Install `google-generativeai` package
- [ ] Load Gemini API key from .env
- [ ] Initialize Gemini model (gemini-1.5-flash)
- [ ] Send user messages to Gemini
- [ ] Display Gemini responses
- [ ] Add error handling

**Validation**:

- Chat responds with actual AI
- API key works
- Errors are handled gracefully

---

### ⏳ Step 4: Add Context Awareness

**Goal**: Make chat aware of map data

**Tasks**:

- [ ] Pass GeoDataFrame summary to chat context
- [ ] Add system prompt about LMMA data
- [ ] Enable chat to answer questions about the map
- [ ] Add "Ask about the map" example prompts

**Validation**:

- Chat knows about the data
- Can answer map-related questions
- Responses are relevant

---

### ⏳ Step 5: Polish & Enhance

**Goal**: Final touches and improvements

**Tasks**:

- [ ] Add chat styling/colors
- [ ] Add example prompts/suggestions
- [ ] Add "Clear chat" button
- [ ] Improve loading states
- [ ] Add avatars for user/AI
- [ ] Final testing

**Validation**:

- App looks polished
- User experience is smooth
- All features work together

---

## 📁 Project Structure

```
streamlit-oceanhub/
├── .env                    # API keys (not in git)
├── .gitignore             # Ignore .env
├── streamlit_map.py       # Main application
├── PROJECT_PLAN.md        # This document
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
└── wio_lmma_ioc.*        # Shapefile components
```

---

## 📦 Required Packages

### Current Dependencies:

```txt
streamlit
pydeck
geopandas
python-dotenv
```

### New Dependencies (to be added):

```txt
google-generativeai
```

---

## 🎨 Final Layout Design

```
┌─────────────────────────────────────────────────────────┐
│              WIO LMMA IOC Map with AI Assistant         │
├──────────────────────────────┬──────────────────────────┤
│                              │  💬 Chat with Gemini     │
│   🗺️ Interactive Map         │  ─────────────────────   │
│   (PyDeck - 60% width)       │  [Message history]       │
│                              │  User: Hello             │
│   - Click features           │  AI: Hi! How can I help? │
│   - Zoom/Pan                 │                          │
│   - Tooltips                 │  [Scrollable area]       │
│                              │                          │
│                              │  ─────────────────────   │
│  [Attribute Preview Below]   │  💭 Type your message... │
└──────────────────────────────┴──────────────────────────┘
```

---

## 🔒 Security Notes

- ✅ `.env` file is in `.gitignore` (API keys not committed)
- ✅ API keys loaded from environment variables
- ✅ Error messages don't expose sensitive data

---

## 📝 Current Status

**Current Step**: Step 1 - Clean Up & Create 2-Column Layout
**Last Updated**: 2025-10-18
**Status**: 🟡 In Progress

---

## 🎯 Success Criteria

- [x] Map displays correctly in left column
- [ ] Chat interface works in right column
- [ ] Gemini AI responds to questions
- [ ] Chat history is maintained
- [ ] Layout is clean and professional
- [ ] All API keys are secure
- [ ] App is ready for production use

---

## 📞 Support Links

- Google AI Studio: https://aistudio.google.com/
- Gemini API Docs: https://ai.google.dev/docs
- Streamlit Docs: https://docs.streamlit.io/
- PyDeck Docs: https://deckgl.readthedocs.io/
