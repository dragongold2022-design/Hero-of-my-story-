import logging
from security_manager import SecurityManager

# إعداد نظام المراقبة المعياري للاختبار
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("StoryCore.SecurityTest")

class SecurityDiagnostics:
    """
    كلاس هندسي مخصص لاختبار كفاءة وسلامة مدير الحماية (SecurityManager).
    يطبق مبدأ فصل الاهتمامات ولاختبار الحالات الطبيعية وحالات التلاعب (Edge Cases).
    """
    
    def __init__(self):
        logger.info("جاري تهيئة بيئة الاختبار وربطها بمدير الحماية...")
        try:
            # استدعاء الكلاس (الذي سيعمل كـ Singleton)
            self.sec_manager = SecurityManager()
        except Exception as e:
            logger.critical(f"فشل تشغيل بيئة الاختبار: {str(e)}")
            raise

    def test_standard_encryption_flow(self):
        """اختبار دورة التشفير وفك التشفير الطبيعية"""
        test_string = "بيانات حساسة: الطفل أحمد، عمره 6 سنوات، يحب الفضاء"
        logger.info(f"النص الأصلي: {test_string}")
        
        try:
            # 1. اختبار التشفير
            encrypted_data = self.sec_manager.encrypt_data(test_string)
            logger.info(f"النص المشفر (مخزن في قاعدة البيانات): {encrypted_data}")
            
            # 2. اختبار فك التشفير
            decrypted_data = self.sec_manager.decrypt_data(encrypted_data)
            logger.info(f"النص بعد فك التشفير: {decrypted_data}")
            
            # 3. التحقق من التطابق
            assert test_string == decrypted_data, "فشل التطابق: النص المسترجع يختلف عن الأصلي!"
            logger.info("✅ نجاح: دورة التشفير وفك التشفير تعمل بكفاءة تامة 100%.")
            
            return encrypted_data
            
        except AssertionError as ae:
            logger.error(f"خطأ في منطق البيانات: {str(ae)}")
        except Exception as e:
            logger.error(f"حدث خطأ غير متوقع أثناء الاختبار الطبيعي: {str(e)}")

    def test_tampering_resistance(self, valid_encrypted_data: str):
        """اختبار قوة النظام ضد التلاعب بالبيانات (محاكاة هجوم اختراق)"""
        logger.info("--- بدء اختبار مناعة النظام ضد التلاعب بالبيانات ---")
        
        # نقوم بتغيير حرف واحد فقط في البيانات المشفرة لمحاكاة تلاعب هاكر في قاعدة البيانات
        tampered_data = valid_encrypted_data[:-5] + "XXXXX"
        logger.warning(f"تم حقن بيانات متلاعب بها: {tampered_data}")
        
        try:
            # محاولة فك تشفير البيانات المزيفة (يجب أن يفشل الكلاس ويصطاد الخطأ)
            self.sec_manager.decrypt_data(tampered_data)
            logger.critical("❌ فشل أمني كارثي: النظام قام بفك تشفير بيانات تم التلاعب بها!")
        except ValueError as ve:
            # هذا هو السلوك الهندسي المطلوب والمثالي
            logger.info(f"✅ نجاح أمني: تم رصد التلاعب واصطياد الخطأ بنجاح (MAC Check). التفاصيل: {str(ve)}")
        except Exception as e:
            logger.error(f"خطأ غير متوقع أثناء محاكاة الهجوم: {str(e)}")

# نقطة تشغيل السكريبت
if __name__ == "__main__":
    print("="*50)
    print("بدء تشغيل بروتوكول التشخيص الأمني - StoryCore Engine")
    print("="*50)
    
    tester = SecurityDiagnostics()
    
    # تنفيذ الاختبارات
    encrypted_payload = tester.test_standard_encryption_flow()
    
    if encrypted_payload:
        tester.test_tampering_resistance(encrypted_payload)
        
    print("="*50)
    print("انتهى الاختبار.")
    print("="*50)