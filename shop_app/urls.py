from django.urls import path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('registration/', views.registration, name='registration'),
    path('category/<int:id>/', views.open_category, name='category_products'),
    path('add_product/<int:id>/', views.add_product, name='add_product'),
    path('delete_product/<int:id>/', views.delete_product, name='delete_product'),
    path('cart/', views.cart, name='cart'),
    path('add_product_in_cart/<int:id>', views.add_product_in_cart, name='add_product_in_cart'),
    path('remove_from_cart/<int:cart_product_id>', views.remove_form_cart, name='remove_from_cart'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)