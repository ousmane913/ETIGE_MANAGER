import json
from django.http import QueryDict

class JsonRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.content_type == 'application/json' and request.method in ('POST', 'PUT', 'PATCH'):
            try:
                body = json.loads(request.body)
                q_data = QueryDict('', mutable=True)
                if isinstance(body, dict):
                    for key, value in body.items():
                        if isinstance(value, list):
                            q_data.setlist(key, value)
                        else:
                            q_data[key] = value
                request.POST = q_data
            except Exception:
                pass
        return self.get_response(request)

from django.contrib import messages
from inertia import share

class FlashMessagesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_flash():
            return [{'message': m.message, 'level': m.tags} for m in messages.get_messages(request)]
        share(request, 'flash', lambda: {'messages': get_flash()})
        return self.get_response(request)
