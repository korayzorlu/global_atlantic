from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import render, redirect
from django.views import View

from hr.models import TheCompany
from beta_profile.forms import UserLoginForm, ProfileForm, UserInfoForm, CustomPasswordResetForm


# Create your views here.


class DashboardView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'user/dashboard.html', context)


class LandingPageView(LoginView):
    template_name = 'landing_page.html'
    form_class = UserLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        remember_me = form.cleaned_data['remember_me']
        if not remember_me:
            self.request.session.set_expiry(0)
            self.request.session.modified = True
        return super(LandingPageView, self).form_valid(form)


class ProfileView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user_form = UserInfoForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.beta_profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form
        }
        return render(request, 'user/profile_page.html', context)

    def post(self, request, *args, **kwargs):
        user_form = UserInfoForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.beta_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # to prevent refresh that sends post data again.
            return redirect("profile_page")
        else:
            context = {
                'user_form': user_form,
                'profile_form': profile_form
            }
            return render(request, 'user/profile_page.html', context)


class CustomPasswordResetView(PasswordResetView):
    html_email_template_name = 'registration/password_reset_email.html'
    form_class = CustomPasswordResetForm

    def __init__(self, **kwargs):
        self.extra_email_context = {'the_company': TheCompany.objects.get(id=1)}
        super().__init__(**kwargs)
