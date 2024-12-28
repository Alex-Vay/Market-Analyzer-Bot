import difflib
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


def smart_function(searched_title: str, index_and_titles: dict):
    best_match_index = 0
    best_ratio = 0
    for index, product_title in index_and_titles.items():
        try:

            sm = difflib.SequenceMatcher(None, searched_title.lower(), product_title.lower())
            similarity_ratio = sm.ratio()

            if similarity_ratio > best_ratio:
                best_ratio = similarity_ratio
                best_match_index = index
        except Exception as e:
            print(f"Ошибка при обработке товара: {e}")
            continue
    return best_match_index


def get_rating_and_sales(soup_object: BeautifulSoup):
    rating_sales_data = soup_object.find('div', attrs={'class': 'product-card__bottom-wrap'}).find('p', attrs={
        'class': 'product-card__rating-wrap'}).find_all('span')
    rating = rating_sales_data[0].text if rating_sales_data[0].text else 'Отсутствует'
    return f"Рейтинг: {rating}. {rating_sales_data[1].text}"


def get_title_and_price(soup_object: BeautifulSoup):
    title_and_price = soup_object.find('div', attrs={'class': 'product-card__middle-wrap'})
    product_price = title_and_price.find('div', attrs={'class': 'product-card__price'}).find('ins')
    product_price = product_price.text.replace('\xa0', '')
    product_title = title_and_price.find('h2', attrs={'class': 'product-card__brand-wrap'}).find('span', attrs={
        "class": 'product-card__name'}).text
    product_title = product_title.strip(' \/')
    return product_title, product_price


def get_product(item_name):
    '''поиск товара сразу в url
    item_name: товар, который вводит пользователь в боте'''
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'  # chrome
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    url = f'https://www.wildberries.ru/catalog/0/search.aspx?search={item_name}&sort=priceup'
    driver.get(url)
    # Ожидание загрузки страницы
    wait_selector = '#app #catalog .catalog-page__content .product-card .product-card__wrapper .product-card__rating-wrap'
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_selector)))
    # ссылка на карточку товара
    cards_count = 3
    xpath_selector = f'//div[@id="catalog"]//div[@class="catalog-page__content"]//article[@data-card-index < {cards_count}]'
    product_cards = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, xpath_selector))
    )
    products_titles = {
        int(product.get_attribute('data-card-index')): product.find_element(
            By.CSS_SELECTOR, '.product-card__middle-wrap .product-card__brand-wrap .product-card__name').text for
        product in product_cards}

    most_matched_titles_index = smart_function(item_name, products_titles)
    product_card = product_cards[most_matched_titles_index]
    soup = BeautifulSoup(product_card.get_attribute('outerHTML'), 'lxml')
    product_link = soup.find('a', attrs={'class': 'product-card__link'}).get('href')
    product_title, product_price = get_title_and_price(soup)
    product_rating_sales = get_rating_and_sales(soup)
    driver.quit()
    return product_title, product_price, product_rating_sales, product_link,


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product('процессор ryzen'))
    print('Поиск завершен.')
