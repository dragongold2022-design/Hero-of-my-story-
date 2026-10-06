import torch

print("="*60)
print(f"📦 إصدار PyTorch المثبت لديك: {torch.__version__}")

if torch.cuda.is_available():
    print("✅ ممتاز جداً! البايثون يرى كرت الشاشة وهو جاهز للعمل.")
    print(f"🚀 اسم كرت الشاشة المتصل: {torch.cuda.get_device_name(0)}")
else:
    print("❌ تحذير: البايثون لا يرى كرت الشاشة! (سيقوم بالرسم ببطء شديد على المعالج العادي CPU)")
print("="*60)