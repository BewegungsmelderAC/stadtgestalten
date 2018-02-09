from django.db import IntegrityError
from django.contrib.messages import info
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, DeleteView

from core.views import PermissionMixin
from features.groups.models import Group
from features.subscriptions.models import Subscription
from features.subscriptions.rules import is_subscribed
from . import forms


class GroupSubscribe(SuccessMessageMixin, PermissionMixin, CreateView):
    permission_required = 'subscriptions.create'
    form_class = forms.Subscribe
    template_name = 'subscriptions/create.html'
    success_message = 'Du erhältst zukünftig Benachrichtigungen für Beiträge dieser Gruppe.'
    already_subscribed_message = 'Du hast diese Gruppe bereits abonniert.'

    def form_valid(self, form):
        try:
            return super().form_valid(form)
        except IntegrityError:
            info(self.request, self.already_subscribed_message)
            return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_instance()
        return kwargs

    def get_instance(self):
        instance = Subscription()
        if self.request.user.is_authenticated:
            instance.subscriber = self.request.user.gestalt
        instance.subscribed_to = self.group
        return instance

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_pk'))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()

    def handle_no_permission(self):
        if (self.request.user.is_authenticated
                and is_subscribed(self.request.user, self.group)):
            info(self.request, self.already_subscribed_message)
            return HttpResponseRedirect(self.get_success_url())
        else:
            return super().handle_no_permission()


class GroupUnsubscribe(PermissionMixin, DeleteView):
    permission_required = 'subscriptions.delete'
    model = Subscription

    def get_object(self):
        return self.request.user.gestalt.subscriptions.filter(
                subscribed_to_type=self.group.content_type, subscribed_to_id=self.group.id)

    def get_permission_object(self):
        self.group = get_object_or_404(Group, pk=self.kwargs.get('group_pk'))
        return self.group

    def get_success_url(self):
        return self.group.get_absolute_url()
