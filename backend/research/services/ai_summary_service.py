import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_document(text: str):
    prompt = f"""
    You are an AI research assistant. Analyze the following market data and summarize
    the top 3 niche opportunities, including potential product directions and audience insights.

    Text:
    {text}
    """
    completion = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content
