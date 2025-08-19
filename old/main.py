import json
import os
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import psycopg2
from apscheduler.schedulers.background import BackgroundScheduler
from psycopg2 import extras
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException
)
from bs4 import BeautifulSoup
from commands import *


data_dict = {}  # сюда будем собирать карточки

# Настройка логирования
logging.basicConfig(
    filename='parser.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def create_table():
    """Создает таблицу flats с улучшенной структурой и индексами."""
    conn = None
    try:
        # Используем контекстный менеджер для подключения
        with psycopg2.connect(
                # dbname=os.getenv("POSTGRES_DB"),
                # user=os.getenv("POSTGRES_USER"),
                # password=os.getenv("POSTGRES_PASSWORD"),
                # host=os.getenv("POSTGRES_HOST"),
                # port=os.getenv("POSTGRES_PORT")
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="postgres",
                port=5432
        ) as conn:
            with conn.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS flats (
                    id SERIAL PRIMARY KEY,
                    url_card TEXT NOT NULL UNIQUE,  -- Обязательное поле с уникальностью
                    title TEXT,
                    address TEXT,
                    discount_price TEXT,  -- Используем числовой тип для цен
                    main_price TEXT,
                    old_price TEXT,
                    price_per_m2 TEXT,
                    year_of_construction TEXT,  -- Целое число для года
                    posted_at TIMESTAMPTZ DEFAULT NOW(),
                    removed_at TIMESTAMPTZ,
                    last_updated TIMESTAMPTZ DEFAULT NOW()  -- Добавляем поле для отслеживания изменений
                );

                CREATE INDEX IF NOT EXISTS idx_flats_url_card ON flats(url_card);
                CREATE INDEX IF NOT EXISTS idx_flats_posted_at ON flats(posted_at);
                """
                cursor.execute(create_table_query)
                logging.info("Таблица flats успешно создана/проверена.")

    except Exception as e:
        logging.error(f"Ошибка при создании таблицы: {e}", exc_info=True)
        raise  # Пробрасываем исключение дальше для обработки на верхнем уровне


def insert_flats(data):
    """Вставляет или обновляет данные о квартирах с пакетной обработкой."""
    if not data:
        logging.warning("Пустые данные, вставка не требуется.")
        return

    conn = None
    try:
        with psycopg2.connect(
                # dbname=os.getenv("POSTGRES_DB"),
                # user=os.getenv("POSTGRES_USER"),
                # password=os.getenv("POSTGRES_PASSWORD"),
                # host=os.getenv("POSTGRES_HOST"),
                # port=os.getenv("POSTGRES_PORT")
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="postgres",
                port=5432
        ) as conn:
            with conn.cursor() as cursor:
                insert_query = """
                INSERT INTO flats (
                    url_card, title, address, 
                    discount_price, main_price, old_price, 
                    price_per_m2, year_of_construction
                ) VALUES %s
                ON CONFLICT (url_card) DO UPDATE SET
                    title = EXCLUDED.title,
                    address = EXCLUDED.address,
                    discount_price = EXCLUDED.discount_price,
                    main_price = EXCLUDED.main_price,
                    old_price = EXCLUDED.old_price,
                    price_per_m2 = EXCLUDED.price_per_m2,
                    year_of_construction = EXCLUDED.year_of_construction,
                    last_updated = NOW(),
                    removed_at = NULL
                """

                # Подготавливаем данные для пакетной вставки
                values = [
                    (
                        flat["url_card"],
                        flat["title"],
                        flat["address"],
                        flat["discount_price"],
                        flat["main_price"],
                        flat["old_price"],
                        flat["price_per_m2"],
                        flat["year_of_construction"]
                    )
                    for flat in data.values()
                ]

                # Используем execute_values для пакетной вставки
                extras.execute_values(
                    cursor,
                    insert_query,
                    values,
                    page_size=100  # Оптимальный размер пакета
                )

                logging.info(f"Успешно обработано {len(values)} записей.")

    except Exception as e:
        logging.error(f"Ошибка при вставке данных: {e}", exc_info=True)
        raise

def load_and_process_json():
    logging.info("Запуск основного процесса")
    try:
        json_file_path = "flats.json"  # Укажите путь к вашему JSON-файлу

        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as file:
                logging.info("Чтение данных из файла")
                data = json.load(file)

                logging.info("Запуск selenium")
                # Настройки для "незаметной" работы
                options = Options()
                options.add_argument("--headless")
                options.add_argument("--disable-gpu")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                # Запуск драйвера
                # Ключевое изменение - подключение к Selenium Hub
                driver = webdriver.Chrome(options=options)

                url = "https://www.cian.ru/kupit-kvartiru-moskva-akademicheskiy-04100/"

                driver.get(url)

                time.sleep(random.uniform(3, 6))

                wait = WebDriverWait(driver, 10)
                page_number = 1


                try:
                    # Ждём появления баннера с куки и нажимаем кнопку "Понятно"
                    cookie_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, '//div[@data-name="CookiesNotification"]//button[span[text()="Понятно"]]'))
                    )
                    cookie_button.click()
                    logging.info("Баннер cookies закрыт.")
                except TimeoutException:
                    logging.error("Баннер cookies не появился — возможно, уже закрыт.")

                try:
                    while True:
                        logging.info(f"Обрабатываем страницу {page_number}")

                        soup = BeautifulSoup(driver.page_source, "html.parser")
                        listings = soup.find_all("article", {"data-name": "CardComponent"})
                        count = 0

                        for card in listings:
                            try:
                                url_card = get_url(card)
                                title = get_title(card)
                                full_address = get_address(card)
                                prices = get_price(card)
                                deadline = get_deadline(card)
                                flat_id = None

                                # Извлекаем ID из URL
                                if url_card:
                                    flat_id = url_card.strip("/").split("/")[-1]

                                # Сохраняем карточку в словарь
                                if flat_id:
                                    data_dict[flat_id] = {
                                        "url_card": url_card,
                                        "title": title,
                                        "address": full_address,
                                        "discount_price": prices[0] if prices[0] else "Отсутствует",
                                        "main_price": prices[1] if prices[1] else "Отсутствует",
                                        "old_price": prices[2] if prices[2] else "Отсутствует",
                                        "price_per_m2": prices[3] if prices[3] else "Отсутствует",
                                        "year_of_construction": deadline
                                    }
                                count += 1

                                logging.info(f'Карточка {count} записана!')

                            except Exception as e:
                                logging.error(f"Ошибка при обработке объявления {count}: {e}", exc_info=True)
                        create_table()
                        insert_flats(data_dict)
                        logging.info("Данные вставлены!")
                        try:
                            next_link = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, '//a[span[text()="Дальше"]]'))
                            )
                            driver.execute_script("arguments[0].scrollIntoView();", next_link)
                            next_link.click()
                            page_number += 1
                            logging.info("Переход на следующую страницу.")

                        except TimeoutException:
                            logging.error("Кнопка 'Дальше' неактивна или отсутствует. Конец пагинации.")
                            break

                        except ElementClickInterceptedException:
                            logging.error("Не удалось кликнуть по кнопке. Возможно, мешает баннер.")
                            break

                        try:
                            # Ждём, пока исчезнет прелоадер
                            WebDriverWait(driver, 10).until(
                                EC.invisibility_of_element_located((By.CLASS_NAME, "_93444fe79c--preloader--NHsG7"))
                            )
                        except Exception as e:
                            print("Не удалось дождаться загрузки следующей страницы:", e)

                except KeyboardInterrupt:
                    logging.error("Парсинг прерван пользователем.")
                finally:
                    driver.quit()

                    # Сохранение собранных данных в JSON
                    with open("flats.json", "w", encoding="utf-8") as file_json:
                        json.dump(data_dict, file_json, ensure_ascii=False, indent=2)

                # Вставка данных в БД
                insert_flats(data)

                logging.info("JSON файл успешно загружен и обработан.")
        else:
            logging.error("Файл JSON не найден.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке и обработке JSON: {e}", exc_info=True)


# Таймер для загрузки и обработки JSON
if __name__ == '__main__':
    logging.info("Создание таблиц")
    create_table()
    logging.info("Создание планировщика")
    scheduler = BackgroundScheduler()  # Не блокирующий
    scheduler.add_job(load_and_process_json, 'interval', days=1, next_run_time=datetime.now())
    scheduler.start()

    # Держим скрипт активным
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logging.info("Парсер остановлен")