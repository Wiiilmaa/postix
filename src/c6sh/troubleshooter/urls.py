from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.logout_view, name='logout'),
    url('^transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    url('^$', views.main_view, name='main'),
]
