from website.models import *
from ConceptMan.models import *
from MatMan.models import *



from django.forms import ModelForm
from django import forms


#class UserForm(forms.ModelForm):
  #  password = forms.CharField(widget=forms.PasswordInput)

  #  class Meta:
  #      model = User
  #      fields = ['username', 'email', 'password']


# class EngineeringMaterialForm(forms.ModelForm):
#     class Meta:
#         model = Engineering_Material
#         fields = '__all__'
#         exclude = ('created_at', 'updated_at', 'user' , 'id')  
