from django.db import models
import logging
from django.contrib.auth.models import User

####### Custom django-db-logger #######

LOG_LEVELS = (
    (logging.NOTSET, ('NotSet')),
    (logging.INFO, ('Info')),
    (logging.WARNING, ('Warning')),
    (logging.DEBUG, ('Debug')),
    (logging.ERROR, ('Error')),
    (logging.FATAL, ('Fatal')),
)

class StatusLog(models.Model):
    logger_name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(choices=LOG_LEVELS, default=logging.ERROR, db_index=True)
    msg = models.TextField()
    trace = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, verbose_name='Created at')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.msg

    class Meta:
        ordering = ('-create_datetime',)
        verbose_name = 'System Log Entry'
        verbose_name_plural ='System Log Entries'
