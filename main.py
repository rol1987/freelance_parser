import requests
from bs4 import BeautifulSoup
import time
import re


def get_default_dict():
    return {'Ссылка': '',
                'ID': '',
                'ФИО': '',
                'Номер свидетельства': '',
                'Действителен до': '',
                'Номер удостоверения': '',
                'Дата выдачи удостоверения': '',
                'Действительно до': '',
                'Вид аттестации': '',
                'Заявленный уровень': '',
                'Присвоеный уровень': '',
                'Объекты контроля': '',
                '(одной строкой) Объекты контроля': '',
                'Методы контроля': '',
    }  


def detect_data_type(text):
    """Определяет тип данных в тексте"""
    text = text.strip()
    
    # Проверка на ФИО (содержит кириллические символы и состоит из нескольких слов)
    if re.match(r'^[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+\s+[А-ЯЁ][а-яё]+$', text):
        return 'fio'
    
    # Проверка на дату (формат DD.MM.YYYY)
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', text):
        return 'date'
    
    # Проверка на номер сертификата (содержит цифры и дефисы, но не точки)
    if re.match(r'^[\d\-]+$', text) and '-' in text and '.' not in text:
        return 'certificate'
    
    return 'unknown'

def parse_experts():
    base_url = "http://www.oaontc.ru/services/registers/expertnk/"
    experts_list = []
    page_num = 1
    
    # Переменные для хранения предыдущих значений
    last_fio = None
    last_link = None
    final_list = []
    while True:
    # while page_num < 5:
        try:
            # Формируем URL
            if page_num == 1:
                url = base_url
            else:
                url = f"{base_url}?&page={page_num}"
            
            print(f"Обрабатывается страница {page_num}")
            
            # Загружаем страницу
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Работаем с текстом страницы
            page = response.text
            soup = BeautifulSoup(page, 'html.parser')
            
            # Ищем таблицу с экспертами
            table = None
            textpage_div = soup.find('div', class_='textpage docs')
            if textpage_div:
                table = textpage_div.find('tbody')
            
            if not table:
                all_tables = soup.find_all('table')
                for tbl in all_tables:
                    headers = tbl.find_all('th')
                    header_texts = [h.get_text(strip=True) for h in headers]
                    if any('ФИО' in text for text in header_texts):
                        table = tbl.find('tbody') or tbl
                        break
            
            if not table:
                print(f"На странице {page_num} не найдена таблица с экспертами")
                break
            
            # Парсим строки таблицы
            rows = table.find_all('tr')
            data_rows = [row for row in rows if not row.find('th')]  # пропускаем заголовки
            
            if not data_rows:
                print(f"На странице {page_num} нет данных экспертов")
                break
            
            print(f"Найдено строк на странице {page_num}: {len(data_rows)}")

 

            # Обрабатываем каждую строку
            for row in data_rows:
                final_dict = get_default_dict()
                cells = row.find_all('td')
                
                # Переменные для данных текущего эксперта
                fio = None
                certificate_number = None
                valid_until = None
                link = None
                
                # Анализируем каждую ячейку в строке
                for cell in cells:

                    cell_text = cell.get_text(strip=True)
                    
                    # Проверяем наличие ссылки
                    cell_link = cell.find('a')
                    if cell_link and cell_link.get('href'):
                        link = cell_link.get('href')
                        # Если в ссылке есть текст, проверяем его тип
                        link_text = cell_link.get_text(strip=True)
                        if link_text and detect_data_type(link_text) == 'fio':
                            fio = link_text
                    
                    # Анализируем текст ячейки
                    if cell_text:
                        data_type = detect_data_type(cell_text)
                        
                        if data_type == 'fio':
                            fio = cell_text
                        elif data_type == 'date':
                            valid_until = cell_text
                        elif data_type == 'certificate':
                            certificate_number = cell_text
                
                # Если ФИО не найдено в текущей строке, используем предыдущее значение
                if not fio and last_fio:
                    fio = last_fio
                    # print(f"  Использовано предыдущее ФИО: {fio}")
                
                # Если ссылка не найдена в текущей строке, используем предыдущее значение
                if not link and last_link:
                    link = last_link
                    # print(f"  Использована предыдущая ссылка: {link}")
                
                # Если нашли все необходимые данные, добавляем в список
                if fio and certificate_number and valid_until:
                    expert_data = {
                        'fio': fio,
                        'certificate_number': certificate_number,
                        'valid_until': valid_until
                    }
                    if link:
                        expert_data['link'] = link

                        detail_link = f'http://www.oaontc.ru{link}'

                        id_url = detail_link.split('/')[-2]

                        detail_html = requests.get(detail_link).text
                        # Парсим HTML
                        soup = BeautifulSoup(detail_html, 'html.parser')
                        # Находим div с классом textpage docs
                        textpage_div = soup.find('div', class_='textpage docs')
                        # Ищем все таблицы внутри этого div
                        tables = textpage_div.find_all('table')
                        tables_count = len(tables)
                        # print(f"Найдено таблиц: {tables_count}")

                        


                        def get_first_table_info(table):
                            # Находим tbody (или сам table, если tbody нет)
                            tbody = table.find('tbody') or table
                            
                            # Ищем все th в заголовке таблицы
                            headers = tbody.find_all('th')
                            
                            # Извлекаем текст из всех th
                            header_texts = [header.get_text(strip=True) for header in headers]
                            
                            # Теперь ищем все td в первой строке данных (первый tr после заголовка)
                            data_row = tbody.find_all('tr')[1]  # первая строка с данными (индекс 1, т.к. 0 - заголовок)
                            data_cells = data_row.find_all('td')
                            data_values = [cell.get_text(strip=True) for cell in data_cells]
                            
                            # Создаем словарь с данными
                            table_data = dict(zip(header_texts, data_values))
                            
                            # Теперь можно сохранить в отдельные переменные
                            номер_свидетельства = table_data.get('Номер удостоверения', '')
                            дата_выдачи_удостоверения = table_data.get('Дата выдачи удостоверения', '')
                            действительно_до = table_data.get('Действительно до', '')
                            вид_аттестации = table_data.get('Вид аттестации', '')
                            
                            # Получаем строку с индексом 2 (третья строка в таблице 1)
                            third_row = tbody.find_all('tr')[2]
                            third_row_text = third_row.get_text(strip=True)

                            # Разбиваем текст по запятой
                            parts = third_row_text.split(',')

                            final_dict['Номер свидетельства'] = номер_свидетельства
                            final_dict['Действителен до'] = действительно_до
                            final_dict['Номер удостоверения'] = номер_свидетельства
                            final_dict['Дата выдачи удостоверения'] = дата_выдачи_удостоверения
                            final_dict['Действительно до'] = действительно_до
                            final_dict['Вид аттестации'] = вид_аттестации

                            if len(parts) >= 2:
                                # Убираем слово "Заявленный уровень:" из первой части
                                заявленный_уровень = parts[0].replace('Заявленный уровень:', '').strip()
                                
                                # Убираем слово "присвоеный уровень" из второй части
                                присвоеный_уровень = parts[1].replace('присвоеный уровень', '').strip()
                                
                                # print("Declared level:", заявленный_уровень)
                                # print("Assigned level:", присвоеный_уровень)
                            else:
                                заявленный_уровень = ""
                                присвоеный_уровень = ""

                            final_dict['ФИО'] = fio
                            final_dict['ID'] = id_url
                            final_dict['Ссылка'] = detail_link

                            final_dict['Заявленный уровень'] = заявленный_уровень
                            final_dict['Присвоеный уровень'] = присвоеный_уровень

                        def get_second_table_info(table):

                            
                            # Находим tbody (или сам table, если tbody нет)
                            tbody = table.find('tbody') or table
                            # Ищем th в заголовке таблицы
                            headers = tbody.find('th')
                            # Теперь ищем все td
                            data_cells = tbody.find_all('td')
                            data_values = [cell.text for cell in data_cells]
                            final_dict['Объекты контроля'] = data_values


                        def get_third_table_info(table):
                            
                            tbody = table.find('tbody') or table
                            # Ищем th в заголовке таблицы
                            headers = tbody.find('th')
                            if headers and headers.text:
                                # if headers.text == 'Методы контроля':
                                # Теперь ищем все td
                                data_cells = tbody.find_all('td')
                                data_values = [cell.text for cell in data_cells]
                                final_dict['Методы контроля'] = data_values


                        # Находим первую таблицу
                        first_table = textpage_div.find('table')
                        if first_table:
                            get_first_table_info(first_table)

                        # Находим вторую таблицу
                        if len(tables) >= 2:
                            table = tables[1]
                            get_second_table_info(table)

                        # Находим третью таблицу
                        if len(tables) >= 3:
                            table = tables[2]
                            get_third_table_info(table)

                        # final_list.append(final_dict)

                        # Находим следующие таблицы
                        if len(tables) >= 4:
                            final_dict = get_default_dict()
                            table = tables[3]
                            get_first_table_info(table)

                        # Находим следующие таблицы
                        if len(tables) >= 5:
                            table = tables[4]
                            get_second_table_info(table)

                        # Находим следующие таблицы
                        if len(tables) >= 6:
                            table = tables[5]
                            get_third_table_info(table)
                        
                        # final_list.append(final_dict)
                        

                        # Находим следующие таблицы
                        if len(tables) >= 7:
                            final_dict = get_default_dict()
                            table = tables[6]
                            get_first_table_info(table)

                        # Находим следующие таблицы
                        if len(tables) >= 8:
                            table = tables[7]
                            get_second_table_info(table)

                        # Находим следующие таблицы
                        if len(tables) >= 9:
                            table = tables[8]
                            get_third_table_info(table)
                        
                        final_list.append(final_dict)

                        # if fio == 'Абаев Алексей Анатольевич':
                        #     print(final_list)
                        #     time.sleep(1111)
                       
                        # time.sleep(1)

                            

                        


                    
                    # experts_list.append(expert_data)
                    
                    # Сохраняем текущие значения для следующих строк
                    last_fio = fio
                    if link:  # сохраняем ссылку только если она есть
                        last_link = link
                    
                    # print(f"  Добавлен: {fio} | {certificate_number} | {valid_until}")
                # else:
                #     missing = []
                #     if not fio: missing.append("ФИО")
                #     if not certificate_number: missing.append("номер сертификата")
                #     if not valid_until: missing.append("дата")
                #     print(f"  Пропущена строка - отсутствуют: {', '.join(missing)}")
            
            # Проверяем есть ли следующая страницу
            pagination_div = soup.find('div', class_='pagination')

            if pagination_div:
                # Находим все элементы списка
                pagination_items = pagination_div.find_all('li')
                
                # Ищем текущую активную страницу (без ссылки)
                current_page = None
                next_page_link = None
                
                for i, item in enumerate(pagination_items):
                    # Если у элемента есть ссылка - это не текущая страница
                    link = item.find('a')
                    if not link:
                        # Это текущая страница (активная без ссылки)
                        current_page = item
                        # Проверяем, есть ли следующий элемент
                        if i + 1 < len(pagination_items):
                            next_item = pagination_items[i + 1]
                            next_link = next_item.find('a')
                            if next_link:
                                next_page_link = next_link.get('href')
                                break
                
                if next_page_link:
                    print(f"Следующая страница: {next_page_link}")
                else:
                    print("Это последняя страница")
                    break
                
            page_num += 1
            time.sleep(0.1)
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса на странице {page_num}: {e}")
            break
        except Exception as e:
            print(f"Ошибка обработки страницы {page_num}: {e}")
            break
    
    return final_list

# Упрощенная версия с наследованием значений
def parse_experts_enhanced():
    base_url = "http://www.oaontc.ru/services/registers/expertnk/"
    experts = []
    page_num = 1
    
    # Переменные для предыдущих значений
    last_fio = None
    last_link = None
    
    def enhanced_detect_data_type(text):
        text = text.strip()
        
        # ФИО: минимум 2 слова с заглавными буквами, кириллица
        if re.match(r'^[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+){1,2}$', text):
            return 'fio'
        
        # Дата: DD.MM.YYYY
        if re.match(r'^\d{2}\.\d{2}\.\d{4}$', text):
            return 'date'
        
        # Номер сертификата: цифры и дефисы, минимум 1 дефис, нет точек
        if re.match(r'^[\d\-]+$', text) and '-' in text and '.' not in text:
            return 'certificate'
        
        return 'unknown'
    
    
    while True:
        url = base_url if page_num == 1 else f"{base_url}?&page={page_num}"
        
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('div', class_='textpage docs')
        if table:
            table = table.find('tbody')
        
        if not table:
            break
        
        rows = table.find_all('tr')[1:]  # пропускаем заголовок
        
        if not rows:
            break
        
        for row in rows:
            cells = row.find_all('td')
            
            fio = None
            certificate = None
            date = None
            link = None
            
            for cell in cells:
                text = cell.get_text(strip=True)
                
                # Проверяем ссылки
                cell_link = cell.find('a')
                if cell_link:
                    href = cell_link.get('href', '')
                    if href:
                        link = href
                    # Текст ссылки тоже анализируем
                    link_text = cell_link.get_text(strip=True)
                    if link_text:
                        link_type = enhanced_detect_data_type(link_text)
                        if link_type == 'fio':
                            fio = link_text
                
                # Анализируем текст ячейки
                if text:
                    data_type = enhanced_detect_data_type(text)
                    if data_type == 'fio':
                        fio = text
                    elif data_type == 'date':
                        date = text
                    elif data_type == 'certificate':
                        certificate = text
            
            # Наследуем ФИО и ссылку если они отсутствуют
            if not fio:
                fio = last_fio
            if not link:
                link = last_link
            
            # Добавляем эксперта если есть основные данные
            if fio and certificate and date:
                expert = {
                    'fio': fio,
                    'certificate_number': certificate,
                    'valid_until': date
                }
                if link:
                    expert['link'] = link
                experts.append(expert)
                
                # Обновляем предыдущие значения
                last_fio = fio
                if link:
                    last_link = link
        
        page_num += 1
    
    return experts

# Запускаем парсинг
if __name__ == "__main__":
    print("Начинаем парсинг списка экспертов...")
    
    experts = parse_experts()
    
    print(f"\n=== РЕЗУЛЬТАТ ===")
    print(f"Всего найдено экспертов: {len(experts)}")
    
    if experts:
        # print("\nПервые 10 записей:")
        # for i, expert in enumerate(experts[:10], 1):
        #     link_info = f", ссылка: {expert.get('link', 'нет')}" if expert.get('link') else ""
        #     print(f"{i}. {expert['ФИО']} | {expert['certificate_number']} | {expert['valid_until']}{link_info}")
        
        # Сохраняем в JSON
        import json
        with open('experts.json', 'w', encoding='utf-8') as f:
            json.dump(experts, f, ensure_ascii=False, indent=2)
        print(f"\nДанные сохранены в файл 'experts.json'")
    else:
        print("Эксперты не найдены")