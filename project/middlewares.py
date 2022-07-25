from django.shortcuts import redirect


class FilterLoginRedirectMiddleware(object):
    def __init__(self, get_response):
        """
        One-time configuration and initialisation.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Code to be executed for each request before the view (and later
        middleware) are called.
        """
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Called just before Django calls the view.
        """
        user = request.user
        if user.is_authenticated and user.is_staff and not user.is_superuser:
            if request.path.startswith('/admin'):
                return redirect('/')
        return None

    def process_request(self, request):
        user = request.user
        if user.is_authenticated and user.is_staff and not user.is_superuser:
            return redirect('/')
        return None
