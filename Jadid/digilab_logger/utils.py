import pdb
import logging
import os.path
from inspect import getframeinfo, stack
from enum import Enum
from pathlib import Path

logger = logging.getLogger('logger')


class LoggingLevel(Enum):
    # https://docs.python.org/3/library/logging.html#logging-levels
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0


def get_log_str(message, caller, args):
    file_name = ""
    root_path = ""
    app_path = ""
    relative_file_name = ""
    function = ""
    line = ""

    file_name = str(caller.filename)
    root_path = os.path.abspath(os.path.dirname(__name__))
    app_path = os.path.dirname(os.path.realpath(__file__))
    relative_file_name = file_name[len(root_path):]
    function = str(caller.function)
    line = str(caller.lineno)
    
    if args:
        for arg in args:
            if type(arg) is Exception:
                message += "\nCause:\t"+str(safe_cast(arg, Exception).__cause__)+"\n"
                message += "self:\t"+str(safe_cast(arg, Exception))+"\n"
            
            else:
                message += " " + str(arg)

    log_str = "[" + relative_file_name + ":" + line + " " + function + "] " + str(message)
    return log_str


def log(message, user=None, *args, **kwargs):
    """Eigene Logging Methode. Über das optionale Keyword-Argument 'level' kann man das LoggingLevel (siehe LoggingLevel Enum) festlegen.
    \n Beispiele:
    \n\t log("Beispielhafte normale (info) log message")
    \n\t log("Beispielhafte log message für debugging", variable1, variable2, level=LoggingLevel.DEBUG)
    \n\t log("Beispielhafte error log message mit exception", exception, level=LoggingLevel.ERROR)
    \n
    :param message: Der Text, der in die Log-Datei geschrieben werden soll (kann durch *args erweitert werden).
    :type message: str
    :param *args: Beliebige Anzahl von beliebigen Objekten, deren String-Repräsentation an die Message angehängt wird.
    :type *args: beliebig, optional
    :param **kwargs['level']: Als optionales Keyword-Argument kann man 'level' angeben, mit dem man das LoggingLevel bestimmt. Default: LoggingLevel.INFO
    :type **kwargs['level']: LoggingLevel, optional
    """

    level = kwargs.get('level', LoggingLevel.INFO) # LoggingLevel.INFO ist hier der default-Wert, falls kein 'level' in kwargs gefunden wird
    
    if user is not None:
        message += f" [User: {str(user)}]"
    
    log_str = get_log_str(message, getframeinfo(stack()[1][0]), args)
    # print(str(message))
    # print(log_str)
    logger.log(level=level.value, msg=log_str)


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default

def create_file_if_not_exists(path_to_file):
    if not os.path.isfile(path_to_file):
        #print(path_to_file + " does not exist. Creating it now...")
        try:
            file_name = path_to_file.split("/")[-1]
            path = path_to_file.replace(file_name, "")
            Path(path).mkdir(parents=True, exist_ok=True)
        except:
            pass
        
        new_file = open(path_to_file, 'w+')
        new_file.close()
    else:
        #print(filename + " already exists.")
        pass
