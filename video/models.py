from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY
from datetime import datetime

User = get_user_model()



Membership_choices = (
    ('Enterprise', 'ent'),
    ('Professional', 'pro'),
    ('Free', 'free'),
)



class Membership(models.Model):
    slug = models.SlugField()
    membership_type = models.CharField(choices=Membership_choices,default='Free', max_length=30)
    price = models.IntegerField(default=15)
    stripe_plan_id = models.CharField(max_length=40)

    def __str__(self):
        return self.membership_type


class UserMemberShip(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=40)
    membership = models.ForeignKey(Membership, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
    if created:
        UserMemberShip.objects.get_or_create(user=instance)

    user_membership, created = UserMemberShip.objects.get_or_create(user=instance)

    if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
        new_customer_id = stripe.Customer.create(email=instance.email)
        user_membership.stripe_customer_id = new_customer_id['id']
        user_membership.save()

post_save.connect(post_save_usermembership_create, sender=User)

class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMemberShip, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=40)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.user_membership.user.username


    def get_created_date(self):
       subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
       return datetime.fromtimeStamp(subscription.created)


    def get_next_billing_date(self):
        subscription = stripe.Subscription.retrieve(self.stripe_subscription_id)
        return datetime.fromtimeStamp(subscription.current_period_end)
