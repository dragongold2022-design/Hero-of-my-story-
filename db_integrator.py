import logging
from sqlalchemy.orm import Session
# استدعاء الجلسة والنماذج من ملف قاعدة البيانات الذي بنيته سابقاً
from database_models import SessionLocal, Story, StoryPage, ChildProfile

# إعداد نظام المراقبة
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("StoryCore.Database")

class DatabaseIntegrator:
    """
    جسر الربط بين محرك الذكاء الاصطناعي وقاعدة البيانات المشفرة.
    """
    def __init__(self):
        self.db: Session = SessionLocal()

    def save_generated_story(self, child_id: int, story_json: dict) -> int:
        """
        تستقبل هذه الدالة الـ JSON الخاص بالقصة وتقوم بتفريغه في الجداول.
        """
        try:
            logger.info("جاري حفظ القصة الجديدة في قاعدة البيانات المشفرة...")
            
            # 1. إنشاء سجل القصة الرئيسية
            new_story = Story(
                child_id=child_id,
                title=story_json.get("title", "قصة بدون عنوان"),
                status="REVIEWING" # حالة القصة الحالية (تم توليد النص، بانتظار الصور)
            )
            self.db.add(new_story)
            self.db.flush() # نستخدم flush للحصول على رقم الـ ID للقصة قبل الحفظ النهائي

            # 2. تفريغ الصفحات (24 صفحة) وربطها بالقصة الرئيسية
            pages_data = story_json.get("pages", [])
            for page in pages_data:
                new_page = StoryPage(
                    story_id=new_story.id,
                    page_number=page.get("page_number"),
                    narrative_text_ar=page.get("narrative_text_ar"),
                    visual_prompt_en=page.get("visual_prompt_en"),
                    image_status="PENDING" # صورة هذه الصفحة لم يتم رسمها بعد
                )
                self.db.add(new_page)

            # 3. الاعتماد النهائي (Commit)
            self.db.commit()
            logger.info(f"✅ تم حفظ القصة بنجاح! رقم القصة في النظام: {new_story.id}")
            logger.info(f"✅ تم حفظ {len(pages_data)} صفحة مرتبطة بهذه القصة.")
            
            return new_story.id

        except Exception as e:
            self.db.rollback() # التراجع عن كل شيء في حال حدوث خطأ لحماية البيانات
            logger.error(f"❌ حدث خطأ فادح أثناء الحفظ في قاعدة البيانات: {str(e)}")
            raise
        finally:
            self.db.close()

# ==========================================
# منطقة الاختبار (كيف نربط الملفين؟)
# ==========================================
if __name__ == "__main__":
    from story_generator import StoryGeneratorEngine
    
    print("="*60)
    print("بدء اختبار النظام المتكامل (توليد + حفظ)")
    print("="*60)
    
    # 1. تشغيل محرك الذكاء الاصطناعي
    ai_engine = StoryGeneratorEngine()
    story_data = ai_engine.generate_story(
        child_name="سارة",
        age=5,
        gender="female",
        hobbies="الرسم وتلوين الفراشات",
        core_value="التعاون ومساعدة الأصدقاء"
    )
    
    # 2. تشغيل محرك قاعدة البيانات للحفظ
    db_manager = DatabaseIntegrator()
    
    # (لأغراض الاختبار، سنفترض أن الطفلة سارة مسجلة مسبقاً ورقمها 1 في النظام)
    TEST_CHILD_ID = 1 
    
    saved_story_id = db_manager.save_generated_story(
        child_id=TEST_CHILD_ID, 
        story_json=story_data
    )
    
    print(f"\n🎉 مبروك! اكتملت الدورة بنجاح. القصة جاهزة الآن لتدخل مرحلة الرسم (ControlNet).")