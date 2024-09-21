from django.db import models 

import math 
import uuid 
class Bolt_Case(models.Model):
  UUID = models.UUIDField(primary_key=True, verbose_name="UUID",   default=uuid.uuid4, editable=False)
  name = models.CharField(max_length=100,  default= 'DUMMY_BOLT_CASE', editable=True)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)
  owner = models.ForeignKey("BoltMan.ProjectUser_BoltMan_Ref", models.SET_NULL, blank=True,null=True,)
  status = models.BooleanField(default=True) #true if all fields are correct

  vehicle=models.ManyToManyField("BoltMan.Vehicle_BoltMan_Ref",  help_text ="Select car or cars for a Bolt Case")
  picture =  models.CharField(max_length=1000,  default= 'EMPTY', )

  bolt_geometry = models.ForeignKey("BoltMan.Bolt_Geometry", help_text="Select a geometry", on_delete=models.CASCADE, default=None, blank=True, null=True)

  part_1 = models.ForeignKey("BoltMan.Bolted_Part", help_text="Select a part", on_delete=models.SET_NULL, default=None, related_name='%(class)s_part1', blank=True, null=True)
  part_2 = models.ForeignKey("BoltMan.Bolted_Part", help_text="Select a part", on_delete=models.SET_NULL, default=None, related_name='%(class)s_part2', blank=True, null=True)
  part_3 = models.ForeignKey("BoltMan.Bolted_Part", help_text="Select a part", on_delete=models.SET_NULL, default=None, related_name='%(class)s_part3', blank=True, null=True)

  BJ = 'Bolted Joint'
  TTJ = 'Tapped Thread Joint'

  BOLT_CASE_CLASS = [
    (BJ, ('Bolted Joint')),
    (TTJ, ('Tapped Thread Joint')),
    ]
      
  bolt_case_class= models.CharField(choices=BOLT_CASE_CLASS, max_length=32, default=TTJ) 
  washer_head = models.ForeignKey("BoltMan.Washer", help_text="Washer head", on_delete=models.CASCADE, default=None, related_name='%(class)s_washer_head', blank=True, null=True) 
  washer_nut = models.ForeignKey("BoltMan.Washer", help_text="Washer nut", on_delete=models.CASCADE, default=None, related_name='%(class)s_washer_nut', blank=True, null=True)

  lappedarea_bolthead = models.FloatField(editable=True, verbose_name= "Lapped area (mm^2)", default=None, blank=True, null=True)
  lappedarea_nut = models.FloatField(editable=True, verbose_name= "Lapped area (mm^2)", default=None, blank=True, null=True)
  nojs = models.PositiveIntegerField(verbose_name="Number of joint separations (-)", default = 1, blank=True, null=True)

  holediameter_part1 = models.FloatField(editable=True, verbose_name= "Hole diameter (mm)", blank=True, null=True)
  holediameter_part2 = models.FloatField(editable=True, verbose_name= "Hole diameter (mm)", blank=True, null=True)
  holediameter_part3 = models.FloatField(editable=True, verbose_name= "Hole diameter (mm)", blank=True, null=True)
  jointdiameter = models.FloatField(editable=True, verbose_name= "Joint diameter (mm)", blank=True, null=True)

  friction_thread = models.ForeignKey("BoltMan.Friction_Thread", on_delete=models.CASCADE, default=None, blank=True, null=True)
  friction_head = models.ForeignKey("BoltMan.Friction_Head", on_delete=models.CASCADE, default=None, blank=True, null=True) 
  friction_joint = models.ForeignKey("BoltMan.Friction_Joint", on_delete=models.CASCADE, default=None, blank=True, null=True)


  #parameters for calculations
  w = models.FloatField(editable=False, verbose_name= "Joint Coefficient", default=None, blank=True, null=True)   #joint coefficient D124
  tan_phi = models.FloatField(editable=False, verbose_name= "Substitutional Cone Angle", default=None, blank=True, null=True)   #substitutional cone angle D125
  nop = models.IntegerField(editable=False, verbose_name= "Number of Clamped parts", default=None, blank=True, null=True)   #number of interfaces D111
  sem = models.BooleanField(default=False) #true if all fields are correct
  d_w =models.FloatField(editable=False, verbose_name= "Head Diameter", default=None, blank=True, null=True)   #Head Diameter D54

  A_n = models.FloatField(editable=False, verbose_name= "Bolt - Nominal cross-section (mm^2)", default=None, blank=True, null=True)   #Nennquerschnitt Schraube A_n
  A_3 = models.FloatField(editable=False, verbose_name= "Bolt - Core cross-section (mm^2)", default=None, blank=True, null=True)      #Kernquerschnitt Gewinde A_3
  delta_S = models.FloatField(editable=False, verbose_name= "Bolt - Longintudinal elasticity (-)", default=None, blank=True, null=True)      #Nachgiebigkeit Schraube delta_S  N/mm^2 Pa?
  w = models.FloatField(editable=False, verbose_name= "Connection - Coefficient", default=None, blank=True, null=True)      #Verbindungskoeffizient w
  tan_phi = models.FloatField(editable=False, verbose_name= "Connection - Deformation Cone", default=None, blank=True, null=True)      #Kegelwinkel Verformungskörper  tan_phi
  D_A = models.FloatField(editable=False, verbose_name= "Connection - outside diameter of the interface", default=None, blank=True, null=True)      #mittlerer Außendurchmesser versp. Teile in Trennfuge D_A
  D_A_prime = models.FloatField(editable=False, verbose_name= "Connection - substitutional outside diameter of the interface", default=None, blank=True, null=True)      #substitutional mittlerer Außendurchmesser versp. Teile in Trennfuge D_A
  Gr = models.FloatField(editable=False, verbose_name= "Connection - Limiting Diameter", default=None, blank=True, null=True)      #Grenzdurchmesser D_A,Gr
  d_H = models.FloatField(editable=False, verbose_name= "Connection - Largest Hole Diameter", default=None, blank=True, null=True)      #maximales Durchgansloch d_h
  delta_p_1 = models.FloatField(editable=False, verbose_name= "Connection - resilience of part 1", default=None, blank=True, null=True)      #Nachgiebigkeit delta_p_1
  delta_p_2 = models.FloatField(editable=False, verbose_name= "Connection - resilience of part 2", default=None, blank=True, null=True)      #Nachgiebigkeit delta_p_1
  delta_p_3 = models.FloatField(editable=False, verbose_name= "Connection - resilience of part 3", default=None, blank=True, null=True)      #Nachgiebigkeit delta_p_1
  delta_p_substituted = models.FloatField(editable=False, verbose_name= "Connection - resilience substituted", default=None, blank=True, null=True)      #delta_p_einfach
  delta_p_total = models.FloatField(editable=False, verbose_name= "Connection - resilience total", default=None, blank=True, null=True)      #D160 delta_p_ges
  l_K = models.FloatField(editable=False, verbose_name= "Connection - clamping length", default=None, blank=True, null=True)      #clamping length

  l_H_1 = models.FloatField(editable=False, verbose_name= "length of the deformation sleeve", default=None, blank=True, null=True) #Länge Verformungshuelse -l_H_1
  l_V_1_a = models.FloatField(editable=False, verbose_name= "length of the deformation cone part 1", default=None, blank=True, null=True) #Länge Verformungskegel 1-Teil1 l_V_1_a
  l_V_1_b = models.FloatField(editable=False, verbose_name= "length of the deformation cone part 2", default=None, blank=True, null=True) #Länge Verformungskegel 1-Teil1 l_V_1_b

  d_W_1_a = models.FloatField(editable=False, verbose_name= "bearing area diameter part 1", default=None, blank=True, null=True) #Auflagedurchmessers d_W_1_a
  d_W_1_b = models.FloatField(editable=False, verbose_name= "bearing area diameter part 2", default=None, blank=True, null=True) #Auflagedurchmessers d_W_1_b


  delta_p_V_1_a = models.FloatField(editable=False, verbose_name= "????", default=None, blank=True, null=True) #????
  delta_p_V_1_b= models.FloatField(editable=False, verbose_name= "????", default=None, blank=True, null=True) #????
  delta_p_H_1 = models.FloatField(editable=False, verbose_name= "????", default=None, blank=True, null=True) #????

  load_factor = models.FloatField(editable=False, verbose_name= "Load Factor", default=None, blank=True, null=True) #D163

  ROUGHNESS_LOW= 'RL'
  ROUGHNESS_MEDIUM = 'RM'
  ROUGHNESS_HIGH = 'RH'

  ROUGHNESS_CHOICES= [
    (ROUGHNESS_LOW, ('<10um')),
    (ROUGHNESS_MEDIUM, ('10μm to 40μm')),
    (ROUGHNESS_HIGH, ('40μm to 160μm')),
  ]

  roughness = models.CharField(choices=ROUGHNESS_CHOICES, max_length=32, default=ROUGHNESS_HIGH)



  EM = 'Elongation Meausurements'
  TAM = 'Torque plus angle monitoring'
  CTW = 'Calibrated Torque Wrench'
  STT = 'Straight Torque Tightening'

  TIGHTENING_METHOD = [
    (EM, ('Elongation Meausurements')),
    (TAM, ('Torque plus angle monitoring')),
    (CTW, ('Calibrated Torque Wrench')),
    (STT, ('Straight Torque Tightening')),
  ]

  tightening_method = models.CharField(choices=TIGHTENING_METHOD, max_length=32, default=CTW)

  DRAFT = 'Draft'
  TESTING = 'Testing'
  RELEASE = 'Release'
  MATURITY = [
    (DRAFT, ('Initial investigation')),
    (TESTING, ('Released for testing')),
    (RELEASE, ('Released for production')),
    ]
  maturity = models.CharField(choices=MATURITY, max_length=32, default=DRAFT)

  def get_absolute_url(self):
    from django.urls import reverse
    return reverse('boltcase-detailview', kwargs={'pk': self.pk}, null=True)

  def __str__(self):
    return str(self.name) + ' - ' + str(self.status)



  class Meta:
    app_label = 'BoltMan'














  def set_vdi_input_param (self):
    try:
        self.d_w =self.bolt_geometry.headdiameter                                                         #Head DIameter                                        D54
        self.h_s = self.washer_head.thickness                                                             #Höhe Beilagscheibe / Washer Height                   D84

        self.l_1 = self.bolt_geometry.shank_length                                                        #"Shank length"                                         D29
        self.D_A =  2 * self.bolt_geometry.mthread.nominaldiameter                                        #substitutional outside diameter of the basic solid   DEF100   have to be corrected

                                                                                        #average substitutional outside diameter of the interface D126
        #calculate number of parts
        self.nop = 0
        if self.part1:
          self.nop = 1
          self.l_H_1 =  self.part1.thickness                                                    #D135 from D99
          self.l_K =  self.part1.thickness                                                      #calculate clamping length        D78    !Senkungen etc nicht berücksigtigt
          if self.part2:
            self.nop = 2
            self.l_H_2 =  self.part2.thickness                                                  #D143 from E99
            self.l_K = self.part1.thickness + self.part2.thickness                              #calculate clamping length        D78    !Senkungen etc nicht berücksigtigt
            if self.part3:
              self.nop = 3
              self.l_H_3 =  self.part3.thickness                                                #D151 from F99
              self.l_K = self.part1.thickness + self.part2.thickness + self.part3.thickness     #calculate clamping length        D78    !Senkungen etc nicht berücksigtigt

        self.d_h_max = max([self.holediameter_part1, self.holediameter_part2, self.holediameter_part3])   #maximum through hole D129
 
        self.l_gew = self.l_K- self.l_1  

        #calculate joint coefficient D124
        self.w = 0                                                                                             
        if self.bolt_case_class == 'Bolted Joint':
          if self.D_A < 1.4 * self.d_w:
            self.w = 1
          elif self.D_A >= 1.4 * self.d_w:
            self.w = 2
        elif self.bolt_case_class == 'Tapped Thread Joint':
          self.w = 2

        #calculate substitutional cone angle D125
        self.tan_phi=0      
        D_A_prime =  2 * self.bolt_geometry.mthread.nominaldiameter                                  #substitutional outside diameter of the basic solid   D127 
                                                                               #"Length of the free loaded thread"              D79                                                                             
        if self.w==1: #  Connection coeeficient = 1
          self.tan_phi = 0.362 + 0.032 * math.log(self.l_K / ( self.d_w + 1.6 * self.h_s ) / 2. ) + 0.153 * math.log( D_A_prime / ( self.d_w + 1.6 * self.h_s) )
        elif self.w==2:   #Connection coeeficient = 2  
          self.tan_phi = 0.348 + 0.013 * math.log(self.l_K/ ( self.d_w + 1.6 * self.h_s ) + 1.6 * self.h_s ) + 0.193 * math.log( D_A_prime / ( self.d_w + 1.6 * self.h_s ) )

        #check if the parts have the same E Modulus
        self.sem = False
        tolerance = 0.05
        if self.part1.material.moeit * (1 - tolerance) < self.part2.material.moeit < self.part1.material.moeit *(1 + tolerance):
          self.sem = True
          if self.nop == 3:
            if self.part3.material.moeit * (1 - tolerance) < self.part2.material.moeit < self.part3.material.moeit *(1 + tolerance):   
              self.sem = True
            else:
                self.sem = False      
        else:
          self.sem = False

        if self.sem == True:
          self.delta_p_total = self.resilience_parts_same_Emodulus()
        else:
          self.delta_p_total = self.resilience_parts_different_Emodulus()

        self.delta_S = self.resilience_bolt()

        self.load_factor = self.delta_p_total/(self.delta_S + self.delta_p_total)
    except (TypeError, AttributeError):
        print('Boltcase noit fully defined')

 ##################################################### 
  def resilience_parts_same_Emodulus (self):
    #just to keep the formulas short and without self
    E_p =self.part1.material.moeit
    tan_phi = self.tan_phi
    d_w = self.d_w
    h_s = self.h_s
    l_K = self.l_K
    w = self.w

    D_A =  2 * self.bolt_geometry.mthread.nominaldiameter                                        #substitutional outside diameter of the basic solid   DEF100   have to be corrected
    D_A_m = D_A                                                                                  #average substitutional outside diameter of the interface D126

    d_h_max =     max([self.holediameter_part1, self.holediameter_part2, self.holediameter_part3])   #maximum through hole D129

    D_A_Gr =d_w+ 1.6 * h_s+ self.w*l_K * self.tan_phi                                                            #limiting diameter D128

    if d_w >= D_A:  #D130
      delta_p1 =( 4 * l_K ) / ( E_p * math.pi * (D_A **2 - d_h_max **2 ) )

    if D_A >= D_A_Gr: #131
      delta_p2 =( 2 * math.log( ( ( d_w + 1.6 * h_s + d_h_max ) * ( d_w + 1.6 * h_s + self.w * l_K * tan_phi - d_h_max ) ) / ( ( d_w + 1.6 * h_s - d_h_max ) * ( d_w + 1.6 * h_s + w * l_K * tan_phi + d_h_max ) ) ) ) / ( w * E_p * math.pi * d_h_max * tan_phi )

    if d_w < D_A and d_w < D_A_Gr:  #132
      delta_p3 = (( 2 / ( self.w * d_h_max * tan_phi ) ) * math.log( ( ( d_w + 1.6 * h_s + d_h_max ) * ( D_A_m - d_h_max ) ) / ( ( d_w + 1.6 * h_s - d_h_max ) * ( D_A_m + d_h_max ) ) ) + ( 4 / ( D_A_m **2 - d_h_max **2 ) * ( l_K - ( D_A_m - ( d_w + 1.6 * h_s ) ) / ( self.w * tan_phi ) ) ) ) / ( E_p * math.pi )

    if  (d_w + 1.6 * h_s) >= D_A_m:  #average substitutional outside diameter of the interface D12:
      delta_P = delta_p1
    elif D_A_m >= D_A_Gr: 
      delta_P =  delta_p2
    else:
      delta_P =  delta_p3
    return delta_P


 #####################################################  
  def resilience_parts_different_Emodulus (self):
    #just to keep the formulas short and without self

    tan_phi = self.tan_phi
    d_w = self.d_w
    h_s = self.h_s
    l_K = self.l_K
    w = self.w
    D_A =self.D_A
    nop = self.nop

    if nop > 0:
      l_H_1 =  self.part1.thickness     #D135 from D99
      d_h_1 = self.holediameter_part1
      E_1 =self.part1.material.moeit
    if nop > 1:    
      l_H_2 =  self.part2.thickness     #D143 from E99
      d_h_2 = self.holediameter_part2
      E_2 =self.part2.material.moeit
    if nop > 2:
      l_H_3 =  self.part3.thickness     #D151 from F99
      d_h_3 = self.holediameter_part3
      E_3 =self.part3.material.moeit 

    #l_V_1_a = D136
    #l_V_1_b = D137   
    if l_H_1 <= (l_K / 2):      
      l_V_1_a = l_H_1 / 2       
      l_V_1_b = l_H_1 / 2       
    else:
      l_V_1_a = l_K / 2
      if nop < 3:   #number of clamped parts variable
        l_V_1_b = l_K / 2 - l_H_2 
      if nop == 3:
        l_V_1_b = l_K / 2 - l_H_2 -l_H_3      

    #l_V_2_a = D144
    #l_V_2_b = D145
    if nop< 3:
      if l_H_1 < l_K / 2:
        l_V_2_a = l_K / 2 - l_H_1
        l_V_2_b = l_K / 2
      else:
        l_V_2_a = l_H_2 / 2
        l_V_2_b = l_H_2 / 2

    if nop == 3:
      if l_H_1 < l_K/2:
        if ( l_H_1 + l_H_2 )<=l_K/2:
          l_V_2_a =  l_H_2  /2
          l_V_2_b =  l_H_2 / 2
        else:
          l_V_2_a =  l_K / 2 - l_H_1
          l_V_2_b =  l_K / 2 - l_H_3
      else:
        l_V_2_a =  l_H_2 / 2
        l_V_2_b =  l_H_2 / 2

    #l_V_3_a = D152
    #l_V_3_b = D153
    if nop< 3:
      l_V_3_a = 0
      l_V_3_b = 0
    else:
      if  l_H_1 <= l_K / 2:
        if (l_H_1 + l_H_2) <= l_K / 2:
          l_V_3_a = l_K / 2 - (l_H_1 + l_H_2)
          l_V_3_b = l_K / 2
        else:
          l_V_3_a = l_H_3 / 2
          l_V_3_b = l_H_3 / 2
      else:  
          l_V_3_a = l_H_3 / 2
          l_V_3_b = l_H_3 / 2

    #d_W_1_a = D138
    d_W_1_a = d_w + 2 * tan_phi * 0 + 1.6 * h_s
    #d_W_1_b = D139    
    d_W_1_b = d_w + 2 * tan_phi  * l_V_1_a + 1.6 * h_s

    #d_W_2_a = D146; 
    #d_W_2_b = d_W_2_b;
    #d_W_3_a = D154; 
    #d_W_3_b = D155;
    if self.nop < 3:
      d_W_2_a = d_w + 1.6 * h_s + 2 * tan_phi * (l_V_2_b)
      d_W_2_b = d_w + 2 * tan_phi * 0 + 1.6 * h_s
      d_W_3_a = 0
      d_W_3_b = 0
    else:
      d_W_2_a = d_w + 2 * tan_phi * ( l_H_1 + l_V_2_a ) + 1.6 * h_s
      d_W_2_b = d_w + 2 * tan_phi * (l_H_3 + l_V_2_a) + 1.6 * h_s
      d_W_3_a = d_w + 2 * tan_phi * l_V_3_b + 1.6 * h_s
      d_W_3_b = d_w + 2  *tan_phi * 0 + 1.6 * h_s



    #delta_p_V_1_a = D140;
    if d_w + 1.6 * h_s >= D_A:
      delta_p_V_1_a = 0
    else:
      delta_p_V_1_a = (math.log((d_W_1_a + d_h_1) * (d_W_1_a + 2.0 * l_V_1_a * tan_phi - d_h_1))  / ((d_W_1_a - d_h_1) * (d_W_1_a + 2.0 * l_V_1_a * tan_phi + d_h_1))) / (E_1 * d_h_1 * math.pi * tan_phi)

    #delta_p_V_1_b = D141
    if d_w + 1.6 * h_s >= D_A:
        delta_p_V_1_b = 0
    else:
      if nop < 3:
        if l_H_1 <= l_K / 2:
          delta_p_V_1_b = (math.log(( d_W_1_b + d_h_1 ) * ( d_W_1_b + 2 * l_V_1_b * tan_phi - d_h_1 )) / ( ( d_W_1_b - d_h_1 ) * ( d_W_1_b + 2 * l_V_1_b * tan_phi + d_h_1 ) ) ) / ( E_1 * d_h_1 * math.pi * tan_phi )
        else:	
          delta_p_V_1_b = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_2 ) + d_h_1 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_2 ) + 2 * l_V_1_b * tan_phi - d_h_1 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_2 ) - d_h_1 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_2 ) + 2 * l_V_1_b * tan_phi + d_h_1 ) ) ) / ( E_1 * d_h_1 *math.pi * tan_phi )
      else:	
        if (l_H_2 + l_H_3) < l_K / 2:
          delta_p_V_1_b = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_2 + l_H_3 ) ) + d_h_1 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_2 + l_H_3 ) ) + 2 * l_V_1_b * tan_phi - d_h_1 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_2 + l_H_3 ) ) - d_h_1 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_2 + l_H_3 ) ) + 2 * l_V_1_b * tan_phi + d_h_1 ) ) ) / ( E_1 * d_h_1 *math.pi * tan_phi )
        else:
          delta_p_V_1_b = (math.log(( d_W_1_b + d_h_1 ) * ( d_W_1_b + 2 * l_V_1_b * tan_phi - d_h_1 )) / ( ( d_W_1_b - d_h_1 ) * ( d_W_1_b + 2 * l_V_1_b * tan_phi + d_h_1 ) ) ) / ( E_1 * d_h_1 * math.pi * tan_phi )

    #delta_p_H_1 = D142
    if d_w + 1.6 * h_s >= D_A:
      delta_p_H_1 = 0
    else:
      delta_p_H_1 = (4 * l_H_1) / (E_1 * math.pi * (D_A **2 - d_h_1 **2))

    #delta_p_V_2_a = D148
    if d_w + 1.6 * h_s >= D_A:
      delta_p_V_2_a=0
    else:	
      if nop < 3:
        if l_H_1 >= l_K / 2:
          delta_p_V_2_a = (math.log(( d_W_2_a + d_h_2 ) * ( d_W_2_a + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( d_W_2_a - d_h_2 ) * ( d_W_2_a + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 *math.pi * tan_phi )
        else:
          delta_p_V_2_a = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_1 ) + d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_1 ) + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_1 ) - d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * l_H_1 ) + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.math.pi * tan_phi )
      else:
        if( l_H_2 + l_H_3 ) <= l_K / 2:
          delta_p_V_2_a = (math.log(( d_W_2_b + d_h_2 ) * ( d_W_2_b + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( d_W_2_b - d_h_2 ) * ( d_W_2_b + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.pi * tan_phi )
        else:		
          delta_p_V_2_a = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 ) ) + d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 ) ) + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 ) ) - d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 ) ) + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.pi * tan_phi )

    #delta_p_V_2_b = D149
    if d_w + 1.6 * h_s >= D_A:
      delta_p_V_2_b = 0
    else:
      if self.nop < 3:
        delta_p_V_2_b = (math.log(( d_W_2_b + d_h_2 ) * ( d_W_2_b + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( d_W_2_b - d_h_2 ) * ( d_W_2_b + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.pi * tan_phi )
      else:
        if( l_H_1 + l_H_2 ) <= l_K / 2:
          delta_p_V_2_b = (math.log(( d_W_2_a + d_h_2 ) * ( d_W_2_a + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( d_W_2_a - d_h_2 ) * ( d_W_2_a + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.pi * tan_phi )
        else:
          delta_p_V_2_b = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_3 ) ) + d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_3 ) ) + 2 * l_V_2_a * tan_phi - d_h_2 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_3 ) ) - d_h_2 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_3 ) ) + 2 * l_V_2_a * tan_phi + d_h_2 ) ) ) / ( E_2 * d_h_2 * math.pi * tan_phi )

    #delta_p_H_2 = D150
    if d_w + 1.6 * h_s >= D_A:
      delta_p_H_2 = 0
    else:
      delta_p_H_2 = (4 * l_H_2) / (E_2 * math.pi * (D_A **2 - d_h_2 **2))

    #delta_p_V_3_a = D156
    if self.nop < 3:
        delta_p_V_3_a = 0
    else:
      if (d_w + 1.6 * h_s) >= D_A:
          delta_p_V_3_a = 0
      else:
        if ( l_H_1 + l_H_2 ) < l_K / 2:
          delta_p_V_3_a = (math.log(( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 + l_H_2 ) ) + d_h_3 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 + l_H_2 ) ) + 2 * l_V_3_a * tan_phi - d_h_3 )) / ( ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 + l_H_2 ) ) - d_h_3 ) * ( ( d_w + 1.6 * h_s + 2 * tan_phi * ( l_H_1 + l_H_2 ) ) + 2 * l_V_3_a * tan_phi + d_h_3 ) ) ) / ( E_3 * d_h_3 * math.pi * tan_phi )
        else:
          delta_p_V_3_a = (math.log(( d_W_3_a + d_h_3 ) * ( d_W_3_a + 2 * l_V_3_a * tan_phi - d_h_3 )) / ( ( d_W_3_a - d_h_3 ) * ( d_W_3_a + 2 * l_V_3_a * tan_phi + d_h_3 ) ) ) / ( E_3 * d_h_3 * math.pi * tan_phi )

    #delta_p_V_3_b = D157
    if self.nop < 3:
      delta_p_V_3_b = 0
    elif self.d_w + 1.6 * h_s >= D_A:
      delta_p_V_3_b = 0
    else:
      delta_p_V_3_b = (math.log((d_W_3_b + d_h_3) * (d_W_3_b + 2 * l_V_3_b * tan_phi - d_h_3)) / ((d_W_3_b - d_h_3) * (d_W_3_b + 2 * l_V_3_b * tan_phi + d_h_3))) / (E_3 * d_h_3 * math.pi * tan_phi)  

    #delta_p_H_3 = D158
    if self.nop < 3:
      delta_p_H_3 = 0
    elif d_w + 1.6 * h_s < D_A:
      delta_p_H_3 = 0
    else:
      delta_p_H_3 = (4 * l_H_3) / (E_3 * math.pi * (D_A **2 - d_h_3 **2))

    if d_w + 1.6 * h_s >= D_A:
      if self.nop < 3:
        delta_P = delta_p_H_1 + delta_p_H_2
      else:
        delta_P = delta_p_H_1 + delta_p_H_2 + delta_p_H_3
    else:
      if self.nop < 3:
        delta_P = delta_p_V_1_a + delta_p_V_1_b + delta_p_V_2_a + delta_p_V_2_b
      else:
        delta_P = delta_p_V_1_a + delta_p_V_1_b + delta_p_V_2_a + delta_p_V_2_b + delta_p_V_3_a + delta_p_V_3_b

    return delta_P

 #####################################################  
  def resilience_bolt (self):

    A_n = self.bolt_geometry.mthread.nominaldiameter ** 2.0 * math.pi / 4.0                             #"Bolt - Nominal cross-section (mm^2)"                  D120
    A_3 = self.bolt_geometry.mthread.minordiameter ** 2.0 *math.pi / 4.0                               #"Bolt - MinorDiameter cross-section (mm^2)"            D121 
    D_n = self.bolt_geometry.mthread.nominaldiameter                                             #"Bolt - thread minor diameter"                         D12
    E = self.bolt_geometry.material.moeit                                                        #"Modulus of elasticity in tension"                     D41

    l_K =self.part1.thickness                    #"Clamping length"                                      D78    !Senkungen etc nicht berücksigtigt
    if self.part2:
      l_K = l_K + self.part2.thickness
    if self.part3:
      l_K = l_K + self.part3.thickness
    

    l_1 = self.bolt_geometry.shank_length                                                        #"Shank length"                                         D29
    l_gew = l_K- l_1                                                                             #"Length of the free loaded thread"              D79

    delta_1 = 1.0 / E * l_1 / A_n
    delta_SK = 1.0 / E * 0.4 * D_n / A_n
    delta_Gew = 1.0 / E * (l_K - l_gew) / A_n

    if self.bolt_case_class == 'Bolted Joint':
      delta_GM = 1.0/E*(0.5*D_n/A_3+0.4*D_n/A_n)
    elif self.bolt_case_class == 'Tapped thread joint':
      delta_GM = 1.0/E*(0.5*D_n/A_3+0.33*D_n/A_n)

    delta_S = delta_SK+delta_1+delta_Gew+delta_GM

    return delta_S







