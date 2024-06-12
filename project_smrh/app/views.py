from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from app.models import (
    Admin_Account,
    Employee,
    SuperAdmin_Account,
    Material,
    Warehouse,
    Section,
    Bill,
    Bill_Details,
    Bill_final,
)
import os
from django.conf import settings
import random
from django.core.mail import send_mail
from datetime import datetime, timedelta,date

# Create your views here.
# from django.contrib.auth.decorators import login_required
# @login_required(login_url='//')
def XX(request):  # بيعرض  اول واجهة للمستخدم فيها كل المستودعات
    if request.method=='POST':
        Mywarehouses = Warehouse.objects.all()
        admin_account_date=request.POST['admin_account_date']
        return render(request, "XX.html", {"Mywarehouses": Mywarehouses,'admin_account_date':admin_account_date})
    else:
        return redirect('/')

# -------------------------------------------------------------------


def CC(request):  # التابع المسؤل عن عرض المواد الخاصة بكل مستودع
    if request.method == "POST":
        warehouse_name = request.POST["warehouse_name"]
        admin_account_date = request.POST["admin_account_date"]
        mymaterial = Material.objects.filter(
            warehouse_id=warehouse_name
        )  # قيمة الwarehouse_id رح تطلع بالداتا بيز هي اسم بس فعليا هي الرقم الخاص ب هالاوبجكت  يعني صاحب الاسم مشان هيك بصفحة html قلتلو warehouse_id موwarehouse_nmae
        story_name = Warehouse.objects.get(id=warehouse_name)

        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        # filtered_materials = mymaterial.filter(
        #     **{search_field + "__icontains": search_value}
        # )

        # return render(
        #     request,
        #     "index.html",
        #     {   'admin_account_date':admin_account_date,
        #         "mymaterial": mymaterial,
        #         "story_name": story_name,
        #         "filtered_materials": filtered_materials,
        #         "warehouse_name": warehouse_name,
        #     },
        # )
        
        if search_field == "date":
            try:
                d1 = request.POST.get("from_date", "2029-10-01")
                d2 = request.POST.get("to_date", "2025-11-01")
                date1 = datetime.strptime(d1, "%Y-%m-%d")
                date2 = datetime.strptime(d2, "%Y-%m-%d")
                print(d1)
                
                filtered_materials = mymaterial.filter(date__range=[date1, date2], warehouse_id=warehouse_name)
            except ValueError:
                print(' errot in date')
                filtered_materials = mymaterial.none()
        else:
            filtered_materials = mymaterial.filter(**{search_field + "__icontains": search_value})
        return render(
            request,
            "index.html",
            {
                'admin_account_date': admin_account_date,
                "mymaterial": mymaterial,
                "story_name": story_name,
                "filtered_materials": filtered_materials,
                "warehouse_name": warehouse_name,
            },
        )


# -------------------------------------------------------------------
def select_warehouse(request):
    Mywarehouses = Warehouse.objects.all()
    clas = "form-control"
    return render(
        request, "select_warehouse.html", {"Mywarehouses": Mywarehouses, "clas": clas}
    )


# -------------------------------------------------------------------
def view_transfer(request):
    if request.method == "POST":
        from_warehouse = request.POST["from_warehouse"]  # id
        to_warehouse = request.POST["to_warehouse"]  # id
        warehouse_id = Warehouse.objects.get(id=from_warehouse)
        from_sections = Section.objects.filter(warehouse_id=from_warehouse)
        to_sections = Section.objects.filter(warehouse_id=to_warehouse)
        Mywarehouses = Warehouse.objects.all()
        # clas='form-control'
        if to_sections.count() == 0:
            result = "Sorry, There are no sections in to warehouse"
            clas = "form-control is-invalid"
            return render(
                request,
                "select_warehouse.html",
                {"Mywarehouses": Mywarehouses, "result": result, "clas": clas},
            )

        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # clas='form-control is-invalid'
        # clas='form-control'

        return render(
            request,
            "view_transfer.html",
            {
                "from_sections": from_sections,
                "to_sections": to_sections,
                "Mywarehouses": Mywarehouses,
                "from_warehouse": from_warehouse,
                "to_warehouse": to_warehouse,
                "bm": bm,
            },
        )


# -------------------------------------------------------------------
def trans_proces(request):
    if request.method == "POST":
        from_warehouse = request.POST["from_warehouse"]  # id
        to_warehouse = request.POST["to_warehouse"]  # id
        from_sections = Section.objects.filter(warehouse_id=from_warehouse)
        to_sections = Section.objects.filter(warehouse_id=to_warehouse)

        warehouse2 = Warehouse.objects.get(id=from_warehouse)
        warehouse = Warehouse.objects.get(id=to_warehouse)
        count = request.POST["count"]
        material_name = request.POST["material_name"]
        count_type = request.POST["count_type"]
        shelf_number = request.POST["shelf_number"]
        to_shelf_number = request.POST["to_shelf_number"]
        from_section = request.POST["from_section"]  # name
        from_section_name = Section.objects.get(
            id=from_section, warehouse_id=from_warehouse
        )
        to_section = request.POST["to_section"]  # name
        to_section_name = Section.objects.get(id=to_section, warehouse_id=to_warehouse)
        to_shelf_number = request.POST["to_shelf_number"]
        date = request.POST.get("date", "2023-11-05")
        print(date)
        date1 = datetime.strptime(date, "%Y-%m-%d")
        x = date1.strftime("%Y-%m-%d")
        print(x)

        warehouse_id = Warehouse.objects.get(id=from_warehouse)
        mymaterial = Material.objects.filter(
            warehouse_id=warehouse_id, section_id=from_section_name
        )
        result = "Not Found"

        bm = Bill.objects.filter(warehouse_id=warehouse_id)

        if material_name:
            if count:
                for i in mymaterial:
                    # if material_name == i.material_name and count_type == i.count_type and int(shelf_number) == int(i.shelf_number) and str(date1) == str(i.date)+' 00:00:00':
                    if (
                        material_name == i.material_name
                        and count_type == i.count_type
                        and int(shelf_number) == int(i.shelf_number)
                        and str(x) == str(i.date)
                        and from_section_name == i.section_id
                    ):
                        if int(count) <= int(i.count):
                            # d_s_material  جبتها هون لانو العدد تحت رح يتغير وما عو اعرف لاقي ال العدد الجديد
                            d_s_material = Material.objects.get(
                                warehouse_id=warehouse2,
                                material_name=material_name,
                                count=i.count,
                                count_type=count_type,
                                date=date,
                                section_id=from_section_name,
                            )

                            i.count = int(i.count) - int(count)
                            my = Material.objects.filter(
                                material_name=material_name,
                                warehouse_id=warehouse2,
                                section_id=from_section_name,
                                date=date,
                                count_type=count_type,
                                shelf_number=shelf_number,
                            )
                            my.update(count=int(i.count))
                            xb = Bill(
                                material_name=material_name,
                                count=count,
                                warehouse_id=warehouse2,
                            )
                            xb.save()
                            # --------------------
                            xx = Material(
                                material_name=material_name,
                                count=count,
                                count_type=count_type,
                                date=date,
                                description=d_s_material.description,
                                shelf_number=int(to_shelf_number),
                                warehouse_id=warehouse,
                                section_id=to_section_name,
                            )
                            # xx.save()

                            z = Material.objects.filter(
                                material_name=material_name,
                                count_type=count_type,
                                date=date,
                                shelf_number=int(to_shelf_number),
                                warehouse_id=warehouse,
                                section_id=to_section_name,
                            )

                            if z.exists():
                                for i in z:
                                    s = int(i.count) + int(count)
                                    z.update(count=s)
                                result = "Sorry, already added and ++"
                                print(result)
                            else:
                                result = "add successfulyc"
                                print(result)

                                xx.save()
                            Mywarehouses = Warehouse.objects.all()
                            return render(
                                request,
                                "view_transfer.html",
                                {
                                    "Mywarehouses": Mywarehouses,
                                    "story_name": warehouse_id,
                                    "bm": bm,
                                    "to_warehouse": to_warehouse,
                                    "from_warehouse": from_warehouse,
                                    "from_sections": from_sections,
                                    "to_sections": to_sections,
                                    "result": result,
                                    "count_type": count_type,
                                    "shelf_number": shelf_number,
                                    "from_section_name": from_section_name.id,
                                    "date": date,
                                    "to_section_name": to_section_name.id,
                                    "to_shelf_number": to_shelf_number,
                                },
                            )

        # mymaterial=Material.objects.filter(warehouse_id=warehouse_id)
        result = "Sorry, Not Success"
        Mywarehouses = Warehouse.objects.all()
        return render(
            request,
            "view_transfer.html",
            {
                "Mywarehouses": Mywarehouses,
                "story_name": warehouse_id,
                "bm": bm,
                "to_warehouse": to_warehouse,
                "from_warehouse": from_warehouse,
                "from_sections": from_sections,
                "to_sections": to_sections,
                "result": result,
                "count_type": count_type,
                "shelf_number": shelf_number,
                "from_section_name": from_section_name.id,
                "date": date,
                "to_section_name": to_section_name.id,
                "to_shelf_number": to_shelf_number,
            },
        )


# -------------------------------------------------------------------
def delete_from_trans(request):
    if request.method == "POST":
        from_warehouse = request.POST["from_warehouse"]  # id
        to_warehouse = request.POST["to_warehouse"]  # id
        from_sections = Section.objects.filter(warehouse_id=from_warehouse)
        to_sections = Section.objects.filter(warehouse_id=to_warehouse)
        print(from_warehouse)
        print(to_warehouse)
        warehouse = Warehouse.objects.get(id=to_warehouse)
        warehouse2 = Warehouse.objects.get(id=from_warehouse)
        print(warehouse)
        print(warehouse2)
        count_type = request.POST["count_type"]
        shelf_number = request.POST["shelf_number"]
        to_shelf_number = request.POST["to_shelf_number"]
        from_section_namee = request.POST["from_section_name"]
        from_section_name = Section.objects.get(id=from_section_namee)
        print(from_section_name)
        to_section_namee = request.POST["to_section_name"]
        to_section_name = Section.objects.get(id=to_section_namee)

        print(to_section_name)
        date = request.POST.get("date", "2023-11-05")

        mymaterial = Material.objects.filter(warehouse_id=from_warehouse)
        story_name = Warehouse.objects.get(id=from_warehouse)
        # -------------------
        bm = Bill.objects.filter(warehouse_id=from_warehouse)
        id_delete = request.POST["id_delete"]
        object_delete = Bill.objects.get(id=id_delete)

        material_name = object_delete.material_name

        material_namef = Material.objects.filter(
            warehouse_id=warehouse2,
            material_name=material_name,
            section_id=from_section_name,
            count_type=count_type,
            shelf_number=int(shelf_number),
            date=date,
        )
        print(material_namef)
        for x in material_namef:
            x.count = int(x.count) + int(object_delete.count)
            material_namef.update(count=int(x.count))

        material_namef_to = Material.objects.filter(
            warehouse_id=warehouse,
            material_name=material_name,
            section_id=to_section_name,
            count_type=count_type,
            shelf_number=int(to_shelf_number),
            date=date,
        )
        print(material_namef_to)
        for x in material_namef_to:
            x.count = int(x.count) - int(object_delete.count)
            material_namef_to.update(count=int(x.count))

            # -------------------

        if id_delete:
            object_delete.delete()
            result = "successfuly"
        # mymaterial=Material.objects.filter(warehouse_id=warehouse_id)
        Mywarehouses = Warehouse.objects.all()
        return render(
            request,
            "view_transfer.html",
            {
                "Mywarehouses": Mywarehouses,
                "story_name": story_name,
                "bm": bm,
                "to_warehouse": to_warehouse,
                "from_sections": from_sections,
                "to_sections": to_sections,
                "result": result,
                "count_type": count_type,
                "shelf_number": shelf_number,
                "from_section_name": from_section_name.id,
                "date": date,
                "to_section_name": to_section_name.id,
                "to_shelf_number": to_shelf_number,
                "from_warehouse": from_warehouse,
            },
        )


# -------------------------------------------------------------------
def trans_from_to(request):
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]  # id (out from her)عملية التخريج
        to_warehouse = request.POST["to_warehouse"]  # name (in to heer)عملية الادخال
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)  # object
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # --------------------
        # --------------------

        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        # اول الشي بدي انشئ اوبجكت من جدول الbill_details
        code = 2
        creat_bill_details = Bill_Details(code=code)
        creat_bill_details.save()

        # تاني شي بدي جيب كل المواد الموجودة بجدولBill
        all_bill = Bill.objects.filter(warehouse_id=warehouse_id)
        # جبت id  تبع الاوبجكت يلي انشأته
        id_bill = creat_bill_details.id
        print(id_bill)

        for i in all_bill:
            bill_final = Bill_final(
                material_name=i.material_name,
                count=i.count,
                bill_details_id=id_bill,
                warehouse_id=warehouse_name,
                code=creat_bill_details.code,
                date=creat_bill_details.date,
            )
            bill_final.save()
            i.delete()

        creat_bill_details.delete()
        # mymaterial=Material.objects.filter(warehouse_id=warehouse_id)
        Mywarehouses = Warehouse.objects.all()
        # خلصت عملية التخريج
        # بداية عملية التدخيل
        # material_name موجود من الفواتير
        # count موجود من الفواتير
        # count_type
        # date
        # section_id
        # shelf_number
        # description
        # warehouse_id
        return render(
            request,
            "view_transfer.html",
            {
                "Mywarehouses": Mywarehouses,
                "story_name": warehouse_id,
                "bm": bm,
                "to_warehouse": to_warehouse,
            },
        )


# -------------------------------------------------------------------
def add_material_proces(request):
    if request.method == "POST":
        result = ""    
        admin_account_date=request.POST['admin_account_date']

        warehouse_name = request.POST["warehouse_id"]
        print(warehouse_name)

        mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
        story_name = Warehouse.objects.get(id=warehouse_name)

        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )

        material_name = request.POST.get("material_name", "")
        count = request.POST.get("count", "")
        count_type = request.POST.get("count_type", "")
        date = request.POST.get("date", "")
        section_id = request.POST.get("section", "")
        shelf_number = request.POST.get("shelf_number", "")
        description = request.POST.get("description", "")
        warehouse_id = request.POST.get("warehouse_id", "")

        if (
            material_name
            and count
            and count_type
            and date
            and section_id
            and shelf_number
            and description
            and warehouse_id
        ):
            try:
                section_id = int(section_id)
                warehouse_id = int(warehouse_id)

                warehouse = Warehouse.objects.get(id=warehouse_id)
                section = Section.objects.get(id=section_id)

                x = Material(
                    material_name=material_name,
                    count=count,
                    count_type=count_type,
                    date=date,
                    description=description,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )
                z = Material.objects.filter(
                    material_name=material_name,
                    count_type=count_type,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )

                if z.exists():
                    for i in z:
                        s = int(i.count) + int(count)
                        z.update(count=s)
                    result = "Sorry, already added"
                    print(result)
                else:
                    result = "success"
                    print(result)

                    x.save()
            except ValueError:
                result = "Erorr in section or warehouse ud"
                print(result)

            return render(
                request,
                "index.html",
                {
                    "result": result,
                    "mymaterial": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,
                    "warehouse_name":warehouse_name,'admin_account_date':admin_account_date
                },
            )
        else:
            result = "missing fields"
            return render(
                request,
                "index.html",
                {
                    "result": result,
                    "mymaterial": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,'admin_account_date':admin_account_date
                },
            )


# -------------------------------------------------------------------
def add_warehouse(request):
    if request.method == "POST":
        first_adminaccount=Admin_Account.objects.filter().first()
        warehouse_name = request.POST["warehouse_name"]
        x = Warehouse(warehouse_name=warehouse_name)
        if Warehouse.objects.filter(warehouse_name=warehouse_name).exists():
            # result=messages.info(request,'already added')
            result = "already added"
            print(result)
            print("done")
            print("done")
            print("done")
            print("done")
            return render(request, "view_add_warehouse.html", {"result": result})
        else:
            # if Warehouse.objects.count() <= 3:
            if Warehouse.objects.count() <= first_adminaccount.max_warehouses:
                # result=messages.info(request,'seccuss')
                result = "seccuss"
                print(result)
                print("xxxxx")
                print("xxxxx")
                print("xxxxx")
                x.save()
                return render(request, "view_add_warehouse.html", {"result": result})

            else:
                result = "The number of your warehousee is Maximum"
                print(result)
                return render(request, "view_add_warehouse.html", {"result": result})

            return redirect(XX)


# -------------------------------------------------------------------
def view_add_warehouse(request):
    template = loader.get_template("view_add_warehouse.html")
    return HttpResponse(template.render())


# -------------------------------------------------------------------
def add_material(request):
    result = ""
    admin_account_date=request.POST['admin_account_date']

    warehouse_name = request.POST["warehouse_id"]
    print(warehouse_name)

    warehouse_id = Warehouse.objects.get(id=warehouse_name)
    print(warehouse_id)

    sections = Section.objects.filter(warehouse_id=warehouse_id)
    context = {
        "warehouse_id": warehouse_name,
        # "section_names": section_names,
        "sections": sections,
        "result": result,'admin_account_date':admin_account_date
    }
    return render(request, "add_material.html", context)


# -------------------------------------------------------------------


def first(request):
    mymaterial = Material.objects.all().values()
    template = loader.get_template("index.html")
    context = {
        "mymaterial": mymaterial,
    }
    return HttpResponse(template.render(context, request))


def add_material_employee(request):
    result = ""
    warehouse_name = request.POST["warehouse_id"]
    employee_code = request.POST["employee_code"]
    print(warehouse_name)

    warehouse_id = Warehouse.objects.get(id=warehouse_name)
    print(warehouse_id)

    sections = Section.objects.filter(warehouse_id=warehouse_id)
    context = {
        "warehouse_id": warehouse_name,
        # "section_names": section_names,
        "sections": sections,
        "result": result,
        "employee_code": employee_code,
    }
    return render(request, "add_material_employee.html", context)


# ------------------------------------------------------------------------------
def add_material_proces_employee(request):
    if request.method == "POST":
        result = ""
        warehouse_id = request.POST["warehouse_id"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        print(warehouse_name)

        mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
        story_name = Warehouse.objects.get(id=warehouse_id)

        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )

        material_name = request.POST.get("material_name", "")
        count = request.POST.get("count", "")
        count_type = request.POST.get("count_type", "")
        date = request.POST.get("date", "")
        section_id = request.POST.get("section", "")
        shelf_number = request.POST.get("shelf_number", "")
        description = request.POST.get("description", "")
        warehouse_id = request.POST.get("warehouse_id", "")

        if (
            material_name
            and count
            and count_type
            and date
            and section_id
            and shelf_number
            and description
            and warehouse_id
        ):
            try:
                section_id = int(section_id)
                warehouse_id = int(warehouse_id)

                warehouse = Warehouse.objects.get(id=warehouse_id)
                section = Section.objects.get(id=section_id)

                x = Material(
                    material_name=material_name,
                    count=count,
                    count_type=count_type,
                    date=date,
                    description=description,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )

                # if Material.objects.filter(
                #     material_name=material_name,
                #     count=count,
                #     count_type=count_type,
                #     date=date,
                #     description=description,
                #     shelf_number=shelf_number,
                #     warehouse_id=warehouse,
                #     section_id=section).exists():
                z = Material.objects.filter(
                    material_name=material_name,
                    count_type=count_type,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )

                if z.exists():
                    for i in z:
                        s = int(i.count) + int(count)
                        z.update(count=s)

                else:
                    result = "success"
                    print(result)

                    x.save()
            except ValueError:
                result = "Erorr in section or warehouse ID"
                print(result)

            mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
            return render(
                request,
                "home_page_employee.html",
                {
                    "result": result,
                    "mymaterials": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,
                },
            )
        else:
            result = "missing fields"
            mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
            return render(
                request,
                "home_page_employee.html",
                {
                    "result": result,
                    "mymaterials": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,
                },
            )


# -------------------------------------------------------------------


def third(request):
    template = loader.get_template("contact.html")
    return HttpResponse(template.render())

# -------------------------------------------------------------------

def four(request):
    template = loader.get_template("delete_emp.html")
    return HttpResponse(template.render())

# -------------------------------------------------------------------

def sign_in(request):
    template = loader.get_template("sign-in.html")
    return HttpResponse(template.render())

# -------------------------------------------------------------------

def send_email(request):
    # هي مشان توليد 4 أرقام عشوائية
    random_numbers = [random.randint(0, 9) for _ in range(4)]

    # اليريد  يلي بدو يستلم
    email = request.POST.get("email")

    # هون عملية إرسال البريد
    send_mail(
        "أرقام عشوائية",
        f"أرقامك العشوائية هي: {random_numbers}",
        "scren@company.com",
        [email],
        fail_silently=False,
    )
    print(random_numbers)

    template = loader.get_template("sign-in.html")
    return HttpResponse(template.render())


def sex(request):
    template = loader.get_template("sign-up.html")
    return HttpResponse(template.render())

# -------------------------------------------------------------------

def creat(request):
    result=''
    # template = loader.get_template("createaccount.html",{'clas':clas})
    # return HttpResponse(template.render())
    return render(request,'createaccount.html',{'result':result})
    # return render(request,os.path.join())

# -------------------------------------------------------------------

def create_account(request):
    if request.method == "POST":
        result=''
        admin_email = request.POST["admin_email"]
        employee_email = request.POST["employee_email"]
        max_warehouses = request.POST["max_warehouses"]
        if int(max_warehouses)<=0:
            result='successfuly add,But [Maximum Count of Warehouses=0]!!!'
            return render(request,'createaccount.html',{'result':result})
        else:
            x = Admin_Account(admin_email=admin_email, employee_email=employee_email,max_warehouses=max_warehouses)
            x.save()
            result='successfuly add'
            # template = loader.get_template("createaccount.html",{'result':result})
            # return HttpResponse(template.render())
            return render(request,'createaccount.html',{'result':result})

    else:
        return redirect('/')


# -------------------------------------------------------------------
def add_employee(request):
    warehouse_name = request.POST["warehouse_name"]
    admin_account_date=request.POST['admin_account_date']
    print(warehouse_name)
    result = ""
    clas = "form-control"
    return render(
        request,
        "add_employee.html",
        {"result": result, "warehouse_name": warehouse_name, "clas": clas,'admin_account_date':admin_account_date},
    )

    # template=loader.get_template('add_employee.html')
    # return HttpResponse(template.render(),)


# -------------------------------------------------------------------
def add(request):
    if request.method == "POST":
        result = ""
        clas = "form-control"
        admin_account_date=request.POST['admin_account_date']
        employee_type=request.POST['employee_type']
        print(employee_type)
        print(employee_type)
        print(employee_type)
        print(employee_type)
        print(employee_type)
        warehouse_id = request.POST["warehouse_name"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        name = request.POST["empname"]
        phone = request.POST["empphone"]
        code = request.POST["empcode"]
        y = "1111"
        x = str(y + "" + code)
        print(int(x + "" + code))
        print(int(x))
        if employee_type=='Manager':
            x = Employee(name=name, phone=phone, code=int(x), warehouse_id=warehouse_name)
        else:
            x = Employee(name=name, phone=phone, code=code, warehouse_id=warehouse_name)
        
        # if Employee.objects.filter(phone=phone, code=code).exists():
        if Employee.objects.filter(code=code).exists():
            result = "The Code Already Added"
            clas = "form-control is-invalid"
            print("done")
        else:
            result = "seccuss"
            x.save()
        return render(
            request,
            "add_employee.html",
            {"result": result, "warehouse_name": warehouse_id, "clas": clas,'admin_account_date':admin_account_date},
        )


# -------------------------------------------------------------------


import random
from django.core.mail import send_mail
from django.conf import settings
from .forms import ContactForm
from django.shortcuts import render


# def random_code():
#     code_message = [random.randint(0, 9) for _ in range(4)]
#     split_code_message = ''.join(str(num) for num in code_message)
#     return split_code_message

# -------------------------------------------------------------------
# renamecontact------------------------------------------------------
# def send_code(request):
#     form = ContactForm(request.POST or None)
#     if request.method == 'POST':
#         # email = form.cleaned_data.get('email')
#         email = request.POST['email']
#         # message = form.cleaned_data.get('message')
#         # name = form.cleaned_data.get('name')
#         # print(email, message, name)
#         if Admin_Account.objects.filter(admin_email=email).exists():
#             subject = 'Mail from django'
#             from_email = settings.EMAIL_HOST_USER
#             to_email = [from_email, email]
#             code_message = [random.randint(0, 9) for _ in range(4)]
#             split_code_message = ''.join(str(num) for num in code_message)
#         # fail_silently=False
#             send_mail(subject, split_code_message, from_email, to_email)
#             return render(request, 'verify.html', {'split_code_message': split_code_message})
#         else:
#             return render(request,'sign-in.html')


#     context = {
#         'form': form
#     }
#     return render(request, 'sign-in.html', context)
# -------------------------------------------------------------------
def send_code(request):  # ما الو داعي
    # form = ContactForm(request.POST or None)
    if request.method == "POST":
        email = request.POST["email"]
        if Admin_Account.objects.filter(admin_email=email).exists():
            admin_account = Admin_Account.objects.get(admin_email=email)
            today = datetime.now().date()
            one_year_ago = today - timedelta(days=365)

            if admin_account.date <= one_year_ago:
                # مشان اذا خلصت مدة العقد
                return render(request, "lock.html")

            subject = "Mail from django"
            from_email = settings.EMAIL_HOST_USER
            to_email = [from_email, email]
            code_message = [random.randint(0, 9) for _ in range(4)]
            split_code_message = "".join(str(num) for num in code_message)

            send_mail(subject, split_code_message, from_email, to_email)
            return render(
                request, "verify.html", {"split_code_message": split_code_message}
            )
        else:
            return render(request, "sign-in.html")

    # context = {
    #     'form': form
    # }
    return render(request, "sign-in.html")

# -------------------------------------------------------------------

def login_all(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Admin_Account.objects.filter(admin_email=email).exists():  # admin
            print("admin")
            if request.method == "POST":
                # email = request.POST['email']
                if Admin_Account.objects.filter(admin_email=email).exists():
                    admin_account = Admin_Account.objects.get(admin_email=email)
                    today = datetime.now().date()
                    # one_year_ago = today - timedelta(days=365)

                    # if admin_account.date <= one_year_ago:
                    if admin_account.date <= today:
                        # مشان اذا خلصت مدة العقد
                        return render(request, "lock.html")

                    subject = "Verification Code From HMSR:"
                    from_email = settings.EMAIL_HOST_USER
                    to_email = [from_email, email]
                    code_message = [random.randint(0, 9) for _ in range(4)]
                    split_code_message = "".join(str(num) for num in code_message)
                    # try:
                    #     send_mail(subject, split_code_message, from_email, to_email)
                    #     return render(
                    #         request,
                    #         "verify.html",
                    #         {"split_code_message": split_code_message,'email':email},
                    #     )
                    # except Exception as e:
                    #     print('errrororor')
                    #     return render(request,'log_in_as.html')
                    send_mail(subject, split_code_message, from_email, to_email)
                    return render(
                        request,
                        "verify.html",
                        {"split_code_message": split_code_message,'email':email},)
        if Admin_Account.objects.filter(employee_email=email).exists():  # employee
            print("employee")
            emp_account = Admin_Account.objects.get(employee_email=email)
            today = datetime.now().date()
            # one_year_ago = today - timedelta(days=365)

            if emp_account.date <= today:
                # مشان اذا خلصت مدة العقد
                return render(request, "lock.html")

            # return redirect('employee_code.html')
            return render(request, "employee_code.html",{'email': email})
    return render(request, "log_in_as.html")

# -------------------------------------------------------------------

def check(request):
    Mywarehouses = Warehouse.objects.all()

    split_code_message = request.POST.get("split_code_message")
    code = request.POST["code"]
    email=request.POST['email']
    admin_account_date=Admin_Account.objects.get(admin_email=email).date
    if split_code_message == code:
        print("Error")
        return render(
            request,
            "XX.html",
            {"split_code_message": split_code_message, "Mywarehouses": Mywarehouses,'admin_account_date':admin_account_date},
        )
    else:
        print("Error")
        return render(request, "log_in_as.html")
    print(split_code_message)
    return render(request, "verify.html", {"split_code_message": split_code_message})

# -------------------------------------------------------------

def view_log_in(request):  # for super admin
    template = loader.get_template("log_in.html")
    return HttpResponse(template.render())

# ----------------------------------------------------

def log_in(request):  # chek for super admin
    if request.method == "POST":
        myaccount = Admin_Account.objects.all().values()
        max_warehouses=Admin_Account.objects.filter().first()
        super_admin_email = request.POST["super_admin_email"]
        super_admin_password = request.POST["super_admin_password"]
        print(max_warehouses.date)
        x = SuperAdmin_Account(
            admin_email=super_admin_email, admin_password=super_admin_password
        )
        if SuperAdmin_Account.objects.filter(
            admin_email=super_admin_email, admin_password=super_admin_password
        ).exists():
            # return render(request, "createaccount.html")
            return render(request, "view_all_account.html",{"myaccount":myaccount,"max_warehouses":max_warehouses.max_warehouses,'date':max_warehouses.date})
        else:
            return render(request, "log_in.html")

# -------------------------------------------------------------------
def update_max_warehouses(request):
    if request.method=='POST':
        new_max_warehouses=request.POST['new_max_warehouses']
        myaccount = Admin_Account.objects.all().values()
        for i in myaccount:
            myaccount.update(max_warehouses=int(new_max_warehouses))
        max_warehouses=Admin_Account.objects.filter().first()
        return render(request,'view_all_account.html',{"myaccount": myaccount,'max_warehouses':max_warehouses.max_warehouses,'date':max_warehouses.date})

    
# -------------------------------------------------------------------
def update_date(request):
    if request.method=='POST':
        new_date=request.POST['new_date']
        myaccount = Admin_Account.objects.all().values()
        for i in myaccount:
            myaccount.update(date=new_date)
        # date=Admin_Account.objects.filter().first()
        max_warehouses=Admin_Account.objects.filter().first()

        return render(request,'view_all_account.html',{"myaccount": myaccount,'max_warehouses':max_warehouses.max_warehouses,"date":max_warehouses.date})
# -------------------------------------------------------------------
def error_page(request):
    return render(request,'error_page.html')
# -------------------------------------------------------------------

def log_in_as(request):  # واجهة الموقع الاولى
    template = loader.get_template("log_in_as.html")
    return HttpResponse(template.render())


# --------------------------------------------------
def view_sign_in_employee(request):
    template = loader.get_template("sign_in_employee.html")
    return HttpResponse(template.render())

# -------------------------------------------------------------------

def sign_in_employee(request):  # login (email) for employee
    if request.method == "POST":
        emp_email = request.POST["employee_email"]
        x = Admin_Account(employee_email=emp_email)
        if Admin_Account.objects.filter(employee_email=emp_email).exists():
            emp_account = Admin_Account.objects.get(employee_email=emp_email)
            today = datetime.now().date()
            one_year_ago = today - timedelta(days=365)

            if emp_account.date <= one_year_ago:
                # مشان اذا خلصت مدة العقد
                return render(request, "lock.html")
            # return redirect('employee_code.html')
            return render(request, "employee_code.html")

        else:
            return render(request, "log_in_as.html")


# ---------------------------------------------
def employee_code(request):  # login check(code) for employee
    if request.method == "POST":
        emp_code = request.POST["employee_code"]
        print(emp_code)
        print(emp_code)
        print(emp_code)
        print(emp_code)
        y = "1111"
        x = str(y + "" + emp_code)
        print(int(x + "" + emp_code))
        print(int(x))
        email=request.POST['email']
        print(email)
        print(email)
        print(email)
        print(email)
        if Employee.objects.filter(code=int(x)).exists():
            myemployee = Employee.objects.get(code=int(x))
            employee_code = myemployee.code
            store_id = myemployee.warehouse_id
            story_name = Warehouse.objects.get(warehouse_name=store_id)  
            store_name = Warehouse.objects.get(warehouse_name=store_id).id  
            sections = Section.objects.filter(warehouse_id=store_id)
            mymaterials = Material.objects.filter(warehouse_id=store_id)

            search_field = request.POST.get("search_field", "material_name")
            search_value = request.POST.get("search_value", "-1")
            valid_fields = [f.name for f in Material._meta.get_fields()]
            if search_field not in valid_fields:
                search_field = ""
            filtered_materials = mymaterials.filter(
                **{search_field + "__icontains": search_value}
            )

            # if emp_code=='9999':
            #     # return render(request,'index.html',{'mymaterial':mymaterial ,'story_name':story_name,'filtered_materials': filtered_materials,'warehouse_name':warehouse_name})

            #     return render(request, 'employee_manager.html', { 'filtered_materials':filtered_materials,'store_name': store_name,'warehouse_name':store_name,'mymaterials': mymaterials,'story_name' : story_name,'store_id':store_id,'employee_code':employee_code})
            # admin_account=Admin_Account.objects.get(admin_email='sultan.jarkas1221@gmail.com').date

            employee_account_date=Admin_Account.objects.get(employee_email=email).date
            # x=datetime(2023,12,11)
            x=datetime.combine(employee_account_date,datetime.min.time())
            y=datetime.now()
            d=x-y
            if d.days>10:
                clas='timer1'
            if d.days<10:
                clas='timer2'
            # print(admin_account)
            # now=datetime.now()
            # y=admin_account.strftime("%Y-%m-%d")
            # x=now.strftime("%Y-%m-%d")
            # # print(now)
            # print(x)
            # print(y)
            # c=admin_account-now
            # print(c.days)
            # print(y-x)
            # d=admin_account - now
            # print(d.days)
            return render(
                request,
                "employee_manager.html",
                {
                    "store_name": store_name,
                    "mymaterial": mymaterials,
                    "story_name": story_name,
                    "store_id": store_id,'email':email,'filtered_materials':filtered_materials,
                    "employee_code": emp_code,'employee_account_date':employee_account_date,"clas":clas,
                    # "employee_code":employee_code
                },
            )
            # else:
            #     return render(request, 'employee_code.html')
        else:
            if Employee.objects.filter(code=emp_code).exists():
                myemployee = Employee.objects.get(code=emp_code)
                employee_code = myemployee.code
                print(employee_code)

                store_id = myemployee.warehouse_id
                print(store_id)
                story_name = Warehouse.objects.get(
                    warehouse_name=store_id
                )  # اسم المستودع
                store_name = Warehouse.objects.get(
                    warehouse_name=store_id
                ).id  # idالمستودع
                sections = Section.objects.filter(warehouse_id=store_id)
                # section_ids = sections.values_list('id', flat=True)

                # mymaterials = Material.objects.filter(section_id__in=section_ids)
                mymaterials = Material.objects.filter(warehouse_id=store_id)

                # today_start=timezone.now().replace(hour=0,minute=0,second=0,microsecond=0)
                # today_end = today_start + timezone.timedelta(days=1)
                # employee=Employee.objects.get(code=emp_code)

                # if not Attendance.objects.filter(employee=employee,login_time__range=(today_start, today_end)).exists():
                #     Attendance.objects.create(employee=employee).save()
                # Attendance.objects.create(employee=employee)
                return render(
                    request,
                    "home_page_employee.html",
                    {
                        "store_name": store_name,
                        "mymaterials": mymaterials,
                        "story_name": story_name,
                        "store_id": store_id,
                        # "employee_code": employee_code,
                        "employee_code": emp_code,
                    },
                )

            return render(request, "employee_code.html")

    return render(request,'lock.html')
# def view_home_page_employee(request):
#     template=loader.get_template("home_page_employee.html")
#     return HttpResponse(template.render())

# -------------------------------------------------------------------

def delete_employee(request):
    if request.method == "POST":
        admin_account_date=request.POST['admin_account_date']

        warehouse_id = request.POST["warehouse_id"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        myemployee = Employee.objects.filter(warehouse_id=warehouse_name)
        template = loader.get_template("delete_emp.html")
        context = {"myemployee": myemployee, "warehouse_id": warehouse_id,'admin_account_date':admin_account_date}
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        return render(request, "delete_emp.html", context)
        # return HttpResponse(template.render(context,request))

# ----------------------------------------------------

def delete(request):
    # myemployee = Employee.objects.all().values()
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]
        admin_account_date=request.POST['admin_account_date']

        id_delete = request.POST["id_delete"]
        object_delete = Employee.objects.get(id=id_delete)
        if id_delete:
            object_delete.delete()
            # myemployee = Employee.objects.all().values()
            myemployee = Employee.objects.filter(warehouse_id=warehouse_id)

        # return render(request, "delete_emp.html", {'myemployee': myemployee})
        # return redirect(delete_employee)
        return render(
            request,
            "delete_emp.html",
            {"myemployee": myemployee, "warehouse_id": warehouse_id,"admin_account_date":admin_account_date},
        )

    else:
        myemployee = Employee.objects.filter(warehouse_id=warehouse_id)

        # myemployee = Employee.objects.all().values()
        return render(
            request,
            "delete_emp.html",
            {"myemployee": myemployee, "warehouse_id": warehouse_id,"admin_account_date":admin_account_date},
        )
    # return render(request, "delete_emp.html", {'myemployee': myemployee})

# -----------------------------------------------------

def show_emp(request):
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        myemployee = Employee.objects.filter(warehouse_id=warehouse_name).values()
        template = loader.get_template("show_emp.html")
        context = {"myemployee": myemployee, "warehouse_id": warehouse_id}
        return HttpResponse(template.render(context, request))

# -----------------------------------------------------

def view_all_account(request):
    myaccount = Admin_Account.objects.all().values()
    max_warehouses=Admin_Account.objects.filter().first()
    template = loader.get_template("view_all_account.html")
    context = {
        "myaccount": myaccount,
        'max_warehouses':max_warehouses.max_warehouses,
        'date':max_warehouses.date,
    }
    return HttpResponse(template.render(context, request))

# ---------------------------------------------

def taking_out_material(request):
    admin_account_date=request.POST['admin_account_date']

    warehouse_id = request.POST["warehouse_id"]
    mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
    story_name = Warehouse.objects.get(id=warehouse_id)

    bm = Bill.objects.filter(warehouse_id=warehouse_id)
    # bm=Bill.objects.all().values().material_name
    search_field = request.POST.get("search_field", "material_name")
    search_value = request.POST.get("search_value", "-1")
    valid_fields = [f.name for f in Material._meta.get_fields()]
    if search_field not in valid_fields:
        search_field = ""
    filtered_materials = mymaterial.filter(
        **{search_field + "__icontains": search_value}
    )
    from_sections = Section.objects.filter(warehouse_id=warehouse_id)

    return render(
        request,
        "taking_out_material.html",
        {
            "warehouse_id": warehouse_id,
            "mymaterial": mymaterial,
            "filtered_materials": filtered_materials,
            "story_name": story_name,
            "bm": bm,
            "from_sections":from_sections,"admin_account_date":admin_account_date
        },
    )

# ------------------------------------------------------

def add_to_bill(request):
    if request.method == "POST":
        # bm=Bill.objects.all().values()
        admin_account_date=request.POST['admin_account_date']

        warehouse_id = request.POST["warehouse_id"]
        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)
        date = request.POST.get("date", "2023-11-05")
        print(date)
        date1 = datetime.strptime(date, "%Y-%m-%d")
        x = date1.strftime("%Y-%m-%d")
        print(date1)
        print(x)

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        story_name = Warehouse.objects.get(id=warehouse_id)
        bm = Bill.objects.filter(warehouse_id=story_name)
        material_name = request.POST["material_name"]
        count = request.POST["count"]
        # --------------------
        if material_name:
            if count:
                if shelf_number:
                    if count_type:
                        if date:
                            for i in mymaterial:
                                # if material_name == i.material_name and count_type == i.count_type and int(shelf_number) == int(i.shelf_number) and str(date1) == str(i.date)+' 00:00:00':
                                if (
                                    material_name == i.material_name
                                    and count_type == i.count_type
                                    and int(shelf_number) == int(i.shelf_number)
                                    and str(x) == str(i.date)
                                    
                                ):
                                    if int(count) <= int(i.count):
                                        i.count = int(i.count) - int(count)
                                        my = Material.objects.filter(material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
                                        my.update(count=int(i.count))

                                        # i.count.update(count=z)
                                        # if int(i.count)==0:
                                        #     i.delete()
                                        x = Bill(
                                            material_name=material_name,
                                            count=count,
                                            warehouse_id=story_name,
                                        )
                                        x.save()
                                # --------------------

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                "count_type":count_type,
                "shelf_number":shelf_number,
                "date":date,
                "from_section":from_section,
                "from_sections":from_sections,"admin_account_date":admin_account_date
            },
        )

# ------------------------------------------------------

def out_bill(request):
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]  # id
        admin_account_date=request.POST['admin_account_date']

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)  # object
        bm = Bill.objects.filter(warehouse_id=warehouse_id)

        from_sections = Section.objects.filter(warehouse_id=warehouse_id)

        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        # --------------------

        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        # اول الشي بدي انشئ اوبجكت من جدول الbill_details
        code = 2
        creat_bill_details = Bill_Details(code=code)
        creat_bill_details.save()

        # تاني شي بدي جيب كل المواد الموجودة بجدولBill
        all_bill = Bill.objects.filter(warehouse_id=warehouse_id)
        # جبت id  تبع الاوبجكت يلي انشأته
        id_bill = creat_bill_details.id
        print(id_bill)

        for i in all_bill:
            bill_final = Bill_final(
                material_name=i.material_name,
                count=i.count,
                bill_details_id=id_bill,
                warehouse_id=warehouse_name,
                code=creat_bill_details.code,
                date=creat_bill_details.date,
            )
            bill_final.save()
            i.delete()

        creat_bill_details.delete()
        return render(
            request,
            "taking_out_material.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                "warehouse_id":warehouse_id,
                "from_sections":from_sections,'admin_account_date':admin_account_date
            },
        )

# -------------------------------------------------------------------

def delete_from_bill(request):
    if request.method == "POST":
        admin_account_date=request.POST['admin_account_date']

        warehouse_id = request.POST["warehouse_id"]
        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        date = request.POST.get("date", "2023-11-05")
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)
        # -------------------
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # bm=Bill.objects.all().values().material_name
        # -------------------
        # for i in bm:
        #     material_name=Material.objects.get(warehouse_id=warehouse_id,material_name=i.material_name)
        #     if material_name == i.material_name:
        #         material_name.count=int(material_name.count)+int(i.count)

        #         material_name.update(count=int(material_name.count))

        # -------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # -------------------
        id_delete = request.POST["id_delete"]
        object_delete = Bill.objects.get(id=id_delete)

        material_name = object_delete.material_name

        # my = Material.objects.filter(material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)

        material_namef = Material.objects.filter(warehouse_id=warehouse_id, material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
        for x in material_namef:
            x.count = int(x.count) + int(object_delete.count)
            material_namef.update(count=int(x.count))
            # -------------------

        if id_delete:
            object_delete.delete()
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,'from_sections':from_sections,
                'admin_account_date':admin_account_date
            },
        )

# -------------------------------------------------------------------

def delete_warehouse(request):
    Mywarehouses = Warehouse.objects.all()

    warehouse_id = request.POST["warehouse_name"]
    x = Warehouse.objects.get(id=warehouse_id)
    if Material.objects.filter(warehouse_id=warehouse_id).exists():
        result = "Sorry, there are material that cannot be deleted the warehouse"

    else:
        x.delete()
        result = ""
    return render(request, "XX.html", {"Mywarehouses": Mywarehouses, "result": result})

# ------------------------------------------------------

def all_bills(request):
    if request.method == "POST":
        admin_account_date=request.POST['admin_account_date']

        warehouse_id = request.POST["warehouse_id"]
        all_bills = (
            Bill_final.objects.filter(warehouse_id=warehouse_id)
            .values("bill_details_id")
            .distinct()
        )
        # al=Bill_final.objects.filter(warehouse_id=warehouse_id).values
        d1 = request.POST.get("d1", "2029-10-01")
        d2 = request.POST.get("d2", "2025-11-01")
        date1 = datetime.strptime(d1, "%Y-%m-%d")
        # date1 = datetime.strptime(d1, "%Y-%m-%d")
        date2 = datetime.strptime(d2, "%Y-%m-%d")
        print(d1)
        print(d2)
        filtered = (
            Bill_final.objects.filter(
                date__range=[date1, date2], warehouse_id=warehouse_id
            )
            .values("bill_details_id")
            .distinct()
        )

        return render(
            request,
            "all_bills.html",
            {
                "filtered": filtered,
                "warehouse_id": warehouse_id,
                "all_bills": all_bills,'admin_account_date':admin_account_date
            },
        )

# -------------------------------------------------------------------

def bill_details(request):
    id_bill = request.POST["id_bill"]
    employee_code=request.POST['employee_code']
    admin_account_date=request.POST.get('admin_account_date','15')
    employee_account_date=request.POST.get('employee_account_date','15')
    warehouse_id = request.POST["warehouse_id"]
    warehouse_name = Warehouse.objects.get(id=warehouse_id)
    # y = "1111"
    # x = str(y + "" + employee_code)
    bill_finals = Bill_final.objects.filter(bill_details_id=id_bill)
    bill_date = (
        Bill_final.objects.filter(bill_details_id=id_bill, warehouse_id=warehouse_id)
        .values("date")
        .distinct()
    )
    bill_employee_code = (
        Bill_final.objects.filter(bill_details_id=id_bill, warehouse_id=warehouse_id)
        .values("code")
        .distinct()
    )
    return render(
        request,
        "bill_details.html",
        {
            "bill_finals": bill_finals,
            "id_bill": id_bill,
            "warehouse_id": warehouse_name,
            "bill_date": bill_date,'employee_account_date':employee_account_date,"employee_code":employee_code,"bill_employee_code":bill_employee_code
        },
    )

# -------------------------------------------------------------------

from reportlab.lib.pagesizes import letter, legal
from reportlab.rl_config import defaultPageSize
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import os


# def generate_files(request):
#     id_bill = request.POST["id_bill"]
#     warehouse_id = request.POST["warehouse_id"]
#     bill_finals = Bill_final.objects.filter(bill_details_id=id_bill)
#     # -------------------

#     doc = SimpleDocTemplate(
#         os.path.expanduser("~/Desktop/bill_details.pdf"), pagesize=letter)
#     styles = getSampleStyleSheet()
#     data = [
#         [
#             "                      Material Name                      ",
#             "                      Count                      ",
#         ]
#     ]
#     for bill_final in bill_finals:
#         data.append([bill_final.material_name, bill_final.count])

#     table = Table(data)
#     style = TableStyle(
#         [
#             ("BACKGROUND", (0, 0), (-1, 0), colors.blue),
#             ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
#             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
#             ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
#             ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
#             ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
#             ("GRID", (0, 0), (-1, -1), 1, colors.black),
#         ]
#     )
#     table.setStyle(style)

#     elements = [table]
#     doc.build(elements)
#     warehouse_name = Warehouse.objects.get(warehouse_name=warehouse_id)
#     bill_finals = Bill_final.objects.filter(bill_details_id=id_bill)
#     return render(
#         request,
#         "bill_details.html",
#         {
#             "bill_finals": bill_finals,
#             "id_bill": id_bill,
#             "warehouse_id": warehouse_name,
#         },
#     )


def generate_files(request):
    id_bill = request.POST["id_bill"]
    warehouse_id = request.POST["warehouse_id"]
    bill_finals = Bill_final.objects.filter(bill_details_id=id_bill)

    doc = SimpleDocTemplate(
        os.path.expanduser("~/Desktop/bill_details.pdf"),
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=30,
        bottomMargin=30,
    )

    styles = getSampleStyleSheet()
    data = [
        [
            "                      Material Name                      ",
            "                      Count                      ",
        ]
    ]
    for bill_final in bill_finals:
        data.append([bill_final.material_name, bill_final.count])
        

    table = Table(data, colWidths=[doc.width / len(data[0])] * len(data[0]))

    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.blue),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
    table.setStyle(style)

    elements = [table]
    doc.build(elements)

    # warehouse_name = Warehouse.objects.get(warehouse_name=warehouse_id)
    # bill_finals = Bill_final.objects.filter(bill_details_id=id_bill)

    return render(
        request,
        "bill_details.html",
        {
            # "bill_finals": bill_finals,
            "id_bill": id_bill,
            # "warehouse_id": warehouse_name,
        },
    )

# -------------------------------------------------------------------

# def generate_rebort(request):
#     warehouse_id=request.POST["warehouse_id"]
#     admin_account_date = request.POST["admin_account_date"]

#     warehouse = Warehouse.objects.get(id=warehouse_id)
#     material_count = Material.objects.filter(warehouse_id=warehouse_id).count()
#     today_materials = Material.objects.filter(warehouse_id=warehouse_id, date=date.today())
#     # all_section=Section.objects.all()
#     # for i in all_section:
#     #     empty_section=Material.objects.filter(warehouse_id=warehouse_id,section_id=i)
#     #     if empty_section.material_name:
#     #         print(empty_section.material_name)
#     #     else:
#     #         print('not empty')
#     last_added_material = Material.objects.filter(warehouse_id=warehouse_id).order_by('-id').first()

#     # report_content = "Warehouse Report for {warehouse.warehouse_name}\n\n"
#     # report_content += f"Total number of materials in the warehouse: {material_count}\n\n"
    
#     # if last_added_material:
#     #     report_content += "Details of the last added material:\n"
#     #     report_content += f"Material Name: {last_added_material.material_name}\n"
#     #     report_content += f"Count: {last_added_material.count}\n"
#     #     report_content += f"Count Type: {last_added_material.count_type}\n"
#     #     report_content += f"Date: {last_added_material.date}\n"
#     #     report_content += f"Description: {last_added_material.description}\n"
#     #     report_content += f"Shelf Number: {last_added_material.shelf_number}\n"
#     # else:
#     #     report_content += "No materiales have been added to the warehouse.\n"
    

#     report_content = "Warehouse Report for ["+warehouse.warehouse_name+"\n\n"
#     report_content += "Total number of materials in the warehouse: "+str(material_count)+"\n\n"
#     if today_materials.exists():
#         report_content += "Details of materials added today:\n"
#         for material in today_materials:
#             report_content += f"Material Name: {material.material_name}\n"
#             report_content += f"Count: {material.count}\n"
#             report_content += f"Count Type: {material.count_type}\n"
#             report_content += f"Date: {material.date}\n"
#             report_content += f"Description: {material.description}\n"
#             report_content += f"Shelf Number: {material.shelf_number}\n\n"
#     else:
#         report_content += "No materials have been added today.\n"

#     if last_added_material:
#         report_content += "Details of the last added material:\n"
#         report_content += "Material Name: "+last_added_material.material_name+"\n"
#         report_content += "Count: "+str(last_added_material.count)+"\n"
#         report_content += "Count Type: "+last_added_material.count_type+"\n"
#         report_content += "Date: "+str(last_added_material.date)+"\n"
#         report_content += "Description: "+last_added_material.description+"\n"
#         report_content += "Shelf Number: "+str(last_added_material.shelf_number)+"\n"
#     else:
#         report_content += "No materiales have been added to the warehouse.\n"

#     file_path = os.path.expanduser("~/Desktop/warehouse_report.txt")
#     with open(file_path, 'w') as file:
#         file.write(report_content)
#     Mywarehouses = Warehouse.objects.all()
#     return render(request, "XX.html", {"Mywarehouses": Mywarehouses,"admin_account_date":admin_account_date})


def generate_rebort(request):
    warehouse_id = request.POST["warehouse_id"]
    admin_account_date = request.POST["admin_account_date"]

    warehouse = Warehouse.objects.get(id=warehouse_id)
    material_count = Material.objects.filter(warehouse_id=warehouse_id).count()

    
    today_materials = Material.objects.filter(warehouse_id=warehouse_id, date=date.today())

    last_added_material = Material.objects.filter(warehouse_id=warehouse_id).order_by('-id').first()

    report_content = f"Warehouse Report for {warehouse.warehouse_name}\n\n"
    report_content += f"Total number of materials in the warehouse: {material_count}\n\n"

    if today_materials.exists():
        report_content += "Details of materials added today:\n"
        for material in today_materials:
            report_content += f"Material Name: {material.material_name}\n"
            report_content += f"Count: {material.count}\n"
            report_content += f"Count Type: {material.count_type}\n"
            report_content += f"Date: {material.date}\n"
            report_content += f"Description: {material.description}\n"
            report_content += f"Shelf Number: {material.shelf_number}\n\n"
    else:
        report_content += "No materials have been added today.\n\n"

    if last_added_material:
        report_content += "Details of the last added material:\n"
        report_content += f"Material Name: {last_added_material.material_name}\n"
        report_content += f"Count: {last_added_material.count}\n"
        report_content += f"Count Type: {last_added_material.count_type}\n"
        report_content += f"Date: {last_added_material.date}\n"
        report_content += f"Description: {last_added_material.description}\n"
        report_content += f"Shelf Number: {last_added_material.shelf_number}\n"
    else:
        report_content += "No materials have been added to the warehouse.\n"

    file_path = os.path.expanduser("~/Desktop/warehouse_report.txt")
    with open(file_path, 'w') as file:
        file.write(report_content)

    Mywarehouses = Warehouse.objects.all()
    return render(request, "XX.html", {"Mywarehouses": Mywarehouses, "admin_account_date": admin_account_date})
# -------------------------------------------------------------------

def view_add_section(request):
    result = ""
    admin_account_date=request.POST['admin_account_date']

    warehouse_name = request.POST["warehouse_id"]
    print(warehouse_name)

    return render(
        request, "add_section.html", {"warehouse_id": warehouse_name, "result": result,"admin_account_date":admin_account_date}
    )


# ------------------------------------------------------

def add_section(request):
    if request.method == "POST":
        result = ""
        admin_account_date=request.POST['admin_account_date']

        warehouse_name = request.POST["warehouse_id"]
        warehouse = Warehouse.objects.get(id=warehouse_name)
        section_name = request.POST["section_name"]
        # number_of_shelf = request.POST["number_of_shelf"]

        x = Section(
            section_name=section_name,
            # number_of_shelf=number_of_shelf,
            warehouse_id=warehouse,
        )
        if Section.objects.filter(
            section_name=section_name, warehouse_id=warehouse
        ).exists():
            result = "Sorry, already added"
            return render(
                request,
                "add_section.html",
                {"warehouse_id": warehouse_name, "result": result,"admin_account_date":admin_account_date},
            )
        else:
            result = "Added successfuly"
            x.save()
            # return redirect(view_add_section)
            # return render(request,'add_section.html',{'warehouse_id':warehouse,'result':result})
            return render(
                request,
                "add_section.html",
                {"warehouse_id": warehouse_name, "result": result,"admin_account_date":admin_account_date},
            )

# -------------------------------------------------------------------

def taking_out_material_employee(request):
    result = ""
    warehouse_id = request.POST["warehouse_id"]
    employee_code = request.POST["employee_code"]
    print(employee_code)
    mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
    story_name = Warehouse.objects.get(id=warehouse_id)

    bm = Bill.objects.filter(warehouse_id=warehouse_id)
    # bm=Bill.objects.all().values().material_name
    search_field = request.POST.get("search_field", "material_name")
    search_value = request.POST.get("search_value", "-1")
    valid_fields = [f.name for f in Material._meta.get_fields()]
    if search_field not in valid_fields:
        search_field = ""
    filtered_materials = mymaterial.filter(
        **{search_field + "__icontains": search_value}
    )
    from_sections = Section.objects.filter(warehouse_id=warehouse_id)

    return render(
        request,
        "taking_out_material_employee.html",
        {
            "warehouse_id": warehouse_id,
            "mymaterial": mymaterial,
            "filtered_materials": filtered_materials,
            "story_name": story_name,
            "bm": bm,
            "employee_code": employee_code,
            "result": result,
            "from_sections":from_sections

        },
    )

# ------------------------------------------------------

def add_to_bill_employee(request):
    if request.method == "POST":
        # bm=Bill.objects.all().values()
        warehouse_id = request.POST["warehouse_id"]
        employee_code = request.POST["employee_code"]
        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)
        date = request.POST.get("date", "2023-11-05")
        print(date)
        date1 = datetime.strptime(date, "%Y-%m-%d")
        x = date1.strftime("%Y-%m-%d")
        print(date1)
        print(x)
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        story_name = Warehouse.objects.get(id=warehouse_id)
        bm = Bill.objects.filter(warehouse_id=story_name)
        material_name = request.POST["material_name"]
        count = request.POST["count"]
        # --------------------
        if material_name:
            if count:
                if shelf_number:
                    if count_type:
                        if date:
                            for i in mymaterial:
                                # if material_name == i.material_name and count_type == i.count_type and int(shelf_number) == int(i.shelf_number) and str(date1) == str(i.date)+' 00:00:00':
                                if (
                                    material_name == i.material_name
                                    and count_type == i.count_type
                                    and int(shelf_number) == int(i.shelf_number)
                                    and str(x) == str(i.date)
                                    
                                ):
                                    if int(count) <= int(i.count):
                                        i.count = int(i.count) - int(count)
                                        my = Material.objects.filter(material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
                                        my.update(count=int(i.count))

                                        # i.count.update(count=z)
                                        # if int(i.count)==0:
                                        #     i.delete()
                                        x = Bill(
                                            material_name=material_name,
                                            count=count,
                                            warehouse_id=story_name,
                                            
                                        )
                                        x.save()

                    # --------------------

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material_employee.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                'from_sections':from_sections,
                "count_type":count_type,
                "shelf_number":shelf_number,
                "date":date,
                "from_section":from_section,
                "employee_code": employee_code,
            },
        )

# ------------------------------------------------------

def out_bill_employee(request):
    if request.method == "POST":
        result = ""
        warehouse_id = request.POST["warehouse_id"]  # id
        employee_code = request.POST["employee_code"]
        print(employee_code)
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)  # object
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)

        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        # --------------------

        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        # اول الشي بدي انشئ اوبجكت من جدول الbill_details

        creat_bill_details = Bill_Details(code=employee_code)
        creat_bill_details.save()

        # تاني شي بدي جيب كل المواد الموجودة بجدولBill
        all_bill = Bill.objects.filter(warehouse_id=warehouse_id)
        # جبت id  تبع الاوبجكت يلي انشأته
        id_bill = creat_bill_details.id
        print(id_bill)

        for i in all_bill:
            bill_final = Bill_final(
                material_name=i.material_name,
                count=i.count,
                bill_details_id=id_bill,
                warehouse_id=warehouse_name,
                code=employee_code,
                date=creat_bill_details.date,
            )
            bill_final.save()
            i.delete()

        creat_bill_details.delete()
        return render(
            request,
            "taking_out_material_employee.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                "employee_code": employee_code,
                "result": result,
                "from_sections":from_sections

            },
        )

# -------------------------------------------------------------------

def delete_from_bill_employee(request):
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]
        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        date = request.POST.get("date", "2023-11-05")
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)
        
        print(date)
        employee_code = request.POST["employee_code"]

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)
        # -------------------
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # bm=Bill.objects.all().values().material_name
        # -------------------
        # for i in bm:
        #     material_name=Material.objects.get(warehouse_id=warehouse_id,material_name=i.material_name)
        #     if material_name == i.material_name:
        #         material_name.count=int(material_name.count)+int(i.count)

        #         material_name.update(count=int(material_name.count))

        # -------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # -------------------
        id_delete = request.POST["id_delete"]
        object_delete = Bill.objects.get(id=id_delete)

        material_name = object_delete.material_name
        material_namef = Material.objects.filter(warehouse_id=warehouse_id, material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
        for x in material_namef:
            x.count = int(x.count) + int(object_delete.count)
            material_namef.update(count=int(x.count))
            # -------------------

        if id_delete:
            object_delete.delete()
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material_employee.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                "employee_code": employee_code,
                'from_sections':from_sections
            },
        )
    # --------------------------------------------------------------------------------
    # manager

# -------------------------------------------------------------------

def add_employee_manager(request):
    warehouse_name = request.POST["warehouse_name"]
    employee_account_date=request.POST['employee_account_date']
    print(warehouse_name)
    result = ""
    clas = "form-control"
    return render(
        request,
        "add_employee_manager.html",
        {"result": result, "warehouse_name": warehouse_name, "clas": clas,'employee_account_date':employee_account_date},
    )

    # template=loader.get_template('add_employee.html')
    # return HttpResponse(template.render(),)

# -------------------------------------------------------------------

def add_manager(request):
    if request.method == "POST":
        result = ""
        clas = "form-control"
        employee_account_date=request.POST['employee_account_date']
        warehouse_id = request.POST["warehouse_name"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        name = request.POST["empname"]
        phone = request.POST["empphone"]
        code = request.POST["empcode"]
        x = Employee(name=name, phone=phone, code=code, warehouse_id=warehouse_name)
        if Employee.objects.filter(phone=phone, code=code).exists():
            result = "already added"
            clas = "form-control is-invalid"
            print("done")
        else:
            result = "seccuss"
            x.save()
        return render(
            request,
            "add_employee_manager.html",
            {"result": result, "warehouse_name": warehouse_id, "clas": clas,'employee_account_date':employee_account_date},
        )

# -------------------------------------------------------------------

def delete_employee_manager(request):
    if request.method == "POST":
        employee_account_date=request.POST['employee_account_date']
        warehouse_id = request.POST["warehouse_id"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        myemployee = Employee.objects.filter(warehouse_id=warehouse_name)
        template = loader.get_template("delete_emp_manager.html")
        context = {"myemployee": myemployee, "warehouse_id": warehouse_id,"employee_account_date":employee_account_date}
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        return render(request, "delete_emp_manager.html", context)
        # return HttpResponse(template.render(context,request))

# ----------------------------------------------------

def delete_manager(request):
    # myemployee = Employee.objects.all().values()
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]
        id_delete = request.POST["id_delete"]
        employee_account_date=request.POST['employee_account_date']
        object_delete = Employee.objects.get(id=id_delete)
        if id_delete:
            object_delete.delete()
            # myemployee = Employee.objects.all().values()
            myemployee = Employee.objects.filter(warehouse_id=warehouse_id)

        # return render(request, "delete_emp.html", {'myemployee': myemployee})
        # return redirect(delete_employee)
        return render(
            request,
            "delete_emp_manager.html",
            {"myemployee": myemployee, "warehouse_id": warehouse_id,'employee_account_date':employee_account_date},
        )

    else:
        myemployee = Employee.objects.filter(warehouse_id=warehouse_id)

        # myemployee = Employee.objects.all().values()
        return render(
            request,
            "delete_emp_manager.html",
            {"myemployee": myemployee, "warehouse_id": warehouse_id,'employee_account_date':employee_account_date},
        )
    # return render(request, "delete_emp.html", {'myemployee': myemployee})

# -----------------------------------------------------

def add_material_manager(request):
    result = ""
    employee_account_date=request.POST['employee_account_date']

    warehouse_name = request.POST["warehouse_id"]
    employee_code = request.POST["employee_code"]
    print(warehouse_name)
    print(warehouse_name)
    print(warehouse_name)
    print(warehouse_name)

    warehouse_id = Warehouse.objects.get(id=warehouse_name)
    print(warehouse_id)

    sections = Section.objects.filter(warehouse_id=warehouse_id)
    context = {
        "warehouse_id": warehouse_name,
        # "section_names": section_names,
        "sections": sections,
        "result": result,
        "employee_code": employee_code,
        'employee_account_date':employee_account_date
    }
    return render(request, "add_material_manager.html", context)

# ------------------------------------------------------------------------------

def add_material_proces_manager(request):
    if request.method == "POST":
        result = ""
        employee_account_date=request.POST['employee_account_date']
        warehouse_id = request.POST["warehouse_id"]
        warehouse_name = Warehouse.objects.get(id=warehouse_id)

        print(warehouse_name)
        print(warehouse_name)
        print(warehouse_name)
        print(warehouse_name)
        print(warehouse_name)

        mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
        story_name = Warehouse.objects.get(id=warehouse_id)
        ww = story_name.id

        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )

        material_name = request.POST.get("material_name", "")
        count = request.POST.get("count", "")
        count_type = request.POST.get("count_type", "")
        date = request.POST.get("date", "")
        section_id = request.POST.get("section", "")
        shelf_number = request.POST.get("shelf_number", "")
        description = request.POST.get("description", "")
        warehouse_id = request.POST.get("warehouse_id", "")

        if (
            material_name
            and count
            and count_type
            and date
            and section_id
            and shelf_number
            and description
            and warehouse_id
        ):
            try:
                section_id = int(section_id)
                warehouse_id = int(warehouse_id)

                warehouse = Warehouse.objects.get(id=warehouse_id)
                section = Section.objects.get(id=section_id)

                x = Material(
                    material_name=material_name,
                    count=count,
                    count_type=count_type,
                    date=date,
                    description=description,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )

                # if Material.objects.filter(
                #     material_name=material_name,
                #     count=count,
                #     count_type=count_type,
                #     date=date,
                #     description=description,
                #     shelf_number=shelf_number,
                #     warehouse_id=warehouse,
                #     section_id=section).exists():
                z = Material.objects.filter(
                    material_name=material_name,
                    count_type=count_type,
                    shelf_number=shelf_number,
                    warehouse_id=warehouse,
                    section_id=section,
                )

                if z.exists():
                    for i in z:
                        s = int(i.count) + int(count)
                        z.update(count=s)

                else:
                    result = "success"
                    print(result)

                    x.save()
            except ValueError:
                result = "Erorr in section or warehouse ID"
                print(result)

            mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
            return render(
                request,
                "employee_manager.html",
                {
                    "result": result,
                    "mymaterial": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,'employee_account_date':employee_account_date
                },
            )
        else:
            result = "missing fields"
            mymaterial = Material.objects.filter(warehouse_id=warehouse_name)
            return render(
                request,
                "employee_manager.html",
                {
                    "result": result,
                    "mymaterial": mymaterial,
                    "filtered_materials": filtered_materials,
                    "story_name": story_name,'employee_account_date':employee_account_date
                },
            )

# -------------------------------------------------------------------

def taking_out_material_manager(request):
    result = ""
    employee_account_date=request.POST['employee_account_date']
    warehouse_id = request.POST["warehouse_id"]
    employee_code = request.POST["employee_code"]
    print(employee_code)
    mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
    story_name = Warehouse.objects.get(id=warehouse_id)

    bm = Bill.objects.filter(warehouse_id=warehouse_id)
    # bm=Bill.objects.all().values().material_name
    search_field = request.POST.get("search_field", "material_name")
    search_value = request.POST.get("search_value", "-1")
    valid_fields = [f.name for f in Material._meta.get_fields()]
    if search_field not in valid_fields:
        search_field = ""
    filtered_materials = mymaterial.filter(
        **{search_field + "__icontains": search_value}
    )
    from_sections = Section.objects.filter(warehouse_id=warehouse_id)

    return render(
        request,
        "taking_out_material_manager.html",
        {
            "warehouse_id": warehouse_id,
            "mymaterial": mymaterial,
            "filtered_materials": filtered_materials,
            "story_name": story_name,
            "bm": bm,
            "employee_code": employee_code,
            "result": result,'from_sections':from_sections,"employee_account_date":employee_account_date
        },
    )

# ------------------------------------------------------

def add_to_bill_manager(request):
    if request.method == "POST":
        # bm=Bill.objects.all().values()
        employee_account_date=request.POST['employee_account_date']

        warehouse_id = request.POST["warehouse_id"]

        employee_code = request.POST["employee_code"]

        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)
        date = request.POST.get("date", "2023-11-05")
        print(date)
        date1 = datetime.strptime(date, "%Y-%m-%d")
        x = date1.strftime("%Y-%m-%d")
        print(date1)
        print(x)
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        story_name = Warehouse.objects.get(id=warehouse_id)
        bm = Bill.objects.filter(warehouse_id=story_name)
        material_name = request.POST["material_name"]
        count = request.POST["count"]
        # --------------------
        if material_name:
            if count:
                for i in mymaterial:
                    # if material_name == i.material_name:
                    if (
                        material_name == i.material_name
                        and count_type == i.count_type
                        and int(shelf_number) == int(i.shelf_number)
                        and str(x) == str(i.date)
                    ):
                        if int(count) <= int(i.count):
                            i.count = int(i.count) - int(count)
                            my = Material.objects.filter(warehouse_id=warehouse_id, material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
                            my.update(count=int(i.count))

                            # i.count.update(count=z)
                            # if int(i.count)==0:
                            #     i.delete()
                            x = Bill(
                                material_name=material_name,
                                count=count,
                                warehouse_id=story_name,
                            )
                            x.save()
                            # result='Added successfuly'

                    # --------------------

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material_manager.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                'from_sections':from_sections,
                "count_type":count_type,
                "shelf_number":shelf_number,
                "date":date,
                "from_section":from_section,
                "employee_code": employee_code,'employee_account_date':employee_account_date
            },
        )

# ------------------------------------------------------

def out_bill_manager(request):
    if request.method == "POST":
        result = ""
        employee_account_date=request.POST['employee_account_date']
        warehouse_id = request.POST["warehouse_id"]  # id
        employee_code = request.POST["employee_code"]
        y = "1111"
        x = str(y + "" + employee_code)
        print(employee_code)
        print(x)
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)  # object
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # --------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # --------------------

        # --------------------

        warehouse_name = Warehouse.objects.get(id=warehouse_id)
        # اول الشي بدي انشئ اوبجكت من جدول الbill_details

        creat_bill_details = Bill_Details(code=x)
        creat_bill_details.save()

        # تاني شي بدي جيب كل المواد الموجودة بجدولBill
        all_bill = Bill.objects.filter(warehouse_id=warehouse_id)
        # جبت id  تبع الاوبجكت يلي انشأته
        id_bill = creat_bill_details.id
        print(id_bill)

        for i in all_bill:
            bill_final = Bill_final(
                material_name=i.material_name,
                count=i.count,
                bill_details_id=id_bill,
                warehouse_id=warehouse_name,
                code=x,
                date=creat_bill_details.date,
            )
            bill_final.save()
            i.delete()

        creat_bill_details.delete()
        return render(
            request,
            "taking_out_material_manager.html",
            {
                "mymaterial": mymaterial,'employee_account_date':employee_account_date,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                "employee_code": employee_code,
                "result": result,
            },
        )

# -------------------------------------------------------------------

def delete_from_bill_manager(request):
    if request.method == "POST":
        admin_account_date=request.POST.get('admin_account_date','15')
        employee_account_date=request.POST.get('employee_account_date','15')
        warehouse_id = request.POST["warehouse_id"]
        shelf_number = request.POST["shelf_number"]
        count_type = request.POST["count_type"]
        from_section = request.POST["from_section"]
        date = request.POST.get("date", "2023-11-05")
        from_sections = Section.objects.filter(warehouse_id=warehouse_id)

        employee_code = request.POST.get("employee_code", False)

        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        story_name = Warehouse.objects.get(id=warehouse_id)
        # -------------------
        bm = Bill.objects.filter(warehouse_id=warehouse_id)
        # bm=Bill.objects.all().values().material_name
        # -------------------
        # for i in bm:
        #     material_name=Material.objects.get(warehouse_id=warehouse_id,material_name=i.material_name)
        #     if material_name == i.material_name:
        #         material_name.count=int(material_name.count)+int(i.count)

        #         material_name.update(count=int(material_name.count))

        # -------------------
        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )
        # -------------------
        id_delete = request.POST["id_delete"]
        object_delete = Bill.objects.get(id=id_delete)

        material_name = object_delete.material_name
        material_namef = Material.objects.filter(warehouse_id=warehouse_id, material_name=material_name,count_type=count_type,shelf_number = shelf_number,date=date,section_id=from_section)
        for x in material_namef:
            x.count = int(x.count) + int(object_delete.count)
            material_namef.update(count=int(x.count))
            # -------------------

        if id_delete:
            object_delete.delete()
        mymaterial = Material.objects.filter(warehouse_id=warehouse_id)
        return render(
            request,
            "taking_out_material_manager.html",
            {
                "mymaterial": mymaterial,
                "filtered_materials": filtered_materials,
                "story_name": story_name,
                "bm": bm,
                'from_sections':from_sections,
                "employee_code": employee_code,"employee_account_date":employee_account_date
            },
        )
    # --------------------------------------------------------------------------------

# -------------------------------------------------------------------

def all_bills_manager(request):
    if request.method == "POST":
        warehouse_id = request.POST["warehouse_id"]
        employee_account_date=request.POST['employee_account_date']
        employee_code=request.POST['employee_code']


        all_bills = (
            Bill_final.objects.filter(warehouse_id=warehouse_id)
            .values("bill_details_id")
            .distinct()
        )
        # al=Bill_final.objects.filter(warehouse_id=warehouse_id).values
        d1 = request.POST.get("d1", "2029-10-01")
        d2 = request.POST.get("d2", "2025-11-01")
        date1 = datetime.strptime(d1, "%Y-%m-%d")
        # date1 = datetime.strptime(d1, "%Y-%m-%d")
        date2 = datetime.strptime(d2, "%Y-%m-%d")
        print(d1)
        print(d2)
        filtered = (
            Bill_final.objects.filter(
                date__range=[date1, date2], warehouse_id=warehouse_id
            )
            .values("bill_details_id")
            .distinct()
        )

        return render(
            request,
            "all_bills_manager.html",
            {
                "filtered": filtered,
                "warehouse_id": warehouse_id,
                "all_bills": all_bills,
                'employee_account_date':employee_account_date,
                "employee_code":employee_code,
            },
        )
    # ----------------------------------------------------------

# -------------------------------------------------------------------

def view_add_section_manager(request):
    result = ""
    warehouse_name = request.POST["warehouse_id"]
    print(warehouse_name)
    employee_account_date=request.POST['employee_account_date']

    return render(
        request,
        "add_section_manager.html",
        {"warehouse_id": warehouse_name,'employee_account_date':employee_account_date, "result": result},
    )

# ------------------------------------------------------

def add_section_manager(request):
    if request.method == "POST":
        result = ""
        employee_account_date=request.POST['employee_account_date']

        warehouse_name = request.POST["warehouse_id"]
        warehouse = Warehouse.objects.get(id=warehouse_name)
        warehouse_id = warehouse.id
        section_name = request.POST["section_name"]
        # number_of_shelf = request.POST["number_of_shelf"]

        x = Section(
            section_name=section_name,
            # number_of_shelf=number_of_shelf,
            warehouse_id=warehouse,
        )
        if Section.objects.filter(
            section_name=section_name, warehouse_id=warehouse
        ).exists():
            result = "Sorry, already added"
            return render(
                request,
                "add_section_manager.html",
                {"warehouse_id": warehouse_id, "result": result,'employee_account_date':employee_account_date},
            )
        else:
            result = "Added successfuly"
            x.save()
            # return redirect(view_add_section)
            # return render(request,'add_section.html',{'warehouse_id':warehouse,'result':result})
            return render(
                request,
                "add_section_manager.html",
                {"warehouse_id": warehouse_name, "result": result,
                'employee_account_date':employee_account_date},
            )

# -------------------------------------------------------------------

def CCC(request):  # التابع المسؤل عن عرض المواد الخاصة بكل مستودع
    if request.method == "POST":
        warehouse_name = request.POST["warehouse_name"]
        employee_account_date=request.POST['employee_account_date']
        print(employee_account_date)
        # employee_code=request.POST['employee_code']

        mymaterial = Material.objects.filter(
            warehouse_id=warehouse_name
        )  # قيمة الwarehouse_id رح تطلع بالداتا بيز هي اسم بس فعليا هي الرقم الخاص ب هالاوبجكت  يعني صاحب الاسم مشان هيك بصفحة html قلتلو warehouse_id موwarehouse_nmae
        story_name = Warehouse.objects.get(id=warehouse_name)

        search_field = request.POST.get("search_field", "material_name")
        search_value = request.POST.get("search_value", "-1")
        valid_fields = [f.name for f in Material._meta.get_fields()]
        if search_field not in valid_fields:
            search_field = ""
        filtered_materials = mymaterial.filter(
            **{search_field + "__icontains": search_value}
        )

        return render(
            request,
            "employee_manager.html",
            {
                "mymaterial": mymaterial,
                "story_name": story_name,
                "filtered_materials": filtered_materials,
                "warehouse_name": warehouse_name,
                "employee_code": employee_code,
                'employee_account_date':employee_account_date,
                'clas':'timer1'
            },
        )

# -------------------------------------------------------------------

