from django.contrib import admin

from .models import Sale, Payment, Kind, Item, Safe, Client, Daycome, Lose, SupplierPay, Supplier

admin.site.register(Sale)
admin.site.register(Payment)
admin.site.register(Kind)
admin.site.register(Item)
admin.site.register(Safe)
admin.site.register(Client)
admin.site.register(Lose)
admin.site.register(Daycome)
admin.site.register(Supplier)
admin.site.register(SupplierPay)