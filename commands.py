import random
import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

# Настройка логирования
logging.basicConfig(
    filename='parser.log',
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


def get_url(card):
    try:
        card1 = card.find('div', attrs={'data-testid': 'offer-card'})
        if not card1:
            logging.error("Карточка не найдена")
            return "Ссылка не обнаружена"

        # Находим ссылку внутри него
        link_tag = card1.find('a', href=True)
        if not link_tag:
            logging.error("Ссылка не найдена")
            return "Ссылка не найдена"

        url = link_tag['href']

        logging.info(f'Найден URL: {url}')

        return url
    except Exception as e:
        logging.error(f"Ошибка при поиске url: {e}", exc_info=True)


def get_title(card):
    try:
        title_tag = card.find("span", {"data-mark": "OfferTitle"})
        title = title_tag.text.strip() if title_tag else ""

        logging.info(f'Заголовок найден: {title}')

        return title

    except Exception as e:
        logging.error(f"Ошибка при обработке карточки: {e}", exc_info=True)


def get_address(card):
    try:
        # Находим все элементы адреса
        geo_links = card.find_all('a', attrs={'data-name': 'GeoLabel'})
        geo_parts = [link.get_text(strip=True).replace('\xa0', ' ') for link in geo_links]

        # Собираем полный адрес
        full_address = ', '.join(geo_parts)

        # Логгируем результат
        logging.info(f'Адрес найден: {full_address}')

        return full_address

    except Exception as e:
        logging.error(f"Ошибка при извлечении адреса: {e}", exc_info=True)


def get_price(card):
    try:
        # Основная цена (если нет скидки)
        main_price_tag = card.find('span', attrs={'data-mark': 'MainPrice'})
        main_price = main_price_tag.get_text(strip=True).replace('\xa0', ' ') if main_price_tag else None

        # Цена по скидке (если есть)
        discount_price_tag = card.find('span', attrs={'data-testid': 'offer-discount-new-price'})
        discount_price = discount_price_tag.get_text(strip=True).replace('\xa0', ' ') if discount_price_tag else None

        # Цена по скидке (если есть)
        old_price = card.find('span', attrs={'data-testid': 'offer-discount-old-price'})
        old_price = old_price.get_text(strip=True).replace('\xa0', ' ') if old_price else None

        # Цена за квадратный метр
        price_per_m2_tag = card.find('p', attrs={'data-mark': 'PriceInfo'})
        price_per_m2 = price_per_m2_tag.get_text(strip=True).replace('\xa0', ' ') if price_per_m2_tag else None


        logging.info(f'Скидочная цена: {discount_price}')
        logging.info(f'Основная цена: {main_price}')
        logging.info(f'Старая цена: {old_price}')
        logging.info(f'Цена за м²: {price_per_m2}')

        return discount_price, main_price, old_price, price_per_m2
    except Exception as e:
        logging.error(f"Ошибка при извлечении цен: {e}", exc_info=True)


def get_deadline(card):
    try:
        # Ищем блок с датой сдачи
        deadline_tag = card.find('span', attrs={'data-mark': 'Deadline'})
        deadline_text = deadline_tag.get_text(strip=True) if deadline_tag else None

        # Вывод
        logging.info(f'Год постройки найден: {deadline_text}')

        return deadline_text
    except Exception as e:
        logging.error(f"Ошибка при извлечении года постройки: {e}", exc_info=True)


def scroll_and_wait(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(random.randint(6, 12)):  # Кол-во прокруток
        cards_before = driver.find_elements(By.CSS_SELECTOR, '[data-testid="offer-card"]')
        num_before = len(cards_before)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(1, 4))  # Дать странице шанс начать загружать данные

        try:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, '[data-testid="offer-card"]')) > num_before
            )
            a = len(driver.find_elements(By.CSS_SELECTOR, '[data-testid="offer-card"]'))
            print(f"Подгружено еще объявлений. Всего: {a}")
        except:
            print("Больше карточек не появилось — возможно, достигнут конец.")
            break

        # Проверка, не достигли ли конца
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height