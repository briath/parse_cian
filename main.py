import json
import random

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, ElementClickInterceptedException
)
from bs4 import BeautifulSoup
from commands import *
import undetected_chromedriver as uc

# Настройки для "незаметной" работы
options = uc.ChromeOptions()
# options.add_argument("--headless")  # Без GUI
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--start-maximized")
# options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")
options.add_argument("--disable-blink-features=AutomationControlled")

url = "https://www.cian.ru/kupit-kvartiru-moskva-akademicheskiy-04100/"
# Запуск драйвера
driver = uc.Chrome(options=options)
driver.get(url)

time.sleep(random.uniform(3, 6))

# Прокрутка вниз
driver.execute_script("window.scrollBy(0, 500)")
time.sleep(random.uniform(1, 2))

# Прокрутка вверх
driver.execute_script("window.scrollBy(0, -300)")
time.sleep(random.uniform(1, 2))

wait = WebDriverWait(driver, 10)
page_number = 1
data_dict = {}  # сюда будем собирать карточки

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
        for i in range(random.randint(1, 3)):
            # Прокрутка вниз
            driver.execute_script(f"window.scrollBy(0, {random.randint(400, 600)})")
            time.sleep(random.uniform(1, 2))

            # Прокрутка вверх
            driver.execute_script(f"window.scrollBy(0, {random.randint(-300, -100)})")
            time.sleep(random.uniform(1, 2))

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

                #  Сохраняем карточку в словарь
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
                # Ищем кнопку "Следующая"
        try:
            next_link = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//a[span[text()="Дальше"]]'))
            )
            # https://www.cian.ru/cat.php?deal_type=sale&district%5B0%5D=100&engine_version=2&offer_type=flat&p=2
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

with open("flats.json", "w", encoding="utf-8") as file_json:
    json.dump(data_dict, file_json, ensure_ascii=False, indent=2)


