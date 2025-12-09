import os, sys, requests
from pathlib import Path
from dotenv import load_dotenv

# Попытка загрузить .env файл
load_dotenv()


def read_text_file(file_path: str) -> str:
    """Читает содержимое текстового файла."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        if not content:
            print("⚠ Предупреждение: файл пустой")
        
        return content
        
    except Exception as e:
        raise IOError(f"Ошибка при чтении файла: {e}")


def send_message(bot_token: str, chat_id: str, text: str) -> bool:
    """Отправляет сообщение в Telegram через бота."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        
        # Получаем JSON ответ даже при ошибке
        try:
            result = response.json()
        except:
            response.raise_for_status()
            return False
        
        if result.get("ok"):
            print(f"✓ Сообщение успешно отправлено в чат {chat_id}")
            return True
        else:
            error_code = result.get("error_code", "?")
            error_desc = result.get("description", "Неизвестная ошибка")
            print(f"✗ Ошибка {error_code}: {error_desc}")
            
            # Дополнительные подсказки для частых ошибок
            if "chat not found" in error_desc.lower():
                print(f"  💡 Убедитесь, что бот добавлен в группу/канал или начат диалог с пользователем")
            elif "bad request" in error_desc.lower():
                if chat_id.startswith("@"):
                    print(f"  💡 Проверьте правильность username: {chat_id}")
                    print(f"  💡 Убедитесь, что это публичный канал/группа или бот имеет доступ")
                else:
                    print(f"  💡 Проверьте правильность chat_id: {chat_id}")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Ошибка при отправке: {e}")
        return False


def read_chat_ids_file(file_path: str) -> list:
    """Читает список chat_id из файла (каждая строка - один chat_id)."""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Убираем пустые строки, пробелы и комментарии (строки начинающиеся с #)
        chat_ids = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                chat_ids.append(line)
        
        if not chat_ids:
            raise ValueError(f"Файл {file_path} пустой или не содержит chat_id")
        
        return chat_ids
        
    except Exception as e:
        raise IOError(f"Ошибка при чтении файла chat_id: {e}")


def send_message_from_file():
    """Основная функция для отправки сообщения из файла во все группы из списка."""
    try:
        # Загружаем конфигурацию из переменных окружения
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_ids_file = os.getenv("CHAT_IDS_FILE", "chat_ids.txt")
        message_file = os.getenv("MESSAGE_FILE", "message.txt")
        
        # Проверяем обязательные параметры
        if not bot_token:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN не указан. "
                "Установите переменную окружения или создайте .env файл"
            )
        
        # Читаем список chat_id из файла
        print(f"📋 Чтение списка групп из файла: {chat_ids_file}")
        chat_ids = read_chat_ids_file(chat_ids_file)
        print(f"✓ Найдено групп: {len(chat_ids)}\n")
        
        # Читаем сообщение из файла
        print(f"📖 Чтение сообщения из файла: {message_file}")
        text = read_text_file(message_file)
        print()
        
        # Отправляем сообщение во все группы
        success_count = 0
        fail_count = 0
        
        for i, chat_id in enumerate(chat_ids, 1):
            print(f"[{i}/{len(chat_ids)}] 📤 Отправка в чат: {chat_id}")
            if send_message(bot_token, chat_id, text):
                success_count += 1
            else:
                fail_count += 1
            print()
        
        # Итоговая статистика
        print("=" * 50)
        print(f"✓ Успешно отправлено: {success_count}")
        if fail_count > 0:
            print(f"✗ Ошибок: {fail_count}")
        print("=" * 50)
        
        return 0 if fail_count == 0 else 1
        
    except ValueError as e:
        print(f"✗ Ошибка конфигурации: {e}")
        return 1
    except FileNotFoundError as e:
        print(f"✗ {e}")
        return 1
    except IOError as e:
        print(f"✗ {e}")
        return 1
    except Exception as e:
        print(f"✗ Неожиданная ошибка: {e}")
        return 1




def main():
    """Главная функция - точка входа в программу."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "help" or command == "--help" or command == "-h":
            print("Использование:")
            print("  python main.py              - отправить сообщение из файла во все группы")
            print("  python main.py help          - показать эту справку")
            sys.exit(0)
        else:
            print(f"✗ Неизвестная команда: {command}")
            print("Используйте 'python main.py help' для справки")
            sys.exit(1)
    else:
        sys.exit(send_message_from_file())


if __name__ == "__main__":
    main()
