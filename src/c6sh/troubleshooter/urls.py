from django.conf.urls import url

from . import views

urlpatterns = [
    url('^login/$', views.LoginView.as_view(), name='login'),
    url('^logout/$', views.logout_view, name='logout'),
    url('^transactions/(?P<pk>[0-9]+)/$', views.TransactionDetailView.as_view(), name='transaction-detail'),
    url('^transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    url('^$', views.main_view, name='main'),
]
