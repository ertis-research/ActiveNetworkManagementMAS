from nturl2path import url2pathname
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views
from DataMonitoring.views import HomeView, LoginView, ErrorView, ForecastingView, ScenariosView, ConsumptionsView, ModelsProcessingView, ActionListAPIRestView, ForeCastingAPIRestView, ConsumptionsAPIRestView, WeatherAPIRestView

urlpatterns = [
    path('Login', LoginView.as_view(), name ='login'),
    path('Index', HomeView.as_view(), name ='index'),
    path('Error', ErrorView.as_view(), name ='error'),
    path('Forecasting', ForecastingView.as_view(), name ='forecasting'),
    path('Models', ScenariosView.as_view(), name ='models'),
    path('Consumptions', ConsumptionsView.as_view(), name ='consumptions'),
    path('UploadFiles', csrf_exempt(ModelsProcessingView.as_view()), name ='uploadFiles'),
    path('getActionList', csrf_exempt(ActionListAPIRestView.as_view()), name ='getActionList'),
    path('getFutureConsumption', csrf_exempt(ForeCastingAPIRestView.as_view()), name ='getFutureConsumption'),
    path('getConsumptions', csrf_exempt(ConsumptionsAPIRestView.as_view()), name ='getConsumptions'),
    path('getWeatherData', csrf_exempt(WeatherAPIRestView.as_view()), name ='getWeatherData'),
]