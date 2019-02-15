import json


class SubdomainCompilingMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request = request
        request.child_app_urls = []
        child_app_urls = ['birthdate', 'lunchmunch', 'tripweather']

        for url in child_app_urls:
            object = {"host": url, "url": request.build_absolute_uri(), }
            request.child_app_urls += object

        return self.get_response(request)

    def process_request(self, request):
        pass


class MultiAuthMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        pass
