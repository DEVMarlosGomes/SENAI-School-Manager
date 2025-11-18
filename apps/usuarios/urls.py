from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('registrar/', views.register_view, name='registrar'),
    path('registro-pendente/', views.registro_pendente, name='registro_pendente'),
    path('complete-profile/', views.complete_profile, name='complete_profile'),
    path('redirecionar-dashboard/', views.redirecionar_dashboard, name='redirecionar_dashboard'),  # ESSENCIAL!
    path('', views.home_view, name='home'),
]
