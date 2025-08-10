#!/usr/bin/env python3
"""
Определение SMTP настроек для домена usafitandjoy.com
"""

import dns.resolver
import socket

domain = "usafitandjoy.com"

print("🔍 Проверяю настройки почты для домена:", domain)

try:
    # Проверяем MX записи
    mx_records = dns.resolver.resolve(domain, 'MX')
    print("\n📧 MX записи:")
    for mx in mx_records:
        print(f"  {mx.preference}: {mx.exchange}")
        
    # Определяем почтовый сервер
    if mx_records:
        mail_server = str(mx_records[0].exchange).rstrip('.')
        
        if "google" in mail_server or "googlemail" in mail_server:
            print("\n✅ Используется Google Workspace")
            print("SMTP настройки:")
            print("  Server: smtp.gmail.com")
            print("  Port: 587")
            print("  Security: TLS")
            
        elif "outlook" in mail_server or "microsoft" in mail_server:
            print("\n✅ Используется Microsoft 365")
            print("SMTP настройки:")
            print("  Server: smtp.office365.com")
            print("  Port: 587")
            print("  Security: STARTTLS")
            
        elif "yandex" in mail_server:
            print("\n✅ Используется Яндекс")
            print("SMTP настройки:")
            print("  Server: smtp.yandex.ru")
            print("  Port: 465")
            print("  Security: SSL")
            
        elif "mail.ru" in mail_server:
            print("\n✅ Используется Mail.ru")
            print("SMTP настройки:")
            print("  Server: smtp.mail.ru")
            print("  Port: 465")
            print("  Security: SSL")
        else:
            print(f"\n📮 Почтовый сервер: {mail_server}")
            print("Попробуйте стандартные порты:")
            print("  Port 587 (TLS)")
            print("  Port 465 (SSL)")
            print("  Port 25 (без шифрования)")
            
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print("\nНе могу определить MX записи")
    print("Возможно используется сторонний почтовый сервис")
