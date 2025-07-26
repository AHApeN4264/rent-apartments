from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .models import User

def register_view(request):
    if request.method == 'POST':
        author = request.POST.get('author')
        username = request.POST.get('username')
        password = request.POST.get('password')
        client_id = request.POST.get('client_id', None)
        client_secret = request.POST.get('client_secret', None)

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Користувач '{username}' вже існує")
            return redirect('register')

        hashed_password = make_password(password)

        try:
            User.objects.create(
                username=username,
                password=hashed_password,
                raw_password=password,
                author=author,
                client_id=client_id,
                client_secret=client_secret
            )
            messages.success(request, "Користувача успішно створено")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Помилка реєстрації: {str(e)}")
            return redirect('register')

    return render(request, 'register.html')

from django.shortcuts import redirect

def root(request):
    return redirect('login')


