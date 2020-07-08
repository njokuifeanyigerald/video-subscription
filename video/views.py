from django.shortcuts import render,get_object_or_404
from django.views.generic import ListView
from .models import Membership,UserMemberShip,Subsription
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings



def get_user_membership(request):
    user_membership_qs = UserMemberShip.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None

def get_user_subscription(request):
    user_subscription_qs = Subsription.objects.filter(
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

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }
    return render(request, 'video/membership_payment.html', context)