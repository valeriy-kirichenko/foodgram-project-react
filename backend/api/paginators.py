from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Разбивает список рецептов на страницы.

    Пользователь может настраивать количество выводимых на страницу рецептов
    указав значение параметра limit в запросе.
    """
    page_size = 6
    page_size_query_param = 'limit'
