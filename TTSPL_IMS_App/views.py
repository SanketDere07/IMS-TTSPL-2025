from django.shortcuts import render,get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from django.shortcuts import render, redirect
import random
import string
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import os
from django.db.models import Max
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
import re
import shutil
from django.core.files.storage import default_storage
from django.db.models import Sum
from django.utils.timezone import now
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageTemplate, Frame
from datetime import datetime
from django.utils import timezone
import time
import os
from django.conf import settings
from datetime import datetime
from django.http import HttpResponse
import csv
import openpyxl
from openpyxl.styles import Font
from django.core.mail import send_mail

def dashboard_page(request):
    return render(request, "dashboard.html")

def location_list_page(request):
    return render(request, "location/list_location.html")

def location_add_page(request):
    return render(request, "location/add_location.html")

def generate_shortcode(name):
    """Generate a two-letter shortcode from the location name."""
    words = re.findall(r'\b\w', name)  # Get the first letter of each word
    if len(words) >= 2:
        shortcode = ''.join(words[:2]).upper()  # Take the first two letters from separate words
    else:
        shortcode = name[:2].upper()  # If single word, take first two letters
    return shortcode

@csrf_exempt
def add_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name')
            details = data.get('details')
            status = data.get('status', 'active')  # Default to 'active' if not provided

            if not name:
                return JsonResponse({'error': 'Location name is required.'}, status=400)

            # Generate the shortcode
            shortcode = generate_shortcode(name)

            # Create a new Location instance with the shortcode
            location = Location.objects.create(name=name, details=details, status=status, shortcode=shortcode)

            return JsonResponse({
                'message': 'Location added successfully!',
                'shortcode': shortcode
            }, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



@csrf_exempt
def get_locations(request):
    if request.method == "GET":
        location_name = request.GET.get("location_name", "")
        shortcode = request.GET.get("shortcode", "")
        status = request.GET.get("status", "")

        locations = Location.objects.all()

        if location_name:
            locations = locations.filter(name__icontains=location_name)

        if shortcode:
            locations = locations.filter(shortcode__iexact=shortcode)

        if status:
            locations = locations.filter(status__iexact=status)

        location_list = [
            {
                "id": location.id,
                "name": location.name,
                'shortcode': location.shortcode,
                'details': location.details,
                'status': location.status,
                'created_at': location.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            for location in locations
        ]

        return JsonResponse({"locations": location_list}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


def location_view_page(request, location_id):
    # Fetch the specific location by ID
    location = get_object_or_404(Location, id=location_id)

    # Pass the location data to the template
    context = {
        'location': {
            'id': location.id,
            'name': location.name,
            'shortcode': location.shortcode,
            'status': location.status,
            'details': location.details,
            'created_at': location.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
    }
    return render(request, "location/view_location.html", context)


@csrf_exempt
def location_update_page(request, id):  
    location = get_object_or_404(Location, id=id)  # Use id instead of location_id
    
    if request.method == "GET":
        # Render the update form with existing data
        return render(request, 'location/update_location.html', {'location': location})
    
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            new_name = data.get('name', location.name)

            # Check if the name is being updated
            if new_name != location.name:
                location.shortcode = generate_shortcode(new_name)  # Update shortcode
            
            location.name = new_name
            location.details = data.get('details', location.details)
            location.status = data.get('status', location.status)
            location.save()

            return JsonResponse({'message': 'Location updated successfully!', 'shortcode': location.shortcode}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def delete_location(request, id):
    if request.method == 'POST':  # Ensure you're handling a POST request
        try:
            location = get_object_or_404(Location, id=id)
            location.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def employee_list_page(request):
    return render(request, "employee/list_employee.html")

def employee_add_page(request):
    return render(request, "employee/add_employee.html")

def generate_employee_code():
    # Get the highest employee ID in the database
    highest_employee = Employee.objects.all().order_by('-employee_id').first()

    # If there are no employees, start from EMP0001
    if highest_employee is None:
        return "EMP0001"
    
    # Increment the last employee ID by 1
    next_employee_id = highest_employee.employee_id + 1
    
    # Format the employee ID with 'EMP' prefix and zero-padded 4-digit number
    return f"EMP{next_employee_id:04d}"


@csrf_exempt
def add_employee(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            name = data.get('name')
            designation = data.get('designation')
            address = data.get('address')
            location = data.get('location')
            date_of_birth = data.get('date_of_birth')
            mobile_number = data.get('mobile_number')
            email = data.get('email')
            aadhaar_card = data.get('aadhaar_card')
            pan_card = data.get('pan_card', None)
            work_location_id = data.get('work_location')
            employee_code = data.get('employee_code', None)  # Optionally, get employee_code if user inputs it
            
             # Validate work_location ID
            work_location = Location.objects.get(id=work_location_id) if work_location_id else None

            # Generate employee code if not provided
            if not employee_code:
                employee_code = generate_employee_code()

            # Create a new Employee instance
            Employee.objects.create(
                employee_code=employee_code,
                name=name,
                designation=designation,
                address=address,
                location=location,
                work_location=work_location,
                date_of_birth=date_of_birth,
                mobile_number=mobile_number,
                email=email,
                aadhaar_card=aadhaar_card,
                pan_card=pan_card,
                created_at=now(),  
                updated_at=now(),
            )

            return JsonResponse({'message': 'Employee added successfully!'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def employee_list(request):
    if request.method == "GET":
        employee_code = request.GET.get("employee_code", "")
        employee_name = request.GET.get("employee_name", "")
        work_location = request.GET.get("work_location", "")  

        employees = Employee.objects.all()

        if employee_code:
            employees = employees.filter(employee_code__iexact=employee_code)

        if employee_name:
            employees = employees.filter(name__icontains=employee_name)

        if work_location:
            employees = employees.filter(work_location__id=work_location)

        employee_list = [
            {
                "id": employee.employee_id,
                "employee_code": employee.employee_code,
                "name": employee.name,
                "designation": employee.designation,
                "mobile_number": employee.mobile_number,
                "email": employee.email,
                "location": employee.location,
                "work_location": employee.work_location.name if employee.work_location else None, 
            }
            for employee in employees
        ]

        return JsonResponse({"employees": employee_list}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)


@csrf_exempt
def get_work_locations(request):
    if request.method == "GET":
        locations = Location.objects.all().values("id", "name")
        return JsonResponse({"work_locations": list(locations)}, status=200)

def employee_view_page(request, employee_id):
    # Fetch the specific employee by ID
    employee = get_object_or_404(Employee, employee_id=employee_id)

    # Pass the employee data to the template
    context = {
        'employee': {
            'id': employee.employee_id,
            'employee_code': employee.employee_code,
            'name': employee.name,
            'designation': employee.designation,
            'address': employee.address,
            'location': employee.location,
            'work_location':employee.work_location,
            'date_of_birth': employee.date_of_birth.strftime('%Y-%m-%d'),
            'mobile_number': employee.mobile_number,
            'email': employee.email,
            'aadhaar_card': employee.aadhaar_card,
            'pan_card': employee.pan_card,
        }
    }
    return render(request, "employee/view_employee.html", context)


def employee_update_page(request, id):
    employee = get_object_or_404(Employee, employee_id=id)

    if request.method == "GET":
        return render(request, 'employee/update_employee.html', {'employee': employee})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            # Assign values safely
            employee.name = data.get('name', employee.name)
            employee.designation = data.get('designation', employee.designation)
            employee.address = data.get('address', employee.address)
            employee.location = data.get('location', employee.location)
            employee.date_of_birth = data.get('date_of_birth', employee.date_of_birth)
            employee.mobile_number = data.get('mobile_number', employee.mobile_number)
            employee.email = data.get('email', employee.email)
            employee.aadhaar_card = data.get('aadhaar_card', employee.aadhaar_card)
            employee.pan_card = data.get('pan_card', employee.pan_card)

            work_location_id = data.get('work_location')
            if work_location_id:
                employee.work_location = get_object_or_404(Location, id=int(work_location_id))

            # Update timestamp
            employee.updated_at = now()
            
            employee.save()
            return JsonResponse({'message': 'Employee updated successfully!'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_employee(request, id):
    if request.method == 'POST':
        try:
            employee = get_object_or_404(Employee, employee_id=id)
            employee.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def company_list_page(request):
    return render(request, "company/list_company.html")

def company_add_page(request):
    return render(request, "company/add_company.html")


def add_company(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            company = Company.objects.create(
                company_name=data['company_name'],
                CIN_number=data['cin_number'],
                GST_number=data['gst_number'],
                location=data['location'],
                address=data['address'],
                email=data['email'],
                phone_number=data['phone_number']
            )
            return JsonResponse({'success': True, 'message': 'Company added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def company_list(request):
    if request.method == "GET":
        # Get filters from request
        company_name = request.GET.get('company_name', '').strip()
        location = request.GET.get('location', '').strip()

        # Start with all companies
        companies = Company.objects.all()

        # Apply filters
        if company_name:
            companies = companies.filter(company_name__icontains=company_name)
        if location:
            companies = companies.filter(location__icontains=location)

        # Format data for DataTable
        company_list = [
            {
                'id': company.company_id,
                'name': company.company_name,
                'CIN_number': company.CIN_number,
                'GST_number': company.GST_number,
                'location': company.location,
                'email': company.email,
                'phone_number': company.phone_number
            }
            for company in companies
        ]

        return JsonResponse({'companies': company_list}, status=200)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def company_view_page(request, company_id):
    # Fetch the specific company by ID
    company = get_object_or_404(Company, company_id=company_id)

    # Pass the company data to the template
    context = {
        'company': {
            'id': company.company_id,
            'name': company.company_name,
            'cin': company.CIN_number,
            'gst': company.GST_number,
            'location': company.location,
            'address': company.address,
            'email': company.email,
            'phone_number': company.phone_number,
        }
    }
    return render(request, "company/view_company.html", context)


def company_update_page(request, id):
    # Fetch company data
    company = get_object_or_404(Company, company_id=id)

    if request.method == "GET":
        # Render the update form with existing data
        return render(request, 'company/update_company.html', {'company': company})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update company fields
            company.company_name = data.get('company_name', company.company_name)
            company.CIN_number = data.get('CIN_number', company.CIN_number)
            company.GST_number = data.get('GST_number', company.GST_number)
            company.location = data.get('location', company.location)
            company.address = data.get('address', company.address)
            company.email = data.get('email', company.email)
            company.phone_number = data.get('phone_number', company.phone_number)
            company.save()

            return JsonResponse({'message': 'Company updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_company(request, id):
    if request.method == 'POST':
        try:
            company = get_object_or_404(Company, company_id=id)
            company.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def category_list_page(request):
    return render(request, "category/list_category.html")

def category_add_page(request):
    return render(request, "category/add_category.html")


def generate_shortcode_category(name):
    """Generate a four-letter shortcode from the category name."""
    shortcode = name[:4].upper()  # Take the first four characters of the name, convert to uppercase
    return shortcode

def add_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category_name = data.get('category_name')
            details = data.get('details')

            if not category_name:
                return JsonResponse({'success': False, 'error': 'Category name is required.'})

            # Generate the shortcode
            shortcode = generate_shortcode_category(category_name)

            # Create a new Category instance and save it
            category = Category.objects.create(
                category_name=category_name,
                details=details,
                shortcode=shortcode  # Save the generated shortcode
            )

            return JsonResponse({'success': True, 'message': 'Category added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def category_list(request):
    if request.method == "GET":
        categories = Category.objects.all()
        category_list = [
            {
                'id': category.category_id,
                'name': category.category_name,
                'shortcode': category.shortcode,
                'description': category.details, 
            }
            for category in categories
        ]
        return JsonResponse({'categories': category_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def category_view_page(request, category_id):
    # Fetch the specific category by ID
    category = get_object_or_404(Category, category_id=category_id)

    # Pass the category data to the template
    context = {
        'category': {
            'id': category.category_id,
            'name': category.category_name,
            'shortcode': category.shortcode,
            'description': category.details,
        }
    }
    return render(request, "category/view_category.html", context)


def category_update_page(request, id):
    # Fetch category data
    category = get_object_or_404(Category, category_id=id)

    if request.method == "GET":
        # Render the update form with existing data
        return render(request, 'category/update_category.html', {'category': category})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update category fields
            new_category_name = data.get('category_name', category.category_name)

            # If the category name has changed, update the shortcode
            if new_category_name != category.category_name:
                category.shortcode = generate_shortcode_category(new_category_name)  # Generate a new shortcode
            
            category.category_name = new_category_name
            category.details = data.get('details', category.details)
            category.save()

            # Send the updated shortcode back in the response
            return JsonResponse({
                'message': 'Category updated successfully!',
                'shortcode': category.shortcode  # Include updated shortcode in response
            }, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_category(request, id):
    if request.method == 'POST':
        try:
            category = get_object_or_404(Category, category_id=id)
            category.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def subcategory_list_page(request):
    return render(request, "subcategory/list_subcategory.html")

def subcategory_add_page(request):
    return render(request, "subcategory/add_subcategory.html")

def generate_shortcode_subcategory(name):
    """Generate a four-letter shortcode from the subcategory name."""
    shortcode = name[:4].upper()  # Take the first four characters and convert to uppercase
    return shortcode

@csrf_exempt
def add_subcategory(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            category = Category.objects.get(category_id=data['category_id'])  # Get Category instance
            
            # Generate shortcode from subcategory name
            shortcode = generate_shortcode_subcategory(data['subcategory_name'])

            # Create SubCategory with the generated shortcode
            subcategory = SubCategory.objects.create(
                category=category,
                subcategory_name=data['subcategory_name'],
                details=data['details'],
                shortcode=shortcode  
            )

            return JsonResponse({
                'success': True, 
                'message': 'Subcategory added successfully!',
                'shortcode': shortcode  # Return shortcode in response
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_categories(request): 
    categories = list(Category.objects.values('category_id', 'category_name','shortcode'))  # Use 'category_id'
    return JsonResponse({'categories': categories})


@csrf_exempt
def subcategory_list(request):
    if request.method == "GET":
        subcategories = SubCategory.objects.all()
        subcategory_list = [
            {
                'id': subcategory.subcategory_id,
                'name': subcategory.subcategory_name,
                'shortcode': subcategory.shortcode,
                'details': subcategory.details,
                'category_name': subcategory.category.category_name,
            }
            for subcategory in subcategories
        ]
        return JsonResponse({'subcategories': subcategory_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def subcategory_view_page(request, subcategory_id):
    # Fetch the specific subcategory by ID
    subcategory = get_object_or_404(SubCategory, subcategory_id=subcategory_id)

    # Pass the subcategory data to the template
    context = {
        'subcategory': {
            'id': subcategory.subcategory_id,
            'name': subcategory.subcategory_name,
            'shortcode': subcategory.shortcode,
            'details': subcategory.details,
            'category_name': subcategory.category.category_name,
        }
    }
    return render(request, "subcategory/view_subcategory.html", context)


def subcategory_update_page(request, id):
    # Fetch subcategory data
    subcategory = get_object_or_404(SubCategory, subcategory_id=id)

    if request.method == "GET":
        return render(request, 'subcategory/update_subcategory.html', {'subcategory': subcategory})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Check if subcategory name has changed
            new_name = data.get('subcategory_name', subcategory.subcategory_name)
            if new_name != subcategory.subcategory_name:
                subcategory.shortcode = generate_shortcode_subcategory(new_name)  # Update shortcode
            
            # Update subcategory fields
            subcategory.subcategory_name = new_name
            subcategory.category_id = data.get('category_id', subcategory.category_id)
            subcategory.details = data.get('details', subcategory.details)
            subcategory.save()

            return JsonResponse({
                'message': 'Subcategory updated successfully!',
                'shortcode': subcategory.shortcode  # Return updated shortcode
            }, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_subcategory(request, id):
    if request.method == 'POST':
        try:
            subcategory = get_object_or_404(SubCategory, subcategory_id=id)
            subcategory.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def box_list_page(request):
    return render(request, "box/list_box.html")

def box_add_page(request):
    return render(request, "box/add_box.html")


def add_box(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            box = Box.objects.create(
                box_name=data['box_name'],
                details=data['details']
            )
            return JsonResponse({'success': True, 'message': 'Box added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@csrf_exempt
def box_list(request):
    if request.method == "GET":
        boxes = Box.objects.all()
        box_list = [
            {
                'id': box.box_id,
                'name': box.box_name,
                'description': box.details,  # If applicable
            }
            for box in boxes
        ]
        return JsonResponse({'boxes': box_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def box_view_page(request, box_id):
    # Fetch the specific box by ID
    box = get_object_or_404(Box, box_id=box_id)

    # Pass the box data to the template
    context = {
        'box': {
            'id': box.box_id,
            'name': box.box_name,
            'details': box.details,
            'created_on': box.created_on,
        }
    }
    return render(request, "box/view_box.html", context)


def box_update_page(request, id):
    # Fetch box data by ID
    box = get_object_or_404(Box, box_id=id)

    if request.method == "GET":
        # Render the update form with existing box data
        return render(request, 'box/update_box.html', {'box': box})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update box fields with the new data
            box.box_name = data.get('box_name', box.box_name)
            box.details = data.get('details', box.details)
            box.save()

            return JsonResponse({'message': 'Box updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_box(request, id):
    if request.method == 'POST':
        try:
            box = get_object_or_404(Box, box_id=id)
            box.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def rank_list_page(request):
    return render(request, "rank/list_rank.html")

def rank_add_page(request):
    return render(request, "rank/add_rank.html")


@csrf_exempt
def add_rank(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rank = Rank.objects.create(
                rank_name=data['rank_name'],
                details=data['details']
            )
            return JsonResponse({'success': True, 'message': 'Rack added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def rank_list(request):
    if request.method == "GET":
        ranks = Rank.objects.all()
        rank_list = [
            {
                'id': rank.rank_id,
                'name': rank.rank_name,
                'description': rank.details,  
            }
            for rank in ranks
        ]
        return JsonResponse({'ranks': rank_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def rank_view_page(request, rank_id):
    # Fetch the specific rank by ID
    rank = get_object_or_404(Rank, rank_id=rank_id)

    # Pass the rank data to the template
    context = {
        'rank': {
            'id': rank.rank_id,
            'name': rank.rank_name,
            'details': rank.details,
            'created_on': rank.created_on,
        }
    }
    return render(request, "rank/view_rank.html", context)


def rank_update_page(request, id):
    # Fetch rank data by ID
    rank = get_object_or_404(Rank, rank_id=id)

    if request.method == "GET":
        # Render the update form with existing rank data
        return render(request, 'rank/update_rank.html', {'rank': rank})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update rank fields with the new data
            rank.rank_name = data.get('rank_name', rank.rank_name)
            rank.details = data.get('details', rank.details)
            rank.save()

            return JsonResponse({'message': 'Rack updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_rank(request, id):
    if request.method == 'POST':
        try:
            # Use rank_id instead of id
            rank = get_object_or_404(Rank, rank_id=id)
            rank.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def product_list_page(request):
    return render(request, "product/list_product.html")

def product_add_page(request):
    return render(request, "product/add_product.html")


def customer_list_page(request):
    return render(request, "customer/list_customer.html")

def customer_add_page(request):
    return render(request, "customer/add_customer.html")


def add_customer(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Fetch the company using the company_id (not company_name)
            company_id = data['company_name']  # This should be the company_id sent from the frontend
            company = Company.objects.get(company_id=company_id)  # Search by company_id
            
            # Create a new customer instance and save it
            customer = Customer.objects.create(
                customer_name=data['customer_name'],
                email=data['email'],
                company=company,  # Linking the customer to the company
                phone_number=data['phone_number'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                country=data['country'],
                details=data['details']
            )

            return JsonResponse({'success': True, 'message': 'Customer added successfully!'})

        except Company.DoesNotExist:
            # Handle the case where the company does not exist
            return JsonResponse({'success': False, 'error': 'Company not found'})

        except Exception as e:
            # Catch any other exceptions and return the error
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def get_companies(request):
    companies = Company.objects.all()
    company_data = [{"company_id": company.company_id, "company_name": company.company_name} for company in companies]
    return JsonResponse(company_data, safe=False)


# Customer List View
def customer_list(request):
    if request.method == "GET":
        customers = Customer.objects.all()
        customer_list = [
            {
                'id': customer.customer_id,
                'name': customer.customer_name,
                'email': customer.email,
                'company_name': customer.company.company_name,  # Getting the company name associated with the customer
                'phone_number': customer.phone_number,
                'address': customer.address,
                'city': customer.city,
                'state': customer.state,
                'zip_code': customer.zip_code,
                'country': customer.country,
                'details': customer.details,
            }
            for customer in customers
        ]
        return JsonResponse({'customers': customer_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def customer_view_page(request, customer_id):
    # Fetch the specific customer by ID
    customer = get_object_or_404(Customer, customer_id=customer_id)

    # Pass the customer data to the template
    context = {
        'customer': {
            'id': customer.customer_id,
            'name': customer.customer_name,
            'email': customer.email,
            'phone_number': customer.phone_number,
            'address': customer.address,
            'city': customer.city,
            'state': customer.state,
            'zip_code': customer.zip_code,
            'country': customer.country,
            'details': customer.details,
        }
    }
    return render(request, "customer/view_customer.html", context)


def customer_update_page(request, id):
    # Fetch customer data
    customer = get_object_or_404(Customer, customer_id=id)

    if request.method == "GET":
        # Render the update form with existing data
        return render(request, 'customer/update_customer.html', {'customer': customer})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update customer fields
            customer.customer_name = data.get('name', customer.customer_name)
            customer.email = data.get('email', customer.email)
            customer.phone_number = data.get('phone_number', customer.phone_number)
            customer.address = data.get('address', customer.address)
            customer.city = data.get('city', customer.city)
            customer.state = data.get('state', customer.state)
            customer.zip_code = data.get('zip_code', customer.zip_code)
            customer.save()

            return JsonResponse({'message': 'Customer updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# Delete Customer View
@csrf_exempt
def delete_customer(request, id):
    if request.method == 'POST':
        try:
            customer = get_object_or_404(Customer, customer_id=id)
            customer.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def supplier_list_page(request):
    return render(request, "supplier/list_supplier.html")

def supplier_add_page(request):
    return render(request, "supplier/add_supplier.html")


def add_supplier(request):
    if request.method == 'POST':
        try:
            # Parse the JSON data from the request body
            data = json.loads(request.body)

            # Fetch the company using the company_id (not company_name)
            company_id = data['company_name']  # This should be the company_id sent from the frontend
            company = Company.objects.get(company_id=company_id)  # Search by company_id
            
            # Create a new supplier instance and save it
            supplier = Supplier.objects.create(
                supplier_name=data['supplier_name'],
                email=data['email'],
                company=company,  # Linking the supplier to the company
                phone_number=data['phone_number'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                zip_code=data['zip_code'],
                country=data['country'],
                details=data['details']
            )

            return JsonResponse({'success': True, 'message': 'Supplier added successfully!'})

        except Company.DoesNotExist:
            # Handle the case where the company does not exist
            return JsonResponse({'success': False, 'error': 'Company not found'})

        except Exception as e:
            # Catch any other exceptions and return the error
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Supplier List View
def supplier_list(request):
    if request.method == "GET":
        suppliers = Supplier.objects.all()  # Assuming Supplier is the model for suppliers
        supplier_list = [
            {
                'id': supplier.supplier_id,
                'name': supplier.supplier_name,
                'email': supplier.email,
                'company_name': supplier.company.company_name,  # Getting the company name associated with the supplier
                'phone_number': supplier.phone_number,
                'address': supplier.address,
                'city': supplier.city,
                'state': supplier.state,
                'zip_code': supplier.zip_code,
                'country': supplier.country,
                'details': supplier.details,
            }
            for supplier in suppliers
        ]
        return JsonResponse({'suppliers': supplier_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def supplier_view_page(request, supplier_id):
    # Fetch the specific supplier by ID
    supplier = get_object_or_404(Supplier, supplier_id=supplier_id)

    # Pass the supplier data to the template
    context = {
        'supplier': {
            'id': supplier.supplier_id,
            'name': supplier.supplier_name,
            'email': supplier.email,
            'phone_number': supplier.phone_number,
            'address': supplier.address,
            'city': supplier.city,
            'state': supplier.state,
            'zip_code': supplier.zip_code,
            'country': supplier.country,
            'details': supplier.details,
        }
    }
    return render(request, "supplier/view_supplier.html", context)


def supplier_update_page(request, id):
    # Fetch supplier data
    supplier = get_object_or_404(Supplier, supplier_id=id)

    if request.method == "GET":
        # Fetch companies data to populate the company dropdown
        companies = Company.objects.all()

        # Render the update form with existing data
        return render(request, 'supplier/update_supplier.html', {'supplier': supplier, 'companies': companies})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            # Update supplier fields
            supplier.supplier_name = data.get('supplier_name', supplier.supplier_name)
            supplier.email = data.get('email', supplier.email)
            supplier.phone_number = data.get('phone_number', supplier.phone_number)
            supplier.address = data.get('address', supplier.address)
            supplier.city = data.get('city', supplier.city)
            supplier.state = data.get('state', supplier.state)
            supplier.zip_code = data.get('zip_code', supplier.zip_code)
            supplier.country = data.get('country', supplier.country)
            supplier.details = data.get('details', supplier.details)
            supplier.company_id = data.get('company_id', supplier.company_id)  # Update company field
            supplier.save()

            return JsonResponse({'message': 'Supplier updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)



# Delete Supplier View
@csrf_exempt
def delete_supplier(request, id):
    if request.method == 'POST':
        try:
            supplier = get_object_or_404(Supplier, supplier_id=id)
            supplier.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)



def validate_image(file):
    # Check if the file type is an image (e.g., jpg, png)
    valid_image_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in valid_image_types:
        raise ValidationError("Invalid image format. Only JPG, PNG, and GIF are allowed.")
    
    # Check the file size (max 5MB in this example)
    max_size = 5 * 1024 * 1024  # 5 MB
    if file.size > max_size:
        raise ValidationError("Image size exceeds the maximum limit of 5MB.")

    # Open the image using Pillow
    img = Image.open(file)

    # Get the original image dimensions
    width, height = img.size

    # You can set a max width and height for resizing if necessary
    max_width, max_height = 1024, 1024

    # Resize the image if it's larger than the maximum allowed dimensions
    if width > max_width or height > max_height:
        img.thumbnail((max_width, max_height))  # Resize while maintaining aspect ratio

    # Save the image to a BytesIO object to handle file size reduction
    img_io = BytesIO()
    # Compress the image to reduce file size (quality can be adjusted)
    img.save(img_io, format='JPEG', quality=85)  # Adjust quality as needed (between 0 and 100)

    # Rewind the BytesIO object to the beginning
    img_io.seek(0)

    # Return the resized image file
    file.image = img_io  # Replace original file with the resized one (optional)

    # Check the new file size after resizing
    if img_io.tell() > max_size:
        raise ValidationError("Image size exceeds the maximum limit of 5MB after compression.")

    return file


def generate_product_code():
    """ Generate the next sequential product code in the format PROD-000001 """
    last_product = Product.objects.aggregate(Max('product_id'))
    last_id = last_product['product_id__max'] or 0  # If no product exists, start from 0
    new_id = last_id + 1
    return f"PROD-{new_id:06d}"  # Formats as PROD-000001, PROD-000002, etc.


def generate_barcode_image(barcode_text, product_id, category_shortcode):
    """ Generate and save a barcode image """
    barcode_class = barcode.get_barcode_class('code128')
    barcode_instance = barcode_class(barcode_text, writer=ImageWriter())

    # Create file path using product_id and category_shortcode
    file_path = os.path.join(settings.MEDIA_ROOT, 'barcodes', f'barcode_{product_id}_{category_shortcode}')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save the barcode without the .png extension
    barcode_instance.save(file_path)

    # Return relative path with .png extension
    return f'barcodes/barcode_{product_id}_{category_shortcode}.png'


def generate_barcode(product_code, product_name, category_shortcode):
    """ Generate a barcode string using product_code, name, and category shortcode """
    barcode_text = f"{product_code}-{slugify(product_name[:5])}-{slugify(category_shortcode[:5])}".upper()
    return barcode_text


def add_product(request):
    if request.method == 'POST':
        try:
            product_name = request.POST['product_name']
            category_id = request.POST['category_id']
            subcategory_id = request.POST['subcategory_id']
            length = request.POST['length']
            breadth = request.POST['breadth']
            height = request.POST['height']
            product_weight = request.POST['product_weight']
            manufacture_name = request.POST['manufacture_name']
            description = request.POST['description']
            vendor = request.POST['vendor']
            purchase_date = request.POST['purchase_date']
            purchase_amount = request.POST['purchase_amount']
            images = request.FILES.getlist('images')

            category = Category.objects.get(category_id=category_id)
            subcategory = SubCategory.objects.get(subcategory_id=subcategory_id)

            # Generate sequential product_code
            product_code = generate_product_code()

            # Create product without barcode initially
            product = Product.objects.create(
                product_code=product_code,
                product_name=product_name,
                category=category,
                subcategory=subcategory,
                product_size_length=length,
                product_size_breadth=breadth,
                product_size_height=height,
                product_weight=product_weight,
                manufacture_name=manufacture_name,
                description=description,
                vendor=vendor,
                purchase_date=purchase_date,
                purchase_amount=purchase_amount,
                barcode=product_code  # Assign generated product_code
            )

            # Generate barcode text and image using product_code instead of product_id
            barcode_text = generate_barcode(product_code, product_name, category.shortcode)
            barcode_image_path = generate_barcode_image(barcode_text, product_code,category.shortcode)

            # Update product with barcode details
            product.barcode = barcode_text
            product.barcode_image = barcode_image_path
            product.save()

            # Save multiple images
            for image in images:
                product_image = ProductImage.objects.create(image=image)
                product.product_images.add(product_image)

            return JsonResponse({'success': True, 'message': 'Product added successfully!'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    categories = Category.objects.all()
    return render(request, 'add_product.html', {'categories': categories})


def get_subcategories(request, category_id):
    subcategories = list(SubCategory.objects.filter(category_id=category_id).values('subcategory_id', 'subcategory_name','shortcode'))
    return JsonResponse({'subcategories': subcategories})


@csrf_exempt 
def get_products(request):
    if request.method == "GET":
        try:
            # Fetch all products
            products = Product.objects.all()

            # Prepare the product data to return as JSON
            product_list = [
                {
                    'id': product.product_id,
                    'product_code': product.product_code,
                    'name': product.product_name,
                    'category': product.category.category_name,  # Changed to category_name
                    'purchase_amount': product.purchase_amount,
                    'purchase_date': product.purchase_date.strftime('%Y-%m-%d'),
                    'image': product.product_images.first().image.url if product.product_images.exists() else None
                }
                for product in products
            ]

            # Return the product list as JSON
            return JsonResponse({'products': product_list}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def product_view_page(request, product_id):
    # Fetch the specific product by ID
    product = get_object_or_404(Product, product_id=product_id)

    # Pass the product data to the template
    context = {
        'product': {
            'id': product.product_id,
            'name': product.product_name,
            'product_code': product.product_code,
            'category': product.category.category_name,
            'subcategory': product.subcategory.subcategory_name if product.subcategory else 'N/A',
            'size': f"{product.product_size_length} x {product.product_size_breadth} x {product.product_size_height}",
            'weight': product.product_weight,
            'manufacture_name': product.manufacture_name,
            'description': product.description,
            'vendor': product.vendor,
            'barcode': product.barcode,
            'barcode_image': product.barcode_image.url if product.barcode_image else None,
            'purchase_date': product.purchase_date.strftime('%Y-%m-%d'),
            'purchase_amount': product.purchase_amount,
            'images': product.product_images.all(),
        }
    }
    return render(request, "product/view_product.html", context)


def update_product(request, id):
    product = get_object_or_404(Product, product_id=id)

    if request.method == "GET":
        categories = Category.objects.all()
        subcategories = SubCategory.objects.filter(category_id=product.category_id)
        return render(request, 'product/update_product.html', {
            'product': product,
            'categories': categories,
            'subcategories': subcategories
        })

    elif request.method == "POST":
        try:
            # Get product details from the form
            old_category_id = product.category_id  # Store the old category for comparison
            product.product_code = request.POST.get('product_code', product.product_code)
            product.product_name = request.POST.get('product_name', product.product_name)
            product.barcode = request.POST.get('barcode', product.barcode)

            # Use 'category' and 'subcategory' instead of 'category_id' and 'subcategory_id'
            new_category = get_object_or_404(Category, category_id=request.POST.get('category'))
            product.category = new_category
            product.subcategory = get_object_or_404(SubCategory, subcategory_id=request.POST.get('subcategory'))

            product.product_size_length = request.POST.get('length', product.product_size_length)
            product.product_size_breadth = request.POST.get('breadth', product.product_size_breadth)
            product.product_size_height = request.POST.get('height', product.product_size_height)
            product.product_weight = request.POST.get('product_weight', product.product_weight)
            product.manufacture_name = request.POST.get('manufacture_name', product.manufacture_name)
            product.description = request.POST.get('description', product.description)
            product.vendor = request.POST.get('vendor', product.vendor)

            # Handle purchase date
            purchase_date_str = request.POST.get('purchase_date')
            if purchase_date_str:
                product.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()

            product.purchase_amount = request.POST.get('purchase_amount', product.purchase_amount)

            # Handle image deletions
            remove_image_ids = request.POST.getlist('remove_image_ids[]')  # Get IDs of images to remove
            if remove_image_ids:
                ProductImage.objects.filter(id__in=remove_image_ids).delete()

            # Handle new images upload
            images = request.FILES.getlist('images')
            for image in images:
                # Validate image before saving
                validate_image(image)
                product_image = ProductImage.objects.create(image=image)
                product.product_images.add(product_image)

           # Regenerate barcode if category or subcategory has changed
            if product.category != old_category_id:
                # Generate barcode text using the product's code, name, and the new category's shortcode
                barcode_text = generate_barcode(product.product_code, product.product_name, new_category.shortcode)

                # Regenerate barcode image
                barcode_image_path = generate_barcode_image(barcode_text, product.product_id, new_category.shortcode)
                product.barcode_image = barcode_image_path


            product.save()

            # Prepare response data
            product_images = [{'id': img.id, 'image_url': img.image.url} for img in product.product_images.all()]
            response_data = {
                'success': True,
                'message': 'Product updated successfully!',
                'barcode_image': product.barcode_image.url if product.barcode_image else None,
                'product_images': product_images  # Updated image list
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def remove_product_image(request, image_id):
    try:
        # Get the image object by its ID
        image = ProductImage.objects.get(id=image_id)
        
        # Delete the image
        image.delete()

        return JsonResponse({'success': True, 'message': 'Image removed successfully.'})

    except ProductImage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Image not found.'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    
@csrf_exempt
def delete_product(request, id):
    if request.method == 'POST':
        try:
            product = get_object_or_404(Product, product_id=id)
            product.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


def exhibition_list_page(request):
    return render(request, "exhibition/list_exhibition.html")

def exhibition_add_page(request):
    return render(request, "exhibition/add_exhibition.html")


def add_exhibition(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            Exhibition.objects.create(
                exhibition_name=data['exhibition_name'],
                location=data['location'],
                address=data['address'],
                city=data['city'],
                state=data['state'],
                pincode=data['pincode'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                details=data['details'],
            )
            return JsonResponse({'success': True, 'message': 'Exhibition added successfully!'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def exhibition_list(request):
    if request.method == "GET":
        exhibitions = Exhibition.objects.all()
        exhibition_list = [
            {
                'id': exhibition.exhibition_id,
                'name': exhibition.exhibition_name,
                'location': exhibition.location,
                'city': exhibition.city,
                'state': exhibition.state,
                'start_date': exhibition.start_date.strftime('%Y-%m-%d'),
                'end_date': exhibition.end_date.strftime('%Y-%m-%d'),
            }
            for exhibition in exhibitions
        ]
        return JsonResponse({'exhibitions': exhibition_list}, status=200)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def exhibition_view_page(request, exhibition_id):
    # Fetch the specific exhibition by ID
    exhibition = get_object_or_404(Exhibition, exhibition_id=exhibition_id)

    # Pass the exhibition data to the template
    context = {
        'exhibition': {
            'id': exhibition.exhibition_id,
            'name': exhibition.exhibition_name,
            'location': exhibition.location,
            'address': exhibition.address,
            'city': exhibition.city,
            'state': exhibition.state,
            'pincode': exhibition.pincode,
            'start_date': exhibition.start_date,
            'end_date': exhibition.end_date,
            'details': exhibition.details,
        }
    }
    return render(request, "exhibition/view_exhibition.html", context)


def exhibition_update_page(request, id):
    exhibition = get_object_or_404(Exhibition, exhibition_id=id)

    if request.method == "GET":
        # Render the update form with existing data
        return render(request, 'exhibition/update_exhibition.html', {'exhibition': exhibition})

    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            # Parse and update the fields
            exhibition.exhibition_name = data.get('exhibition_name', exhibition.exhibition_name)
            exhibition.location = data.get('location', exhibition.location)
            exhibition.address = data.get('address', exhibition.address)
            exhibition.city = data.get('city', exhibition.city)
            exhibition.state = data.get('state', exhibition.state)
            exhibition.pincode = data.get('pincode', exhibition.pincode)

            # Parse and update start_date and end_date
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            if start_date:
                exhibition.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if end_date:
                exhibition.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            exhibition.details = data.get('details', exhibition.details)
            exhibition.save()

            return JsonResponse({'message': 'Exhibition updated successfully!'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@csrf_exempt
def delete_exhibition(request, id):
    if request.method == 'POST':
        try:
            exhibition = get_object_or_404(Exhibition, exhibition_id=id)
            exhibition.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)




def stock_list_page(request):
    return render(request, "stock/stock_list.html")

def stock_entry_page(request):
    return render(request, "stock/stock_entry.html")


# Fetch products based on selected subcategory
def get_products_stock(request, subcategory_id):
    products = list(Product.objects.filter(subcategory_id=subcategory_id)
                    .values('product_id', 'product_name', 'barcode_image'))
    return JsonResponse({'products': products})

# Fetch locations for Select2 dropdown
def get_locations_entry(request):
    locations = list(Location.objects.filter(status="active").values('id', 'name', 'shortcode'))
    return JsonResponse({'locations': locations})



import os
import qrcode
from django.conf import settings

def generate_barcode_stock_image(barcode_text, product_code, category_shortcode, location_shortcode, quantity_number):
    """ Generate and save a QR code image temporarily for preview """
    try:
        # ✅ Encode barcode_text and product_code into the QR code
        qr_data = f"Barcode: {barcode_text}\nProduct Code: {product_code}"

        # ✅ Generate QR Code
        qr = qrcode.QRCode(
            version=None,  # Let the library determine the version automatically
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Error correction level
            box_size=10,  # Size of each box in the QR code
            border=4,  # Border size around the QR code
        )
        qr.add_data(qr_data)
        qr.make(fit=True)  # Automatically adjust version based on data size

        # Create the QR code image
        qr_img = qr.make_image(fill='black', back_color='white')

        # ✅ Temporary folder for QR code images
        temp_folder = os.path.join(settings.MEDIA_ROOT, 'temp_barcodes')
        os.makedirs(temp_folder, exist_ok=True)

        # ✅ Remove `.png` from filename because we'll add it manually
        file_name = f"{product_code}_{category_shortcode}_{location_shortcode}_{str(quantity_number).zfill(2)}"
        file_path = os.path.join(temp_folder, file_name + ".png")  # Add .png extension

        # Save the QR code image
        qr_img.save(file_path)

        # ✅ Explicitly return the correct file path
        return f'temp_barcodes/{file_name}.png'

    except Exception as e:
        print(f"Error generating QR code: {e}")
        return None


def move_barcode_to_stock(temp_image_url, stock_entry):
    """ Move barcode image from temporary folder to stock folder and delete it from temp_barcodes """
    try:
        # Resolve full path of the temporary image
        temp_image_path = os.path.join(settings.MEDIA_ROOT, temp_image_url.replace(settings.MEDIA_URL, ""))
        
        # Ensure the file exists before proceeding
        if not os.path.exists(temp_image_path):
            print(f"Warning: Temp image {temp_image_path} not found!")
            return None

        # Define new folder for storing barcode images permanently
        new_folder = os.path.join(settings.MEDIA_ROOT, 'stock_barcodes')
        os.makedirs(new_folder, exist_ok=True)  # Create the folder if it doesn't exist

        # Get the file name and define the new storage path
        new_image_name = os.path.basename(temp_image_path)
        new_image_path = os.path.join(new_folder, new_image_name)

        # Move the file from temp_barcodes to stock_barcodes
        shutil.move(temp_image_path, new_image_path)

        print(f"Barcode image moved to: {new_image_path}")
        
        # Return the new relative path for saving in the database
        return f'stock_barcodes/{new_image_name}'

    except Exception as e:
        print(f"Error moving barcode image: {e}")
        return None


def add_stock(request):   
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        location_id = request.POST.get('location_id')
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        quantity = int(request.POST.get('quantity', 1))
        serial_numbers = request.POST.getlist('serial_number[]')

        if not product_id or not location_id or not category_id:
            return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

        try:
            product = Product.objects.get(product_id=product_id)
            category = Category.objects.filter(category_id=category_id).first()
            subcategory = SubCategory.objects.filter(subcategory_id=subcategory_id).first()
            location = Location.objects.get(id=location_id)

            if not category:
                return JsonResponse({"status": "error", "message": "Invalid Category ID"}, status=400)

            barcode_list = []

            # Get existing barcodes from TempStockBarcode
            existing_temp_barcodes = TempStockBarcode.objects.filter(
                product=product, location=location
            )

            if existing_temp_barcodes.exists():
                barcode_list = [
                    {
                        "barcode": temp_barcode.barcode_text,
                        "image": temp_barcode.barcode_image.url if temp_barcode.barcode_image else None,
                        "product_name": temp_barcode.product.product_name,
                        "location_name": temp_barcode.location.name,
                        "serial_number": temp_barcode.serial_number
                    }
                    for temp_barcode in existing_temp_barcodes
                ]

                return JsonResponse({
                    "status": "success",
                    "barcodes": barcode_list,
                    "product_name": product.product_name,
                    "location_name": location.name
                })

            # If no barcodes exist in TempStockBarcode, check StockBarcode
            existing_barcodes = list(StockBarcode.objects.filter(
                barcode_text__startswith=f"{product.product_code}-{category.shortcode}-{location.shortcode}-"
            ).values_list('barcode_text', flat=True))

            # Extract numerical part of existing barcodes
            quantity_numbers = []
            pattern = re.compile(rf"{product.product_code}-{category.shortcode}-{location.shortcode}-(\d+)")

            for barcode in existing_barcodes:
                match = pattern.match(barcode)
                if match:
                    quantity_numbers.append(int(match.group(1)))

            last_number = max(quantity_numbers) if quantity_numbers else 0

            for i in range(1, quantity + 1):
                quantity_number = last_number + i

                while True:
                    barcode_text = f"{product.product_code}-{category.shortcode}-{location.shortcode}-{str(quantity_number).zfill(2)}".upper()
                    if barcode_text not in existing_barcodes:
                        break
                    quantity_number += 1

                # Generate barcode image
                temp_barcode_path = generate_barcode_stock_image(
                    barcode_text, 
                    product.product_code, 
                    category.shortcode, 
                    location.shortcode, 
                    quantity_number
                )

                # Get corresponding serial number from user input
                serial_number = serial_numbers[i - 1] if i - 1 < len(serial_numbers) else ""


                # ✅ Save Product & Location in TempStockBarcode
                temp_barcode = TempStockBarcode.objects.create(
                    barcode_text=barcode_text,
                    barcode_image=temp_barcode_path,
                    product=product,  
                    location=location,
                    serial_number=serial_number  
                )

                barcode_list.append({
                    "barcode": temp_barcode.barcode_text,
                    "image": temp_barcode.barcode_image.url,
                    "product_name": product.product_name,
                    "location_name": location.name,
                    "serial_number": temp_barcode.serial_number
                })

            return JsonResponse({
                "status": "success",
                "barcodes": barcode_list,
                "product_name": product.product_name,
                "location_name": location.name
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def get_existing_barcodes(request):
    product_id = request.GET.get('product_id')
    location_id = request.GET.get('location_id')

    if not product_id or not location_id:
        return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

    try:
        product = Product.objects.get(product_id=product_id)
        location = Location.objects.get(id=location_id)

        existing_barcodes = TempStockBarcode.objects.filter(product=product, location=location)

        barcode_list = [
            {
                "barcode": barcode.barcode_text,
                "image": barcode.barcode_image.url
            } 
            for barcode in existing_barcodes
        ]

        return JsonResponse({
            "status": "success",
            "barcodes": barcode_list,
            "product_name": product.product_name,
            "location_name": location.name,
        })

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
    
    

@csrf_exempt
def submit_stock(request):
    """ Save Stock Entry and Barcodes to Database and delete TempStockBarcode """
    if request.method == 'POST':
        try:
            # Debugging: Log received data
            print("Received Data:", request.POST)

            # Extract form data
            product_id = request.POST.get('product_id')
            location_id = request.POST.get('location_id')
            category_id = request.POST.get('category_id')
            subcategory_id = request.POST.get('subcategory_id')
            quantity = int(request.POST.get('quantity', 1))
            product_status_list = request.POST.getlist('product_status[]')  # Extract as list
            import ast
            barcodes_json = request.POST.get('barcodes', '[]')
            barcode_list = ast.literal_eval(barcodes_json) if isinstance(barcodes_json, str) else []

            if not barcode_list:
                return JsonResponse({"status": "error", "message": "No barcodes received"}, status=400)

            # Debugging: Print extracted values
            print(f"Product ID: {product_id}, Location ID: {location_id}, Quantity: {quantity}, Barcodes: {barcode_list}")

            product = Product.objects.get(product_id=product_id)
            location = Location.objects.get(id=location_id)
            category = Category.objects.get(category_id=category_id)
            subcategory = SubCategory.objects.get(subcategory_id=subcategory_id)

            # Process each barcode
            for index, barcode in enumerate(barcode_list):
                rank_id = barcode.get("rank_id")
                box_id = barcode.get("box_id")
                serial_number = barcode.get("serial_number", "")
                product_status = product_status_list[index]  # Get product_status for this barcode

                rack = Rank.objects.get(rank_id=rank_id)
                box = Box.objects.get(box_id=box_id)

                stock_entry = StockEntry.objects.create(
                    product=product,
                    location=location,
                    category=category,
                    subcategory=subcategory,
                    rack=rack,
                    box=box,
                    quantity=1,  # Each barcode corresponds to 1 quantity
                    serial_number=serial_number,
                    product_status=product_status  # Pass product_status here
                )

                # Fetch the temp barcode object
                temp_barcode = TempStockBarcode.objects.get(barcode_text=barcode['barcode'])

                # Move barcode image and save in StockBarcode
                stock_image_path = move_barcode_to_stock(temp_barcode.barcode_image.url, stock_entry)
                StockBarcode.objects.create(
                    stock_entry=stock_entry,
                    barcode_text=temp_barcode.barcode_text,
                    barcode_image=stock_image_path
                )

                # Delete the temp barcode
                temp_barcode.delete()

            return JsonResponse({"status": "success", "message": "Stock submitted successfully"})

        except Exception as e:
            print("Error:", str(e))
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



def delete_temp_barcode(request):
    """ Delete a barcode from temp folder and remove its entry from the database """
    if request.method == 'POST':
        temp_image_path = request.POST.get('image_path')  # Get full URL from AJAX
        barcode_text = request.POST.get('barcode_text')  # Get barcode text
        
        # Convert full URL to relative path
        media_url = settings.MEDIA_URL  # Example: '/media/'
        if temp_image_path.startswith(media_url):
            relative_path = temp_image_path[len(media_url):]  # Remove '/media/' prefix
        else:
            relative_path = temp_image_path  # Fallback

        try:
            # Find the barcode in the database using barcode_text (safer than image path)
            barcode_obj = TempStockBarcode.objects.filter(barcode_text=barcode_text).first()
            
            if barcode_obj:
                # Delete the barcode record from the database
                barcode_obj.delete()

                # Delete the barcode image from the filesystem
                full_path = os.path.join(settings.MEDIA_ROOT, relative_path)
                if default_storage.exists(full_path):
                    default_storage.delete(full_path)

                return JsonResponse({"status": "success", "message": "Barcode deleted from DB and filesystem"})

            return JsonResponse({"status": "error", "message": "Barcode not found in DB"}, status=404)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)



def remove_barcode(request):
    """ Remove barcode entry from database """
    if request.method == 'POST':
        barcode_text = request.POST.get('barcode')

        try:
            barcode = StockBarcode.objects.get(barcode_text=barcode_text)
            barcode.barcode_image.delete()  # Delete image file
            barcode.delete()
            return JsonResponse({"status": "success", "message": "Barcode removed successfully"})
        except StockBarcode.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Barcode not found"}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def get_boxes(request):
    boxes = list(Box.objects.values('box_id', 'box_name'))
    return JsonResponse({'boxes': boxes})

def get_ranks(request):
    ranks = list(Rank.objects.values('rank_id', 'rank_name'))
    return JsonResponse({'ranks': ranks})


# def fetch_barcode(request):
#     category_id = request.GET.get("category")
#     subcategory_id = request.GET.get("subcategory")
#     product_id = request.GET.get("product")
#     location_id = request.GET.get("location")

#     print(f"Received Parameters - Category: {category_id}, SubCategory: {subcategory_id}, Product: {product_id}, Location: {location_id}")

#     # Fetch matching stock entries
#     stock_entries = StockEntry.objects.filter(
#         category_id=category_id,
#         subcategory_id=subcategory_id,
#         product_id=product_id,
#         location_id=location_id
#     ).select_related("product", "location", "rack", "box")

#     if stock_entries.exists():
#         print(f"Stock Entries Found: {stock_entries.count()}")

#         barcode_list = []

#         for stock_entry in stock_entries:
#             # Fetch all barcodes associated with each stock entry
#             barcodes = stock_entry.barcodes.all()  # Uses related_name="barcodes" in StockBarcode model
#             barcode_data = [
#                 {
#                     "barcode_text": barcode.barcode_text,
#                     "barcode_image": barcode.barcode_image.url,
#                     "stock_id": stock_entry.stock_id,
#                     "serial_number": stock_entry.serial_number,
#                     "product_name": stock_entry.product.product_name,
#                     "location": stock_entry.location.name,
#                     "rank": stock_entry.rack.rank_name,  
#                     "box": stock_entry.box.box_name
#                 }
#                 for barcode in barcodes
#             ]
#             barcode_list.extend(barcode_data)

#         print(f"Barcodes Found: {barcode_list}")  
#         return JsonResponse({"barcodes": barcode_list})

#     else:
#         print("No Stock Entries Found!")
#         return JsonResponse({"barcodes": []})
    
def stock_entry_fetch_barcode(request):
    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")
    product_id = request.GET.get("product")
    location_id = request.GET.get("location")

    print(f"Stock Entry Received Parameters - Category: {category_id}, SubCategory: {subcategory_id}, Product: {product_id}, Location: {location_id}")
    stock_entries = StockEntry.objects.filter(
        category_id=category_id,
        subcategory_id=subcategory_id,
        product_id=product_id,
        location_id=location_id,
    ).select_related("product", "location", "rack", "box")

    total_quantity = stock_entries.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    if stock_entries.exists():
        print(f"Stock Entries Found: {stock_entries.count()} | Total Quantity: {total_quantity}")

        barcode_list = []

        for stock_entry in stock_entries:
            # Fetch all barcodes associated with each stock entry
            barcodes = stock_entry.barcodes.all()  
            barcode_data = [
                {
                    "barcode_text": barcode.barcode_text,
                    "barcode_image": barcode.barcode_image.url,
                    "stock_id": stock_entry.stock_id,
                    "serial_number": stock_entry.serial_number,
                    "product_name": stock_entry.product.product_name,
                    "location": stock_entry.location.name,
                    "rank": stock_entry.rack.rank_name,  
                    "box": stock_entry.box.box_name,
                    "product_status": stock_entry.product_status,
                }
                for barcode in barcodes
            ]
            barcode_list.extend(barcode_data)

        print(f"Barcodes Found: {barcode_list}")  
        return JsonResponse({"barcodes": barcode_list, "available_quantity": total_quantity})

    else:
        print("No Stock Entries Found!")
        return JsonResponse({"barcodes": [], "available_quantity": 0})

def fetch_barcode(request):
    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")
    product_id = request.GET.get("product")
    location_id = request.GET.get("location")

    print(f"Received Parameters - Category: {category_id}, SubCategory: {subcategory_id}, Product: {product_id}, Location: {location_id}")

    # Fetch matching stock entries
    stock_entries = StockEntry.objects.filter(
        category_id=category_id,
        subcategory_id=subcategory_id,
        product_id=product_id,
        location_id=location_id,
        product_status ="INSTOCK"
    ).select_related("product", "location", "rack", "box")

    total_quantity = stock_entries.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    if stock_entries.exists():
        print(f"Stock Entries Found: {stock_entries.count()} | Total Quantity: {total_quantity}")

        barcode_list = []

        for stock_entry in stock_entries:
            # Fetch all barcodes associated with each stock entry
            barcodes = stock_entry.barcodes.all()  
            barcode_data = [
                {
                    "barcode_text": barcode.barcode_text,
                    "barcode_image": barcode.barcode_image.url,
                    "stock_id": stock_entry.stock_id,
                    "serial_number": stock_entry.serial_number,
                    "product_name": stock_entry.product.product_name,
                    "location": stock_entry.location.name,
                    "rank": stock_entry.rack.rank_name,  
                    "box": stock_entry.box.box_name,
                    "product_status": stock_entry.product_status,
                }
                for barcode in barcodes
            ]
            barcode_list.extend(barcode_data)

        print(f"Barcodes Found: {barcode_list}")  
        return JsonResponse({"barcodes": barcode_list, "available_quantity": total_quantity})

    else:
        print("No Stock Entries Found!")
        return JsonResponse({"barcodes": [], "available_quantity": 0})



@csrf_exempt
def delete_stock(request, stock_id):
    """ Deletes stock entry, related barcodes, and barcode images """
    if request.method == "DELETE":
        try:
            stock_entry = StockEntry.objects.get(stock_id=stock_id)

            # Delete associated barcodes and remove their images
            for barcode in stock_entry.barcodes.all():
                # Resolve the barcode image path
                barcode_image_path = os.path.join(settings.MEDIA_ROOT, str(barcode.barcode_image))

                # Remove image file if it exists
                if os.path.exists(barcode_image_path):
                    os.remove(barcode_image_path)

                # Delete barcode entry from the database
                barcode.delete()

            # Delete the stock entry
            stock_entry.delete()

            return JsonResponse({"status": "success", "message": "Stock entry deleted successfully"})
        except StockEntry.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Stock entry not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)



@csrf_exempt
def update_stock(request):
    """ Update stock's rank and box based on user selection """
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON data
            stock_id = data.get("stock_id")
            new_rank_id = data.get("rank_id")  # Corrected field name
            new_box_id = data.get("box_id")

            # Ensure required data is provided
            if not stock_id or not new_rank_id or not new_box_id:
                return JsonResponse({"status": "error", "message": "Missing required fields"}, status=400)

            # Fetch the stock entry
            stock_entry = StockEntry.objects.get(stock_id=stock_id)  # Use stock_id as primary key
            
            # Fetch the new rank and box using correct primary keys
            new_rank = Rank.objects.get(rank_id=new_rank_id)  # Use rank_id instead of id
            new_box = Box.objects.get(box_id=new_box_id)  # Use box_id instead of id

            # Update the stock entry
            stock_entry.rack = new_rank  # Ensure this matches ForeignKey field
            stock_entry.box = new_box
            stock_entry.save()

            return JsonResponse({"status": "success", "message": "Stock updated successfully!"})

        except StockEntry.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Stock entry not found"}, status=404)
        except Rank.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Rank not found"}, status=404)
        except Box.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Box not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


def fetch_stock_list(request):
    if request.method == "GET":
        category_id = request.GET.get("category", None)
        subcategory_id = request.GET.get("subcategory", None)
        product_id = request.GET.get("product", None)
        location_id = request.GET.get("location", None)

        stock_entries = StockEntry.objects.select_related(
            "product","category", "subcategory", "location", "rack", "box"
        ).all()

        # Apply filters only if values exist
        if category_id:
            stock_entries = stock_entries.filter(category_id=category_id)
        if subcategory_id:
            stock_entries = stock_entries.filter(subcategory_id=subcategory_id)
        if product_id:
            stock_entries = stock_entries.filter(product_id=product_id)
        if location_id:
            stock_entries = stock_entries.filter(location_id=location_id)

        stock_list = [
            {
                "stock_id": stock.stock_id,
                "product_name": stock.product.product_name,
                "category_name": stock.category.category_name,
                "subcategory_name": stock.subcategory.subcategory_name,
                "barcode_text": barcode.barcode_text,
                "barcode_image": barcode.barcode_image.url if barcode.barcode_image else "",
                "location": stock.location.name,
                "rack": stock.rack.rank_name if stock.rack else "N/A",
                "box": stock.box.box_name if stock.box else "N/A",
                "product_status" : stock.product_status
            }
            for stock in stock_entries
            for barcode in stock.barcodes.all()  # Assuming a ForeignKey or related_name="barcodes"
        ]

        return JsonResponse({"stocks": stock_list}, status=200)

    return JsonResponse({"error": "Invalid request method."}, status=405)



def stock_view_page(request, stock_id): 
    # Fetch the specific stock entry by ID
    stock = get_object_or_404(StockEntry, stock_id=stock_id)

    # Fetch all related barcodes from StockBarcode
    barcodes = StockBarcode.objects.filter(stock_entry=stock)

    # Prepare stock data for template rendering
    context = {
        'stock': {
            'stock_id': stock.stock_id,
            'product_name': stock.product.product_name,
            'category_name': f"{stock.category.category_name} ({stock.category.shortcode})" if stock.category else 'N/A',
            'subcategory_name': f"{stock.subcategory.subcategory_name} ({stock.subcategory.shortcode})" if stock.subcategory else 'N/A',
            'location': f"{stock.location.name} ({stock.location.shortcode})" if stock.location else 'N/A',
            'rack': stock.rack.rank_name if stock.rack else 'N/A',
            'box': stock.box.box_name if stock.box else 'N/A',
        },
        'barcodes': barcodes  # Pass all barcode entries to the template
    }
    
    return render(request, "stock/view_stock.html", context)


def stock_update_page(request, stock_id):
    stock = get_object_or_404(StockEntry, stock_id=stock_id)

    if request.method == "GET":
        # Fetch related barcodes including proper image URLs
        barcodes = StockBarcode.objects.filter(stock_entry=stock)
        barcode_data = [
            {
                'barcode_text': barcode.barcode_text,
                'barcode_image_url': barcode.barcode_image.url if barcode.barcode_image else None
            }
            for barcode in barcodes
        ]

        # Fetch available racks and boxes
        racks = Rank.objects.all().values('rank_id', 'rank_name')
        boxes = Box.objects.all().values('box_id', 'box_name')

        context = {
            'stock': {
                'stock_id': stock.stock_id,
                'product_name': stock.product.product_name,
                'category_name': stock.category.category_name if stock.category else 'N/A',
                'subcategory_name': stock.subcategory.subcategory_name if stock.subcategory else 'N/A',
                'location': stock.location.name if stock.location else 'N/A',
                'rack': stock.rack.rank_id if stock.rack else '',
                'box': stock.box.box_id if stock.box else '',
            },
            'racks': list(racks),
            'boxes': list(boxes),
            'barcodes': barcode_data,  # Now correctly formatted with image URLs
        }

        return render(request, "stock/update_stock.html", context)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            rack_id = data.get('rack')
            box_id = data.get('box')

            stock.rack = Rank.objects.get(rank_id=rack_id) if rack_id else None
            stock.box = Box.objects.get(box_id=box_id) if box_id else None
            stock.save()

            return JsonResponse({'message': 'Stock updated successfully!'}, status=200)

        except Rank.DoesNotExist:
            return JsonResponse({'error': 'Invalid rack selected'}, status=400)
        except Box.DoesNotExist:
            return JsonResponse({'error': 'Invalid box selected'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def stock_scan_page(request):
    return render(request, "scanstock/scan_stock.html")


def assign_list_page(request):
    return render(request, "assign/list_assign.html")


def assign_stock_page(request):
    return render(request, "assign/assign_stock.html")


def get_employees(request):
    employees = Employee.objects.all().values("employee_id", "name", "designation")
    return JsonResponse({"employees": list(employees)})  # Return all employees

def get_exhibitions(request):
    exhibitions = Exhibition.objects.all().values("exhibition_id", "exhibition_name", "city")
    return JsonResponse({"exhibitions": list(exhibitions)})


def get_companies(request):
    """
    Fetch all companies and return as JSON response.
    """
    companies = Company.objects.all().values("company_id", "company_name")
    return JsonResponse({"companies": list(companies)})


def get_customers(request):
    customers = Customer.objects.all().values('customer_id', 'customer_name', 'email', 'company_id', 'phone_number', 'address', 'city', 'state', 'zip_code', 'country', 'details')
    
    return JsonResponse({"customers": list(customers)})



def generate_employee_pdf(request):   
    # Get filter parameters from request
    employee_code = request.GET.get('employee_code', '').strip()
    employee_name = request.GET.get('employee_name', '').strip()
    work_location = request.GET.get('work_location', '')

    # Filter Employee data based on provided filters
    employees = Employee.objects.all()
    
    if employee_code:
        employees = employees.filter(employee_code__icontains=employee_code)
    if employee_name:
        employees = employees.filter(name__icontains=employee_name)
    if work_location:
        employees = employees.filter(work_location_id=work_location)
        
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="employee_details.pdf"'

    # Define page size
    page_width, page_height = A4

    # Create PDF Document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=0.7 * inch,  
        rightMargin=0.7 * inch,  
        topMargin=1.5 * inch,  
        bottomMargin=1.5 * inch  
    )

    elements = []
    styles = getSampleStyleSheet()

    # Define Custom Style for Paragraphs
    custom_normal = ParagraphStyle(
        'custom_normal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=14,  # Adjusted line spacing
        spaceAfter=8
    )

    # Load images
    header_path = os.path.join(settings.STATIC_ROOT, "assets/images/pdf/report_header.png")
    footer_path = os.path.join(settings.STATIC_ROOT, "assets/images/pdf/report_footer.png")

    # Get Current Date
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define Header/Footer Function
    def on_page(canvas, doc):
        width, height = A4

        # Draw header
        if os.path.exists(header_path):
            header_img = Image(header_path, width=width, height=1.5 * inch)
            header_img.drawOn(canvas, 0, height - 1.5 * inch)  

        # Draw footer
        if os.path.exists(footer_path):
            footer_img = Image(footer_path, width=width, height=1 * inch)
            footer_img.drawOn(canvas, 0, 0)  

        # Add Report Date/Time below header (Right-aligned)
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(width - 0.8 * inch, height - 1.7 * inch, f"Generated On: {report_date}")  

    # Define Page Template with Frames
    frame = Frame(
        x1=0.7 * inch, y1=1.5 * inch,  
        width=page_width - 1.4 * inch,  
        height=page_height - 3 * inch,  
        id='normal'
    )
    template = PageTemplate(id='custom', frames=frame, onPage=on_page)
    doc.addPageTemplates([template])

    # **Header Section with Increased Font Size and Margin**
    elements.append(Spacer(1, 45))  

    # Report Title (Centered, Larger Font)
    elements.append(Paragraph('<para align="center"><b><font size=16>EMPLOYEE DETAILS REPORT</font></b></para>', styles["Normal"]))
    elements.append(Spacer(1, 30))  

    # Date (Left-aligned, Proper Formatting)
    elements.append(Paragraph('<font size=12><b>Date:</b> {}</font>'.format(report_date), custom_normal))
    
    # Department (Left-aligned)
    elements.append(Paragraph('<font size=12><b>Department:</b> HR/Management</font>', custom_normal))

    # Subject & Description
    elements.append(Paragraph('<font size=12><b>Subject:</b> Employee Details Summary</font>', custom_normal))
    
    elements.append(Paragraph( 
        '<font size=11>Please find below the detailed report of employees. '
        'This report contains vital employee information, including personal details, '
        'job roles, and employment status.</font>', 
        custom_normal
    ))

    elements.append(Spacer(1, 10))  

    # **Table Title**
    elements.append(Paragraph("<strong>Employee Information Summary</strong>", styles["Heading3"]))
    elements.append(Spacer(1, 10))

    # **Table Headers**
    data = [["Code", "Name", "Designation", "Mobile", "Work Location"]]

    # Fetch Employees and Append to Table Data (Use already filtered employees)
    if employees.exists():  
        for emp in employees:
            data.append([
                emp.employee_code, emp.name, emp.designation,
                emp.mobile_number, str(emp.work_location) if emp.work_location else "N/A"  
            ])
    else:
        data.append(["No Data", "-", "-", "-", "-"])  

    # **Reduced Table Width**
    col_widths = [0.8 * inch, 1.8 * inch, 1.4 * inch, 1.3 * inch, 1.6 * inch]  
    row_height = 22  

    table = Table(data, colWidths=col_widths, rowHeights=row_height)

    # **Table Styling**
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  
        ('FONTSIZE', (0, 0), (-1, -1), 9),  
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),  
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  
        ('WORDWRAP', (0, 0), (-1, -1)),  
    ])
    table.setStyle(style)

    # Add Table to PDF
    elements.append(table)

    # **Add Note at the End**
    elements.append(Spacer(1, 15))  
    note = Paragraph("<strong>Note:</strong> This is a system-generated report. No manual modifications have been made.", custom_normal)
    elements.append(note)

    # Build PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response


def generate_employee_csv(request): 
    # Get filter parameters from request
    employee_code = request.GET.get('employee_code', '').strip()
    employee_name = request.GET.get('employee_name', '').strip()
    work_location = request.GET.get('work_location', '')

    # Filter Employee data based on provided filters
    employees = Employee.objects.all()
    
    if employee_code:
        employees = employees.filter(employee_code__icontains=employee_code)
    if employee_name:
        employees = employees.filter(name__icontains=employee_name)
    if work_location:
        employees = employees.filter(work_location_id=work_location)

    # Create CSV Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_details.csv"'

    writer = csv.writer(response)

    # Write CSV Header with additional fields
    writer.writerow([
        "Employee ID", "Employee Code", "Name", "Designation", "Address", "Location",
        "Work Location", "Date of Birth", "Mobile Number", "Email", 
        "Aadhaar Card", "PAN Card", "Created At", "Updated At"
    ])
    
    # Write Employee Data
    for emp in employees:
        writer.writerow([
            emp.employee_id,
            emp.employee_code,
            emp.name,
            emp.designation,
            emp.address,
            emp.location,
            emp.work_location.name if emp.work_location else "N/A",
            emp.date_of_birth.strftime('%Y-%m-%d'),  # Formatting Date of Birth
            emp.mobile_number,
            emp.email,
            emp.aadhaar_card,
            emp.pan_card if emp.pan_card else "N/A",
            emp.created_at.strftime('%Y-%m-%d %H:%M:%S'),  # Formatting DateTime
            emp.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response


def generate_employee_excel(request):
    # Get filter parameters from request
    employee_code = request.GET.get('employee_code', '').strip()
    employee_name = request.GET.get('employee_name', '').strip()
    work_location = request.GET.get('work_location', '')

    # Filter Employee data based on provided filters
    employees = Employee.objects.all()
    
    if employee_code:
        employees = employees.filter(employee_code__icontains=employee_code)
    if employee_name:
        employees = employees.filter(name__icontains=employee_name)
    if work_location:
        employees = employees.filter(work_location_id=work_location)

    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Employee Details"

    # Define Excel headers
    headers = [
        "Employee ID", "Employee Code", "Name", "Designation", "Address", "Location",
        "Work Location", "Date of Birth", "Mobile Number", "Email", 
        "Aadhaar Card", "PAN Card", "Created At", "Updated At"
    ]

    # Add headers to the first row with bold formatting
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = Font(bold=True)

    # Add Employee Data
    for row_num, emp in enumerate(employees, 2):
        ws.cell(row=row_num, column=1, value=emp.employee_id)
        ws.cell(row=row_num, column=2, value=emp.employee_code)
        ws.cell(row=row_num, column=3, value=emp.name)
        ws.cell(row=row_num, column=4, value=emp.designation)
        ws.cell(row=row_num, column=5, value=emp.address)
        ws.cell(row=row_num, column=6, value=emp.location)
        ws.cell(row=row_num, column=7, value=emp.work_location.name if emp.work_location else "N/A")
        ws.cell(row=row_num, column=8, value=emp.date_of_birth.strftime('%Y-%m-%d'))
        ws.cell(row=row_num, column=9, value=emp.mobile_number)
        ws.cell(row=row_num, column=10, value=emp.email)
        ws.cell(row=row_num, column=11, value=emp.aadhaar_card)
        ws.cell(row=row_num, column=12, value=emp.pan_card if emp.pan_card else "N/A")
        ws.cell(row=row_num, column=13, value=emp.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        ws.cell(row=row_num, column=14, value=emp.updated_at.strftime('%Y-%m-%d %H:%M:%S'))

    # Create HTTP response for file download
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="employee_details.xlsx"'
    
    # Save workbook to response
    wb.save(response)
    
    return response


def generate_location_csv(request):
    # Get filter parameters from request
    location_name = request.GET.get('location_name', '').strip()
    shortcode = request.GET.get('shortcode', '').strip()
    status = request.GET.get('status', '')

    # Filter Location data based on provided filters
    locations = Location.objects.all()
    
    if location_name:
        locations = locations.filter(name__icontains=location_name)
    if shortcode:
        locations = locations.filter(shortcode__icontains=shortcode)
    if status:
        locations = locations.filter(status=status)

    # Create CSV Response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="location_details.csv"'

    writer = csv.writer(response)

    # Write CSV Header
    writer.writerow(["Location ID", "Name", "Shortcode", "Details", "Status", "Created At"])

    # Write Location Data
    for loc in locations:
        writer.writerow([
            loc.id, loc.name, loc.shortcode, loc.details, loc.status,
            loc.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response


def generate_location_excel(request):
    # Get filter parameters from request
    location_name = request.GET.get('location_name', '').strip()
    shortcode = request.GET.get('shortcode', '').strip()
    status = request.GET.get('status', '')

    # Filter Location data
    locations = Location.objects.all()
    
    if location_name:
        locations = locations.filter(name__icontains=location_name)
    if shortcode:
        locations = locations.filter(shortcode__icontains=shortcode)
    if status:
        locations = locations.filter(status=status)

    # Create an Excel workbook and sheet
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Location Details"

    # Define headers
    headers = ["Location ID", "Name", "Shortcode", "Details", "Status", "Created At"]
    
    # Add headers to the first row (bold formatting)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = openpyxl.styles.Font(bold=True)

    # Add Location Data
    for row_num, loc in enumerate(locations, 2):
        ws.cell(row=row_num, column=1, value=loc.id)
        ws.cell(row=row_num, column=2, value=loc.name)
        ws.cell(row=row_num, column=3, value=loc.shortcode)
        ws.cell(row=row_num, column=4, value=loc.details)
        ws.cell(row=row_num, column=5, value=loc.status)
        ws.cell(row=row_num, column=6, value=loc.created_at.strftime('%Y-%m-%d %H:%M:%S'))

    # Create HTTP response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="location_details.xlsx"'
    
    # Save workbook to response
    wb.save(response)
    
    return response


def generate_location_pdf(request):
    # Get filter parameters
    name = request.GET.get('name', '').strip()
    shortcode = request.GET.get('shortcode', '').strip()
    status = request.GET.get('status', '')

    # Filter locations based on query parameters
    locations = Location.objects.all()
    if name:
        locations = locations.filter(name__icontains=name)
    if shortcode:
        locations = locations.filter(shortcode__icontains=shortcode)
    if status:
        locations = locations.filter(status=status)

    # Create response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="location_details.pdf"'

    # Define PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=1.5 * inch,
        bottomMargin=1.5 * inch
    )

    elements = []
    styles = getSampleStyleSheet()
    custom_normal = ParagraphStyle('custom_normal', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=8)

    # Load images (Header/Footer)
    header_path = os.path.join(settings.STATIC_ROOT, "assets/images/pdf/report_header.png")

    # Get current date/time
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def on_page(canvas, doc):
        width, height = A4
        if os.path.exists(header_path):
            header_img = Image(header_path, width=width, height=1.5 * inch)
            header_img.drawOn(canvas, 0, height - 1.5 * inch)

        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(width - 0.8 * inch, height - 1.7 * inch, f"Generated On: {report_date}")

    # Define Page Template with Frames
    frame = Frame(x1=0.7 * inch, y1=1.5 * inch, width=A4[0] - 1.4 * inch, height=A4[1] - 3 * inch, id='normal')
    template = PageTemplate(id='custom', frames=frame, onPage=on_page)
    doc.addPageTemplates([template])

    # Report Title
    elements.append(Spacer(1, 45))
    elements.append(Paragraph('<para align="center"><b><font size=16>LOCATION DETAILS REPORT</font></b></para>', styles["Normal"]))
    elements.append(Spacer(1, 30))

    # Report Date
    elements.append(Paragraph('<font size=11>This report contains the details of locations, including their names, shortcodes, and statues.</font>', custom_normal))
    elements.append(Spacer(1, 10))

    # Table Title
    elements.append(Paragraph("<strong>Location Information Summary</strong>", styles["Heading3"]))
    elements.append(Spacer(1, 10))

    # Table Headers
    data = [["Name", "Shortcode", "Details", "Status"]]

    # Add location data to the table
    if locations.exists():
        for location in locations:
            data.append([location.name, location.shortcode, location.details, location.get_status_display()])
    else:
        data.append(["No Data", "-", "-", "-"])

    # Define Table
    col_widths = [1.8 * inch, 1.0 * inch, 2.5 * inch, 1.2 * inch]
    row_height = 22
    table = Table(data, colWidths=col_widths, rowHeights=row_height)

    # Table Styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0, 0), (-1, -1)),
    ])
    table.setStyle(style)

    # Add Table to PDF
    elements.append(table)

    # Footer Note
    elements.append(Spacer(1, 15))
    note = Paragraph("<strong>Note:</strong> This is a system-generated report. No manual modifications have been made.", custom_normal)
    elements.append(note)

    # Build PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response


def generate_company_csv(request):
    # Get filter parameters
    company_name = request.GET.get('company_name', '').strip()
    location = request.GET.get('location', '').strip()

    # Filter company data
    companies = Company.objects.all()
    
    if company_name:
        companies = companies.filter(company_name__icontains=company_name)  # Fixed field name
    if location:
        companies = companies.filter(location__icontains=location)

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="company_details.csv"'

    writer = csv.writer(response)

    # Write CSV Header
    writer.writerow(["Company ID", "Company Name", "CIN Number", "GST Number", "Location", "Email", "Phone Number"])

    # Write Company Data
    for company in companies:
        writer.writerow([
            company.company_id,  # Use correct field
            company.company_name,  # Use correct field
            company.CIN_number,
            company.GST_number,
            company.location,
            company.email,
            company.phone_number
        ])

    return response

def generate_company_excel(request):
    # Get filter parameters
    company_name = request.GET.get('company_name', '').strip()
    location = request.GET.get('location', '').strip()

    # Filter company data
    companies = Company.objects.all()
    
    if company_name:
        companies = companies.filter(company_name__icontains=company_name)  # Fixed field name
    if location:
        companies = companies.filter(location__icontains=location)

    # Create an Excel workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Company Details"

    # Define headers
    headers = ["Company ID", "Company Name", "CIN Number", "GST Number", "Location", "Email", "Phone Number"]

    # Add headers to the first row (bold formatting)
    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = openpyxl.styles.Font(bold=True)

    # Add Company Data
    for row_num, company in enumerate(companies, 2):
        ws.cell(row=row_num, column=1, value=company.company_id)
        ws.cell(row=row_num, column=2, value=company.company_name)  # Fixed field name
        ws.cell(row=row_num, column=3, value=company.CIN_number)
        ws.cell(row=row_num, column=4, value=company.GST_number)
        ws.cell(row=row_num, column=5, value=company.location)
        ws.cell(row=row_num, column=6, value=company.email)
        ws.cell(row=row_num, column=7, value=company.phone_number)

    # Create HTTP response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename="company_details.xlsx"'

    # Save workbook to response
    wb.save(response)
    
    return response


def generate_company_pdf(request):
     # Get filter parameters
    print(f"Received GET parameters: {request.GET}")

    name = request.GET.get('company_name', '').strip()
    location = request.GET.get('location', '').strip()

    print(f"Filters received - Name: {name}, Location: {location}")

    companies = Company.objects.all()
    if name:
        print(f"Filtering by Name: {name}")
        companies = companies.filter(company_name__icontains=name)
    if location:
        print(f"Filtering by Location: {location}")
        companies = companies.filter(location__icontains=location)

    print(f"Filtered Companies Count: {companies.count()}")  
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="company_details.pdf"'

    # Define PDF document
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=1.5 * inch,
        bottomMargin=1.5 * inch
    )

    elements = []
    styles = getSampleStyleSheet()
    custom_normal = ParagraphStyle('custom_normal', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=14, spaceAfter=8)

    # Load images (Header/Footer)
    header_path = os.path.join(settings.STATIC_ROOT, "assets/images/pdf/report_header.png")

    # Get current date/time
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def on_page(canvas, doc):
        width, height = A4
        if os.path.exists(header_path):
            header_img = Image(header_path, width=width, height=1.5 * inch)
            header_img.drawOn(canvas, 0, height - 1.5 * inch)

        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(width - 0.8 * inch, height - 1.7 * inch, f"Generated On: {report_date}")

    # Define Page Template with Frames
    frame = Frame(x1=0.7 * inch, y1=1.5 * inch, width=A4[0] - 1.4 * inch, height=A4[1] - 3 * inch, id='normal')
    template = PageTemplate(id='custom', frames=frame, onPage=on_page)
    doc.addPageTemplates([template])

    # Report Title
    elements.append(Spacer(1, 45))
    elements.append(Paragraph('<para align="center"><b><font size=16>COMPANY DETAILS REPORT</font></b></para>', styles["Normal"]))
    elements.append(Spacer(1, 30))

    # Report Description
    elements.append(Paragraph('<font size=11>This report contains the details of companies, including their names, locations, emails, and phone numbers.</font>', custom_normal))
    elements.append(Spacer(1, 10))

    # Table Title
    elements.append(Paragraph("<strong>Company Information Summary</strong>", styles["Heading3"]))
    elements.append(Spacer(1, 10))

    # Table Headers
    data = [["ID", "Name", "Location", "Email", "Phone Number"]]

    # Add company data to the table
    if companies.exists():
        for company in companies:
            data.append([
                str(company.company_id), 
                company.company_name, 
                company.location, 
                company.email, 
                company.phone_number
            ])
    else:
        data.append(["No Data"] + ["-"] * 4)  # Adjusting for column count

    # Define Table
    col_widths = [0.8 * inch, 1.5 * inch, 1.5 * inch, 2.0 * inch, 1.5 * inch]
    row_height = 22
    table = Table(data, colWidths=col_widths, rowHeights=row_height)

    # Table Styling
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('WORDWRAP', (0, 0), (-1, -1)),
    ])
    table.setStyle(style)

    # Add Table to PDF
    elements.append(table)

    # Footer Note
    elements.append(Spacer(1, 15))
    note = Paragraph("<strong>Note:</strong> This is a system-generated report. No manual modifications have been made.", custom_normal)
    elements.append(note)

    # Build PDF
    doc.build(elements, onFirstPage=on_page, onLaterPages=on_page)

    return response

import traceback  # Import traceback module

import time
import random
import uuid
# def save_assigned_stock(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
            
#             assign_id = uuid.uuid4()
#             print("The product Assign Code Is : ",data)
#             for item in data:
#                 print("The item is:", item)
#                 stock_product = StockEntry.objects.get(stock_id=item['stockId'])
#                 product = stock_product.product
#                 assign_product_mode = item['assign_product_mode']
                
#                 assign_employee = None
#                 assign_company = None
#                 assign_exhibition = None
#                 assign_customer = None

#                 assign_stock_id = StockEntry.objects.get(stock_id=item['stockId'])
#                 if item['mode'] == "Users":
#                     assign_employee = Employee.objects.get(employee_id=item['relatedFields']['employee'])
#                 elif item['mode'] == "Company":
#                     assign_company = Company.objects.get(company_id=item['relatedFields']['company'])
#                 elif item['mode'] == "Exhibition":
#                     assign_exhibition = Exhibition.objects.get(exhibition_id=item['relatedFields']['exhibition'])
#                     assign_employee = Employee.objects.get(employee_id=item['relatedFields']['employee'])
#                 elif item['mode'] == "Customers":
#                     assign_customer = Customer.objects.get(customer_id=item['relatedFields']['customer'])
#                 else:
#                     raise ValueError("Invalid mode provided")

#                 # Create and save the AssignProduct instance
#                 assign_product = AssignProduct(
#                     assign_id=assign_id,
#                     stock_id = assign_stock_id,
#                     assign_mode = item['mode'],
#                     assign_product=product,
#                     assign_employee=assign_employee,
#                     assign_company=assign_company,
#                     assign_exhibition=assign_exhibition,
#                     assign_customer=assign_customer,
#                     assign_quantity=1,  # Assuming 1 quantity per item
#                     assign_customer_details=item['relatedFields'].get('customerDetails', ''),  # Optional field
#                     assign_at=timezone.now()
#                 )
#                 assign_product.save()

#                 return_assign_product = ReturnProductHistory(
#                     assign_return_id=assign_id,
#                     return_id = "",
#                     return_stock_id = assign_stock_id,
#                     return_mode = item['mode'],                                    
#                     return_product=product,
#                     return_employee=assign_employee,
#                     return_company=assign_company,
#                     return_exhibition=assign_exhibition,
#                     return_customer=assign_customer,
#                     return_quantity=0,  # Assuming 1 quantity per item
#                     return_customer_details=item['relatedFields'].get('customerDetails', ''),  # Optional field
#                     return_product_status = assign_product_mode,
#                     reuturn_assign_at=timezone.now(),
#                     return_at = "-",
#                 )
#                 return_assign_product.save()

#                 stock_product.product_status = assign_product_mode
#                 stock_product.save()
#             return JsonResponse({"success": True})
#         except Exception as e:
#             traceback_str = traceback.format_exc()
#             print("Traceback:", traceback_str)
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False, "error": "Invalid request method"})

from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings  # Import settings

def save_assigned_stock(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            assign_id = uuid.uuid4()
            print("The product Assign Code Is : ", data)

            # Dictionary to group products by user
            user_products = {}

            for item in data:
                print("The item is:", item)
                stock_product = StockEntry.objects.select_related(
                    'product',  # Fetch related product
                    'product__category',  # Fetch related category of the product
                    'product__subcategory'  # Fetch related subcategory of the product
                ).get(stock_id=item['stockId'])

                product = stock_product.product
                assign_product_mode = item['assign_product_mode']

                assign_employee = None
                assign_company = None
                assign_exhibition = None
                assign_customer = None

                assign_stock_id = stock_product
                if item['mode'] == "Users":
                    assign_employee = Employee.objects.get(employee_id=item['relatedFields']['employee'])
                    user_key = f"employee_{assign_employee.employee_id}"
                elif item['mode'] == "Company":
                    assign_company = Company.objects.get(company_id=item['relatedFields']['company'])
                    user_key = f"company_{assign_company.company_id}"
                elif item['mode'] == "Exhibition":
                    assign_exhibition = Exhibition.objects.get(exhibition_id=item['relatedFields']['exhibition'])
                    assign_employee = Employee.objects.get(employee_id=item['relatedFields']['employee'])
                    user_key = f"exhibition_{assign_exhibition.exhibition_id}"
                elif item['mode'] == "Customers":
                    assign_customer = Customer.objects.get(customer_id=item['relatedFields']['customer'])
                    user_key = f"customer_{assign_customer.customer_id}"
                else:
                    raise ValueError("Invalid mode provided")

                # Create and save the AssignProduct instance
                assign_product = AssignProduct(
                    assign_id=assign_id,
                    stock_id=assign_stock_id,
                    assign_mode=item['mode'],
                    assign_product=product,
                    assign_employee=assign_employee,
                    assign_company=assign_company,
                    assign_exhibition=assign_exhibition,
                    assign_customer=assign_customer,
                    assign_quantity=1,  # Assuming 1 quantity per item
                    assign_customer_details=item['relatedFields'].get('customerDetails', ''),  # Optional field
                    assign_at=timezone.now()
                )
                assign_product.save()

                return_assign_product = ReturnProductHistory(
                    assign_return_id=assign_id,
                    return_id="",
                    return_stock_id=assign_stock_id,
                    return_mode=item['mode'],
                    return_product=product,
                    return_employee=assign_employee,
                    return_company=assign_company,
                    return_exhibition=assign_exhibition,
                    return_customer=assign_customer,
                    return_quantity=0,  # Assuming 1 quantity per item
                    return_customer_details=item['relatedFields'].get('customerDetails', ''),  # Optional field
                    return_product_status=assign_product_mode,
                    reuturn_assign_at=timezone.now(),
                    return_at="-",
                )
                return_assign_product.save()

                stock_product.product_status = assign_product_mode
                stock_product.save()

                # Group products by user
                if user_key not in user_products:
                    user_products[user_key] = {
                        'user': assign_employee or assign_company or assign_exhibition or assign_customer,
                        'products': []
                    }
                user_products[user_key]['products'].append({
                    'product': product,
                    'stock_id': item['stockId'],
                    'barcode_text': item['barcodeText'],
                    'assign_product_mode': item['assign_product_mode']
                })

            # Send email to each user with their assigned products
            for user_key, user_data in user_products.items():
                user = user_data['user']
                products = user_data['products']

                # Prepare email content
                subject = "Your Assigned Products"
                html_message = render_to_string('assign_product_email.html', {
                    'user': user,
                    'products': products,  # Pass grouped products with item details
                    'assign_id': assign_id,
                })
                plain_message = strip_tags(html_message)
                from_email = settings.EMAIL_HOST_USER
                to_email = user.email  # Ensure the user model has an email field

                # Send email
                send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

            return JsonResponse({"success": True})
        except Exception as e:
            traceback_str = traceback.format_exc()
            print("Traceback:", traceback_str)
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@csrf_exempt
def get_all_assigned_data(request):
    category_id = request.GET.get("category")
    subcategory_id = request.GET.get("subcategory")
    product_id = request.GET.get("product")
    location_id = request.GET.get("location")
    mode = request.GET.get("mode")
    assigned_product_count = AssignProduct.objects.filter(assign_mode=mode).count()
    print("assigned_product_count",assigned_product_count)
    stock = AssignProduct.objects.filter(
        assign_product__category__category_id=category_id,
        assign_product__subcategory__subcategory_id=subcategory_id, 
        assign_product__product_id=product_id,
        stock_id__location = location_id,
        assign_mode = mode,
    )
    stock_data = []
    for entry in stock:
            entry_dict = {
                "assign_id": entry.assign_id,
                "product_name": entry.assign_product.product_name,
                "category_name": entry.assign_product.category.category_name,
                "subcategory_name": entry.assign_product.subcategory.subcategory_name,
                "assign_mode": entry.assign_mode,
                "product_status": entry.stock_id.product_status,
            }
            stock_data.append(entry_dict)
    return JsonResponse(stock_data, safe=False)

def return_stock(request):
    return render(request, "stock/stock_return.html")

@csrf_exempt
def get_assign_data_all(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            type = data.get("type")
            value = data.get("value")
            print("The Type Is:", type, "The Value Is:", value)
            assigned_products = []
            if type == "User":
                assign_type ="Users"
                assign_employee = AssignProduct.objects.filter(assign_employee__employee_id=value,assign_mode = assign_type)
                for i in assign_employee:
                    barcode_text = i.stock_id.barcodes.first().barcode_text if i.stock_id.barcodes.exists() else " - "
                    assigned_products.append({
                        "assign_id": i.assign_id,
                        "stock_id": i.stock_id.stock_id,
                        "barcode_text": barcode_text,
                        "product_name": i.assign_product.product_name,
                        "product_category": i.assign_product.category.category_name,
                        "product_subcategory": i.assign_product.subcategory.subcategory_name,
                        "employee_name": i.assign_employee.name,
                        "mode": assign_type,
                        "product_status": i.stock_id.product_status,
                        
                    })
            elif type == "Company":
                assign_company = AssignProduct.objects.filter(assign_company__company_id=value,assign_mode = type)
                for i in assign_company:
                    barcode_text = i.stock_id.barcodes.first().barcode_text if i.stock_id.barcodes.exists() else " - "
                    assigned_products.append({
                        "assign_id": i.assign_id,
                        "stock_id": i.stock_id.stock_id,
                        "barcode_text": barcode_text,
                        "product_name": i.assign_product.product_name,
                        "product_category": i.assign_product.category.category_name,
                        "product_subcategory": i.assign_product.subcategory.subcategory_name,
                        "company_name": i.assign_company.company_name,
                        "mode": type,
                        "product_status": i.stock_id.product_status,
                    })
            elif type == "Exhibition":
                try:
                    assign_exhibition = AssignProduct.objects.filter(assign_exhibition__exhibition_id=value,assign_mode = type)
                except:
                    assign_exhibition = AssignProduct.objects.filter(assign_mode = type)
                for i in assign_exhibition:
                    barcode_text = i.stock_id.barcodes.first().barcode_text if i.stock_id.barcodes.exists() else " - "
                    assigned_products.append({
                        "assign_id": i.assign_id,
                        "stock_id": i.stock_id.stock_id,
                        "barcode_text": barcode_text,
                        "product_name": i.assign_product.product_name,
                        "product_category": i.assign_product.category.category_name,
                        "product_subcategory": i.assign_product.subcategory.subcategory_name,
                        "exhibition_name": i.assign_exhibition.exhibition_name,
                        "mode": type,
                        "product_status": i.stock_id.product_status,
                        "employee_name": i.assign_employee.name,
                    })
            elif type == "Customer":
                assign_mode = "Customers"
                assign_customer = AssignProduct.objects.filter(assign_customer__customer_id=value,assign_mode = assign_mode)
                for i in assign_customer:
                    barcode_text = i.stock_id.barcodes.first().barcode_text if i.stock_id.barcodes.exists() else " - "
                    assigned_products.append({
                        "assign_id": i.assign_id,
                        "stock_id": i.stock_id.stock_id,
                        "barcode_text": barcode_text,
                        "product_name": i.assign_product.product_name,
                        "product_category": i.assign_product.category.category_name,
                        "product_subcategory": i.assign_product.subcategory.subcategory_name,
                        "customer_name": i.assign_customer.customer_name,
                        "mode": type,
                        "product_status": i.stock_id.product_status,
                    })
            elif type == "ALL":
                assign_employee = AssignProduct.objects.filter(assign_employee__employee_id=value)
                for i in assign_employee:
                    barcode_text = i.stock_id.barcodes.first().barcode_text if i.stock_id.barcodes.exists() else " - "
                    assigned_products.append({
                        "assign_id": i.assign_id,
                        "stock_id": i.stock_id.stock_id,
                        "barcode_text": barcode_text,
                        "product_name": i.assign_product.product_name,
                        "product_category": i.assign_product.category.category_name,
                        "product_subcategory": i.assign_product.subcategory.subcategory_name,
                        "employee_name": i.assign_employee.name,
                        "mode": i.assign_mode,
                        "product_status": i.stock_id.product_status,
                        "exhibition_name": i.assign_exhibition.exhibition_name if i.assign_exhibition else " - ",
                    })
            else:
                raise ValueError("Invalid type provided")
            # Return the assigned products in the response
            return JsonResponse({
                "status": "success",
                "type": type,
                "value": value,
                "assigned_products": assigned_products,  # Include assigned products data
            })
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
        except ValueError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)
    

@csrf_exempt
def update_product_status(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)
        stock_id = data.get("stock_id")
        product_status = data.get("product_status")
        assign_id = data.get("assign_id")
        if not stock_id or not product_status:
            return JsonResponse({"status": "error", "message": "Missing stock_id or product_status"}, status=400)

        print("--------------", stock_id, product_status,assign_id)

        if product_status == "RETURN":
            try:
                assign_product = AssignProduct.objects.get(stock_id=stock_id)
                return_stock_data, created = ReturnProductHistory.objects.get_or_create(return_stock_id=stock_id,assign_return_id=assign_id)
                return_stock_data.return_id = uuid.uuid4()
                return_stock_data.return_quantity = assign_product.assign_quantity
                return_stock_data.return_at = timezone.now()
                return_stock_data.reuturn_status = "Success"
                return_stock_data.save()

                product = StockEntry.objects.get(stock_id=stock_id)
                product.product_status = "INSTOCK"
                product.save()

                assign_product.delete()

                return JsonResponse({"status": "success", "message": "Product status updated and moved to return history successfully!"})
            except AssignProduct.DoesNotExist:
                print(traceback.format_exc())
                return JsonResponse({"status": "error", "message": "Product not found in AssignProduct"}, status=404)
            except StockEntry.DoesNotExist:
                print(traceback.format_exc())
                return JsonResponse({"status": "error", "message": "StockEntry not found"}, status=404)
        print(traceback.format_exc())
        return JsonResponse({"status": "success", "message": "Product status updated successfully!"})

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON data"}, status=400)
    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

def return_stock_history(request):
    return render(request, "stock/stock_return_history.html")
from django.db.models import Q


def get_return_history(request):
    # data = ReturnProductHistory.objects.filter(return_id__isnull=False)
    data = ReturnProductHistory.objects.filter(~Q(return_id__isnull=True) & ~Q(return_id=""))
    return_data = []
    for product in data:
        employee_name = product.return_employee.name if product.return_employee else ""
        if product.return_mode == "Exhibition":
            employee_name = (
                (product.return_employee.name if product.return_employee else "") +
                " - " +
                (product.return_exhibition.exhibition_name if product.return_exhibition else "")
            )
        elif product.return_mode == "Customers":
            employee_name = product.return_customer.customer_name if product.return_customer else None,
        elif product.return_mode == "Company":
            employee_name= product.return_company.company_name if product.return_company else None
        print("==========",employee_name)
        return_data.append({
            'return_id': product.return_id,
            'assign_return_id': product.assign_return_id,
            "barcode": product.return_stock_id.barcodes.first().barcode_text if product.return_stock_id.barcodes.exists() else " - ",
            'product_name': product.return_product.product_name,
            'employee_name': employee_name,
            'return_mode': product.return_mode,
            'reuturn_status': product.reuturn_status,
            'return_assign_status': product.return_product_status,
            'assign_return_id': product.assign_return_id,
            'return_product_status': product.return_product_status,
            'reuturn_assign_at': product.reuturn_assign_at if product.reuturn_assign_at else "",
            'return_at': product.return_at.strftime('%Y-%m-%d %H:%M:%S') if product.return_at else None,
        })
    
    return JsonResponse(return_data, safe=False)
import subprocess


@csrf_exempt
def receive_barcode(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            barcode = data.get('barcode')
            print(f"Received barcode: {barcode}")
            return JsonResponse({'status': 'success', 'barcode': barcode})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)





from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cv2
import os
from django.core.files.storage import default_storage

@csrf_exempt
def scan_qr_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Save the uploaded file temporarily
        file = request.FILES['image']
        file_name = default_storage.save(file.name, file)
        file_path = default_storage.path(file_name)

        # Read the image using OpenCV
        img = cv2.imread(file_path)

        if img is not None:
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(img)

            # Clean up the uploaded file
            default_storage.delete(file_name)

            if data:
                return JsonResponse({"qr_data": data})
            else:
                return JsonResponse({"error": "No QR code detected in the image!"}, status=400)
        else:
            return JsonResponse({"error": "Error reading the image!"}, status=400)
    else:
        return JsonResponse({"error": "No image provided!"}, status=400)

def scan_via_mobile(request):
    return render(request, "scanstock/scan_via_mobile.html")


latest_scanned_data = None

@csrf_exempt
def get_backend_data_scanned_data(request):
    global latest_scanned_data
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            qr_data = data.get('qr_data')
            system_ip_data = data.get('system_ip')
            get_temporary_ipv6 = data.get('get_temporary_ipv6')
            print("QR DATA : ",qr_data,"SYSTEM IP : ",system_ip_data,"get_temporary_ipv6",get_temporary_ipv6)
            if not qr_data:
                return JsonResponse({"status": "error", "message": "Missing 'qr_data' in request."}, status=400)
            if isinstance(qr_data, str):
                barcode_text = qr_data.split(":")[1].strip().split("\n")[0]  # Extract "PROD-000001-ELEC-BO-01"
            elif isinstance(qr_data, dict) and 'Barcode' in qr_data:
                barcode_text = qr_data['Barcode']
            else:
                return JsonResponse({"status": "error", "message": "Invalid 'qr_data' format."}, status=400)
            try:
                assign_product = AssignProduct.objects.get(stock_id__barcodes__barcode_text=barcode_text)
                if assign_product.assign_mode == "Users":
                    emp_name = assign_product.assign_employee.name
                elif assign_product.assign_mode == "Customer":
                    emp_name = assign_product.assign_customer.customer_name
                elif assign_product.assign_mode == "Exhibition":
                    emp_name = f"{assign_product.assign_employee.name} - {assign_product.assign_exhibition.exhibition_name}"
                elif assign_product.assign_mode == "Company":
                    emp_name = assign_product.assign_company.company_name
                else:
                    emp_name = None
                response_data = {
                    "barcode": barcode_text,
                    "stock_id": assign_product.stock_id.stock_id,
                    "product_name": assign_product.assign_product.product_name,
                    "product_category": assign_product.assign_product.category.category_name,
                    "product_subcategory": assign_product.assign_product.subcategory.subcategory_name,
                    "assign_mode": assign_product.assign_mode,
                    "assign_at": assign_product.assign_at,
                    "emp_name": emp_name,
                    "box": assign_product.stock_id.box.box_name,
                    "rack": assign_product.stock_id.rack.rank_name,
                    "product_status": assign_product.stock_id.product_status,
                    "location": assign_product.stock_id.location.name,
                    "from": "assign_product",
                    "system_ip": system_ip_data,
                }
            except AssignProduct.DoesNotExist:
                stock_entry = StockEntry.objects.get(barcodes__barcode_text=barcode_text)
                response_data = {
                    "barcode": barcode_text,
                    "stock_id": stock_entry.stock_id,
                    "product_name": stock_entry.product.product_name,
                    "product_category": stock_entry.product.category.category_name,
                    "product_subcategory": stock_entry.product.subcategory.subcategory_name,
                    "box": stock_entry.box.box_name,
                    "rack": stock_entry.rack.rank_name,
                    "product_status": stock_entry.product_status,
                    "location": stock_entry.location.name,
                    "from": "stock_entry",
                    "system_ip": system_ip_data,
                }
            html = render_to_string('scanstock/scan_barcode_data_table.html', {"data": response_data})
            latest_scanned_data = html  
            return JsonResponse({
                "status": "success",
                "message": "Data retrieved successfully",
                "data": response_data,
                "html": html 
            })
        except Exception as e:
            print("Error:", traceback.format_exc())
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method. Only POST is allowed."}, status=405)

@csrf_exempt
def get_latest_scanned_data(request):
    global latest_scanned_data
    if latest_scanned_data:
        return JsonResponse({
            "status": "success",
            "html": latest_scanned_data,
        })
    else:
        return JsonResponse({
            "status": "error",
            "message": "No data available.",
        })

def assign_exhibition(request):
    return render(request, "exhibition_operation/assign_exhibition.html")

def return_exhibition(request):
    return render(request, "exhibition_operation/return_exhibition.html")

def assign_operation_exhibition_list(request):
    return render(request, "exhibition_operation/assign_operation_exhibition_list.html")

def fetch_exhibition_list(request):
    exb_list = Exhibition.objects.all().values(
        'exhibition_id',
        'exhibition_name',
        'location',
        'city',
        'state',
        'start_date',
        'end_date'
    )
    return JsonResponse({
        "status": "success",
        "data": list(exb_list),
    })