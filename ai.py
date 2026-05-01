import os
from openai import OpenAI
import json

# OpenRouter setup
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

def analyse_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's goal.

User goal: '{user_goal}'

STRICT RULES:
- Extract only relevant skills
- Remove irrelevant tools
- Identify real gaps
- Generate roadmap only for missing fields

Return ONLY JSON:
{{
"ats_score": 85,
"ats_suggestions": [],
"skills": [],
"missing_skills": [],
"roadmap": [],
"interview_questions": []
}}

Resume:
{resume_text}
"""

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-4b-it:free",   # ✅ FREE model
            temperature=0.3,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()

        start = content.find("{")
        end = content.rfind("}") + 1

        return json.loads(content[start:end])

    except Exception as e:
        return {
            "ats_score": 0,
            "ats_suggestions": [],
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }