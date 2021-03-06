from rest_framework import permissions, viewsets
from rest_framework.response import Response
from core.templatetags import core
from core import api

_PRESETS = {
    'content': {
        'heading_baselevel': 2,
    },
}


class MarkdownView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        preset = _PRESETS[request.data.get('preset', 'content')]
        text = request.data.get('content')
        return Response({
            'content': str(core.markdown(text, **preset))
        })


@api.register
def load(router):
    router.register(r'content/markdown', MarkdownView, base_name='markdown')
