from django.urls import path
from app import views 


 
urlpatterns=[
path('',views.log_in_as,name="log_in_as"),
path('home_page/',views.first,name="first"),

path('send_code/',views.send_code,name="send_code"),
path('check/' ,views.check , name="check"),

path('delete_employee/',views.delete_employee,name="delete_employee"),
path('delete/',views.delete,name="delete"),

path('sign_in/',views.sign_in,name="sign_in"),
path('create_account/',views.create_account,name="create_account"),
path('creat/',views.creat,name="creat"),

path('add_material/',views.add_material,name="add_material"),

path('add_employee/',views.add_employee,name="add_employee"),
path('add/',views.add,name="add"),

path('send/',views.send_email,name="send"),
path('show_emp/',views.show_emp,name="show_emp"),
path('view_log_in/',views.view_log_in,name="view_log_in"),
path('log_in/',views.log_in,name="log_in"),

path('view_sign_in_employee/',views.view_sign_in_employee,name="view_sign_in_employee"),
path('sign_in_employee/',views.sign_in_employee,name="sign_in_employee"),
path('employee_code/',views.employee_code,name="employee_code"),
# path('view_home_page_employee/',views.view_home_page_employee,name="view_home_page_employee"),
path('add_material_employee/',views.add_material_employee,name="add_material_employee"),
path('add_material_proces_employee/',views.add_material_proces_employee,name="add_material_proces_employee"),

path('view_all_account/',views.view_all_account,name="view_all_account"),
# path('view_all_materials/',views.view_all_materials,name="view_all_materials"),

path('XX/',views.XX,name='XX'),
path('CC/',views.CC,name='CC'),
path('add_material_proces/',views.add_material_proces,name='add_material_proces'),
path('view_add_warehouse/',views.view_add_warehouse,name="view_add_warehouse"),
path('add_warehouse/',views.add_warehouse,name="add_warehouse"),
path('delete_warehouse/',views.delete_warehouse,name="delete_warehouse"),

path('taking_out_material/',views.taking_out_material,name="taking_out_material"),
path('view_add_section/',views.view_add_section,name="view_add_section"),
path('add_section/',views.add_section,name="add_section"),

path('add_to_bill/',views.add_to_bill,name="add_to_bill"),
path('out_bill/',views.out_bill,name="out_bill"),


path('all_bills/',views.all_bills,name="all_bills"),
path('bill_details/',views.bill_details,name="bill_details"),
path('delete_from_bill/',views.delete_from_bill,name="delete_from_bill"),
path('generate_files/',views.generate_files,name="generate_files"),


path('taking_out_material_employee/',views.taking_out_material_employee,name="taking_out_material_employee"),
path('add_to_bill_employee/',views.add_to_bill_employee,name="add_to_bill_employee"),
path('out_bill_employee/',views.out_bill_employee,name="out_bill_employee"),
path('delete_from_bill_employee/',views.delete_from_bill_employee,name="delete_from_bill_employee"),

path('view_transfer/',views.view_transfer,name="view_transfer"),
path('select_warehouse/',views.select_warehouse,name="select_warehouse"),
path('trans_proces/',views.trans_proces,name="trans_proces"),
path('delete_from_trans/',views.delete_from_trans,name="delete_from_trans"),
path('trans_from_to/',views.trans_from_to,name="trans_from_to"),
path('login_all/',views.login_all,name="login_all"),
#------------------------------------------------------------
#manager
path('add_employee_manager/',views.add_employee_manager,name="add_employee_manager"),
path('add_manager/',views.add_manager,name="add_manager"),
path('delete_employee_manager/',views.delete_employee_manager,name="delete_employee_manager"),
path('delete_manager/',views.delete_manager,name="delete_manager"),
path('add_material_manager/',views.add_material_manager,name="add_material_manager"),
path('add_material_proces_manager/',views.add_material_proces_manager,name="add_material_proces_manager"),
path('taking_out_material_manager/',views.taking_out_material_manager,name="taking_out_material_manager"),
path('add_to_bill_manager/',views.add_to_bill_manager,name="add_to_bill_manager"),
path('out_bill_manager/',views.out_bill_manager,name="out_bill_manager"),
path('delete_from_bill_manager/',views.delete_from_bill_manager,name="delete_from_bill_manager"),
path('all_bills_manager/',views.all_bills_manager,name="all_bills_manager"),
path('view_add_section_manager/',views.view_add_section_manager,name="view_add_section_manager"),
path('add_section_manager/',views.add_section_manager,name="add_section_manager"),
path('CCC/',views.CCC,name='CCC'),
path('generate_rebort/',views.generate_rebort,name='generate_rebort'),

path('update_max_warehouses/',views.update_max_warehouses,name='update_max_warehouses'),
path('update_date/',views.update_date,name='update_date'),

path('error_page/',views.error_page,name='error_page'),


]