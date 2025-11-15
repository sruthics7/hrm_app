from django.urls import resolve
from django.shortcuts import redirect
from .models import UserPermission, Module

class PermissionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not request.user.is_authenticated:
            return self.get_response(request)

        user = request.user

        # Superadmin can access everything
        if user.role == "superadmin":
            return self.get_response(request)

        url_name = resolve(request.path).url_name
        url_path = request.path.strip("/")

        # Get first part of URL
        # Example: payroll/list → payroll
        module_key = url_path.split("/")[0]

        # Public URLs
        public = ["login", "logout", "", "media", "static"]
        if module_key in public:
            return self.get_response(request)

        # Check permission
        allowed = UserPermission.objects.filter(
            user=request.user,
            module__url_prefix=module_key
        ).exists()

        if not allowed:
            return redirect("index")

        return self.get_response(request)
