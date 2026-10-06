from database_models import SessionLocal, Story, StoryPage

def view_story(story_id):
    db = SessionLocal()
    try:
        # البحث عن القصة
        story = db.query(Story).filter(Story.id == story_id).first()
        if not story:
            print("القصة غير موجودة!")
            return
            
        print("="*60)
        print(f"📖 عنوان القصة: {story.title}")
        print(f"حالة القصة: {story.status}")
        print("="*60)
        
        # جلب الصفحات مرتبة
        pages = db.query(StoryPage).filter(StoryPage.story_id == story_id).order_by(StoryPage.page_number).all()
        
        for page in pages:
            print(f"\n[صفحة رقم {page.page_number}]")
            print(f"📝 النص العربي: {page.narrative_text_ar}")
            print(f"🎨 وصف الرسم: {page.visual_prompt_en}")
            print("-" * 40)
            
    finally:
        db.close()

if __name__ == "__main__":
    # نحن نبحث عن القصة رقم 3 التي تم توليدها للتو
    view_story(3)