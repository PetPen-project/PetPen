from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView

from user.forms import UserCreateForm

class UserCreateView(CreateView):
    model = User
    template_name = 'registration/create_user.html'
    form_class = UserCreateForm
    success_url = '/accounts/login/'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, *kwargs)
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))
