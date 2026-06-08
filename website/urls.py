from django.urls import path
from . import views

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('packages/', views.packages, name='packages'),
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('visa-requirements/', views.visa_requirements, name='visa'),
    path('contact/', views.contact, name='contact'),
]
