from django.urls import path
from . import insurance_views, views
from .access import staff_required

app_name = 'website'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('packages/', views.packages, name='packages'),
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('visa-requirements/', views.visa_requirements, name='visa'),
    path('travel-insurance/', staff_required(insurance_views.insurance), name='insurance'),
    path('travel-insurance/quote/', staff_required(insurance_views.insurance_quote), name='insurance_quote'),
    path('travel-insurance/lookup/', staff_required(insurance_views.insurance_lookup), name='insurance_lookup'),
    path('travel-insurance/purchase/', staff_required(insurance_views.insurance_purchase), name='insurance_purchase'),
    path('travel-insurance/order/<int:pk>/', staff_required(insurance_views.insurance_success), name='insurance_success'),
    path('travel-insurance/order/<int:pk>/pdf/', staff_required(insurance_views.insurance_pdf), name='insurance_pdf'),
    path('travel-insurance/order/<int:pk>/resend-email/', staff_required(insurance_views.insurance_resend_email), name='insurance_resend_email'),
    path('esim/', staff_required(views.esim), name='esim'),
    path('esim/load-more/', staff_required(views.esim_load_more), name='esim_load_more'),
    path('esim/lookup/', staff_required(views.esim_lookup), name='esim_lookup'),
    path('esim/purchase/', staff_required(views.esim_purchase), name='esim_purchase'),
    path('esim/order/<int:pk>/', staff_required(views.esim_success), name='esim_success'),
    path('esim/order/<int:pk>/resend-email/', staff_required(views.esim_resend_email), name='esim_resend_email'),
    path('esim/order/<int:pk>/qr.png', staff_required(views.esim_qr), name='esim_qr'),
    path('contact/', views.contact, name='contact'),
]
