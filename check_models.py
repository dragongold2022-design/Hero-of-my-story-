import os
from google import genai
from dotenv import load_dotenv

print("جاري فحص الموديلات المتاحة لمفتاحك...")
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    print("\n[الموديلات المتاحة]:")
    
    # جلب قائمة بكل الموديلات المسموحة لهذا المفتاح
    for model in client.models.list():
        print(f"- {model.name}")
        
    print("\n✅ تم الفحص بنجاح.")
except Exception as e:
    print(f"حدث خطأ أثناء الفحص: {e}")