import os
import base64
import logging
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# إعداد نظام المراقبة والتسجيل المعياري (Enterprise Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("StoryCore.SecurityManager")

class SecurityManager:
    """
    مدير الحماية المركزي للنظام (Singleton Class).
    مسؤول عن التشفير وفك التشفير الآمن للبيانات الحساسة باستخدام AES-GCM.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecurityManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """تهيئة مفاتيح التشفير من ملفات البيئة بأمان مطلق"""
        try:
            load_dotenv()
            encoded_key = os.getenv("AES_SECRET_KEY")
            
            if not encoded_key:
                logger.critical("فشل أمني: مفتاح AES_SECRET_KEY مفقود من ملف .env")
                raise ValueError("System Halt: Missing Encryption Key.")
                
            self._key = base64.b64decode(encoded_key)
            
            # التحقق من طول المفتاح لمعيار AES-256 الصحيح (32 بايت)
            if len(self._key) != 32:
                logger.critical("فشل أمني: طول مفتاح AES غير صالح، يجب أن يكون 32 بايت.")
                raise ValueError("Invalid AES Key Length.")
                
            logger.info("تمت تهيئة SecurityManager بنجاح وتحميل مفاتيح الحماية بأمان.")
            
        except (ValueError, base64.binascii.Error) as e:
            logger.error(f"خطأ في تهيئة مفاتيح الحماية: {str(e)}")
            raise
        except Exception as e:
            logger.critical(f"خطأ غير متوقع أثناء التهيئة الأمنية: {str(e)}")
            raise

    def encrypt_data(self, plaintext: str) -> str:
        """تشفير النصوص الحساسة باستخدام خوارزمية AES-GCM المعتمدة أمنياً"""
        if not plaintext:
            return plaintext
            
        try:
            # توليد متجه تهيئة عشوائي فريد (Nonce) لكل عملية تشفير لمنع هجمات التكرار
            nonce = get_random_bytes(12)
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
            
            ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode('utf-8'))
            
            # دمج الـ Nonce و Tag و Ciphertext وتحويلهم لـ Base64 لتخزينها بسهولة في قاعدة البيانات
            encrypted_payload = base64.b64encode(nonce + tag + ciphertext).decode('utf-8')
            return encrypted_payload
            
        except Exception as e:
            logger.error(f"فشل في عملية التشفير: {str(e)}")
            raise RuntimeError("Encryption Process Failed")

    def decrypt_data(self, encrypted_payload: str) -> str:
        """فك تشفير النصوص مع التحقق الصارم من سلامة وعدم التلاعب بالبيانات"""
        if not encrypted_payload:
            return encrypted_payload
            
        try:
            raw_data = base64.b64decode(encrypted_payload)
            
            # استخراج المكونات بناءً على أطوالها الهندسية المحددة
            nonce = raw_data[:12]
            tag = raw_data[12:28]
            ciphertext = raw_data[28:]
            
            cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
            
            return plaintext.decode('utf-8')
            
        except ValueError:
            logger.warning("محاولة فك تشفير فاشلة: البيانات تالفة أو تم التلاعب بها (MAC Check Failed).")
            raise ValueError("Data Integrity Compromised.")
        except Exception as e:
            logger.error(f"فشل في عملية فك التشفير: {str(e)}")
            raise RuntimeError("Decryption Process Failed")