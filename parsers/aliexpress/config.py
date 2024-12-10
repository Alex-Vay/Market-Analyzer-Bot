
from selenium import webdriver

headers = {
    'accept': '*/*',
    'accept-language': 'ru,en;q=0.9',
    'bx-v': '2.5.22',
    'content-type': 'application/json',
    # 'cookie': 'aer_rh=1747440015; aer_ec=wbFWf167RRUqN53eE1oAbi9D3lYd1Rb6DurEErGZ5SQFJnb0heAd/FdrfYUL6UPGoWxCPwRDpyk7Z63KJW6GA08w2qfOxTM0orLpQ+7Czr8=; _ym_uid=1674755153583905214; cna=TqpZHAGa43MCAbziNtOwWb13; aer_abid=1e2ef7493fb5439e.31d337fc.55f863b6716fd325; aep_usuc_f=b_locale=ru_RU&c_tp=RUB&region=RU&site=rus&province=917483860000000000&city=917483866975000000; adrcid=A3C-I8Qve1zDuzGpty-jLIg; tmr_lvid=b470c0dcc87e0271e4b94122bf023a49; tmr_lvidTS=1674755153034; autoRegion=lastGeoUpdate=1732129875&regionCode=917483860000000000&cityCode=917483866975000000&countryCode=RU&postalCode=620075&latitude=56.8456&longitude=60.6083; xlly_s=1; _gid=GA1.2.1154545623.1732129883; _ym_d=1732129883; acs_3=%7B%22hash%22%3A%22768a608b20ce960ff29026da95a81203ec583ad1%22%2C%22nextSyncTime%22%3A1732216283496%2C%22syncLog%22%3A%7B%22224%22%3A1732129883496%2C%221228%22%3A1732129883496%2C%221230%22%3A1732129883496%7D%7D; domain_sid=LLmN5g3WBfiMdgHBmwQ0T%3A1732129884434; aep_common_f=ESoXR0ISl/RV5xPJHysVZtGvNc+LkKTruI0hnU1QUshJcpNzkRAGwg==; xman_f=id6fRRx7PvRICKatsz/vM57MznDdOJq+h7hDNedFD3Vbw6PXfgtSTjvRZIv79BK6Au6NDvPZaNScifN6534FqSzgYN/Gvs2VvKQbUmvoil9a4WcrZNF+TNwTvwQenkPWJjrD/NccKcCoBgt6U68Tg4Fewd8JYmp/o1t03pxOuPmuTxanlIyB9xHwLLasWByhBrtNEY9RYn9qa+p4zmbxc1GTFxH3FC9Aw/8RLBwQSyu/Jws/dckex9eeB3sJ3go9xwMNq1Tgc4oxJQ/qqknRAv5JzvadVWLDvYcMETlHMRh7yhibgP9U8Kv9nDKWkiKXglaGUMwvyfEzsFFMZYf79DLKfFUIuCcW+5/WyxEm+fYWNZiDb/YKlPTHlHcJeRzOb6GOuNTP+Hj7LCqb4uuBr/tPu3nx1Cp4lWAAovVD+ZZSYZzpOibzLQ==; aer_auth_track_info=yMW2ERQkpZN6IqJU78tCTkX/6E8X0Rq5JtlZMNpncNqB1vr0F4S24IXEYHCVAyzl5ocR5X2evSNoLMkiboyf+ycR5aFztHhpaalxfxJJrRzlqOgBfz+RCx+c0XlWyhYEhDhASDoLAwYTgzCNFLERIw==; xman_us_f=x_locale=ru_RU&x_l=0&x_user=RU|sasha.ignatov93|Key|ifm|835926012&x_lid=ru1216252041usbw; ae_ru_pp_v=1.0.2; uxs_uid=06544a80-a77e-11ef-87de-1bb9f540d8e5; _ga=GA1.2.651990034.1728989787; _ga_LHVQFP44DC=GS1.1.1732134518.1.1.1732134767.60.0.0; xman_us_t=; xman_t=n+kqFQRtileh56zz2oMlCHTp6zgjV/okIaIo6goEzTYjKg9PrMHeovinltdLNVO4; _ym_isad=2; adrdel=1732209680564; _ym_visorc=b; tmr_detect=0%7C1732211500941; a_r_t_info=%7B%22name%22%3A%22wholesale%22%2C%22id%22%3A%22e9157276-432d-4832-85ae-c55fa84c686f%22%2C%22chinaName%22%3A%22productlist%22%7D; a_t_info=%7B%22name%22%3A%22wholesale%22%2C%22id%22%3A%222c5e8098-cdc5-4853-b5c6-593959187416%22%2C%22chinaName%22%3A%22productlist%22%7D; _gat_UA-164782000-1=1; isg=BCcnD8ceDAE23oxgVZS6I8cNtlvxrPuOSt2JUPmUQ7bd6EeqAXyL3mXuC_D2NtMG; intl_common_forever=SxAuHqa2LP/BpQQnzCEh6+ElAhanunepnhDsgYDw63Zi8vTorIHDbA==; ali_apache_id=33.22.87.194.1732211566397.976086.0; JSESSIONID=2C634262D9CF9DDC2AB1E8E79E0AC5F1; tfstk=fd0tiZ9BFpvGorCdvit3nvSOh2AHtqhZIAl5o-2GcvHKnvGijZ40cZhjgoN0sP6fMvMIjNxZnZCZJYQcSd-ZGZU0lLvkrUcw_rzXE7bLhMwagXwby7sSbfz4lp4cocmr_YNFSo0blBUQMS1_lZN_dBF0a5abCo6CA7wQl-MbfkZQ_7If5ZZ6RBF4d-ablXH16-f_HZn0ot5Ozp2llZgpble-1ibfl2FTXbc_pXcnJ5ETFkDwqG0sKjgi7k-Pqrln2xnjdeQtHfiShR0BFZem4ShbwzTPwJgtM2EZxOs_wPeTVVZCZah8cD3LSV9V4XcLCuUnxHJgmPHt48r6Ypkx9RDjWk69K-motVZKFpbK3onsBWa54J3oy4VCE8FcfBdd0ir_T-cZ7lKsx5du98AhxiS4xWPLEBdd0ir_TWektUjV0kVF.',
    'origin': 'https://aliexpress.ru',
    'priority': 'u=1, i',
    'referer': 'https://aliexpress.ru/wholesale?SearchText=%D0%BD%D0%BE%D1%83%D1%82%D0%B1%D1%83%D0%BA+lenovo+legion+5+pro&g=y&page=1',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}
user_agent = headers['user-agent']
options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={user_agent}')
driver = webdriver.Chrome()
driver.get('https://aliexpress.ru')
row_cookies = driver.get_cookies()
driver.quit()
cookies = {row['name']: row['value'] for row in row_cookies}


