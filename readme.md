# Marine Protected Areas Explorer

A Streamlit application that transforms uploaded photos into cartoon fish characters while educating users about Marine Protected Areas (MPAs) and Locally Managed Marine Areas (LMMAs).

## Features

- 🐠 **Fish Transformation**: Upload a photo and get transformed into a marine protector fish using Google Gemini AI
- 🌊 **Educational Content**: Learn about MPAs and LMMAs through interactive chat
- 💬 **AI Chat**: Ask questions about marine conservation, protected areas, and eco-tourism
- 🎨 **Modern UI**: Clean, responsive interface with marine-themed styling

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamlit-oceanhub
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Get your Google Gemini API key from [Google AI Studio](https://ai.google.dev/)
   - Add your API key to the `.env` file:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

5. **Run the application**
   ```bash
   streamlit run pages/chat.py
   ```

## API Costs & Usage

⚠️ **Important**: This application uses Google Gemini AI services which may incur costs:

- **Image Generation**: Uses `gemini-2.5-flash-image` model for fish transformations
- **Text Generation**: Uses `gemini-2.5-flash` model for chat responses
- **Rate Limits**: Be mindful of API usage to avoid unexpected charges

### Cost Management Tips

- Images are limited to 10MB maximum size
- Each upload generates one transformation (no reprocessing of identical images)
- Consider implementing rate limiting for production deployments

## File Structure

```
streamlit-oceanhub/
├── pages/
│   └── chat.py              # Main application file
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key for AI services | Yes |

## Technical Details

### Dependencies

- **streamlit**: Web application framework
- **google-genai**: Google Gemini AI client library
- **python-dotenv**: Environment variable management

### Key Features

- **Deterministic Image Processing**: Uses SHA256 hashing to prevent reprocessing identical images
- **Defensive API Handling**: Robust error handling for API responses
- **Session State Management**: Maintains chat history and processed images
- **Responsive Design**: Mobile-friendly interface with custom CSS

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `.env` file exists and contains `GEMINI_API_KEY`
   - Verify the API key is valid and has proper permissions

2. **Image Upload Issues**
   - Check file size (must be under 10MB)
   - Ensure file format is JPG, JPEG, or PNG

3. **API Errors**
   - Check your internet connection
   - Verify API key has sufficient quota
   - Check Google AI Studio for service status

### Getting Help

- Check the [Google Gemini API documentation](https://ai.google.dev/gemini-api/docs)
- Review Streamlit documentation for UI issues
- Check the application logs for detailed error messages

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for image and text generation capabilities
- Streamlit for the web application framework
- Marine conservation organizations for educational content inspiration