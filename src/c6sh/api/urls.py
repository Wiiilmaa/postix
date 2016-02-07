from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'preorders', views.PreorderViewSet)
router.register(r'preorderpositions', views.PreorderPositionViewSet)
router.register(r'transactions', views.TransactionViewSet)
router.register(r'listconstraints', views.ListConstraintViewSet)
router.register(r'listconstraintentries', views.ListConstraintEntryViewSet)

urlpatterns = [
    url(r'', include(router.urls, namespace='api'))
]