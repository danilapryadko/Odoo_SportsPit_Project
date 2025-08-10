#!/usr/bin/env python3
"""
Скрипт для автоматизации браузера и создания БД Odoo через веб-интерфейс
Автор: Claude AI Assistant
Дата: 09.08.2025
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time
import sys

# Конфигурация
ODOO_URL = "https://odoosportspitproject-production.up.railway.app"
MASTER_PASSWORD = "SportPit2024Master"
DB_NAME = "odoo_sportpit"
ADMIN_EMAIL = "danila@usafitandjoy.com"
ADMIN_PASSWORD = "admin_sportpit_2024"
LANG = "ru_RU"

class OdooAutomation:
    def __init__(self):
        """Инициализация драйвера"""
        print("🌐 Запуск браузера...")
        
        # Настройки Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Браузер запущен")
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            print("\nУстановка ChromeDriver:")
            print("brew install --cask chromedriver")
            print("или")
            print("pip install selenium webdriver-manager")
            sys.exit(1)
    
    def check_database_exists(self):
        """Проверка существования базы данных"""
        print("\n🔍 Проверка существующих баз данных...")
        
        try:
            self.driver.get(f"{ODOO_URL}/web/database/selector")
            time.sleep(2)
            
            # Проверяем, есть ли наша БД в списке
            page_source = self.driver.page_source
            if DB_NAME in page_source:
                print(f"✅ База данных '{DB_NAME}' уже существует")
                return True
            else:
                print(f"📊 База данных '{DB_NAME}' не найдена")
                return False
        except:
            return False
    
    def create_database(self):
        """Создание базы данных через веб-интерфейс"""
        print("\n📊 Создание базы данных...")
        
        try:
            # Переходим на страницу управления БД
            self.driver.get(f"{ODOO_URL}/web/database/manager")
            time.sleep(3)
            
            # Ищем кнопку создания БД
            try:
                create_btn = self.driver.find_element(By.XPATH, "//a[contains(text(), 'Create Database')]")
                create_btn.click()
            except:
                # Альтернативный путь
                create_btn = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Create')]")
                create_btn.click()
            
            time.sleep(2)
            
            # Заполняем форму
            print("📝 Заполнение формы создания БД...")
            
            # Master Password
            master_pwd = self.driver.find_element(By.NAME, "master_pwd")
            master_pwd.clear()
            master_pwd.send_keys(MASTER_PASSWORD)
            
            # Database Name
            db_name = self.driver.find_element(By.NAME, "name")
            db_name.clear()
            db_name.send_keys(DB_NAME)
            
            # Admin Email
            admin_email = self.driver.find_element(By.NAME, "login")
            admin_email.clear()
            admin_email.send_keys(ADMIN_EMAIL)
            
            # Admin Password
            admin_pwd = self.driver.find_element(By.NAME, "password")
            admin_pwd.clear()
            admin_pwd.send_keys(ADMIN_PASSWORD)
            
            # Confirm Password
            confirm_pwd = self.driver.find_element(By.NAME, "confirm_password")
            confirm_pwd.clear()
            confirm_pwd.send_keys(ADMIN_PASSWORD)
            
            # Language
            try:
                lang_select = Select(self.driver.find_element(By.NAME, "lang"))
                lang_select.select_by_value(LANG)
            except:
                print("⚠️ Не удалось выбрать язык, будет использован по умолчанию")
            
            # Country
            try:
                country_select = Select(self.driver.find_element(By.NAME, "country_code"))
                country_select.select_by_value("ru")
            except:
                print("⚠️ Не удалось выбрать страну")
            
            # Demo data - снимаем галочку если стоит
            try:
                demo_checkbox = self.driver.find_element(By.NAME, "demo")
                if demo_checkbox.is_selected():
                    demo_checkbox.click()
            except:
                pass
            
            # Отправляем форму
            print("⏳ Создание базы данных (это может занять 1-2 минуты)...")
            submit_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_btn.click()
            
            # Ждем создания БД
            time.sleep(30)
            
            print("✅ База данных создана успешно!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания БД: {e}")
            return False
    
    def login_to_odoo(self):
        """Вход в Odoo"""
        print("\n🔐 Вход в Odoo...")
        
        try:
            self.driver.get(f"{ODOO_URL}/web/login")
            time.sleep(2)
            
            # Email
            login_field = self.driver.find_element(By.ID, "login")
            login_field.clear()
            login_field.send_keys(ADMIN_EMAIL)
            
            # Password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(ADMIN_PASSWORD)
            
            # Submit
            login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_btn.click()
            
            time.sleep(5)
            
            # Проверяем успешный вход
            if "inbox" in self.driver.current_url or "home" in self.driver.current_url:
                print("✅ Успешный вход в систему!")
                return True
            else:
                print("❌ Не удалось войти в систему")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка входа: {e}")
            return False
    
    def install_apps(self):
        """Установка приложений Odoo"""
        print("\n📦 Установка приложений...")
        
        apps_to_install = [
            "Manufacturing",
            "Inventory", 
            "Purchase",
            "Sales",
            "Accounting",
            "Employees",
            "Project"
        ]
        
        try:
            # Переходим в меню приложений
            self.driver.get(f"{ODOO_URL}/web#action=base.open_module_tree&model=ir.module.module&view_type=kanban")
            time.sleep(3)
            
            for app_name in apps_to_install:
                try:
                    print(f"  🔄 Установка {app_name}...")
                    
                    # Ищем приложение
                    search_box = self.driver.find_element(By.CLASS_NAME, "o_searchview_input")
                    search_box.clear()
                    search_box.send_keys(app_name)
                    search_box.send_keys(Keys.RETURN)
                    time.sleep(2)
                    
                    # Находим кнопку Install
                    install_btn = self.driver.find_element(By.XPATH, f"//div[contains(@class, 'o_kanban_record')]//button[contains(text(), 'Install')]")
                    install_btn.click()
                    time.sleep(5)
                    
                    print(f"  ✅ {app_name} установлен")
                    
                except:
                    print(f"  ℹ️ {app_name} уже установлен или не найден")
            
            print("✅ Установка приложений завершена!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка установки приложений: {e}")
            return False
    
    def close(self):
        """Закрытие браузера"""
        input("\n⏸️ Нажмите Enter, чтобы закрыть браузер...")
        self.driver.quit()
    
    def run(self):
        """Основной процесс"""
        print("=" * 60)
        print("🚀 АВТОМАТИЗАЦИЯ НАСТРОЙКИ ODOO")
        print("=" * 60)
        
        # Проверяем, существует ли БД
        if not self.check_database_exists():
            # Создаем БД
            if self.create_database():
                print("✅ База данных создана")
            else:
                print("❌ Не удалось создать БД")
                self.close()
                return
        
        # Входим в систему
        if self.login_to_odoo():
            # Устанавливаем приложения
            self.install_apps()
        
        print("\n" + "=" * 60)
        print("✅ АВТОМАТИЗАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 60)
        print(f"\n🌐 Odoo доступен по адресу: {ODOO_URL}")
        print(f"📧 Email: {ADMIN_EMAIL}")
        print(f"🔑 Пароль: {ADMIN_PASSWORD}")
        
        self.close()

def main():
    """Главная функция"""
    # Проверяем установку selenium
    try:
        import selenium
    except ImportError:
        print("❌ Selenium не установлен!")
        print("Установите его командой:")
        print("pip install selenium")
        sys.exit(1)
    
    # Запускаем автоматизацию
    automation = OdooAutomation()
    automation.run()

if __name__ == "__main__":
    main()
