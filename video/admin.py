from django.contrib import admin
from .models import Membership , UserMemberShip, Subscription

admin.site.register(Membership)
admin.site.register(UserMemberShip)
admin.site.register(Subscription)