from django import apps, template
from django.template.base import FilterExpression
from django.template.loader import get_template
from django.utils import safestring

register = template.Library()


@register.filter
def connect(val1, val2):
    return val1, val2


@register.filter
def cuttrailing(s1, s2):
    if s1.endswith(s2):
        return s1[:-len(s2)]
    return s1


@register.filter
def limit(indexable, count):
    return indexable[:count]


@register.filter
def override(override, overridden):
    if type(override) == type(overridden):
        return override
    else:
        return overridden


@register.filter
def url_for(gestalt, user):
    if user.has_perm('entities.view_gestalt', gestalt):
        return gestalt.get_profile_url()
    else:
        return gestalt.get_contact_url()


@register.simple_tag(takes_context=True)
def include_features(context, template_name):
    result = ''
    for app in apps.apps.get_app_configs():
        try:
            t = context.template.engine.get_template('{}/{}'.format(app.label, template_name))
            result += t.render(context)
        except template.TemplateDoesNotExist:
            pass
    return safestring.mark_safe(result)


def parse_token_args(args, filterval=lambda value: value):
    result_kwargs = {}
    result_args = []

    for arg in args:
        if '=' in arg:
            name, value = arg.split('=')
            result_kwargs[name] = filterval(value)
        else:
            result_args.append(filterval(arg))
    return result_args, result_kwargs


def _setup_macros_dict(parser):
    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    try:
        # Only try to access it to eventually trigger an exception
        parser._macros
    except AttributeError:
        parser._macros = {}


class DefineMacroNode(template.Node):
    def __init__(self, name, nodelist, args):

        self.name = name
        self.nodelist = nodelist
        self.args, self.kwargs = parse_token_args(args)

    def render(self, context):
        # empty string - {% macro %} tag does no output
        return ''


@register.tag(name="kwacro")
def do_macro(parser, token):
    try:
        args = token.split_contents()
        macro_name, args = args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    # TODO: could do some validations here,
    # for now, "blow your head clean off"
    nodelist = parser.parse(('endkwacro', ))
    parser.delete_first_token()

    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    parser._macros[macro_name] = DefineMacroNode(macro_name, nodelist, args)
    return parser._macros[macro_name]


class LoadMacrosNode(template.Node):
    def render(self, context):
        # empty string - {% loadmacros %} tag does no output
        return ''


@register.tag(name="loadkwacros")
def do_loadmacros(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    if filename[0] in ('"', "'") and filename[-1] == filename[0]:
        filename = filename[1:-1]
    t = get_template(filename)
    macros = t.nodelist.get_nodes_by_type(DefineMacroNode)
    # Metadata of each macro are stored in a new attribute
    # of 'parser' class. That way we can access it later
    # in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    for macro in macros:
        parser._macros[macro.name] = macro
    return LoadMacrosNode()


class UseMacroNode(template.Node):

    def __init__(self, macro, fe_args, fe_kwargs):
        self.macro = macro
        self.fe_args = fe_args
        self.fe_kwargs = fe_kwargs

    def render(self, context):
        for i, arg in enumerate(self.macro.args):
            try:
                fe = self.fe_args[i]
                context[arg] = fe.resolve(context)
            except IndexError:
                context[arg] = ""
        for name, default in iter(self.macro.kwargs.items()):
            if name in self.fe_kwargs:
                context[name] = self.fe_kwargs[name].resolve(context)
            else:
                context[name] = FilterExpression(default,
                                                 self.macro.parser
                                                 ).resolve(context)
        return self.macro.nodelist.render(context)


@register.tag(name="usekwacro")
def do_usemacro(parser, token):
    try:
        args = token.split_contents()
        macro_name, values = args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    try:
        macro = parser._macros[macro_name]
    except (AttributeError, KeyError):
        m = "Macro '%s' is not defined" % macro_name
        raise template.TemplateSyntaxError(m)

    fe_args, fe_kwargs = parse_token_args(values, lambda value: FilterExpression(value, parser))
    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)