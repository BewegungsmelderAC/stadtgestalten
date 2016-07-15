from . import forms
from content import models as content_models
from crispy_forms import helper, layout
from django import forms as django_forms, http
from django.contrib.auth import views as auth_views
from django.contrib.messages import views as messages_views
from django.core import exceptions, urlresolvers
from django.utils import six
from django.views import generic
from django.views.generic import edit as edit_views
from entities import models as entities_models
from rules.contrib import views as rules_views


class ContentMixin:
    def get_context_data(self, **kwargs):
        kwargs['content'] = self.get_content()
        return super().get_context_data(**kwargs)

    def get_content(self):
        if 'content_pk' in self.kwargs:
            return content_models.Content.objects.get(pk=self.kwargs['content_pk'])
        return None


class GestaltMixin:
    def get_context_data(self, **kwargs):
        kwargs['gestalt'] = self.get_gestalt()
        return super().get_context_data(**kwargs)

    def get_gestalt(self):
        if 'gestalt_pk' in self.kwargs:
            return entities_models.Gestalt.objects.get(pk=self.kwargs['gestalt_pk'])
        if 'gestalt_slug' in self.kwargs:
            return entities_models.Gestalt.objects.get(user__username=self.kwargs['gestalt_slug'])
        return None

class GroupMixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, entities_models.Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                if hasattr(instance, 'groups'):
                    return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return entities_models.Group.objects.get(pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return entities_models.Group.objects.get(slug=self.kwargs['group_slug'])
            if 'group' in self.request.GET:
                return entities_models.Group.objects.get(slug=self.request.GET['group'])
            if 'content_pk' in self.kwargs:
                return content_models.Content.objects.get(pk=self.kwargs['content_pk']).groups.first()
        except (content_models.Content.DoesNotExist,
                entities_models.Group.DoesNotExist):
            pass
        finally:
            return None


class FormMixin(forms.LayoutMixin):
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not hasattr(form, 'helper'):
            form.helper = self.get_helper()
        return form

    def get_form_class(self):
        return super().get_form_class() or django_forms.Form

    def get_layout(self):
        if hasattr(self, '_fields'):
            l = self._fields
        else:
            l = super().get_layout()
        if hasattr(self, 'description'):
            l = (layout.HTML('<p>{}</p>'.format(self.description)),) + l
        l += (forms.Submit(self.get_action()),)
        return l


class MenuMixin:
    def get_context_data(self, **kwargs):
        menu = self.get_menu()
        if menu and not isinstance(menu, six.string_types):
            menu = menu.__name__
        kwargs['menu'] = menu
        return super().get_context_data(**kwargs)

    def get_menu(self):
        if hasattr(self, 'menu'):
            return self.menu
        for instance in (getattr(self, 'related_object', None), self.get_parent()):
            if instance:
                t = type(instance)
                if t == content_models.Content:
                    return type(instance.get_content())
                return t
        return None


class MessageMixin(messages_views.SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        if hasattr(self, 'message'):
            return self.message
        return None

class NavigationMixin:
    def get_breadcrumb(self):
        objects = [self.get_parent(), self.get_breadcrumb_object()]
        objects = [o for o in objects if o is not None]
        if objects:
            entity = self.get_parent_entity(objects[0])
            if entity:
                objects.insert(0, entity)
            breadcrumb = [self.get_navigation_data(o) for o in objects[:-1]]
            breadcrumb.append((str(objects[-1]), None))
            return breadcrumb
        return []

    def get_context_data(self, **kwargs):
        kwargs['breadcrumb'] = self.get_breadcrumb()
        return super().get_context_data(**kwargs)

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

    def get_parent(self):
        if hasattr(self, 'parent'):
            return self.parent
        else:
            return None

    def get_parent_entity(self, child):
        if isinstance(child, content_models.Content):
            if child.groups.exists():
                return child.groups.first()
            else:
                return child.author
        else:
            return None

    def get_success_url(self):
        try:
            return super().get_success_url()
        except AttributeError:
            return self.get_navigation_data(self.get_parent())[1]


class PaginationMixin:
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['params'] = self.request.GET.copy()
        if 'page' in kwargs['params']:
            del kwargs['params']['page']
        return super().get_context_data(**kwargs)


class PermissionMixin(rules_views.PermissionRequiredMixin):
    def get_permissions(self):
        return {self.permission: self.get_permission_object()}

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise exceptions.PermissionDenied(self.get_permission_denied_message())
        else:
            return auth_views.redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())

    def has_permission(self, permission=None):
        permissions = self.get_permissions()
        if permission in permissions:
            permissions = {permission: permissions[permission]}
        for permission, object in permissions.items():
            if self.request.user.has_perm(permission, object):
                return True
        return False

class SidebarMixin:
    sidebar = ('calendar', 'groups')

    def get_context_data(self, **kwargs):
        kwargs['sidebar'] = self.sidebar
        return super().get_context_data(**kwargs)

class TemplateMixin:
    ignore_base_templates = False

    def get_template_names(self):
        if not self.ignore_base_templates:
            try:
                names = super().get_template_names()
            except exceptions.ImproperlyConfigured:
                names = []
        else:
            names = []
        names += [self.fallback_template_name]
        return names


class TitleMixin:
    def get_action(self):
        if hasattr(self, 'action'):
            return self.action
        else:
            return None

    def get_breadcrumb_object(self):
        return self.get_title()

    def get_context_data(self, **kwargs):
        kwargs['title'] = self.get_title()
        return super().get_context_data(**kwargs)

    def get_title(self):
        if hasattr(self, 'title'):
            return self.title
        else:
            return self.get_action()


class ActionMixin(
        ContentMixin,
        FormMixin,
        GestaltMixin,
        GroupMixin,
        MenuMixin,
        MessageMixin,
        NavigationMixin,
        PermissionMixin,
        SidebarMixin,
        TemplateMixin,
        TitleMixin,
        ):
    fallback_template_name = 'stadt/form.html'
    sidebar = tuple()


class PageMixin(
        GestaltMixin,
        GroupMixin,
        MenuMixin,
        NavigationMixin,
        PaginationMixin,
        PermissionMixin,
        SidebarMixin,
        TemplateMixin,
        TitleMixin,
        ):
    fallback_template_name = 'stadt/list.html'
    sidebar = ('calendar', 'groups')


class RelatedObjectMixin:
    def dispatch(self, request, *args, **kwargs):
        self.related_object = self.get_related_object()
        if not self.related_object:
            raise http.Http404('Zugehöriges Objekt nicht gefunden')
        return super().dispatch(request, *args, **kwargs)


class Create(RelatedObjectMixin, ActionMixin, generic.CreateView):
    def __init__(self, *args, **kwargs):
        self._fields = self.fields
        self.fields = self.get_fields()
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_field_name(field):
        if isinstance(field, layout.Field):
            return field.fields[0]
        else:
            return field

    def get_fields(self):
        return [self.get_field_name(f) for f in self._fields]

    def get_form(self):
        form = super().get_form()
        for field in self._fields:
            if getattr(field, 'constant', False):
                form.fields[self.get_field_name(field)].disabled = True
        return form

    def get_parent(self):
        return self.related_object

    def get_permission_object(self):
        return self.related_object


class Delete(RelatedObjectMixin, ActionMixin, edit_views.FormMixin, generic.DeleteView):
    pass


class List(PageMixin, generic.ListView):
    pass
