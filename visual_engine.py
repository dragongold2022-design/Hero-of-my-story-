import os
import logging
import torch
from PIL import Image
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel, DDIMScheduler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger("StoryCore.FinalEngine")

class FinalVisualEngine:
    def __init__(self):
        logger.info("🚀 تهيئة المحرك النهائي (Deliberate + ControlNet + IP-Adapter)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        if self.device == "cpu":
            raise RuntimeError("CUDA is mandatory!")

        # 1. تحميل ControlNet (للتحكم بالوضعية وحل مشكلة الأيدي)
        logger.info("جاري تحميل ControlNet (OpenPose)...")
        self.controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/control_v11p_sd15_openpose",
            torch_dtype=torch.float16
        )

        # 2. تحميل الموديل الأساسي (Deliberate - ملك التشريح والملامح)
        logger.info("جاري تحميل الموديل (XpucT/Deliberate)... (حجمه حوالي 2 جيجا لمرة واحدة)")
        self.pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "stablediffusionapi/deliberate-v3", # النسخة البرمجية المطابقة تماماً
            controlnet=self.controlnet,
            torch_dtype=torch.float16,
            safety_checker=None
        )

        # 3. إعداد المجدول
        self.pipe.scheduler = DDIMScheduler.from_config(self.pipe.scheduler.config)

        # 4. دمج IP-Adapter (للهوية)
        logger.info("جاري دمج IP-Adapter...")
        self.pipe.load_ip_adapter(
            "h94/IP-Adapter", 
            subfolder="models", 
            weight_name="ip-adapter-plus-face_sd15.bin"
        )
        # توازن ممتاز لـ Deliberate لضمان دمج الوجه بدون رعب
        self.pipe.set_ip_adapter_scale(0.65)

        # 5. حماية الذاكرة لتعمل بسلاسة على 8GB
        self.pipe.enable_model_cpu_offload()
        logger.info("✅ المحرك جاهز للإنتاج!")

    def generate_test(self, prompt, neg_prompt, face_path, pose_path, output_path):
        if not os.path.exists(face_path) or not os.path.exists(pose_path):
            logger.error("⚠️ تأكد من وجود صورتي: face_test.jpeg و pose_test.png")
            return

        face_img = Image.open(face_path).convert("RGB")
        pose_img = Image.open(pose_path).convert("RGB") # الهيكل العظمي

        logger.info("🎨 جاري التوليد الآن (بياخذ ثواني معدودة)...")
        image = self.pipe(
            prompt=prompt,
            negative_prompt=neg_prompt,
            image=pose_img,
            ip_adapter_image=face_img,
            num_inference_steps=35,
            guidance_scale=7.5,
            controlnet_conditioning_scale=1.0 # إجبار الموديل على الالتزام بالهيكل العظمي
        ).images[0]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        logger.info(f"✅ تم الحفظ بنجاح في: {output_path}")

if __name__ == "__main__":
    engine = FinalVisualEngine()
    
    # البرومبت الجديد الخالي من كلمة Pixar لتجنب القوالب الآسيوية
    test_prompt = (
        "Western 3D animation style, Disney style, masterpiece, "
        "cute 5-year-old Middle Eastern girl, authentic Arab facial features, "
        "dark brown curly hair in two pigtails, big brown eyes, "
        "wearing a yellow t-shirt and blue denim overalls, sitting in a bright sunny room, "
        "perfect anatomy, perfectly drawn hands, 5 fingers"
    )
    
    # الجدار الناري الصارم
    neg_prompt = (
        "Asian, anime, manga, oriental, chinese, deformed hands, bad hands, missing fingers, extra fingers, "
        "fused fingers, mutated, ugly, uncanny, bad anatomy"
    )
    
    # ⚠️ تذكير: يجب أن يكون لديك صورة باسم pose_test.png (خريطة هيكل عظمي OpenPose)
    engine.generate_test(
        prompt=test_prompt, 
        neg_prompt=neg_prompt, 
        face_path="face_test.jpeg", 
        pose_path="pose_test.png", 
        output_path="output_images/deliberate_test.png"
    )