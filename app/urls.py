from .views import (
    home, index, about, contact, register, register_delete, login, menu,
    update_room, room_for_sell, delete_room, delete_reservation, cancel_reservation,
    search_room, rooms_list, room_info, rent, all_room_views, error_continued,
    settings_view, user_data, booking, wallet
)
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView

def catch_all_redirect(request, path=None):
    if request.user.is_authenticated:
        return redirect('menu', id=str(request.user.id))
    else:
        return redirect('menu', id='none')


urlpatterns = [
    path('', lambda request: redirect('menu', id=request.user.id if request.user.is_authenticated else 'none')),
    path('home/', home, name='home'),
    path('index/', index, name='index'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('register', register, name='register'),
    path('register-delete', register_delete, name='register-delete'),
    path('login', login, name='login'),
    path('logout/', LogoutView.as_view(next_page='/login'), name='logout'),
    path('menu/<str:id>', menu, name='menu'),
    path('room-for-sell/<str:id>', room_for_sell, name='room-for-sell'),
    path('rooms-list/<str:id>', rooms_list, name='rooms-list'),
    path('update-room/<int:user_id>/<int:room_id>', update_room, name='update_room'),
    path('delete-room/<int:id>', delete_room, name='delete-room'),
    path('delete_reservation<int:id>', delete_reservation, name='delete_reservation'),
    path('cancel_reservation<int:id>', cancel_reservation, name='cancel_reservation'),
    path('search-room/<str:id>', search_room, name='search-room'),
    path('room-info/room_id=<int:room_id>', room_info, name='room-info'),
    path('rent/user_id=<int:user_id>/room_id=<int:room_id>', rent, name='rent'),
    path('all-room-views', all_room_views, name='all-room-views'),
    path('error-continued', error_continued, name='error-continued'),
    path('settings', settings_view, name='settings'),
    path('user-data', user_data, name='user-data'),
    path('booking', booking, name='booking'),
    path('wallet', wallet, name='wallet'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^(?P<path>.*)$', catch_all_redirect),
]
