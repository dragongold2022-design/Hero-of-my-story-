import os
import json
import logging
from google import genai
from google.genai import types
from dotenv import load_dotenv

# إعداد نظام المراقبة المعياري (Enterprise Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("StoryCore.AIEngine")

class StoryGeneratorEngine:
    """
    محرك الذكاء الاصطناعي المركزي لتوليد القصص (مُحدّث لأحدث معمارية Google GenAI).
    مسؤول عن بناء الـ Master Prompt واسترجاع البيانات بتنسيق JSON صارم.
    """
    def __init__(self):
        logger.info("جاري تهيئة محرك الذكاء الاصطناعي بالمعمارية الجديدة...")
        try:
            load_dotenv()
            self.api_key = os.getenv("GEMINI_API_KEY")
            
            if not self.api_key:
                logger.critical("فشل أمني: مفتاح GEMINI_API_KEY مفقود من ملف .env")
                raise ValueError("Missing Gemini API Key.")
                
            # إعداد الاتصال بالعميل الجديد (GenAI Client)
            self.client = genai.Client(api_key=self.api_key)
            self.model_id = 'gemini-3.6-flash'          
            logger.info("تم الاتصال بنجاح بخوادم Google Gemini (New SDK).")
            
        except Exception as e:
            logger.critical(f"فشل في تهيئة محرك الذكاء الاصطناعي: {str(e)}")
            raise

    def _build_master_prompt(self, child_name: str, age: int, gender: str, hobbies: str, core_value: str) -> str:
        """بناء الـ Master Prompt الهندسي لضمان جودة قصة بـ 24 صفحة"""
        pronoun = "لها" if gender == "female" else "له"
        child_type = "طفلة" if gender == "female" else "طفل"

        prompt = f"""
        أنت كاتب قصص أطفال محترف وخبير في علم النفس التربوي. 
        المهمة: كتابة قصة مخصصة من 24 صفحة בדיוק لـ {child_type} اسمه/اسمها "{child_name}" وعمره {age} سنوات.
        هوايات البطل: {hobbies}.
        الهدف التربوي للقصة: غرس قيمة "{core_value}" بطريقة غير مباشرة وممتعة.

        معمارية القصة المطلوبة (24 صفحة):
        - المقدمة والتعريف بالبطل (4 صفحات).
        - بداية المغامرة والتحدي (8 صفحات).
        - ذروة الأحداث وتطبيق القيمة (7 صفحات).
        - الخاتمة والتكريم (5 صفحات).

        القواعد الصارمة للإخراج (يجب الالتزام بها 100%):
        1. الإخراج يجب أن يكون حصراً بتنسيق JSON صالح (Valid JSON) دون أي نصوص إضافية.
        2. النص السردي (narrative_text_ar) يجب أن يكون باللغة العربية الفصحى البسيطة والقصيرة المناسبة لعمر {age} سنوات.
        3. الوصف البصري (visual_prompt_en) يجب أن يكون باللغة الإنجليزية، يصف المشهد بدقة لتوجيه ذكاء اصطناعي للرسم، مع إضافة هذه الكلمات في نهايته: 
           "highly detailed, pixar 3d style, children book illustration, master piece".
        4. ملامح البطل ولبسه يجب أن تكون موحدة في الوصف البصري في جميع الصفحات.

        هيكل الـ JSON المطلوب:
        {{
            "title": "عنوان القصة المشوق بالعربية",
            "pages": [
                {{
                    "page_number": 1,
                    "narrative_text_ar": "النص العربي هنا...",
                    "visual_prompt_en": "English visual description here..."
                }}
            ]
        }}
        """
        return prompt

    def generate_story(self, child_name: str, age: int, gender: str, hobbies: str, core_value: str) -> dict:
        """الاتصال بـ Gemini واسترجاع القصة كـ Dictionary"""
        prompt = self._build_master_prompt(child_name, age, gender, hobbies, core_value)
        logger.info(f"جاري إرسال الطلب لتوليد قصة البطل: {child_name}...")
        
        try:
            # استخدام المعمارية الجديدة لتوليد المحتوى وإجبار الموديل على JSON
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.7
                )
            )
            
            story_data = json.loads(response.text)
            pages_count = len(story_data.get("pages", []))
            logger.info(f"✅ تم استلام القصة! العنوان: {story_data.get('title')} | عدد الصفحات: {pages_count}")
            
            return story_data

        except json.JSONDecodeError as json_err:
            logger.error(f"فشل ذريع: Gemini لم يُرجع JSON صالح. التفاصيل: {str(json_err)}")
            raise RuntimeError("AI Output Formatting Error.")
        except Exception as e:
            logger.error(f"خطأ غير متوقع أثناء التخاطب مع Gemini: {str(e)}")
            raise

# ==========================================
# منطقة الاختبار السريع
# ==========================================
if __name__ == "__main__":
    print("="*60)
    print("بدء فحص محرك الذكاء الاصطناعي (New SDK Architecture)")
    print("="*60)
    
    engine = StoryGeneratorEngine()
    
    test_story = engine.generate_story(
        child_name="أحمد",
        age=6,
        gender="male",
        hobbies="كرة القدم، واستكشاف الفضاء",
        core_value="الشجاعة ومواجهة المخاوف"
    )
    
    print("\n[عينة من الصفحة الأولى]:")
    print(f"النص العربي: {test_story['pages'][0]['narrative_text_ar']}")
    print(f"الوصف الإنجليزي (ControlNet): {test_story['pages'][0]['visual_prompt_en']}")
    print("="*60)