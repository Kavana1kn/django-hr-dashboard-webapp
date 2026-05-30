from django.contrib import admin
from django.urls import path
from dashboard import views  # <-- Corrected import target

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_home, name='dashboard_home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
]