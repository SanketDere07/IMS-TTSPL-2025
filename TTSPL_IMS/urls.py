"""
URL configuration for TTSPL_IMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from TTSPL_IMS_App import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_page, name='dashboard-page'),
    path('location_list_page', views.location_list_page, name='location-list-page'),
    path('location_add_page', views.location_add_page, name='location-add-page'),

    path('add-location/', views.add_location, name='add_location'),
    path('get-locations/', views.get_locations, name='get_locations'),
    path('view-location/<int:location_id>/', views.location_view_page, name='location_view_page'),
    path('update-location/<int:id>/', views.location_update_page, name='location_update_page'),
    path('delete-location/<int:id>/', views.delete_location, name='delete_location'),
    path('generate-location-pdf/', views.generate_location_pdf, name='generate_location_pdf'),
    path('generate-location-csv/', views.generate_location_csv, name='generate_location_csv'),
    path('generate-location-excel/', views.generate_location_excel, name='generate_location_excel'),

    
    path('employee_add_page', views.employee_add_page, name='employee-add-page'),
    path('employee_list_page', views.employee_list_page, name='employee-list-page'),

    path('add-employee/', views.add_employee, name='add_employee'),
    path('get-work-locations/', views.get_work_locations, name='get_work_locations'),
    path('employee-list/', views.employee_list, name='employee_list'),
    path('view-employee/<int:employee_id>/', views.employee_view_page, name='employee_view_page'),
    path('update-employee/<int:id>/', views.employee_update_page, name='employee_update_page'),
    path('delete-employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('generate-employee-pdf/', views.generate_employee_pdf, name='generate_employee_pdf'),
    path('generate-employee-csv/', views.generate_employee_csv, name='generate_employee_csv'),
    path('generate-employee-excel/', views.generate_employee_excel, name='generate_employee_excel'),


    path('company_list_page', views.company_list_page, name='company-list-page'),
    path('company_add_page', views.company_add_page, name='company-add-page'),
    
    path('add-company/', views.add_company, name='add_company'),
    path('company-list/', views.company_list, name='company_list'),
    path('view-company/<int:company_id>/', views.company_view_page, name='company_view_page'),
    path('update-company/<int:id>/', views.company_update_page, name='company_update_page'),
    path('delete-company/<int:id>/', views.delete_company, name='delete_company'),
    path('generate-company-csv/', views.generate_company_csv, name='generate_company_csv'),
    path('generate-company-excel/', views.generate_company_excel, name='generate_company_excel'),
    path('generate-company-pdf/', views.generate_company_pdf, name='generate_company_pdf'),

    
    
    path('category_list_page', views.category_list_page, name='category-list-page'),
    path('category_add_page', views.category_add_page, name='category-add-page'),
    
    path('add-category/', views.add_category, name='add_category'),
    path('category-list/', views.category_list, name='category_list'),
    path('view-category/<int:category_id>/', views.category_view_page, name='category_view_page'),
    path('update-category/<int:id>/', views.category_update_page, name='category_update_page'),
    path('delete-category/<int:id>/', views.delete_category, name='delete_category'),
    
    
    path('subcategory_list_page', views.subcategory_list_page, name='subcategory-list-page'),
    path('subcategory_add_page', views.subcategory_add_page, name='subcategory-add-page'),
    
    path('add-subcategory/', views.add_subcategory, name='add_subcategory'),
    path('get-categories/', views.get_categories, name='get_categories'),
    path('subcategory-list/', views.subcategory_list, name='subcategory_list'),
    path('view-subcategory/<int:subcategory_id>/', views.subcategory_view_page, name='subcategory_view_page'),
    path('update-subcategory/<int:id>/', views.subcategory_update_page, name='subcategory_update_page'),
    path('delete-subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    
    
    path('box_list_page', views.box_list_page, name='box-list-page'),
    path('box_add_page', views.box_add_page, name='box-add-page'),
    
    path('add-box/', views.add_box, name='add_box'),
    path('box-list/', views.box_list, name='box_list'),
    path('view-box/<int:box_id>/', views.box_view_page, name='box_view_page'),
    path('update-box/<int:id>/', views.box_update_page, name='box_update_page'),
    path('delete-box/<int:id>/', views.delete_box, name='delete_box'),
    
    
    path('rank_list_page', views.rank_list_page, name='rank-list-page'),
    path('rank_add_page', views.rank_add_page, name='rank-add-page'),
    
    path('add-rank/', views.add_rank, name='add_rank'),
    path('rank-list/', views.rank_list, name='rank_list'),
    path('view-rank/<int:rank_id>/', views.rank_view_page, name='rank_view_page'),
    path('update-rank/<int:id>/', views.rank_update_page, name='rank_update_page'),
    path('delete-rank/<int:id>/', views.delete_rank, name='delete_rank'),
    
    path('product_list_page', views.product_list_page, name='product-list-page'),
    path('product_add_page', views.product_add_page, name='product-add-page'),
    
    path('add-product/', views.add_product, name='add_product'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get-products/', views.get_products, name='get_products'),
    path('view-product/<int:product_id>/', views.product_view_page, name='product_view_page'),
    path('update-product/<int:id>/', views.update_product, name='update_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('remove-product-image/<int:image_id>/', views.remove_product_image, name='remove_product_image'),

    
    path('exhibition_list_page', views.exhibition_list_page, name='exhibition-list-page'),
    path('exhibition_add_page', views.exhibition_add_page, name='exhibition-add-page'),
    
    path('add-exhibition/', views.add_exhibition, name='add_exhibition'),
    path('exhibition-list/', views.exhibition_list, name='exhibition_list'),
    path('view-exhibition/<int:exhibition_id>/', views.exhibition_view_page, name='exhibition_view_page'),
    path('update-exhibition/<int:id>/', views.exhibition_update_page, name='exhibition_update_page'),
    path('delete-exhibition/<int:id>/', views.delete_exhibition, name='delete_exhibition'),
    
    
    path('customer_list_page', views.customer_list_page, name='customer-list-page'),
    path('customer_add_page', views.customer_add_page, name='customer-add-page'),
    
    path('add-customer/', views.add_customer, name='add_customer'), 
    path('get-companies/', views.get_companies, name='get_companies'),
    path('customer-list/', views.customer_list, name='customer_list'),
    path('view-customer/<int:customer_id>/', views.customer_view_page, name='customer_view_page'),
    path('update-customer/<int:id>/', views.customer_update_page, name='customer_update_page'),
    path('delete-customer/<int:id>/', views.delete_customer, name='delete_customer'),
    
    path('supplier_list_page', views.supplier_list_page, name='supplier-list-page'),
    path('supplier_add_page', views.supplier_add_page, name='supplier-add-page'),
    
    path('add-supplier/', views.add_supplier, name='add_supplier'), 
    path('supplier-list/', views.supplier_list, name='supplier_list'),
    path('view-supplier/<int:supplier_id>/', views.supplier_view_page, name='supplier_view_page'),
    path('update-supplier/<int:id>/', views.supplier_update_page, name='supplier_update_page'),
    path('delete-supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),
    
    
    path('stock_entry_page', views.stock_entry_page, name='stock-add-page'),
    path('stock_list_page', views.stock_list_page, name='stock-list-page'),
    path('get-products-stock/<int:subcategory_id>/', views.get_products_stock, name='get_products_stock'),
    path('get-locations-entry/', views.get_locations_entry, name='get_locations_entry'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('submit-stock/', views.submit_stock, name='submit_stock'),
    path('delete_temp_barcode/', views.delete_temp_barcode, name='delete_temp_barcode'),
    path('remove-barcode/', views.remove_barcode, name='remove_barcode'),
    path('get-boxes/', views.get_boxes, name='get_boxes'),
    path('get-ranks/', views.get_ranks, name='get_ranks'),
    path('fetch-barcode/', views.fetch_barcode, name='fetch_barcode'),
    path('stock_entry_fetch_barcode/', views.stock_entry_fetch_barcode, name='stock_entry_fetch_barcode'),
    path("delete-stock/<int:stock_id>/", views.delete_stock, name="delete_stock"),
    path('update-stock/', views.update_stock, name='update_stock'),
    path('get-existing-barcodes/', views.get_existing_barcodes, name='get_existing_barcodes'), 
    path("fetch-stock-list/", views.fetch_stock_list, name="fetch_stock_list"),
    path('view-stock/<int:stock_id>/', views.stock_view_page, name='stock_view_page'),
    path('update-stock-page/<int:stock_id>/', views.stock_update_page, name='update_stock_page'),
    
    
    path('stock_scan_page', views.stock_scan_page, name='stock-scan-page'),
    path('assign_list_page', views.assign_list_page, name='assign-list-page'),
    path('assign_stock_page', views.assign_stock_page, name='assign-stock-page'),
    path("get-employees/", views.get_employees, name="get_employees"),
    path('get-exhibitions/', views.get_exhibitions, name='get_exhibitions'),
    path("get_companies/", views.get_companies, name="get_companies"),
    path('get-customers/', views.get_customers, name='get_customers'),


    path("save_assigned_stock/", views.save_assigned_stock, name="save_assigned_stock"),
    path('return_stock/', views.return_stock, name='return_stock'),
    path("get_all_assigned_data/", views.get_all_assigned_data, name="get_all_assigned_data"),
    path("get_assign_data_all/", views.get_assign_data_all, name="get_assign_data_all"),
    path('update_product_status/', views.update_product_status, name='update_product_status'),
    path('return_stock_history/', views.return_stock_history, name='return_stock_history'),
    path('get_return_history/', views.get_return_history, name='get_return_history'),

    path('api/receive_barcode/', views.receive_barcode, name='receive_barcode'),
    path('scan_qr_image/', views.scan_qr_image, name='scan_qr_image'),
    path('scan_via_mobile/', views.scan_via_mobile, name='scan_via_mobile'),
    path('get_backend_data_scanned_data/', views.get_backend_data_scanned_data, name='get_backend_data_scanned_data'),
    path('get_latest_scanned_data/', views.get_latest_scanned_data, name='get_latest_scanned_data'),
    path('assign_exhibition/', views.assign_exhibition, name='assign_exhibition'),
    path('return_exhibition/', views.return_exhibition, name='return_exhibition'),
    path('assign_operation_exhibition_list/', views.assign_operation_exhibition_list, name='assign_operation_exhibition_list'),
    path('fetch_exhibition_list/', views.fetch_exhibition_list, name='fetch_exhibition_list'),






] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




