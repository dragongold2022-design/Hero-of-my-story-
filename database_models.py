import enum
import logging
from datetime import datetime
from sqlalchemy import create_engine, ForeignKey, String, Integer, Text, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy.types import TypeDecorator
from sqlalchemy.exc import SQLAlchemyError

# استدعاء مدير الحماية
from security_manager import SecurityManager

# إعداد نظام المراقبة المعياري (Enterprise Logging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(name)s: %(message)s')
logger = logging.getLogger("StoryCore.Database")

# ==========================================
# 1. المترجم السري (الكلاس الوسيط للتشفير)
# ==========================================
class EncryptedString(TypeDecorator):
    """
    كلاس معماري وسيط (Decorator) يقوم بتشفير النصوص الحساسة تلقائياً قبل حفظها،
    وفك تشفيرها تلقائياً عند استدعائها. متوافق تماماً مع SQLAlchemy 2.0.
    """
    impl = String
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.security_manager = SecurityManager()

    def process_bind_param(self, value, dialect):
        """التشفير قبل الحفظ في قاعدة البيانات"""
        if value is not None:
            try:
                return self.security_manager.encrypt_data(value)
            except Exception as e:
                logger.error(f"فشل أمني (تشفير) أثناء الحفظ: {str(e)}")
                raise SQLAlchemyError("Encryption Engine Failed during DB Insert.")
        return value

    def process_result_value(self, value, dialect):
        """فك التشفير عند القراءة من قاعدة البيانات"""
        if value is not None:
            try:
                return self.security_manager.decrypt_data(value)
            except Exception as e:
                logger.error(f"فشل أمني (فك تشفير) أثناء القراءة: {str(e)}")
                raise SQLAlchemyError("Decryption Engine Failed during DB Read.")
        return value


# ==========================================
# 2. الكلاس الأساسي والحالات الثابتة (Enums)
# ==========================================
class Base(DeclarativeBase):
    pass

class GenderEnum(enum.Enum):
    MALE = "male"
    FEMALE = "female"

class StoryStatusEnum(enum.Enum):
    PENDING_TEXT = "pending_text"          # جاري توليد النص
    REVIEWING = "reviewing"                # في انتظار المراجعة البشرية
    GENERATING_IMAGES = "generating_images" # جاري توليد الصور عبر ControlNet/IP-Adapter
    COMPLETED = "completed"                # جاهزة للطباعة
    FAILED = "failed"                      # فشل

class PageImageStatusEnum(enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ==========================================
# 3. جداول قاعدة البيانات (Models) 
# ==========================================
class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    # حقل الإيميل: نستخدم EncryptedString لحمايته
    email: Mapped[str] = mapped_column(EncryptedString(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    children: Mapped[list["ChildProfile"]] = relationship("ChildProfile", back_populates="user", cascade="all, delete-orphan")

class ChildProfile(Base):
    __tablename__ = "children_profiles"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # حقل الاسم والهوايات: تشفير كامل لأنها بيانات طفل حساسة
    full_name: Mapped[str] = mapped_column(EncryptedString(255), nullable=False)
    gender: Mapped[GenderEnum] = mapped_column(Enum(GenderEnum), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    photo_url: Mapped[str] = mapped_column(String(255), nullable=True) # مسار صورة الوجه لـ IP-Adapter
    hobbies: Mapped[str] = mapped_column(EncryptedString(1000), nullable=True) 
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="children")
    stories: Mapped[list["Story"]] = relationship("Story", back_populates="child", cascade="all, delete-orphan")

class Story(Base):
    __tablename__ = "stories"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    child_id: Mapped[int] = mapped_column(ForeignKey("children_profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=True)
    status: Mapped[StoryStatusEnum] = mapped_column(Enum(StoryStatusEnum), default=StoryStatusEnum.PENDING_TEXT)
    pdf_path: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    child: Mapped["ChildProfile"] = relationship("ChildProfile", back_populates="stories")
    pages: Mapped[list["StoryPage"]] = relationship("StoryPage", back_populates="story", cascade="all, delete-orphan")

class StoryPage(Base):
    __tablename__ = "story_pages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    story_id: Mapped[int] = mapped_column(ForeignKey("stories.id"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    narrative_text_ar: Mapped[str] = mapped_column(Text, nullable=False)
    visual_prompt_en: Mapped[str] = mapped_column(Text, nullable=False)
    
    image_path: Mapped[str] = mapped_column(String(255), nullable=True)
    image_status: Mapped[PageImageStatusEnum] = mapped_column(Enum(PageImageStatusEnum), default=PageImageStatusEnum.PENDING)

    story: Mapped["Story"] = relationship("Story", back_populates="pages")

# ==========================================
# 4. محرك قاعدة البيانات (Database Engine)
# ==========================================
def init_db(db_url="sqlite:///kids_story_system.db"):
    try:
        engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.info("تم الاتصال بقاعدة البيانات وتهيئة الجداول بنجاح مع تفعيل نظام التشفير.")
        return engine, SessionLocal
    except SQLAlchemyError as e:
        logger.critical(f"فشل ذريع في الاتصال بقاعدة البيانات: {str(e)}")
        raise

if __name__ == "__main__":
    print("[*] جاري تهيئة وهندسة قاعدة البيانات...")
    engine, Session = init_db()
    print("[✓] تم إنشاء الجداول بنجاح! قاعدة البيانات جاهزة ومحصنة للعمل.")
    # ==========================================
# إعدادات محرك الاتصال بقاعدة البيانات (Database Engine)
# ==========================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. إنشاء محرك الاتصال بقاعدة بيانات SQLite المحلية
engine = create_engine("sqlite:///kids_story_system.db", connect_args={"check_same_thread": False})

# 2. إنشاء بوابة الاتصال (SessionLocal) التي يبحث عنها ملف db_integrator
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. أمر بناء الجداول الفعلي (لن يمسح البيانات إذا كانت الجداول موجودة مسبقاً)
Base.metadata.create_all(bind=engine)