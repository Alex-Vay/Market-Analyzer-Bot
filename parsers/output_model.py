class ProductOutput:
    def __init__(self, shop_name, title, price, rating_info, link):
        self.__shop_name = shop_name
        self.__title = title
        self.__price = price
        self.__rating_info = rating_info
        self.__link = link

    @property
    def shop_name(self):
        return self.__shop_name

    @property
    def title(self):
        return self.__title

    @property
    def price(self):
        return self.__price

    @property
    def rating_info(self):
        return self.__rating_info

    @property
    def link(self):
        return self.__link