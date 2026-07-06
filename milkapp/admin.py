from django.contrib import admin
from milkapp.models import milkShiftNameModel, userProfileModel, updateMilkEntryModel, totalPriceModel

admin.site.register(userProfileModel)
admin.site.register(updateMilkEntryModel)
admin.site.register(milkShiftNameModel)
admin.site.register(totalPriceModel)