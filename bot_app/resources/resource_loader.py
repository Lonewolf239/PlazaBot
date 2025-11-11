import os
from pathlib import Path
from typing import Optional
from PIL import Image, ImageFont


class ResourceLoader:
    @staticmethod
    def load_image(dir_name: str, image_name: str, size: Optional[int] = None) -> Optional[Image.Image]:
        """
        Загружает и масштабирует PNG изображение

        Args:
            dir_name: Название папки
            image_name: Название файла PNG
            size: Размер для масштабирования (если None, оригинальный размер)

        Returns:
            PIL Image или None если файл не найден
        """
        script_dir = Path(__file__).parent.parent
        resources_path = script_dir / "resources" / dir_name / image_name
        try:
            if not os.path.exists(resources_path):
                print(f"⚠️ Файл не найден: {resources_path}")
                return None
            img = Image.open(resources_path).convert('RGBA')
            if size:
                img = img.resize((size, size), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"❌ Ошибка при загрузке изображения {resources_path}: {e}")
            return None

    @staticmethod
    def paste_image_centered(base_img: Image.Image, overlay_img: Image.Image, x: int, y: int, cell_size: int):
        """
        Вставляет изображение в центр ячейки

        Args:
            base_img: Базовое изображение для вставки
            overlay_img: Изображение для вставки
            x: Координаты верхнего левого угла ячейки
            y: Координаты верхнего левого угла ячейки
            cell_size: Размер ячейки
        """
        overlay_width, overlay_height = overlay_img.size
        paste_x = x + (cell_size - overlay_width) // 2
        paste_y = y + (cell_size - overlay_height) // 2
        base_img.paste(overlay_img, (paste_x, paste_y), overlay_img)

    @staticmethod
    def load_fonts():
        """Загружает шрифты с fallback механизмом"""
        try:
            return {
                'medium': ImageFont.truetype("arial.ttf", 28),
                'small': ImageFont.truetype("arial.ttf", 20),
            }
        except IOError:
            try:
                return {
                    'medium': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28),
                    'small': ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20),
                }
            except IOError:
                default = ImageFont.load_default()
                return {
                    'medium': default,
                    'small': default,
                }