from django.urls import path

from . import views

app_name = 'barter'

urlpatterns = [
    path('', views.home, name='home'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail, name='post_detail'),
    path('post/add/', views.product_create_or_update, name='post_add'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:post>/edit/', views.product_create_or_update, name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
]
