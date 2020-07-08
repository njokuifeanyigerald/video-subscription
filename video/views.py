from django.shortcuts import render,get_object_or_404, redirect
from django.views.generic import ListView
from .models import Membership,UserMemberShip,Subscription
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import stripe


def profile_view(request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    context = {
        'user_subscription':user_subscription,
        "user_membership":user_membership
    }
    return render(request, 'video/profile.html', context)


def get_user_membership(request):
    user_membership_qs = UserMemberShip.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(
        user_membership= get_user_membership(request)
    )
    if user_subscription_qs.exists():
        return user_subscription_qs.first()
        
    return None

def get_selected_membership(request):
    membership_type = request.session['selected_memebership_type']
    selected_membership_qs = Membership.objects.filter(
        membership_type = membership_type
    )
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None



class MembershipSelectView(LoginRequiredMixin,ListView):
    model = Membership
    template_name = 'video/membership_list.html'

    def get_context_data(self, *args,**kwargs):
        context = super().get_context_data(**kwargs)
        current_membership = get_user_membership(self.request)
        context['current_membership'] = str(current_membership.membership)
        return context
    def post(self, *args,**kwargs):
        selected_membership_type  = self.request.POST.get('membership_type')
        user_membership = get_user_membership(self.request)
        user_subscription = get_user_subscription(self.request)
        selected_membership_qs = Membership.objects.filter(
            membership_type = selected_membership_type
        )
        if selected_membership_qs.exists():
            selected_membership = selected_membership_qs.first()

        # validation
        if user_membership.membership == selected_membership:
            if user_subscription != None:
                messages.info(self.request, "you already have this memebership,\
                     your  next payment is due {}".format('get this value from stripe')
                )
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        #assign to session
        self.request.session['selected_memebership_type'] = selected_membership.membership_type
        return HttpResponseRedirect(reverse('videos:payment'))


def PaymentView(request):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    publishKey = settings.STRIPE_PUBLISHABLE_KEY
    if request.method == 'POST':
        try:
            # stripe.api_key = "sk_test_4fZvDGB3VzQ2OYQOyRuhq9bK00b8BiWAVb"

            token = request.POST['stripeToken']
            subscription = stripe.Subscription.create(
            customer=user_membership.stripe_customer_id,
            items=[
                {
                    "plan": selected_membership.stripe_plan_id
                    },
                ],
                source = token  #42424242424242
            )
            return redirect(reverse('videos:update-transactions',
                kwargs={
                    'subscription_id': subscription.id
                }))
        except:
            messages.info(request, "An error has occurred, investigate it in the console")
    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }
    return render(request, 'video/membership_payment.html', context)


def updateTransactions(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership()
    user_membership.membership = selected_membership
    user_membership.save()
    

    sub, created = Subscription.objects.get_or_create(user_membership=user_membership)
    sub.stripe_subscription_id  = subscription_id
    sub.active = True
    sub.save()
    try:
        del request.session['selected_membership_type']
    except:
        pass

    messages.info(request, 'successfully created {} membership'.format(selected_membership))
    return redirect('/courses')


def cancelSubscription(request):
    user_sub = get_user_subscription(request)
    if user_sub.active == False:
        messages.info(request,"you don't have an active membership")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    sub  = stripe.SubScription.retrieve(user_sub.stripe_subscription_id)

    sub.delete()
    user_sub.active = False
    user_sub.save()

    free_membership = Membership.objects.filter(membership_type = 'Free').first()
    user_membership = get_user_membership(request)
    user_membership.membership = free_membership
    user_membership.save()
    messages.info(request,"successfully cancelled membership, we have sent an email")
    return redirect('/')

