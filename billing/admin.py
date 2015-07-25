from django.contrib import admin

from .models import Membership, Transaction, UserMerchantId


admin.site.register(Membership)
admin.site.register(Transaction)
admin.site.register(UserMerchantId)
