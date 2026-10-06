import os
from json import load
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

class StoryPDFCompiler:
    def __init__(self, font_path="Cairo-Bold.ttf"):
        # استخدام خط الويندوز الداعم للعربية تلقائياً في حال عدم وجود Cairo-Bold.ttf
        if not os.path.exists(font_path):
            system_font = r"C:\Windows\Fonts\arialbd.ttf"
            if os.path.exists(system_font):
                font_path = system_font
            else:
                font_path = r"C:\Windows\Fonts\arial.ttf"

        pdfmetrics.registerFont(TTFont("ArabicFont", font_path))
        self.page_width, self.page_height = landscape(A4)
    def format_arabic_text(self, text):
        """إعادة تشكيل النص العربي ليدعم الاتجاه من اليمين لليسار والتشكيل"""
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)

    def build_pdf(self, json_story_data, images_dir, output_pdf_path):
        """دمج الصور والنصوص في ملف PDF فاخر بدقة 300 DPI"""
        c = canvas.Canvas(output_pdf_path, pagesize=landscape(A4))
        
        for page_data in json_story_data["pages"]:
            page_num = page_data["page_number"]
            text_ar = page_data["narrative_text_ar"]
            img_path = os.path.join(images_dir, f"page_{page_num}.png")

            # 1. رسم الصورة الفاخرة على كامل مساحة الصفحة
            if os.path.exists(img_path):
                c.drawImage(img_path, 0, 0, width=self.page_width, height=self.page_height)

            # 2. إضافة خلفية شبه شفافة للنص لضمان التباين والوضوح
            c.setFillColorRGB(0, 0, 0, alpha=0.45)
            c.rect(0, 0, self.page_width, 110, fill=1, stroke=0)

            # 3. صياغة النص العربي وتقسيمه تلقائياً على أسطر مرتبة
            c.setFont("ArabicFont", 18)
            c.setFillColorRGB(1, 1, 1) # لون أبيض ناصع
            
            words = text_ar.split(' ')
            lines = [' '.join(words[i:i+8]) for i in range(0, len(words), 8)]
            
            y_position = 70
            for line in lines:
                formatted_line = self.format_arabic_text(line)
                c.drawCentredString(self.page_width / 2, y_position, formatted_line)
                y_position -= 25 # المسافة العمودية بين الأسطر

            # الانتقال للصفحة التالية
            c.showPage()

        c.save()
        print(f"تم تصدير القصة بنجاح: {output_pdf_path}")