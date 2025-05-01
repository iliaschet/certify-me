from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from pdf_utils import create_certificate
import json
from datetime import datetime
import logging
from config import (
    SERVER_PORT, SERVER_HOST,
    DATA_DIR,
    get_pdf_template
)
import uuid
import zipfile
import io

# TODO - логирование добавлений и удалений сертификатов

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Создаем директории
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Константы для уровней сертификатов
CERTIFICATE_LEVELS = [
    {"label": "Certificate of appreciation", "value": "level-1"},
    {"label": "Certificate of achievement", "value": "level-2"},
    {"label": "Distinguished Certificate", "value": "level-3"},
]

# Путь к директории с сертификатами
CERTIFICATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certificates')

# Создаем директорию, если она не существует
if not os.path.exists(CERTIFICATES_DIR):
    os.makedirs(CERTIFICATES_DIR)
    logger.info(f"Создана директория для сертификатов: {CERTIFICATES_DIR}")

def save_certificate_data(data):
    data_file = os.path.join(DATA_DIR, 'certificates.json')
    certificates = []
    
    # Загружаем существующие сертификаты
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            certificates = json.load(f)
    
    # Добавляем новый сертификат
    new_certificate = {
        **data,
        'addedAt': data.get('addedAt', datetime.now().isoformat())
    }
    certificates.append(new_certificate)
    
    # Сохраняем обновленный список
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(certificates, f, ensure_ascii=False)
    logger.debug(f"Сохранены данные сертификата: {new_certificate}")

def load_certificate_data(cert_id):
    """
    Загружает данные сертификата по id
    
    Args:
        cert_id: id сертификата
    """
    data_file = os.path.join(DATA_DIR, 'certificates.json')
    if os.path.exists(data_file):
        with open(data_file, 'r', encoding='utf-8') as f:
            certificates = json.load(f)
            # Ищем сертификат по id
            for cert in certificates:
                if cert.get('id') == cert_id:
                    return cert
    return None

def delete_certificate_data(cert_id):
    """
    Удаляет данные сертификата из certificates.json
    
    Args:
        cert_id: id сертификата
    """
    data_file = os.path.join(DATA_DIR, 'certificates.json')
    if not os.path.exists(data_file):
        return False
        
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            certificates = json.load(f)
        
        # Находим и удаляем сертификат по id
        certificates = [cert for cert in certificates if cert.get('id') != cert_id]
        
        # Сохраняем обновленный список
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(certificates, f, ensure_ascii=False)
            
        return True
    except Exception as e:
        logger.error(f"Ошибка при удалении данных сертификата: {str(e)}")
        return False

def generate_id():
    """Генерирует уникальный id для сертификата"""
    return str(uuid.uuid4())

@app.route('/levels', methods=['GET'])
def get_certificate_levels():
    """Получение списка доступных уровней сертификатов"""
    return jsonify(CERTIFICATE_LEVELS)

@app.route('/certificates', methods=['GET'])
def get_certificates():
    """Получение списка всех сертификатов"""
    certificates = []
    
    # Проверяем существование директории
    if not os.path.exists(CERTIFICATES_DIR):
        logger.warning(f"Директория {CERTIFICATES_DIR} не существует")
        return jsonify([])
    
    try:
        # Читаем файлы из директории
        for filename in os.listdir(CERTIFICATES_DIR):
            if filename.endswith('.pdf'):
                file_path = os.path.join(CERTIFICATES_DIR, filename)
                file_stat = os.stat(file_path)
                
                # Получаем id из имени файла
                cert_id = filename.replace('.pdf', '')
                
                # Загружаем данные сертификата из JSON
                cert_data = load_certificate_data(cert_id)
                if cert_data:
                    certificates.append({
                        'id': cert_id,
                        'fullName': cert_data.get('fullName', 'Неизвестно'),
                        'date': cert_data.get('date', 'Неизвестно'),
                        'addedAt': datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                        'level': cert_data.get('level', '')
                    })
        
        return jsonify(certificates)
    except Exception as e:
        logger.error(f"Ошибка при получении списка сертификатов: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_certificates():
    """Генерация сертификатов"""
    data = request.json
    
    if not data or 'names' not in data or 'date' not in data or 'cert' not in data:
        return jsonify({'error': 'Необходимо указать names, date и cert'}), 400
    
    # Разделяем имена по запятым и переносам строк, удаляем лишние пробелы
    names_raw = data['names']
    names = [name.strip() for name in names_raw.replace('\n', ',').split(',') if name.strip()]
    date = data['date']
    cert_level = data['cert']
    
    generated_files = []
    
    # Фиксируем время создания для всех сертификатов в этом запросе
    current_time = datetime.now().isoformat()
    
    for name in names:
        name = name.strip()
        if not name:
            continue
            
        # Ограничиваем длину ФИО до 32 символов
        if len(name) > 32:
            name = name[:32]
            logger.info(f"ФИО сокращено до 32 символов: {name}")
            
        # Генерируем уникальный id
        cert_id = generate_id()
            
        # Формируем имя файла используя id
        filename = f"{cert_id}.pdf"
        file_path = os.path.join(CERTIFICATES_DIR, filename)
        
        # Генерируем PDF с использованием шаблона
        try:
            # Подготавливаем данные для вставки в PDF
            text_data = {
                'fullName': name,
                'date': datetime.fromisoformat(date.replace("Z", "+00:00")).strftime("%Y-%m-%d"),
                'id': cert_id
            }

            # Получаем путь к шаблону для конкретного уровня
            template_path = get_pdf_template(cert_level)
            
            # Создаем сертификат
            create_certificate(template_path, file_path, text_data)
            
            # Сохраняем данные сертификата с фиксированным временем
            save_certificate_data({
                'id': cert_id,
                'fullName': name,
                'date': date,
                'level': cert_level,
                'addedAt': current_time
            })
            
            generated_files.append(filename)
            logger.info(f"Сгенерирован сертификат: {filename}")
        except Exception as e:
            logger.error(f"Ошибка при генерации сертификата для {name}: {str(e)}")
            return jsonify({'error': f'Ошибка при генерации сертификата: {str(e)}'}), 500
    
    return jsonify({
        'message': f'Сгенерировано {len(generated_files)} сертификатов',
        'files': generated_files
    })

@app.route('/certificates/<cert_id>', methods=['DELETE'])
def delete_certificate(cert_id):
    """Удаление сертификата"""
    try:
        # Убираем .pdf из cert_id, если оно есть
        cert_id = cert_id.replace('.pdf', '')
        file_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
        logger.debug(f"Попытка удаления сертификата: {file_path}")
        
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            logger.warning(f"Файл не найден при удалении: {file_path}")
            # Проверяем, есть ли данные в JSON
            if not load_certificate_data(cert_id):
                # Если файла нет и данных в JSON тоже нет, значит сертификат уже удален
                return jsonify({'message': 'Сертификат уже удален'}), 200
            else:
                # Если файла нет, но данные в JSON есть, удаляем только данные
                delete_certificate_data(cert_id)
                return jsonify({'message': 'Данные сертификата удалены'}), 200
        
        try:
            # Удаляем файл
            os.remove(file_path)
            logger.info(f"Файл удален: {file_path}")
            
            # Удаляем данные из JSON
            if delete_certificate_data(cert_id):
                logger.info(f"Данные сертификата удалены из JSON: {cert_id}")
            else:
                logger.warning(f"Не удалось удалить данные сертификата из JSON: {cert_id}")
            
            return jsonify({'message': 'Сертификат успешно удален'})
        except Exception as e:
            logger.error(f"Ошибка при удалении файла: {str(e)}")
            return jsonify({'error': f'Ошибка при удалении сертификата: {str(e)}'}), 500
            
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса на удаление: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/certificates/<cert_id>', methods=['GET'])
def get_certificate(cert_id):
    """Получение сертификата по id"""
    try:
        # Убираем .pdf из cert_id, если оно есть
        cert_id = cert_id.replace('.pdf', '')
        file_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
        logger.debug(f"Запрос сертификата: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"Файл не найден: {file_path}")
            return jsonify({'error': 'Файл не найден'}), 404
            
        logger.info(f"Отправка файла: {file_path}")
        return send_file(
            file_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f"{cert_id}.pdf"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении сертификата: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generated/<path:filename>')
def serve_generated(filename):
    return send_from_directory(DATA_DIR, filename)

@app.route('/recently', methods=['GET'])
def get_recently_certificates():
    """Получение архива с последними созданными сертификатами"""
    try:
        # Загружаем данные сертификатов
        data_file = os.path.join(DATA_DIR, 'certificates.json')
        if not os.path.exists(data_file):
            return jsonify({'error': 'Сертификаты не найдены'}), 404
            
        with open(data_file, 'r', encoding='utf-8') as f:
            certificates = json.load(f)
            
        if not certificates:
            return jsonify({'error': 'Сертификаты не найдены'}), 404
            
        # Сортируем сертификаты по дате добавления (от новых к старым)
        sorted_certificates = sorted(
            certificates, 
            key=lambda x: x.get('addedAt', ''), 
            reverse=True
        )
        
        # Находим время добавления самого последнего сертификата
        if not sorted_certificates:
            return jsonify({'error': 'Сертификаты не найдены'}), 404
            
        latest_time = sorted_certificates[0].get('addedAt', '')
        
        # Фильтруем сертификаты, добавленные в то же время
        latest_certificates = [
            cert for cert in sorted_certificates 
            if cert.get('addedAt', '') == latest_time
        ]
        
        # Создаем архив в памяти
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            for cert in latest_certificates:
                cert_id = cert.get('id')
                if cert_id:
                    file_path = os.path.join(CERTIFICATES_DIR, f"{cert_id}.pdf")
                    if os.path.exists(file_path):
                        # Добавляем файл в архив с именем, включающим ФИО
                        full_name = cert.get('fullName', 'unknown')
                        safe_name = "".join(c for c in full_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_name = safe_name.replace(' ', '_')
                        if not safe_name:
                            safe_name = 'unknown'
                        zip_filename = f"{safe_name}_{cert_id}.pdf"
                        zf.write(file_path, zip_filename)
        
        memory_file.seek(0)
        
        # Форматируем дату для отображения
        date_obj = datetime.fromisoformat(latest_time)
        formatted_date = date_obj.strftime('%d.%m.%Y_%H.%M')
        
        # Возвращаем архив
        return send_file(
            memory_file,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'certificates_{formatted_date}.zip'
        )
    except Exception as e:
        logger.error(f"Ошибка при создании архива сертификатов: {str(e)}")
        return jsonify({'error': f'Ошибка при создании архива: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)