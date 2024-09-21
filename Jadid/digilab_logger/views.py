from django.shortcuts import render, redirect
from .utils import log, LoggingLevel
from digilab_user_auth.utils import is_superuser_test
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)


@login_required(login_url=reverse_lazy("user:login"))
@user_passes_test(lambda user: is_superuser_test(user))
def testing_create_info_logs(request):
    i = 0
    while i < 30:
        log("Test-Log Nr. " + str(i+1), level=LoggingLevel.INFO)
        i += 1
    return redirect("home")


@login_required(login_url=reverse_lazy("user:login"))
@user_passes_test(lambda user: is_superuser_test(user))
def testing_raise_exception(request):
    raise Exception("Test-Exception für Logging (Handler)")
