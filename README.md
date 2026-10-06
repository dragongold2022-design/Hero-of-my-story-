# Kids Story System

مشروع لتوليد قصص الأطفال ورسوماتها تلقائياً وتجميعها في ملفات PDF.

## 🚀 طريقة التثبيت والتشغيل (للمطورين)

### 1. استنساخ المستودع (Clone)
```bash
git clone <REPO_URL>
cd my_compny
```

### 2. إنشاء البيئة الافتراضية وتفعيلها
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. تثبيت المكتبات المطلوبة
```bash
pip install -r requirements.txt
```

### 4. إعداد المتغيرات السرية (.env)
قم بنسخ ملف `.env.example` وتسميته `.env`:
```bash
copy .env.example .env
```
ثم ضع مفاتيح الـ API الخاصة بك:
- `GEMINI_API_KEY`: مفتاح Google Gemini API.
- `AES_SECRET_KEY`: مفتاح التشفير.

### 5. تشغيل المشروع
```bash
python main_pipeline.py
```
