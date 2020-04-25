from django.urls import path

from rates_api.views import GetExchangeRatesAPIView

urlpatterns = [
    path('', GetExchangeRatesAPIView.as_view())
]
