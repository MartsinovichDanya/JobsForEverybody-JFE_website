from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('index', views.index),
    path('login', views.login),
    path('logout', views.logout),
    path('registration', views.registration),
    path('settings', views.settings),
    path('delete_vacancy/<int:vac_id>', views.delete_vacancy),
]
