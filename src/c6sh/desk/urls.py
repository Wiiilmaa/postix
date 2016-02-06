from django.conf.urls import url
from . import views

urlpatterns = [
    url('^login/', views.LoginView.as_view(), name='login'),
    url('^$', views.main_view, name='main'),
]