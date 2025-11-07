from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'rewards'

router = DefaultRouter()
router.register(r'items', views.RedeemableItemViewSet, basename='redeemable-item')
router.register(r'transactions', views.RewardTransactionViewSet, basename='reward-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('redeem/', views.RedeemRewardView.as_view(), name='redeem-reward'),
]