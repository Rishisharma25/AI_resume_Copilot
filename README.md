# AI Career Copilot 🚀

AI Career Copilot is a powerful, modern web application designed to help job seekers optimize their resumes, beat Applicant Tracking Systems (ATS), and land their dream jobs. By leveraging advanced generative AI models, the copilot analyzes your resume against specific career goals, providing real-time, actionable feedback.

## ✨ Features

- **🧠 AI-Powered Resume Analysis**: Upload a PDF or paste your resume text, and the AI will analyze it against your target job title, providing a detailed ATS compatibility score.
- **📈 Actionable ATS Suggestions**: Receive specific, step-by-step suggestions on how to reword, format, or improve your resume to bypass automated hiring filters.
- **📝 Built-in Resume Builder**: Don't have a PDF? Use the built-in Profile Form to structure your Personal Info, Summary, Experience, Education, and Skills. The app will automatically assemble it for AI analysis.
- **🔐 Secure Authentication**: Full user account system featuring email/password login, alongside integrated **OAuth Social Logins** for Google, GitHub, and LinkedIn.
- **🎨 Modern UI/UX**: A beautiful, responsive interface featuring a custom dark-mode aesthetic, split-screen authentication layouts, glassmorphic elements, and smooth micro-animations.
- **📊 History Tracking**: All past resume analyses and scores are saved to your dashboard, allowing you to track your improvement over time.

## 🛠️ Tech Stack

- **Backend**: Python, Flask, SQLAlchemy (ORM)
- **AI Engine**: OpenRouter API (`google/gemma-3-4b-it:free`) for LLM text analysis
- **Frontend**: HTML5, Vanilla CSS3, Javascript, Jinja2 Templating
- **Authentication**: Authlib (OAuth 2.0 Integration)
- **Utilities**: PyPDF2 (PDF Parsing), python-dotenv (Environment Management)

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/ai-career-copilot.git
cd ai-career-copilot
```

### 2. Set up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: If `requirements.txt` is missing, manually install `flask`, `sqlalchemy`, `PyPDF2`, `python-docx`, `authlib`, `requests`, `python-dotenv`, and `openai`)*

### 4. Environment Variables
Create a `.env` file in the root directory to store your API keys:
```env
# OpenRouter / AI API Key
OPENROUTER_API_KEY="your_openrouter_api_key"

# OAuth Secrets (Generate these on respective developer portals)
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
GITHUB_CLIENT_ID="your_github_client_id"
GITHUB_CLIENT_SECRET="your_github_client_secret"
LINKEDIN_CLIENT_ID="your_linkedin_client_id"
LINKEDIN_CLIENT_SECRET="your_linkedin_client_secret"
```

### 5. Run the Application
```bash
python app.py
```
The application will be available locally at `http://127.0.0.1:5000/`.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
