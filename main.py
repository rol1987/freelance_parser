from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import requests, os, json, time
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime


url = f'https://freelance.ru/' 

# Словарь ключевых слов для поиска
KEYWORDS = [
    'скрипт',
    'парсер', 
    'парсинг', 
    'скраппер', 
    'распарсить',
    'excel',
    'эксель',
    'json',
    'маркетплейс',
    'пайтон',
    'python',
    'создать сайт',
    'сделать сайт',
    'восстановить сайт',
    'скопировать сайт',
    'дублировать сайт',
    'вордпресс',
    'wordpress',
    'интеграц',
    'озон',
    'ozon',
    'wildberries',
    'wildberries',
    'сайт визит',
]

# Список слов для исключения
EXCLUDE_KEYWORDS = [
    '1с',
    '1c',
    'битрикс',
    'бухгалтер',
    'юрист',
    'копирайтинг',
    'рерайтинг',
    'дизайнер',
    'illustrator',
    'photoshop',
    'figma',
    'разработка товарного',
    'java',
    'c++',
    'с++',
    'instagram',
    'facebook',
    'тильд',
    'обзвон',
]

def filter_projects_by_keywords(projects_data, include_keywords, exclude_keywords=None):
    """Фильтрует проекты по ключевым словам с исключениями"""
    my_projects = []
    found_keywords = {}
    
    if exclude_keywords is None:
        exclude_keywords = []
    
    # Приводим все ключевые слова к нижнему регистру
    include_lower = [keyword.lower() for keyword in include_keywords]
    exclude_lower = [keyword.lower() for keyword in exclude_keywords]
    
    for project in projects_data:
        title = project.get('title', '').lower()
        description = project.get('description', '').lower()
        full_text = f"{title} {description}"
        
        # Проверяем исключения сначала
        should_exclude = False
        for exclude_keyword in exclude_lower:
            if exclude_keyword in full_text:
                print(f"❌ Исключен: '{title}' - содержит '{exclude_keyword}'")
                should_exclude = True
                break
        
        if should_exclude:
            continue
        
        # Проверяем ключевые слова для включения
        for keyword in include_lower:
            if keyword in full_text:
                my_projects.append(project)
                project['matched_keyword'] = keyword
                found_keywords[keyword] = found_keywords.get(keyword, 0) + 1
                print(f"✅ Найден: '{title}' - ключ: '{keyword}'")
                break
    
    return my_projects, found_keywords



    

def send_filtered_projects_to_telegram(projects_data, token='7807464690:AAGJ9mTZxUZuiqUuOptyYfbgAXmNIVWMK8Q', chat_id='772382203'):
    """Отправляет проекты, отфильтрованные по ключевым словам"""
    
    # Фильтруем проекты
    my_projects, found_keywords = filter_projects_by_keywords(projects_data, KEYWORDS, EXCLUDE_KEYWORDS)
    
    print(f"Найдено проектов по ключевым словам: {len(my_projects)}")
    print(f"Найденные ключи: {found_keywords}")
    
    if not my_projects:
        message = "🔍 Проекты по заданным ключевым словам не найдены"
        try:
            requests.post(f'https://api.telegram.org/bot{token}/sendMessage', 
                        data={'chat_id': chat_id, 'text': message})
        except Exception as e:
            print(f"Ошибка отправки: {e}")
        return
    
    # Отправляем найденные проекты
    successful_sends = 0
    
    for i, project in enumerate(my_projects, 1):
        matched_keyword = project.get('matched_keyword', 'Неизвестно')
        
        message = f"""📋 Проект #{i} [{matched_keyword}]
🏷️ Название: {project.get('title', 'Нет данных')}
🔗 Ссылка: {project.get('url', 'Нет данных')}
"""
        
        description = project.get('description', '')
        # if description:
        #     message += f"📝 Описание: {description[:300]}..."
        
        try:
            # print(message)
            response = requests.post(
                f'https://api.telegram.org/bot{token}/sendMessage',
                data={'chat_id': chat_id, 'text': message}
            )
            time.sleep(0.1)
            
            if response.status_code == 200:
                successful_sends += 1
                print(f"✅ Проект #{i} отправлен в Telegram")
            else:
                print(f"❌ Ошибка отправки проекта #{i}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Ошибка при отправке проекта #{i}: {e}")
    
    # Итоговое сообщение со статистикой
    keyword_stats = ", ".join([f"{KEYWORDS[k]}: {v}" for k, v in found_keywords.items()])
    # summary = f"✅ Отправлено {successful_sends} из {len(my_projects)} проектов\n📊 Найдено по: {keyword_stats}"
    
    # try:
    #     requests.post(f'https://api.telegram.org/bot{token}/sendMessage', 
    #                 data={'chat_id': chat_id, 'text': summary})
    # except Exception as e:
    #     print(f"Ошибка отправки итогов: {e}")



        
caps = DesiredCapabilities().CHROME
# caps["pageLoadStrategy"] = "normal"
# caps["pageLoadStrategy"] = "eager" 
caps["pageLoadStrategy"] = "none"

print("Подключение")


def get_stealth_driver():
    option = Options()
    
    # Базовые настройки
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-gpu")
    option.add_argument("--ignore-certificate-errors")

    # Отключение логов и сообщений
    option.add_argument("--log-level=3")
    option.add_argument("--disable-logging")
    option.add_argument("--disable-dev-shm-usage")
    option.add_argument("--disable-gpu")
    option.add_argument("--no-sandbox")
    option.add_argument("--disable-software-rasterizer")
    option.add_argument("--disable-features=VizDisplayCompositor")
    option.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # User-Agent (ваш текущий)
    option.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.3.904 Yowser/2.5 Safari/537.36")
    
    # Критические настройки против детекта
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    option.add_experimental_option('useAutomationExtension', False)
    
    # Размер окна (важно!)
    option.add_argument("--window-size=1920,1080")
    option.add_argument("--headless=new")
    option.add_argument("--start-maximized")
    
    # Убираем headless режим
    # option.add_argument("--headless")  # ЗАКОММЕНТИРУЙТЕ ЭТУ СТРОКУ!
    
    driver = webdriver.Chrome(options=option)
    
    # Переопределяем свойства
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']})")
    
    # Скрываем CDP
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 YaBrowser/23.5.3.904 Yowser/2.5 Safari/537.36"
    })
    
    return driver


# Подключаем Selenium
try:
    driver = get_stealth_driver()
    driver.set_page_load_timeout(10)
    
    try:
        driver.get(url)
        print("Страница загружена")
    except TimeoutException:
        print("Прерываем долгую загрузку...")
        driver.execute_script("window.stop();")
    
    # Ждем нужный элемент
    wait = WebDriverWait(driver, 15)
    navbar_element = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul.nav.navbar-nav.navbar-right"))
    )
    
    # Находим и кликаем на ссылку "Вход"
    login_link = navbar_element.find_element(By.XPATH, ".//a[contains(text(), 'Вход')]")
    login_link.click()
    print('Кликнули на ссылку "Вход"')
    
    # Ждем 5 секунд
    time.sleep(5)
    
    # Заполняем поле логина
    login_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Логин или почта']")))
    login_field.clear()
    login_field.send_keys("rol1987@yandex.ru")
    print('Ввели логин')
    
    # Заполняем поле пароля
    password_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Пароль'][type='password']")
    password_field.clear()
    password_field.send_keys("83FrkWrt")
    print('Ввели пароль')

    # Ищем кнопку "Авторизоваться"
    login_button = driver.find_element(By.CSS_SELECTOR, "button.form__button")
    login_button.click()

    # Нажали ENTER
    password_field.send_keys(Keys.ENTER)

    # Ждем появления элемента "Продолжить как" и нажимаем на него
    continue_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Продолжить как')]")))
    continue_button.click()


    def load_processed_projects():
        """Загружает историю обработанных проектов из JSON файла"""
        if os.path.exists(PROJECTS_HISTORY_FILE):
            try:
                with open(PROJECTS_HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
            except Exception as e:
                print(f"Ошибка загрузки истории проектов: {e}")
        return set()

    def save_processed_projects(processed_projects):
        """Сохраняет историю проектов в JSON файл"""
        try:
            with open(PROJECTS_HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(processed_projects), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории проектов: {e}")

    def get_project_unique_id(project_data):
        """Создает уникальный идентификатор для проекта (можно использовать URL)"""
        return project_data['url']  # URL обычно уникален для каждого проекта

    # Файл для хранения уже обработанных проектов
    PROJECTS_HISTORY_FILE = 'processed_projects.json'

    # Загружаем историю проектов один раз при старте
    processed_projects = load_processed_projects()
    print(f"Загружено {len(processed_projects)} проектов из истории")

    # Основной цикл
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n=== Начало проверки в {current_time} ===")
            
            driver.get("https://freelance.ru/project/search?q=&a=0&a=1&v=0&v=1&c=&c%5B%5D=4") # это для фильтра "ИТ и Разработка"
            # driver.get("https://freelance.ru/project/search?q=&a=0&a=1&v=0&v=1&c=") # все результаты, без фильтров

            # Собираем информацию со всех проектов
            projects = driver.find_elements(By.CSS_SELECTOR, "div.project-item-default-card.project")

            projects_data = []
            new_projects_count = 0

            for project in projects:
                try:
                    # Название проекта
                    title_element = project.find_element(By.CSS_SELECTOR, "h2.title a")
                    title = title_element.text.strip()
                    project_url = title_element.get_attribute("href")
                    
                    # Описание проекта
                    description_element = project.find_element(By.CSS_SELECTOR, "a.description")
                    description = description_element.text.strip()
                    
                    # Категория
                    category_element = project.find_element(By.CSS_SELECTOR, "div.specs-list b")
                    category = category_element.text.strip()
                    
                    # Бюджет
                    cost_element = project.find_element(By.CSS_SELECTOR, "div.cost")
                    cost = cost_element.text.strip()
                    
                    # Срок выполнения
                    term_element = project.find_element(By.CSS_SELECTOR, "div.term span")
                    term = term_element.text.strip()
                    
                    # Способ оплаты
                    pay_method_element = project.find_element(By.CSS_SELECTOR, "div.prepay-opt")
                    pay_method = pay_method_element.text.strip()
                    
                    # Заказчик
                    owner_element = project.find_element(By.CSS_SELECTOR, "div.project-owner span.user-name")
                    owner = owner_element.text.strip()
                    
                    # Просмотры и отклики
                    views_element = project.find_element(By.CSS_SELECTOR, "span.view-count")
                    views = views_element.text.strip()
                    
                    responses_element = project.find_element(By.CSS_SELECTOR, "span.comments-count")
                    responses = responses_element.text.strip()
                    
                    # Дата публикации
                    publish_element = project.find_element(By.CSS_SELECTOR, "div.publish-time time")
                    publish_date = publish_element.get_attribute("datetime")
                    publish_text = publish_element.text.strip()
                    
                    # Сохраняем данные проекта
                    project_data = {
                        'title': title,
                        'url': project_url,
                        'description': description,
                        'category': category,
                        'cost': cost,
                        'term': term,
                        'pay_method': pay_method,
                        'owner': owner,
                        'views': views,
                        'responses': responses,
                        'publish_date': publish_date,
                        'publish_text': publish_text
                    }
                    
                    # Проверяем, не обрабатывали ли мы уже этот проект
                    project_id = get_project_unique_id(project_data)
                    
                    if project_id not in processed_projects:
                        projects_data.append(project_data)
                        processed_projects.add(project_id)  # Добавляем в историю
                        new_projects_count += 1
                        print(f"✅ Новый проект: {title}")
                    else:
                        print(f"⏩ Пропущен (уже в истории): {title}")
                    
                except Exception as e:
                    continue

            # Сохраняем обновленную историю проектов
            save_processed_projects(processed_projects)

            # Отправляем только новые проекты
            if projects_data:
                
                send_filtered_projects_to_telegram(projects_data)
                
                print(f"📤 Отправлено {len(projects_data)} новых проектов в Telegram")
            else:
                print("📭 Новых проектов не найдено")

            print(f"📊 Статистика: {new_projects_count} новых из {len(projects)} на странице")
            print(f"💾 В истории: {len(processed_projects)} проектов")

        except Exception as e:
            print(f'❌ ОШИБКА: {e}')
            # Можно добавить перезапуск драйвера при ошибках
            # driver.quit()
            # driver = get_stealth_driver()

        # Ожидание 60 секунд до следующей проверки
        print("⏳ Ожидание 60 секунд до следующей проверки...")
        time.sleep(60)

except Exception as e:
    print(f'Ошибка: {e}')
    # Закрываем драйвер только при ошибке
    if 'driver' in locals():
        driver.close()
        driver.quit()


