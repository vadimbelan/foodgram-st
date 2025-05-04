from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Универсальная пагинация: `?page=<n>&limit=<m>`.

    limit — элементов на страницу (по умолчанию — 6)
    """
    
    page_size_query_param = "limit"
    page_size = 6
