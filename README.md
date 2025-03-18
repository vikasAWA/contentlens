# ContentLens

[![ContentLens](https://img.shields.io/badge/Try%20It-Live%20Demo-blue)](https://contentlens-production.up.railway.app)

**ContentLens** is an AI-powered document analysis tool that processes various document formats through the lens of artificial intelligence to extract insights, generate summaries, and transform content.

![ContentLens Screenshot](https://via.placeholder.com/800x400?text=ContentLens+Screenshot)

## ✨ Features

- **Multi-format Support**: Process TXT, Markdown, JSON, DOCX files and images
- **AI-Powered Analysis**: Leverages Google's Gemini LLM for intelligent document processing
- **Customizable Instructions**: Tell ContentLens exactly what you want to do with your document
- **Secure Processing**: Files are processed and immediately deleted for privacy
- **Markdown Output**: Results are provided in clean, formatted markdown

## 🚀 Try It Out

Visit our live demo: [contentlens-production.up.railway.app](https://contentlens-production.up.railway.app)

## 💡 Example Use Cases

- Summarize long documents
- Extract key points from research papers
- Convert content to different formats (emails, blog posts, etc.)
- Analyze sentiment in text
- Translate content to other languages
- Create structured data from unstructured text

## 🛠️ Technical Details

ContentLens is built with:
- Python
- FastHTML & MonsterUI for the frontend
- Google's Gemini AI for content processing
- Async processing for efficient file handling

## 🔒 Privacy

Your privacy matters:
- Documents are processed securely
- Files are deleted immediately after processing
- Results are deleted after download
- No data is stored permanently

## 🧩 Local Development

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Google Gemini API key (see `.env.example`)
4. Run the application: `python app.py`
5. Visit `http://localhost:5000` in your browser

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ using Python, FastHTML, and Google Gemini AI


