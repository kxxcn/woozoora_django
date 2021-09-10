from django.urls import path

from . import views

urlpatterns = [
    path('', views.index),

    path('policy/personal', views.personal),
    path('policy/source', views.source),

    path('dashboard', views.dashboard),

    path('user/register', views.register_user),
    path('user/<str:user_id>', views.users),
    path('user/<str:user_id>/token', views.token),
    path('user/<str:user_id>/transactions', views.transactions),
    path('user/<str:user_id>/code', views.code),
    path('user/<str:user_id>/year', views.year),
    path('user/<str:user_id>/budget', views.budget),
    path('user/<str:user_id>/ask', views.ask),
    path('user/<str:user_id>/leave', views.leave),

    path('transaction', views.transaction),

    path('notice', views.notice),

    path('reply', views.reply),
]
