import logging
import pdb
from .utils import log, LoggingLevel

db_default_formatter = logging.Formatter()

class DatabaseLogHandler(logging.Handler):
    """Eigener Logging-Handler, der die Log-Einträge in die Datenbank schreibt, wenn ein ERROR oder CRITICAL Log-Eintrag
    auftaucht. Benutzt einen Ringpuffer, um auch eine bestimmte Anzahl von Log-Einträgen abzuspeichern, die vor dem Error aufgetreten sind, 
    damit man einen Kontext hat.
    Dieser DatabaseLogHandler basiert auf dem django-db-logger package: https://pypi.org/project/django-db-logger/
    """

    # Config:
    LOGS_RINGBUFFER_SIZE = 25 # Anzahl der Log-Einträge, die im Ringpuffer gespeichert werden sollen
    ENABLE_FORMATTER = True

    # class variables
    counter = 1
    logs_ringbuffer = []

    def emit(self, record):
        """Wird bei jedem neuen Log-Eintrag eines Loggers aufgerufen, dem dieser Handler zugewiesen wurde.
        (Siehe settings.py LOGGING-dictionary)

        :param record: Log-Eintrag
        :type record: logging.LogRecord
        """
        from .models import StatusLog
        
        trace = None

        if record.exc_info:
            trace = db_default_formatter.formatException(record.exc_info)

        if self.ENABLE_FORMATTER:
            msg = self.format(record)
        else:
            msg = record.getMessage()

        kwargs = {
            'logger_name': record.name,
            'level': record.levelno,
            'msg': msg,
            'trace': trace
        }

        if record.levelno in [logging.ERROR, logging.CRITICAL]: # wenn der Log-Eintrag ERROR oder CRITICAL ist
            for entry in self.logs_ringbuffer:
                entry.save()
                
            StatusLog.objects.create(**kwargs)

        else:
            status_log = StatusLog(
                logger_name=record.name,
                msg=msg,
                trace=trace,
                level=record.levelno
            )
            
            length = len(self.logs_ringbuffer)
            if length <= self.LOGS_RINGBUFFER_SIZE:
                if length == self.LOGS_RINGBUFFER_SIZE:
                    del self.logs_ringbuffer[0] # entferne den ersten Log-Eintrag im Puffer

                self.logs_ringbuffer.append(status_log)

            else:
                #log("Im DatabaseLogHandler hat die logs_ringbuffer Liste eine falsche Länge:", level=LoggingLevel.ERROR)
                
                # Ein (echter) Log-Eintrag (s.o.) an dieser Stelle könnte unter schlechten Umständen evtl. eine Endlosschleife erzeugen, vermute ich.
                print("Fehler: Im DatabaseLogHandler hat die logs_ringbuffer Liste eine falsche Länge: " + str(length) + " anstatt 0 < length <=" + str(self.LOGS_RINGBUFFER_SIZE))

            if self.counter == self.LOGS_RINGBUFFER_SIZE:
                self.counter = 1
            else:
                self.counter += 1


    def format(self, record):
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = db_default_formatter

        if type(fmt) == logging.Formatter:
            record.message = record.getMessage()

            if fmt.usesTime():
                record.asctime = fmt.formatTime(record, fmt.datefmt)

            # ignore exception traceback and stack info

            return fmt.formatMessage(record)
        else:
            return fmt.format(record)
