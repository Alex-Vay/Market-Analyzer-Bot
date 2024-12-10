import difflib
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_product_title(product_element):
    try:
        title_element = product_element.find_element(By.CSS_SELECTOR, '.product-card__name')
        title = title_element.text.strip().replace("/", "").strip()
        return title
    except:
        return None

def extract_product_price(product_element):
    try:
        price_element = product_element.find_element(By.CSS_SELECTOR, '.price__lower-price')
        price = price_element.text.strip().replace('&nbsp;', ' ')  # Удаляем &nbsp; и заменяем на пробел
        # Дополнительная очистка цены (удаление символов, кроме цифр и пробелов)
        price = ''.join(c for c in price if c.isdigit() or c.isspace())
        return price.strip()
    except:
        return None

def extract_product_rating(product_element):
    try:
        rating_element = product_element.find_element(By.CSS_SELECTOR, '.product-card__rating-wrap')
        # Проверяем наличие оценок
        rating_text = rating_element.text.strip()
        if "Нет оценок" in rating_text:
            return "Нет оценок"  # Возвращаем "Нет оценок", если оценок нет
        else:
            return ""
    except:
        return None

def extract_product_url(product_element):
    try:
        url_element = product_element.find_element(By.TAG_NAME, 'a')
        return url_element.get_attribute('href')
    except:
        return None


def get_product(item_name='', num_products_to_check=15):
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={item_name}'
    driver.get(url)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'searchInput')))
    time.sleep(2)

    products = driver.find_elements(By.CSS_SELECTOR, '.product-card')[:num_products_to_check]

    best_match = None
    best_ratio = 0

    for product in products:
        try:
            product_title = extract_product_title(product)
            if product_title:
                sm = difflib.SequenceMatcher(None, item_name.lower(), product_title.lower())
                similarity_ratio = sm.ratio()
                if similarity_ratio > best_ratio:
                    best_ratio = similarity_ratio
                    best_match = product

        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")
            continue

    if best_match:
        product_title = extract_product_title(best_match)
        product_price = extract_product_price(best_match)
        product_rating = extract_product_rating(best_match)
        product_url = extract_product_url(best_match)
        driver.quit()
        return product_url, product_title, product_price, product_rating
    else:
        driver.quit()
        return None, None, None, None


if name == 'main':
    print('Поиск товара...')
    result = get_product('ноутбук lenovo legion 7')
    if result[0]:
        print(result)
    else:
        print("Товар не найден")
    print('Поиск завершен.')