from django.contrib import admin
from django.urls import path
from .views import thank_you_view, register_event_view,MpesaExpressCallback,initiate_mpesa_stk_push

app_name = 'events'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', register_event_view, name='register_event'),
    path('thank-you/', thank_you_view, name='thank_you'),
    path('initiate/', initiate_mpesa_stk_push, name='initiate_stk_push'),
    path('callback/',MpesaExpressCallback.as_view(), name='mpesa_express_callback'),
]