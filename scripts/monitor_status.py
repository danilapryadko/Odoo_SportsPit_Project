#!/usr/bin/env python3
"""
Скрипт для мониторинга статуса проекта Odoo SportPit
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

import requests
import json
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
RAILWAY_API_TOKEN = "e2a89410-8aeb-419c-8020-741fba8f9bf9"
RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
PROJECT_ID = "daa4ac63-d597-4ba7-b10e-1baf84cbacad"
ENVIRONMENT_ID = "d312f78e-aea8-46ab-a1a6-0b20b9e94e74"

# Цвета для вывода
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    """Печать заголовка"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")

def check_odoo_status():
    """Проверка статуса Odoo"""
    print(f"\n{Colors.BOLD}🌐 Проверка Odoo...{Colors.END}")
    
    try:
        # Проверяем доступность главной страницы
        response = requests.get(ODOO_URL, timeout=10)
        
        if response.status_code == 200:
            print(f"  {Colors.GREEN}✅ Odoo доступен{Colors.END}")
            print(f"  📍 URL: {ODOO_URL}")
            
            # Проверяем страницу логина
            login_response = requests.get(urljoin(ODOO_URL, "/web/login"), timeout=10)
            if login_response.status_code == 200:
                print(f"  {Colors.GREEN}✅ Страница входа доступна{Colors.END}")
            else:
                print(f"  {Colors.YELLOW}⚠️ Страница входа недоступна{Colors.END}")
                
            return True
        else:
            print(f"  {Colors.RED}❌ Odoo недоступен (HTTP {response.status_code}){Colors.END}")
            return False
            
    except requests.Timeout:
        print(f"  {Colors.RED}❌ Время ожидания истекло{Colors.END}")
        return False
    except Exception as e:
        print(f"  {Colors.RED}❌ Ошибка: {e}{Colors.END}")
        return False

def check_railway_status():
    """Проверка статуса Railway"""
    print(f"\n{Colors.BOLD}🚂 Проверка Railway...{Colors.END}")
    
    headers = {
        "Authorization": f"Bearer {RAILWAY_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # GraphQL запрос для получения информации о проекте
    query = """
    query GetProject($projectId: String!, $environmentId: String!) {
        project(id: $projectId) {
            name
            createdAt
            environments {
                edges {
                    node {
                        id
                        name
                    }
                }
            }
            services {
                edges {
                    node {
                        id
                        name
                        createdAt
                    }
                }
            }
        }
        deployments(
            first: 5,
            input: {
                projectId: $projectId,
                environmentId: $environmentId
            }
        ) {
            edges {
                node {
                    id
                    status
                    createdAt
                    service {
                        name
                    }
                }
            }
        }
    }
    """
    
    try:
        response = requests.post(
            RAILWAY_API_URL,
            headers=headers,
            json={
                "query": query,
                "variables": {
                    "projectId": PROJECT_ID,
                    "environmentId": ENVIRONMENT_ID
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if "data" in data and data["data"]:
                project = data["data"].get("project", {})
                deployments = data["data"].get("deployments", {}).get("edges", [])
                
                print(f"  {Colors.GREEN}✅ Railway API доступен{Colors.END}")
                print(f"  📁 Проект: {project.get('name', 'N/A')}")
                
                # Показываем статус последних деплоев
                if deployments:
                    print(f"\n  {Colors.BOLD}📊 Последние деплои:{Colors.END}")
                    for deploy in deployments[:3]:
                        node = deploy["node"]
                        status = node["status"]
                        service = node["service"]["name"] if node.get("service") else "Unknown"
                        
                        if status == "SUCCESS":
                            status_color = Colors.GREEN
                            status_icon = "✅"
                        elif status == "FAILED":
                            status_color = Colors.RED
                            status_icon = "❌"
                        else:
                            status_color = Colors.YELLOW
                            status_icon = "⏳"
                        
                        created = datetime.fromisoformat(node["createdAt"].replace("Z", "+00:00"))
                        created_str = created.strftime("%d.%m %H:%M")
                        
                        print(f"    {status_icon} {service}: {status_color}{status}{Colors.END} ({created_str})")
                
                return True
            else:
                print(f"  {Colors.YELLOW}⚠️ Railway API вернул пустой ответ{Colors.END}")
                return False
                
        else:
            print(f"  {Colors.RED}❌ Railway API недоступен (HTTP {response.status_code}){Colors.END}")
            return False
            
    except Exception as e:
        print(f"  {Colors.RED}❌ Ошибка Railway API: {e}{Colors.END}")
        return False

def check_database_status():
    """Проверка статуса базы данных"""
    print(f"\n{Colors.BOLD}🗄️ Проверка базы данных...{Colors.END}")
    
    try:
        # Проверяем доступность страницы выбора БД
        response = requests.get(urljoin(ODOO_URL, "/web/database/selector"), timeout=10)
        
        if response.status_code == 200:
            print(f"  {Colors.GREEN}✅ Менеджер баз данных доступен{Colors.END}")
            
            # Пытаемся получить список БД (может не работать из-за безопасности)
            list_url = urljoin(ODOO_URL, "/web/database/list")
            list_response = requests.post(
                list_url,
                json={"jsonrpc": "2.0", "method": "call", "params": {}, "id": 1},
                timeout=10
            )
            
            if list_response.status_code == 200:
                data = list_response.json()
                if "result" in data and data["result"]:
                    databases = data["result"]
                    print(f"  📊 Найдено баз данных: {len(databases)}")
                    for db in databases:
                        print(f"    - {db}")
                else:
                    print(f"  {Colors.YELLOW}⚠️ Список БД недоступен (возможно, отключен по безопасности){Colors.END}")
            
            return True
        else:
            print(f"  {Colors.YELLOW}⚠️ Менеджер БД недоступен{Colors.END}")
            return False
            
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️ Не удалось проверить БД: {e}{Colors.END}")
        return False

def get_project_stats():
    """Получение статистики проекта"""
    print(f"\n{Colors.BOLD}📊 Статистика проекта:{Colors.END}")
    
    try:
        # Читаем PROJECT_STATUS.md
        with open("/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project/PROJECT_STATUS.md", "r") as f:
            content = f.read()
            
            # Ищем процент прогресса
            if "Общий прогресс:" in content:
                progress_line = [line for line in content.split("\n") if "Общий прогресс:" in line][0]
                progress = progress_line.split("**")[1].replace("%", "")
                
                progress_int = int(progress)
                if progress_int < 30:
                    color = Colors.RED
                elif progress_int < 60:
                    color = Colors.YELLOW
                else:
                    color = Colors.GREEN
                
                print(f"  📈 Общий прогресс: {color}{progress}%{Colors.END}")
                
                # Визуализация прогресса
                bar_length = 40
                filled = int(bar_length * progress_int / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"  [{bar}]")
        
        # Читаем статистику из Git
        import subprocess
        
        # Количество коммитов
        commit_count = subprocess.check_output(
            ["git", "-C", "/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project", 
             "rev-list", "--count", "HEAD"],
            text=True
        ).strip()
        
        # Последний коммит
        last_commit = subprocess.check_output(
            ["git", "-C", "/Users/danilapryadkoicloud.com/Documents/Odoo_SportsPit_Project",
             "log", "-1", "--pretty=%B"],
            text=True
        ).strip()
        
        print(f"\n  {Colors.BOLD}📝 Git статистика:{Colors.END}")
        print(f"  📌 Коммитов: {commit_count}")
        print(f"  💬 Последний: {last_commit[:50]}...")
        
    except Exception as e:
        print(f"  {Colors.YELLOW}⚠️ Не удалось получить статистику: {e}{Colors.END}")

def main():
    """Основная функция"""
    print_header("МОНИТОРИНГ ODOO SPORTPIT")
    
    print(f"\n⏰ Время проверки: {datetime.now().strftime('%d.%m.%025 %H:%M:%S')}")
    
    # Проверяем все компоненты
    odoo_ok = check_odoo_status()
    railway_ok = check_railway_status()
    db_ok = check_database_status()
    
    # Статистика проекта
    get_project_stats()
    
    # Итоговый статус
    print_header("ИТОГОВЫЙ СТАТУС")
    
    all_ok = odoo_ok and railway_ok
    
    if all_ok:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ВСЕ СИСТЕМЫ РАБОТАЮТ НОРМАЛЬНО{Colors.END}")
        print(f"\n📋 Рекомендации:")
        print(f"  1. Запустите init_odoo_database.py для создания БД")
        print(f"  2. Запустите install_odoo_modules.py для установки модулей")
        print(f"  3. Войдите в Odoo и проверьте настройки")
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ ОБНАРУЖЕНЫ ПРОБЛЕМЫ{Colors.END}")
        
        if not odoo_ok:
            print(f"  - Проверьте деплой Odoo на Railway")
        if not railway_ok:
            print(f"  - Проверьте Railway API токен")
        if not db_ok:
            print(f"  - Создайте базу данных через init_odoo_database.py")
    
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.END}")

if __name__ == "__main__":
    # Для непрерывного мониторинга
    if len(sys.argv) > 1 and sys.argv[1] == "--watch":
        while True:
            main()
            print(f"\n{Colors.YELLOW}Следующая проверка через 30 секунд...{Colors.END}")
            time.sleep(30)
    else:
        main()
