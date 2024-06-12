from django.contrib import admin
from app.models import Admin_Account,Employee,SuperAdmin_Account,Material,Section,Bill,Admin,Warehouse,Bill_Details,Bill_final
# Register your models here.
admin.site.register(Admin_Account)
admin.site.register(SuperAdmin_Account)

admin.site.register(Employee)
admin.site.register(Material)
admin.site.register(Section)
admin.site.register(Bill)
admin.site.register(Admin)
admin.site.register(Warehouse)
admin.site.register(Bill_Details)
admin.site.register(Bill_final)
# admin.site.register(Attendance)