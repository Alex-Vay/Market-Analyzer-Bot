import bs4
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import undetected_chromedriver as uc


# div тег, класс которого начинается с шаблона, а в конце уникальные значения
# div = driver.find_element(By.CSS_SELECTOR, '[class^="contai"]')
# так можно див искать по id (*id="/content/page/fancyPage/*)

def get_product(item_name='realme 10'):
    '''поиск товара на главной страничке
    item_name: товар, который вводит пользователь в боте'''

    driver = uc.Chrome()
    driver.implicitly_wait(5)
    url = f'https://market.yandex.ru/search?text={item_name}'
    driver.get(url)
    # Ожидание загрузки страницы
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'aside')))
    # прогрутим браузер до первой кнопки 'В корзину', т.к. div тег с товаром не видно
    cart_button = driver.find_element(By.XPATH,
                                      '//button[@aria-label="В корзину" and @data-auto="cartButton" and @type="button"]')
    driver.execute_script("return arguments[0].scrollIntoView(true);", cart_button)
    # div тег где находится информация о товаре
    div_product = driver.find_element(By.CSS_SELECTOR,
                                      'div[data-auto-themename="listDetailed"] div._1H-VK').get_attribute('outerHTML')
    soup = bs4.BeautifulSoup(div_product, 'lxml')
    description = soup.find('div', attrs={'class': '_1ENFO'})
    title = description.find('div', attrs={'data-baobab-name': 'title'}).text
    link = description.find('a').get('href')
    rating = description.find('div', attrs={'data-baobab-name': 'rating'}).find_all('span', limit=2)
    rating = f"{rating[0].text}, {rating[1].text}"
    link = f'https://market.yandex.ru/{link}'
    price = soup.find('span', attrs={'data-auto': 'snippet-price-current'}).text

    driver.close()
    driver.quit()
    return title, link, rating, price


if __name__ == '__main__':
    print('Поиск товара...')
    print(get_product())
    print('Поиск завершен.')
