import json
import os
from pdf_compiler import StoryPDFCompiler

def mock_generate_image(page_num, visual_prompt, child_photo):
    """دالة وهمية لتجربة خط الإنتاج مجاناً وبدون استهلاك أي رصيد"""
    print(f"  [محاكاة الرسوم] تجربة رسم الصفحة {page_num} بـ IP-Adapter و ControlNet...")
    images_dir = "output_images"
    os.makedirs(images_dir, exist_ok=True)
    
    # إنشاء صورة مؤقتة للتجربة البرمجية
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (1920, 1080), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((100, 100), f"Page {page_num} Preview", fill=(255, 255, 0))
    
    img_path = os.path.join(images_dir, f"page_{page_num}.png")
    img.save(img_path)
    return img_path

def run_dry_run_test():
    print("[1/4] جاري تحميل ملفات التهيئة والهيكل...")
    request_data = json.load(open("story_request_schema.json", "r", encoding="utf-8"))
    
    child_name = request_data["child_identity"]["full_name"]
    print(f"[*] بدء اختبار خط الإنتاج للطفل: {child_name}")

    # محاكاة استجابة القصة الـ 24 صفحة
    mock_story_data = {
        "pages": [
            {
                "page_number": 1,
                "narrative_text_ar": f"كَانَتْ {child_name} تُحِبُّ الرَّسْمَ وَالْمُغَامَرَاتِ كَثِيرًا فِي يَوْمِهَا الْجَمِيلِ.",
                "visual_prompt_en": "A cute Arab child drawing happily"
            }
        ]
    }

    print("[2/4] جاري محاكاة توليد الصور وحقن ملامح الوجه...")
    for page in mock_story_data["pages"]:
        mock_generate_image(
            page["page_number"], 
            page["visual_prompt_en"], 
            request_data["child_identity"]["photo_url"]
        )

    print("[3/4] جاري تجميع ملف الـ PDF والتأكد من التشكيل العربي...")
    compiler = StoryPDFCompiler()
    output_pdf = f"{child_name}_Test_Story.pdf"
    compiler.build_pdf(mock_story_data, "output_images", output_pdf)
    
    print(f"[✓] نجح الاختبار! تم تصدير الملف التجريبي: {output_pdf}")

if __name__ == "__main__":
    run_dry_run_test()