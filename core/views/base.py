from django.contrib.auth import views as auth
from django.core import exceptions, urlresolvers
from django.utils import six
from django.views import generic as django
from django.views.generic import base as django_base
from rules.contrib import views as rules


class PermissionMixin(rules.PermissionRequiredMixin):
    """
    Handle permissions
    """
    def get_permission_required(self):
        return (self.permission,)

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise exceptions.PermissionDenied(
                    self.get_permission_denied_message())
        else:
            return auth.redirect_to_login(
                    self.request.get_full_path(),
                    self.get_login_url(),
                    self.get_redirect_field_name())


class StadtMixin(django_base.ContextMixin):
    """
    Insert Stadtgestalten specific attributes into context
    """
    def get_breadcrumb(self):
        objects = list(filter(None, [self.get_parent(), self.get_title()]))
        if objects:
            grandparent = self.get_grandparent(objects[0])
            if grandparent:
                objects.insert(0, grandparent)
            breadcrumb = [self.get_navigation_data(o) for o in objects[:-1]]
            breadcrumb.append((str(objects[-1]), None))
            return breadcrumb
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumb'] = self.get_breadcrumb()
        kwargs['menu'] = self.get_menu()
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_menu(self):
        return getattr(self, 'menu', None)

    def get_navigation_data(self, instance):
        title = str(instance)
        try:
            if isinstance(instance, six.string_types):
                url = urlresolvers.reverse(instance)
                title = urlresolvers.resolve(url).func.view_class.title
            else:
                url = instance.get_absolute_url()
        except (AttributeError, urlresolvers.NoReverseMatch):
            url = None
        return title, url

    def get_grandparent(self, parent):
        return None

    def get_parent(self):
        return getattr(self, 'parent', None)

    def get_title(self):
        return getattr(self, 'title', None)


class View(PermissionMixin, StadtMixin, django.View):
    """
    Stadtgestalten base view
    """
    def dispatch(self, *args, **kwargs):
        self.object = None
        self.related_object = self.get_view_object(None)
        return super().dispatch(*args, **kwargs)

    def get_menu(self):
        return type(self.related_object).__name__

    def get_parent(self):
        return self.related_object

    def get_permission_object(self):
        return self.related_object

    def get_view_object(self, key):
        if key is None and hasattr(self, 'get_related_object'):
            return self.get_related_object()
        return None
