from django.urls import path
from milkapp.views import (
   login,
   register,
   calendar,
   logout_view,
   add_milk_shift,
   dashboard,
   update_state,
   get_month_states,
   get_milk_shifts,
   add_milk_entry
)

urlpatterns = [
   path('', login, name='login'),
   path('register/', register, name='register'),
   path('calendar/', calendar, name='calendar'),
   path('add-milk-shift/', add_milk_shift, name='add_milk_shift'),
   path('dashboard/',dashboard,name='dashboard'),
   path('update_state/', update_state, name='update_state'),

   path('get_month_states/',get_month_states,name='get_month_states'),
   path('logout/', logout_view, name='logout'),  
   path('add-milk-entry/', add_milk_entry, name='add_milk_entry'),
   path('get_milk_shifts/<int:shift_id>/', get_milk_shifts, name='get_milk_shifts'),  
]
