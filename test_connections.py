print("Starting test...")

from dotenv import load_dotenv
import os
import openai
from supabase import create_client

load_dotenv()
print("Env loaded")

# Test OpenAI
try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "say hi"}],
        max_tokens=5
    )
    print("OpenAI connected:", response.choices[0].message.content)
except Exception as e:
    print("OpenAI error:", e)

# Test Supabase
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    result = supabase.table("raw_comments").select("*").limit(1).execute()
    print("Supabase connected. Rows:", len(result.data))
except Exception as e:
    print("Supabase error:", e)