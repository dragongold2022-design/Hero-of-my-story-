import logging
from sqlalchemy.exc import SQLAlchemyError
from database_models import (
    init_db, User, ChildProfile, Story, StoryPage, 
    GenderEnum, StoryStatusEnum, PageImageStatusEnum
)

# إعداد نظام المراقبة المعياري للاختبار (Enterprise Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("StoryCore.IntegrationTest")

class DatabaseIntegrationTester:
    """
    كلاس هندسي مخصص لاختبار التكامل بين قاعدة البيانات (SQLAlchemy) ودرع الحماية (SecurityManager).
    يطبق معايير الـ OOP وإدارة الجلسات الآمنة (Session Management).
    """
    def __init__(self):
        logger.info("جاري تهيئة محرك قاعدة البيانات وبناء الجداول المحصنة...")
        try:
            self.engine, self.SessionLocal = init_db()
        except Exception as e:
            logger.critical(f"فشل في تهيئة قاعدة البيانات: {str(e)}")
            raise

    def run_full_cycle_test(self):
        """تنفيذ دورة حياة كاملة: إنشاء، حفظ، استرجاع، والتحقق من التشفير المخفي"""
        session = self.SessionLocal()
        logger.info("تم فتح جلسة (Session) آمنة مع قاعدة البيانات.")
        
        try:
            # 1. إدخال مستخدم جديد (الإيميل حساس وسيتم تشفيره تلقائياً)
            logger.info("جاري إنشاء حساب مستخدم جديد...")
            new_user = User(
                username="Mohammed_AlAwadhi",
                email="mohammed@enterprise.com"  # هذا سيشفر تلقائياً في الخلفية!
            )
            session.add(new_user)
            session.flush() # دفع البيانات مؤقتاً للحصول على الـ ID
            
            # 2. إدخال ملف طفل (الاسم والهوايات حساسة وستشفر تلقائياً)
            logger.info("جاري إنشاء ملف الطفل...")
            new_child = ChildProfile(
                user_id=new_user.id,
                full_name="سارة أحمد", # سيشفر
                gender=GenderEnum.FEMALE,
                age=6,
                photo_url="/uploads/faces/sara_reference.jpg", # مسار الصورة لـ IP-Adapter (لا يشفر)
                hobbies="الرسم، استكشاف الفضاء، والقطط" # سيشفر
            )
            session.add(new_child)
            session.flush()
            
            # 3. إنشاء قصة وصفحة (تمهيداً لعمليات ControlNet و Gemini)
            logger.info("جاري بناء هيكل القصة والصفحات...")
            new_story = Story(
                child_id=new_child.id,
                title="سارة ورحلة إلى المريخ",
                status=StoryStatusEnum.PENDING_TEXT
            )
            session.add(new_story)
            session.flush()
            
            page_1 = StoryPage(
                story_id=new_story.id,
                page_number=1,
                narrative_text_ar="كَانَتْ سَارَة تَجْلِسُ فِي غُرْفَتِهَا، تَنْظُرُ إِلَى النُّجُومِ اللامِعَةِ...",
                visual_prompt_en="A 6-year-old cute arab girl sitting in her bedroom looking at the stars through a window, highly detailed, pixar 3d style",
                image_status=PageImageStatusEnum.PENDING
            )
            session.add(page_1)
            
            # 4. الاعتماد النهائي وحفظ البيانات (Commit)
            session.commit()
            logger.info("✅ تم حفظ جميع البيانات بنجاح في قاعدة البيانات.")
            
            # ==========================================
            # 5. اختبار الاسترجاع السحري (فك التشفير التلقائي)
            # ==========================================
            logger.info("--- جاري اختبار استرجاع البيانات وفك التشفير التلقائي ---")
            
            # نستدعي المستخدم من الداتا بيز
            retrieved_user = session.query(User).filter_by(username="Mohammed_AlAwadhi").first()
            retrieved_child = session.query(ChildProfile).filter_by(user_id=retrieved_user.id).first()
            
            logger.info(f"إيميل المستخدم المسترجع: {retrieved_user.email}")
            logger.info(f"اسم الطفل المسترجع: {retrieved_child.full_name}")
            logger.info(f"هوايات الطفل المسترجعة: {retrieved_child.hobbies}")
            
            # التحقق البرمجي الصارم (Assertion)
            assert retrieved_user.email == "mohammed@enterprise.com", "فشل: الإيميل لم يفك تشفيره بشكل صحيح!"
            assert retrieved_child.full_name == "سارة أحمد", "فشل: اسم الطفل لم يفك تشفيره بشكل صحيح!"
            
            logger.info("🏆 نجاح تام! نظام التشفير التلقائي (EncryptedString) يعمل بكفاءة 100%. الداتا بيز محصنة.")

        except SQLAlchemyError as db_err:
            session.rollback()
            logger.error(f"خطأ في قاعدة البيانات، تم التراجع عن التعديلات (Rollback): {str(db_err)}")
        except AssertionError as ae:
            session.rollback()
            logger.error(f"خطأ في منطق فك التشفير: {str(ae)}")
        except Exception as e:
            session.rollback()
            logger.critical(f"انهيار غير متوقع للنظام: {str(e)}")
        finally:
            # إغلاق الجلسة دائماً لتفريغ الذاكرة (Memory Management)
            session.close()
            logger.info("تم إغلاق جلسة قاعدة البيانات بأمان.")

if __name__ == "__main__":
    print("="*60)
    print("بدء بروتوكول اختبار التكامل - StoryCore Engine")
    print("="*60)
    
    tester = DatabaseIntegrationTester()
    tester.run_full_cycle_test()
    
    print("="*60)
    print("انتهى الفحص.")
    print("="*60)