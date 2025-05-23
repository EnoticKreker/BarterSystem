from django.urls import path

from . import views

app_name = 'barter'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('post/add/', views.product_create_or_update, name='post_add'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:post>/edit/', views.product_create_or_update, name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('offer/<int:post_id>/', views.create_offer, name='create_offer'),
    path('my_offers/', views.my_offers, name='my_offers'),
    path('offer/<int:offer_id>/accept/', views.accept_offer, name='accept_offer'),
    path('offer/<int:offer_id>/reject/', views.reject_offer, name='reject_offer'),

]
