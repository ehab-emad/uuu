import random
import uuid
def generate_pk():
  number = random.randint(100000000000, 999999999999)
  return '{}'.format(number)

def generate_pk_GUID():
  number = uuid.uuid4().hex
  return number

def check_pk(pk):
  if len(pk)== 12:
    try : 
      string_integer = int(pk)
      return string_integer
    except ValueError:
      return None
    
