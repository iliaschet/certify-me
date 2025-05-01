from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color
import os
import io
import logging
from config import PDF_TEXT_POSITIONS, PDF_FONTS, PDF_FONT_SIZES, PDF_TEXT_COLORS

logger = logging.getLogger(__name__)

# Функция для конвертации hex цвета в RGB
def hex_to_rgb(hex_color):
    """Конвертирует hex цвет в RGB значения от 0 до 1"""
    # Убираем # если есть
    hex_color = hex_color.lstrip('#')
    # Конвертируем в RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    return (r, g, b)

# Регистрируем шрифты
try:
    # Регистрируем PinyonScript-Regular
    regular_path = os.path.join(os.path.dirname(__file__), 'fonts', 'PinyonScript-Regular.ttf')
    pdfmetrics.registerFont(TTFont('PinyonScript-Regular', regular_path))
    logger.debug("Шрифт PinyonScript-Regular успешно зарегистрирован")

except Exception as e:
    logger.error(f"Ошибка регистрации шрифтов: {str(e)}")
    # В случае ошибки используем стандартный шрифт
    PDF_FONTS = {key: 'Helvetica' for key in PDF_FONTS}

def add_text_to_pdf(input_pdf_path, output_pdf_path, text_data):
    """
    Добавляет текст в PDF файл
    
    Args:
        input_pdf_path: путь к входному PDF файлу
        output_pdf_path: путь для сохранения результата
        text_data: словарь с данными для вставки
    """
    logger.debug(f"Добавление текста в PDF: {input_pdf_path} -> {output_pdf_path}")
    logger.debug(f"Данные для вставки: {text_data}")
    
    # Читаем размер шаблона
    with open(input_pdf_path, 'rb') as file:
        pdf = PdfReader(file)
        page = pdf.pages[0]
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
    
    # Создаем временный PDF с текстом
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    
    # Добавляем текст на указанные позиции с соответствующими размерами шрифта и цветами
    for key, text in text_data.items():
        if key in PDF_TEXT_POSITIONS:
            x, y = PDF_TEXT_POSITIONS[key]
            font = PDF_FONTS.get(key, 'Helvetica')
            font_size = PDF_FONT_SIZES.get(key, 24)
            color_hex = PDF_TEXT_COLORS.get(key, '#000000')  # По умолчанию черный цвет
            
            # Конвертируем hex в RGB
            color = hex_to_rgb(color_hex)
            
            # Устанавливаем шрифт и цвет
            c.setFont(font, font_size)
            c.setFillColor(Color(*color))
            
            # Убеждаемся, что текст в правильной кодировке
            if isinstance(text, str):
                # Проверяем, что текст уже в UTF-8
                try:
                    text.encode('utf-8').decode('utf-8')
                except UnicodeError:
                    # Если текст не в UTF-8, пробуем преобразовать его
                    try:
                        # Пробуем разные кодировки
                        for encoding in ['cp1251', 'latin1', 'ascii']:
                            try:
                                text = text.encode(encoding).decode('utf-8')
                                break
                            except (UnicodeError, UnicodeDecodeError):
                                continue
                    except Exception as e:
                        logger.error(f"Ошибка преобразования кодировки: {str(e)}")
                        # Если не удалось преобразовать, используем текст как есть
                        pass
            
            c.drawString(x, y, text)
            logger.debug(f"Добавлен текст '{text}' в позицию {x}, {y} с шрифтом {font} размером {font_size} и цветом {color_hex}")
    
    c.save()
    packet.seek(0)
    
    # Объединяем шаблон и текст
    new_pdf = PdfReader(packet)
    output = PdfWriter()
    
    # Получаем страницу из шаблона
    template = PdfReader(input_pdf_path)
    page = template.pages[0]
    
    # Накладываем текст
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    
    # Сохраняем результат
    with open(output_pdf_path, "wb") as output_file:
        output.write(output_file)
    logger.debug(f"PDF сохранен: {output_pdf_path}")

def create_certificate(template_path, output_path, data):
    """
    Создает сертификат на основе шаблона
    
    Args:
        template_path: путь к шаблону PDF
        output_path: путь для сохранения сертификата
        data: словарь с данными для вставки
    """
    logger.debug(f"Создание сертификата: {template_path} -> {output_path}")
    if not os.path.exists(template_path):
        logger.error(f"Шаблон {template_path} не найден")
        raise FileNotFoundError(f"Шаблон {template_path} не найден")
    add_text_to_pdf(template_path, output_path, data)
