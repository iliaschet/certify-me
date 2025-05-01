import os

# Настройки сервера
SERVER_PORT = 5001
SERVER_HOST = '0.0.0.0'

# Пути к директориям
DATA_DIR = 'data'
TEMPLATES_DIR = 'templates'


# Настройки PDF
def get_pdf_template(level):
    return os.path.join(TEMPLATES_DIR, f'{level}.pdf')


# Координаты для текста на PDF (координаты в точках, 1 точка = 1/72 дюйма)
PDF_TEXT_POSITIONS = {
    'fullName': (30, 260),  # x, y координаты для ФИО
    'date': (30, 43),  # x, y координаты для даты
    'id': (200, 43)  # x, y координаты для ID
}

# Настройки шрифтов
PDF_FONTS = {
    'fullName': 'PinyonScript-Regular',  # Шрифт для ФИО
    'date': 'PinyonScript-Regular',  # Шрифт для даты
    'id': 'PinyonScript-Regular'  # Шрифт для ID
}

# Размеры шрифтов для разных полей
PDF_FONT_SIZES = {
    'fullName': 73,  # Размер шрифта для ФИО
    'date': 16,  # Размер шрифта для даты
    'id': 16  # Размер шрифта для ID
}

# Цвета текста для разных полей (hex)
PDF_TEXT_COLORS = {
    'fullName': '#9c7928',  # Синий цвет для ФИО
    'date': '#212121',  # Серый цвет для даты
    'id': '#212121'  # Светло-серый цвет для ID
}
