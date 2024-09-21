from website.models import *
from ConceptMan.models import *
from BoltMan.models import *



from django.forms import ModelForm
from django import forms


#class UserForm(forms.ModelForm):
  #  password = forms.CharField(widget=forms.PasswordInput)

  #  class Meta:
  #      model = User
  #      fields = ['username', 'email', 'password']


class BoltMaterialForm(forms.ModelForm):
    class Meta:
        model = Bolt_Material
        fields = '__all__'
        exclude ='user',

class BoltGeometryForm(forms.ModelForm):
    class Meta:
        model = Bolt_Geometry
        fields = '__all__'
        exclude = ('created_at', 'updated_at', 'user' , 'id')  

class FrictionThreadForm(forms.ModelForm):
    class Meta:
        model = Friction_Thread
        fields = '__all__'
        exclude = ('created_at', 'updated_at', 'user' , 'id')

class FrictionHeadForm(forms.ModelForm):
    class Meta:
        model = Friction_Head
        fields = '__all__'
        exclude = ('created_at', 'updated_at', 'user' , 'id')    

class FrictionJointForm(forms.ModelForm):
    class Meta:
        model = Friction_Joint
        fields = '__all__'
        exclude = ('created_at', 'updated_at', 'user' , 'id')    
        
class BoltCaseForm(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('vehicle' , 'picture','bolt_geometry','tightening_method','status')

class BoltCaseFormCreate(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('name', 'picture', 'maturity', 'vehicle')
class BoltCaseInstanceFormCreate(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('name', 'picture', 'maturity', 'vehicle')
class BoltCaseFormPart(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('vehicle', )#'part1','part2','part3'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        self.fields['part1'].queryset = Part.objects.none()
        self.fields['part2'].queryset = Part.objects.none()  
        self.fields['part3'].queryset = Part.objects.none()              
        if 'vehicle' in self.initial:
            try:
                vehicle_id = self.initial.get('vehicle')
                parts=Part.objects.all()
                for item in vehicle_id:
                    parts=parts.filter(vehicles__in=[item])
                self.fields['part1'].queryset = parts.order_by('name')
                self.fields['part2'].queryset = parts.order_by('name')
                self.fields['part3'].queryset = parts.order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty City queryset
        elif self.instance.pk:
            self.fields['part1'].queryset = self.instance.part1.vehicles.order_by('name')   
            self.fields['part2'].queryset = self.instance.part1.vehicles.order_by('name')   
            self.fields['part3'].queryset = self.instance.part1.vehicles.order_by('name')   


# class BoltCaseInstanceForm(forms.ModelForm):
#     class Meta:
#         model = Bolt_Case
#         fields = ('vehicle', 'boltcaseinstance')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)


#         self.fields['boltcaseinstance'].queryset = Bolt_Case_Instance.objects.none()         
#         if 'vehicle' in self.initial:
#             try:
#                 vehicle_id = self.initial.get('vehicle')
#                 parts=Bolt_Case_Instance.objects.all()
#                 for item in vehicle_id:
#                     parts=parts.filter(car__in=[item])
#                 self.fields['boltcaseinstance'].queryset = parts.order_by('name')
#             except (ValueError, TypeError):
#                 pass  # invalid input from the client; ignore and fallback to empty City queryset
#         elif self.instance.pk:
#             self.fields['boltcaseinstance'].queryset = self.instance.boltcaseinstance.car.order_by('name')   

class BoltCaseInstanceForm(forms.ModelForm):
    class Meta:
        model = Bolt_Case_Instance
        fields = ('name', 'status', )  #'vehicle'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BoltCaseFormWasher(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('washer_head', 'washer_nut', ) 

class BoltCaseFormBoltGeometry(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('bolt_geometry', ) 



class BoltCaseFormFrictionThread(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('friction_thread',)

class BoltCaseFormFrictionHead(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('friction_head',)

class BoltCaseFormFrictionJoint(forms.ModelForm):
    class Meta:
        model = Bolt_Case
        fields = ('friction_joint',)

            