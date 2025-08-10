#!/usr/bin/env python3
"""
Тест подключения к МойСклад API
"""

import urllib.request
import json
import ssl

# Токен API
TOKEN = "7bbede5c5ac9c28ddf7995042fcbbe1fecb274e1"

def test_moysklad():
    """Простой тест API МойСклад"""
    
    print("🔍 Тестирование подключения к МойСклад...")
    print("-" * 50)
    
    # URL для теста - получаем информацию о компании
    url = "https://api.moysklad.ru/api/remap/1.2/context/companysettings"
    
    # Создаем запрос
    request = urllib.request.Request(url, method='GET')
    
    # Добавляем только необходимые заголовки
    request.add_header('Authorization', f'Bearer {TOKEN}')
    
    # Отключаем проверку SSL для теста
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        # Выполняем запрос
        with urllib.request.urlopen(request, context=ssl_context) as response:
            data = response.read()
            result = json.loads(data.decode('utf-8'))
            
            print("✅ Успешное подключение к МойСклад!")
            print("\n📊 Информация о компании:")
            
            if 'name' in result:
                print(f"  Название: {result.get('name', 'Не указано')}")
            if 'legalTitle' in result:
                print(f"  Юр. лицо: {result.get('legalTitle', 'Не указано')}")
            
            # Теперь попробуем получить товары
            print("\n📦 Проверка доступа к товарам...")
            
            url2 = "https://api.moysklad.ru/api/remap/1.2/entity/product?limit=1"
            request2 = urllib.request.Request(url2, method='GET')
            request2.add_header('Authorization', f'Bearer {TOKEN}')
            
            with urllib.request.urlopen(request2, context=ssl_context) as response2:
                data2 = response2.read()
                result2 = json.loads(data2.decode('utf-8'))
                
                if 'meta' in result2:
                    total = result2['meta'].get('size', 0)
                    print(f"  Найдено товаров: {total}")
                    
                    if result2.get('rows'):
                        print(f"  Пример товара: {result2['rows'][0].get('name', 'Без названия')}")
            
            print("\n✅ Токен рабочий! Можно использовать для синхронизации.")
            return True
            
    except urllib.error.HTTPError as e:
        print(f"❌ Ошибка HTTP {e.code}: {e.reason}")
        
        # Читаем тело ошибки
        error_body = e.read().decode('utf-8')
        try:
            error_json = json.loads(error_body)
            if 'errors' in error_json:
                for err in error_json['errors']:
                    print(f"  Детали: {err.get('error', err.get('parameter', str(err)))}")
        except:
            print(f"  Ответ сервера: {error_body[:200]}")
        
        if e.code == 401:
            print("\n⚠️ Ошибка авторизации. Возможные причины:")
            print("  1. Неверный токен")
            print("  2. Токен истек")
            print("  3. Недостаточно прав")
        elif e.code == 415:
            print("\n⚠️ Ошибка типа контента")
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def test_with_curl():
    """Команда для теста через curl"""
    print("\n" + "="*60)
    print("📝 Альтернативный тест через curl:")
    print("-" * 50)
    print("Скопируйте и выполните эту команду в терминале:\n")
    print(f'curl -H "Authorization: Bearer {TOKEN}" \\')
    print('     "https://api.moysklad.ru/api/remap/1.2/entity/product?limit=1"')
    print("\nЕсли получите JSON ответ - токен рабочий.")

if __name__ == "__main__":
    print("="*60)
    print("🔍 ТЕСТ API МОЙСКЛАД")
    print("="*60)
    
    if test_moysklad():
        print("\n" + "="*60)
        print("✅ Все работает! Можно запускать синхронизацию.")
    else:
        test_with_curl()
