from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Room, Reservation
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from datetime import date
import datetime
from django.views.decorators.csrf import csrf_exempt
from datetime import date, timedelta, datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction

# home, index, about, contact, register, register_delete, login, menu, update_room, room_for_sell, delete_room, delete_reservation, cancel_reservation,
# search_room, rooms_list, room_info, rent, all_room_views, error_continued, settings_view, user_data, booking

User = get_user_model()

def home(request):
    return HttpResponse(request, 'home.html')

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def settings_view(request):
    return render(request, 'settings.html')

def user_data(request):
    return render(request, 'user_data.html')

def menu(request, id=None):
    if id == 'none' or id is None:
        user = None
    else:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return redirect('menu_none')
    return render(request, 'menu.html', {'user': user})

def update_room(request, user_id, room_id):
    user = None
    if str(user_id) != 'none':
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            user = None
    if user is None:
        return redirect('error-continued')

    room = get_object_or_404(Room, id=room_id, owner=user)

    if request.method == 'POST':
        room.title = request.POST.get('title')
        room.description = request.POST.get('description')
        if 'photo' in request.FILES:
            room.photo = request.FILES['photo']
        price_raw = request.POST.get('price')
        try:
            room.price = Decimal(price_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Ціна має бути числом")
        room.address = request.POST.get('address')
        room.phone_number = request.POST.get('phone_number')
        room.save()
        messages.success(request, "Інформацію про кімнату оновлено")
        return redirect('rooms-list', id=user_id)

    return render(request, 'update-room.html', {
        'user': user,
        'room': room,
        'today': date.today().isoformat()
    })

def rooms_list(request, id):
    all_rooms = Room.objects.filter(owner_id=id)
    valid_rooms = []

    for room in all_rooms:
        try:
            Decimal(room.price)
            valid_rooms.append(room)
        except InvalidOperation as e:
            print(f"[!] Ошибка в комнате: id={room.id}, price={room.price} — {e}")
            continue

    return render(request, 'rooms_list.html', {
        'rooms': valid_rooms,
        'title': 'Список кімнат'
    })

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Користувач з ім'ям '{username}' вже існує")
            return redirect('register')
        if User.objects.filter(email=email).exists():
            messages.error(request, f"Користувач з email '{email}' вже існує")
            return redirect('register')
        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, f"Користувач з номером телефону '{phone_number}' вже існує")
            return redirect('register')
        User.objects.create(
            username=username,
            phone_number=phone_number,
            email=email,
            password=make_password(password)
        )
        messages.success(request, "Користувача успішно створено")
        return redirect('login')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not phone_number or not email or not password:
            messages.error(request, "Пожалуйста, заполните все поля.")
            return render(request, 'login.html')

        errors = []

        user_by_username = User.objects.filter(username=username).first()
        if not user_by_username:
            errors.append("Ім'я користувача не знайдено.")
        
        user_by_phone = User.objects.filter(phone_number=phone_number).first()
        if not user_by_phone:
            errors.append("Номер телефону не знайдено.")

        user_by_email = User.objects.filter(email=email).first()
        if not user_by_email:
            errors.append("Електронну пошту не знайдено.")

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'login.html')

        try:
            user = User.objects.get(username=username, phone_number=phone_number, email=email)
        except User.DoesNotExist:
            messages.error(request, "Користувача з такими комбінаціями даних не знайдено.")
            return render(request, 'login.html')

        if not check_password(password, user.password):
            messages.error(request, "Невірний пароль.")
            return render(request, 'login.html')

        auth_login(request, user)
        return redirect(reverse('menu', args=[user.id]))

    return render(request, 'login.html')

def register_delete(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(phone_number=phone_number)
            except User.DoesNotExist:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None
        if user:
            if check_password(password, user.password):
                user.delete()
                messages.success(request, "Користувача успішно видалено")
                return redirect('login')
            else:
                messages.error(request, "Невірний пароль")
        else:
            messages.error(request, "Користувач з такими даними не знайдений")

    return render(request, 'register-delete.html')

@login_required(login_url='/error-continued')
def room_for_sell(request, id):
    if not request.user.is_authenticated or str(request.user.id) != str(id):
        return redirect('/error-continued')

    user = get_object_or_404(User, id=id)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        price_raw = request.POST.get('price')

        try:
            price = Decimal(price_raw)
        except (InvalidOperation, TypeError):
            messages.error(request, "Ціна має бути числом")
            return redirect('room-for-sell', id=user.id)

        Room.objects.create(
            owner=user,
            title=title,
            description=description,
            photo=photo,
            price=price,
            address=address,
            phone_number=phone_number,
            first_data=date.today(),
            last_data=date.today()  
        )

        messages.success(request, "Кімнату успішно виставлено на продаж!")
        return redirect('menu', id=user.id)

    return render(request, 'room-for-sell.html', {'user': user})

@csrf_exempt
def delete_room(request, id):
    if request.method == 'POST':
        try:
            room = Room.objects.get(id=id)
            user_id = room.owner.id
            room.delete()
            messages.success(request, f"Кімнату з ID {id} видалено")
        except Room.DoesNotExist:
            messages.error(request, f"Кімнату з ID {id} не знайдено")
        return redirect('rooms-list', id=user_id)
    else:
        return redirect('rooms-list', id=request.user.id)
    
@csrf_exempt
def delete_reservation(request, id):
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=id)
            user_id = reservation.room.owner.id
            reservation.delete()
            messages.success(request, f"Бронювання з ID {id} видалено")
        except Reservation.DoesNotExist:
            messages.error(request, f"Бронювання з ID {id} не знайдено")
        return redirect('booking') 
    else:
        return redirect('booking')
    
def cancel_reservation(request, id):
    if request.method == 'POST':
        try:
            reservation = Reservation.objects.get(id=id)
            user = reservation.user  # Предполагается, что Reservation имеет ForeignKey на user

            # Возвращаем деньги пользователю
            user.wallet += reservation.total_price
            user.save()

            reservation.delete()
            messages.success(request, f"Бронювання з ID {id} скасовано. Кошти {reservation.total_price} грн повернено на ваш баланс.")
        except Reservation.DoesNotExist:
            messages.error(request, f"Бронювання з ID {id} не знайдено")
        except Exception as e:
            messages.error(request, f"Помилка при скасуванні: {str(e)}")
        return redirect('booking')
    else:
        return redirect('booking')

def search_room(request, id):
    title_query = request.GET.get('title')
    rooms = []

    if title_query:
        all_rooms = Room.objects.filter(title__icontains=title_query)
        for room in all_rooms:
            try:
                Decimal(room.price)
                rooms.append(room)
            except (InvalidOperation, TypeError, ValueError):
                continue

    context = {
        'title': 'Знайти Кімнату',
        'rooms': rooms,
        'user': request.user,
    }
    return render(request, 'search-room.html', context)

def room_info(request, room_id):
    room = get_object_or_404(Room, id=room_id)

    context = {
        'title': f'Інформація про кімнату: {room.title}',
        'room': room,
    }

    return render(request, 'room-info.html', context)

def rent(request, user_id, room_id): 
    if user_id == 'none':
        return redirect('error-continued')
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('error-continued')

    room = get_object_or_404(Room, id=room_id)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    context = {
        'title': f'Інформація про кімнату: {room.title}',
        'room': room,
        'user': request.user,
        'owner': user,
        'today': today.isoformat(),
        'tomorrow': tomorrow.isoformat(),
    }

    if request.method == 'POST':
        start_str = request.POST.get('first_data')
        end_str = request.POST.get('last_data')
        
        if not start_str or not end_str:
            messages.error(request, "Будь ласка, введіть дати початку та завершення.")
        else:
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_date = datetime.strptime(end_str, "%Y-%m-%d").date()
                if end_date >= start_date:
                    days = (end_date - start_date).days + 1
                    total_price = days * room.price

                    if request.user.wallet < total_price:
                        messages.error(request, "Недостатньо коштів для оренди.")
                        return render(request, 'rent.html', context)

                    with transaction.atomic():
                        Reservation.objects.create(
                            user=request.user,
                            title=room.title,
                            photo=room.photo,
                            room=room,
                            phone_number=getattr(request.user, 'phone_number', ''),
                            start_date=start_date,
                            end_date=end_date,
                            price=room.price,
                            total_price=total_price,
                            address=room.address
                        )
                        request.user.wallet -= total_price
                        request.user.save()

                    messages.success(
                        request,
                        f"Кімнату успішно заброньовано! з {start_date} по {end_date} — {days} днів, {total_price:.2f} грн"
                    )
                    return redirect('menu', id=request.user.id)
                else:
                    messages.error(request, "Дата завершення не може бути раніше за початкову.")
            except ValueError as e:
                print("Date parsing error:", e)
                messages.error(request, "Помилка у форматі дат.")
    return render(request, 'rent.html', context)

def all_room_views(request):
    title_query = request.GET.get('title')
    rooms = []

    if title_query:
        all_rooms = Room.objects.filter(title__icontains=title_query)
        for room in all_rooms:
            try:
                Decimal(room.price)
                rooms.append(room)
            except (InvalidOperation, TypeError, ValueError):
                continue
    else:
        rooms = list(Room.objects.all())

    context = {
        'title': 'Знайти Кімнату',
        'rooms': rooms,
        'user': request.user,
    }
    return render(request, 'all-room-views.html', context)

def error_continued(request):
    return render(request, 'error-continued.html')

def booking(request):
    reservations = Reservation.objects.all()  

    context = {
        'title': 'Всі бронювання',
        'rooms': reservations, 
    }
    return render(request, 'booking.html', context)

@login_required
def wallet(request):
    if request.method == 'POST':
        amount = request.POST.get('amount') or request.POST.get('custom_amount')
        try:
            amount = Decimal(amount)
            if amount > 0:
                request.user.wallet += amount
                request.user.save()
                messages.success(request, f'Баланс успішно поповнено на {amount:.2f} грн.')
            else:
                messages.error(request, 'Сума має бути більшою за 0.')
        except Exception:
            messages.error(request, 'Некоректне значення.')

        return redirect('wallet')

    return render(request, 'wallet.html', {'title': 'Поповнення балансу'})

