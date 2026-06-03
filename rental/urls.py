from django.urls import path
from . import views

urlpatterns = [
    # Halaman Umum / Landing
    path('', views.landing_view, name='landing'),

    # Autentikasi
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard Pusat
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Fitur Pengguna (User)
    path('motor/browse/', views.motor_browse_view, name='motor_browse'),
    path('motor/book/<int:motor_id>/', views.booking_create_view, name='booking_create'),
    path('booking/cancel/<int:rental_id>/', views.booking_cancel_view, name='booking_cancel'),

    # Fitur Admin - CRUD Motor
    path('manage/motors/', views.motor_list_view, name='motor_list'),
    path('manage/motor/add/', views.motor_create_view, name='motor_create'),
    path('manage/motor/edit/<int:motor_id>/', views.motor_edit_view, name='motor_edit'),
    path('manage/motor/delete/<int:motor_id>/', views.motor_delete_view, name='motor_delete'),

    # Fitur Admin - Kelola Sewa & Pengguna
    path('manage/rentals/', views.rental_list_view, name='rental_list'),
    path('manage/rental/status/<int:rental_id>/<str:action>/', views.rental_update_status_view, name='rental_update_status'),
    path('manage/users/', views.user_list_view, name='user_list'),
]
