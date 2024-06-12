from django.db import models
from datetime import datetime
from django.conf import settings
from django.utils import timezone

# Create Account To Admin
#_________________________________________________________________________________
class Admin_Account(models.Model):
  admin_email = models.EmailField(max_length=255,default=None,null=True,blank=True)#
  employee_email = models.EmailField(max_length=255,default=None,null=True,blank=True)#
  date = models.DateField(default=datetime.now)#مشان انتهء الصلاحية
  max_warehouses=models.IntegerField(max_length=2,default=0)


  def __str__(self):
    return f'{self.pk}  .  {self.admin_email}'

#_________________________________________________________________________________
class Warehouse(models.Model):
  warehouse_name=models.CharField(max_length=255,null=True,blank=True,default=None)

  def __str__(self):
        return self.warehouse_name
#_________________________________________________________________________________ 
class SuperAdmin_Account(models.Model):
  admin_email = models.EmailField(max_length=255,null=True,blank=True,default=None,verbose_name='super_admin_email')
  admin_password = models.CharField(max_length=255,null=True,blank=True,default=None,verbose_name='super_admin_passsword')

  def __str__(self):
    return f'{self.pk}  .  {self.admin_email}'  
#________________________________________________________________________________
class Admin(models.Model):
  admin_name= models.CharField(max_length=255,null=True,blank=True,default=None)

  def __str__(self):
    return f'{self.pk}  .  {self.admin_name}' 
#__________________________________________________________________________________
class Employee(models.Model):
  name = models.CharField(max_length=255,null=True,blank=True,default=None)
  phone = models.IntegerField()
  # code = models.CharField(max_length=255,unique=True,null=True,blank=True,default=None)
  code = models.CharField(max_length=255,null=True,blank=True,default=None)
  warehouse_id= models.ForeignKey(Warehouse, on_delete=models.PROTECT,null=True,blank=True)

  def __str__(self):
    return f'{self.pk}  .  {self.name}'

#_________________________________________________________________________________
# class Attendance(models.Model):
#   employee=models.ForeignKey(Employee,on_delete=models.CASCADE)
#   Warehouse=models.ForeignKey(Warehouse,on_delete=models.CASCADE)
#   login_time=models.DateField(auto_now_add=True)
#   # login_time=models.DateField(default=datetime.now())
#_________________________________________________________________________________
class Section(models.Model):
  section_name= models.CharField(max_length=255,null=True,blank=True,default=None)
  # number_of_shelf = models.IntegerField()
  warehouse_id= models.ForeignKey(Warehouse, on_delete=models.PROTECT,null=True,blank=True)

  def __str__(self):
        # return str(self.id)+'.'+ self.section_name+'( '+str(self.number_of_shelf)+' )-'
        return self.section_name
#_________________________________________________________________________________
class Material(models.Model):
  material_name = models.CharField(max_length=255,null=True,blank=True,default=None)
  count = models.IntegerField()
  count_type = models.CharField(max_length=255,null=True,blank=True,default=None)
  date = models.DateField()
  description = models.TextField()
  shelf_number = models.IntegerField(default=1)#location
  warehouse_id= models.ForeignKey(Warehouse, on_delete=models.CASCADE,null=True,blank=True)
  section_id=models.ForeignKey(Section, on_delete=models.CASCADE,null=True,blank=True)

  def __str__(self):
        # return self.material_name+'( '+str(self.count)+'['+str(self.count_type)+'] )-'
        return self.material_name+','+str(self.count)
#_________________________________________________________________________________

class Bill_Details(models.Model):
  date = models.DateField(default=datetime.now)
  code = models.CharField(max_length=255,null=True,blank=True,default=None)
  
  def __str__(self):
      return  'Bill_Details '+str(self.id)
# -------------------------------------------------------------------

class Bill(models.Model):
  material_name = models.CharField(max_length=255,null=True,blank=True,default=None)
  count = models.IntegerField()
  # materials=models.JSONField()
  # CHOICES = (
  #       ('input', 'input'),
  #       ('output', 'output'),
  #   )
  # bill_type = models.CharField(max_length=10, choices=CHOICES,null=True,blank=True,default=None)
  warehouse_id= models.ForeignKey(Warehouse, on_delete=models.PROTECT,null=True,blank=True)
  bill_details_id=models.IntegerField(default=-1)
  
  # employee_id= models.ForeignKey(Employee, on_delete=models.PROTECT,null=True,blank=True)
  # admin_id=models.ForeignKey(Admin, on_delete=models.PROTECT,null=True,blank=True)
  def __str__(self):
        return  'Bill '+str(self.id)
#__________________________________________________________________________________

class Bill_final(models.Model):
  date = models.DateField(null=True,blank=True)
  code = models.CharField(max_length=255,null=True,blank=True,default=None)
  material_name = models.CharField(max_length=255,null=True,blank=True,default=None)
  count = models.IntegerField()
  warehouse_id= models.ForeignKey(Warehouse, on_delete=models.PROTECT,null=True,blank=True)
  bill_details_id=models.IntegerField()
  def __str__(self):
        return  'Bill_final '+str(self.id)


