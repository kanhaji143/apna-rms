import os
import uuid
from pathlib import Path
from PIL import Image
from core.database import DatabaseManager

class ImageOptimizer:
    @staticmethod
    def save_and_optimize_screenshot(source_path: str, max_dimension: int = 1280, target_kb: int = 150) -> str:
        """
        Takes an uploaded screenshot, resizes it if excessively large,
        compresses it into high-quality JPEG/PNG under ~150KB,
        and saves it into the storage/screenshots folder with a unique name.
        Returns the relative or absolute path of the saved file.
        """
        if not source_path or not os.path.exists(source_path):
            return ""

        db = DatabaseManager.get_instance()
        target_dir = db.screenshots_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = f"PAY_{uuid.uuid4().hex[:10].upper()}.jpg"
        dest_path = target_dir / filename

        try:
            with Image.open(source_path) as img:
                # Convert to RGB (in case of RGBA/PNG)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")

                # Resize if larger than max_dimension
                w, h = img.size
                if w > max_dimension or h > max_dimension:
                    if w > h:
                        new_w = max_dimension
                        new_h = int(h * (max_dimension / w))
                    else:
                        new_h = max_dimension
                        new_w = int(w * (max_dimension / h))
                    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Save with progressive optimization
                quality = 85
                img.save(str(dest_path), format="JPEG", optimize=True, quality=quality)

                # Check file size and reduce quality slightly if still above target
                while os.path.getsize(str(dest_path)) > target_kb * 1024 and quality > 40:
                    quality -= 10
                    img.save(str(dest_path), format="JPEG", optimize=True, quality=quality)

            return str(dest_path)
        except Exception as e:
            print(f"Error optimizing screenshot: {e}")
            # Fallback: copy file as is
            dest_fallback = target_dir / (f"PAY_{uuid.uuid4().hex[:10].upper()}" + Path(source_path).suffix)
            import shutil
            shutil.copy2(source_path, str(dest_fallback))
            return str(dest_fallback)

    @staticmethod
    def get_thumbnail(image_path: str, size=(120, 120)):
        if not image_path or not os.path.exists(image_path):
            return None
        try:
            with Image.open(image_path) as img:
                img.thumbnail(size)
                return img.copy()
        except Exception:
            return None
