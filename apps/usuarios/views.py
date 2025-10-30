# apps.usuarios/views.py

from django.shortcuts import render

def login_view(request):
    # Por enquanto, apenas renderiza um template de placeholder
    return render(request, 'usuarios/login.html')