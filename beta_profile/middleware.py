import time

from django.contrib.auth.models import User

from beta_profile.models import Record

# to work on earlier versions of django
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


# class RecordMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         request.record_obj = None
#         # Skip favicon requests cause I do not care about them
#         if request.path == "/favicon.ico":
#             return

#         # Only log requests of authenticated users / if request.user is a User instance, then it is authenticated
#         if not isinstance(request.user, User):
#             return

#         record = Record.objects.create(
#             session_id=request.session.session_key,
#             user=request.user,
#             username=request.user.username,
#             path=request.path,
#             query_string=request.META.get("QUERY_STRING"),
#             method=request.method,
#             secure=request.is_secure(),
#             ajax=request.is_ajax(),
#             meta=request.META.__str__(),
#             # https://stackoverflow.com/a/4581997/14506165
#             address=request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')),
#             created_at=str(time.time()),
#         )
#         request.record_obj = record
#         return

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         if request.path == "/favicon.ico":
#             return

#         if not isinstance(request.user, User):
#             return

#         return

#     def process_response(self, request, response):
#         if request.path == "/favicon.ico":
#             return response

#         if not isinstance(request.user, User):
#             return response

#         if request.record_obj:
#             request.record_obj.response_code = response.status_code
#             request.record_obj.save()

#         return response
