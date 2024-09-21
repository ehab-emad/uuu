import traceback
from .db_log_handler import DatabaseLogHandler
from django.contrib.auth.models import User
from .models import StatusLog

class ExceptionMiddleware(object):
    """Eigene Middleware, mit der man bestimmen kann, was beim Auftreten von beliebigen Exceptions im Projekt passieren soll (z.B. Anlegen von DB-Log-Einträgen).
    Wird aktuell nicht benutzt. Siehe settings.py -> Eintrag in MIDDLEWARE-Liste "digilab_logger.middleware.ExceptionMiddleware".

    :param object: [description]
    :type object: [type]
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    def process_exception(self, request, exception):
        user = None
        url = None

        traceback_obj = exception.__traceback__
        traceback_lines = traceback.format_tb(traceback_obj)
        traceback_str = ""

        for line in traceback_lines:
            traceback_str += line
        
        current_traceback = traceback_str
        if request:
            if request.user and isinstance(request.user, User):
                user = request.user

                status_log = StatusLog(
                    msg=str(exception),
                    user=user,
                    trace=current_traceback,
                )
                status_log.save()

            else:
                status_log = StatusLog(
                    msg=str(exception),
                    trace=current_traceback,
                )
                status_log.save()