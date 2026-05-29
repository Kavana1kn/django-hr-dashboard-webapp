from django.contrib import admin
from django.urls import path
from dashboard import views # This imports the file we updated above

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_home, name='dashboard_home'), # Links to the missing function
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]