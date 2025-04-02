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
    path('', views.login_view, name='login'),  # Root URL pattern
    path('logout/', views.logout_view, name='logout'),

    
    path('login_page', views.login_page, name='login-page'),
    path('reset_password_page', views.reset_password_page, name='reset-password-page'),


    path('send-reset-otp/', views.send_reset_otp, name='send_reset_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),



    path('dashboard_page', views.dashboard_page, name='dashboard-page'),
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
    path('generate-category-csv/',  views.generate_category_csv, name='generate_category_csv'),
    path('generate-category-excel/',  views.generate_category_excel, name='generate_category_excel'),
    path('generate-category-pdf/', views.generate_category_pdf, name='generate_category_pdf'),

    
    
    path('subcategory_list_page', views.subcategory_list_page, name='subcategory-list-page'),
    path('subcategory_add_page', views.subcategory_add_page, name='subcategory-add-page'),
    
    path('add-subcategory/', views.add_subcategory, name='add_subcategory'),
    path('get-categories/', views.get_categories, name='get_categories'),
    path('subcategory-list/', views.subcategory_list, name='subcategory_list'),
    path('view-subcategory/<int:subcategory_id>/', views.subcategory_view_page, name='subcategory_view_page'),
    path('update-subcategory/<int:id>/', views.subcategory_update_page, name='subcategory_update_page'),
    path('delete-subcategory/<int:id>/', views.delete_subcategory, name='delete_subcategory'),
    path('generate-subcategory-csv/', views.generate_subcategory_csv, name='generate_subcategory_csv'),
    path('generate-subcategory-excel/', views.generate_subcategory_excel, name='generate_subcategory_excel'),
    path('generate-subcategory-pdf/', views.generate_subcategory_pdf, name='generate_subcategory_pdf'),

    
    
    path('box_list_page', views.box_list_page, name='box-list-page'),
    path('box_add_page', views.box_add_page, name='box-add-page'),
    
    path('add-box/', views.add_box, name='add_box'),
    path('box-list/', views.box_list, name='box_list'),
    path('view-box/<int:box_id>/', views.box_view_page, name='box_view_page'),
    path('update-box/<int:id>/', views.box_update_page, name='box_update_page'),
    path('delete-box/<int:id>/', views.delete_box, name='delete_box'),
    path('generate-box-pdf/', views.generate_box_pdf, name='generate_box_pdf'),
    path('generate-box-csv/', views.generate_box_csv, name='generate_box_csv'),
    path('generate-box-excel/', views.generate_box_excel, name='generate_box_excel'),
    
    
    path('rank_list_page', views.rank_list_page, name='rank-list-page'),
    path('rank_add_page', views.rank_add_page, name='rank-add-page'),
    
    path('add-rank/', views.add_rank, name='add_rank'),
    path('rank-list/', views.rank_list, name='rank_list'),
    path('view-rank/<int:rank_id>/', views.rank_view_page, name='rank_view_page'),
    path('update-rank/<int:id>/', views.rank_update_page, name='rank_update_page'),
    path('delete-rank/<int:id>/', views.delete_rank, name='delete_rank'),
    path('generate-rank-csv/',  views.generate_rank_csv, name='generate_rank_csv'),
    path('generate-rank-excel/',  views.generate_rank_excel, name='generate_rank_excel'),
    path('generate-rank-pdf/', views.generate_rank_pdf, name='generate_rank_pdf'),


    path('product_list_page', views.product_list_page, name='product-list-page'),
    path('product_add_page', views.product_add_page, name='product-add-page'),
    
    path('add-product/', views.add_product, name='add_product'),
    path('get-subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get-products/', views.get_products, name='get_products'),
    path('search-products/', views.search_products, name='search_products'),

    path('view-product/<int:product_id>/', views.product_view_page, name='product_view_page'),
    path('update-product/<int:id>/', views.update_product, name='update_product'),
    path('delete-product/<int:id>/', views.delete_product, name='delete_product'),
    path('remove-product-image/<int:image_id>/', views.remove_product_image, name='remove_product_image'),
    path('generate-product-pdf/', views.generate_product_pdf, name='generate_product_pdf'),
    path('generate-product-csv/', views.generate_product_csv, name='generate_product_csv'),
    path('generate-product-excel/', views.generate_product_excel, name='generate_product_excel'),

    
    path('exhibition_list_page', views.exhibition_list_page, name='exhibition-list-page'),
    path('exhibition_add_page', views.exhibition_add_page, name='exhibition-add-page'),
    
    path('add-exhibition/', views.add_exhibition, name='add_exhibition'),
    path('exhibition-list/', views.exhibition_list, name='exhibition_list'),
    path('view-exhibition/<int:exhibition_id>/', views.exhibition_view_page, name='exhibition_view_page'),
    path('update-exhibition/<int:id>/', views.exhibition_update_page, name='exhibition_update_page'),
    path('delete-exhibition/<int:id>/', views.delete_exhibition, name='delete_exhibition'),
    path('generate-exhibition-pdf/', views.generate_exhibition_pdf, name='generate_exhibition_pdf'),
    path('generate-exhibition-csv/', views.generate_exhibition_csv, name='generate_exhibition_csv'),
    path('generate-exhibition-excel/', views.generate_exhibition_excel, name='generate_exhibition_excel'),
    
    
    path('customer_list_page', views.customer_list_page, name='customer-list-page'),
    path('customer_add_page', views.customer_add_page, name='customer-add-page'),
    
    path('add-customer/', views.add_customer, name='add_customer'), 
    path('get-companies/', views.get_companies, name='get_companies'),
    path('customer-list/', views.customer_list, name='customer_list'),
    path('view-customer/<int:customer_id>/', views.customer_view_page, name='customer_view_page'),
    path('update-customer/<int:id>/', views.customer_update_page, name='customer_update_page'),
    path('delete-customer/<int:id>/', views.delete_customer, name='delete_customer'),
    path('generate-customer-pdf/', views.generate_customer_pdf, name='generate_customer_pdf'),
    path('generate-customer-csv/', views.generate_customer_csv, name='generate_customer_csv'),
    path('generate-customer-excel/', views.generate_customer_excel, name='generate_customer_excel'),
    
    path('supplier_list_page', views.supplier_list_page, name='supplier-list-page'),
    path('supplier_add_page', views.supplier_add_page, name='supplier-add-page'),
    
    path('add-supplier/', views.add_supplier, name='add_supplier'), 
    path('supplier-list/', views.supplier_list, name='supplier_list'),
    path('view-supplier/<int:supplier_id>/', views.supplier_view_page, name='supplier_view_page'),
    path('update-supplier/<int:id>/', views.supplier_update_page, name='supplier_update_page'),
    path('delete-supplier/<int:id>/', views.delete_supplier, name='delete_supplier'),
    path('generate-supplier-pdf/', views.generate_supplier_pdf, name='generate_supplier_pdf'),
    path('generate-supplier-csv/', views.generate_supplier_csv, name='generate_supplier_csv'),
    path('generate-supplier-excel/', views.generate_supplier_excel, name='generate_supplier_excel'),
    
    
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

    path('print_barcode_page', views.print_barcode_page, name='print-barcode-page'),
    path('generate-barcode-pdf/', views.generate_barcode_pdf, name='generate_barcode_pdf'),
    path('generate-barcode-details-pdf/', views.generate_barcode_details_pdf, name='generate_barcode_details_pdf'),


    path('create_user_page', views.create_user_page, name='create-user-page'),
    path('user_list_page', views.user_list_page, name='assign-list-page'),

    path('add_user', views.add_user, name='add_user'),
    path('user-list/', views.user_list, name='user_list'),
    path('get_user_data/', views.get_user_data, name='get_user_data'),
    path('get_user_details/<int:user_id>/', views.get_user_details, name='get_user_details'),
    path('update_user/', views.update_user, name='update_user'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('generate-user-csv/', views.generate_user_csv, name='generate_user_csv'),
    path('generate-user-excel/', views.generate_user_excel, name='generate_user_excel'),
    path('generate-user-pdf/',  views.generate_user_pdf, name='generate_user_pdf'),

    

    path('create_rol_permission_page', views.create_rol_permission_page, name='create-rol-permission-page'),
    path('rol_permission_list_page', views.rol_permission_list_page, name='rol-permission-list-page'),
    path('add_role/', views.add_role, name='add_role'),
    path('get_roles/', views.get_roles, name='get_roles'),
    path('fetch_role_permission_datatable_data/', views.fetch_role_permission_datatable_data, name='fetch_role_permission_datatable_data'),
    path('get_role_details/<int:role_id>/', views.get_role_details, name='get_role_details'),
    path('get_role_update_details/<int:role_id>/', views.get_role_update_details, name='get_role_update_details'),
    path('update_role/<int:role_id>/', views.update_role, name='update_role'),
    path('delete_role/', views.delete_role, name='delete_role'),
    path('generate-role-permission-csv/', views.generate_role_permission_csv, name='generate_role_permission_csv'),
    path('generate-role-permission-excel/', views.generate_role_permission_excel, name='generate_role_permission_excel'),
    path('generate-role-permission-pdf/', views.generate_role_permission_pdf, name='generate_role_permission_pdf'),



    path('others_settings_page', views.others_settings_page, name='others-settings-page'),
    path('save-secondary-email-config/', views.save_secondary_email_config, name='save_secondary_email_config'),

    path('audit_logs', views.audit_logs, name='audit-logs-page'),
    path('get_filter_options_users/', views.get_filter_options_users, name='get_filter_options_users'),
    path('get_user_audit_logs/', views.get_user_audit_logs, name='get_user_audit_logs'),
    path('generate-user-audit-pdf/', views.generate_user_audit_pdf, name='generate_user_audit_pdf'),
    path('generate-audit-log-csv/', views.generate_audit_log_csv, name='generate_audit_log_csv'),
    path('generate-audit-log-excel/', views.generate_audit_log_excel, name='generate_audit_log_excel'),


    path('get_role_permission_audit_logs/', views.get_role_permission_audit_logs, name='get_role_permission_audit_logs'),
    path('get_filter_options_role_permissions/', views.get_filter_options_role_permissions, name='get_filter_options_role_permissions'),
    path('generate-role-permission-audit-csv/', views.generate_role_permission_audit_csv, name='generate_role_permission_audit_csv'),
    path('generate-role-permission-audit-excel/', views.generate_role_permission_audit_excel, name='generate_role_permission_audit_excel'),
    path('generate-role-permission-audit-pdf/', views.generate_role_permission_audit_pdf, name='generate_role_permission_audit_pdf'),




    path('backup_recovery_page', views.backup_recovery_page, name='backup-recovery-page'),
    path('get-tables/', views.get_tables_ajax, name='get_tables_ajax'),
    path('fetch-backup-details/', views.fetch_backup_details, name='fetch_backup_details'),
    path('import_db/', views.import_db, name='import_db'),
    path('export-db/', views.export_db, name='export_db'),
    path('schedule-backup/', views.schedule_backup, name='schedule_backup'),
    path('get-scheduled-backups/', views.get_scheduled_backups, name='get_scheduled_backups'),
    path('download-sql/<int:backup_id>/', views.download_sql_file, name='download_sql_file'),
    path('download-txt/<int:backup_id>/', views.download_txt_file, name='download_txt_file'),



    path('master_reports_page', views.master_reports_page, name='master-reports-page'),
    path('report-generate-employee-csv/', views.report_generate_employee_csv, name='report_generate_employee_csv'),
    path('report-generate-employee-excel/', views.report_generate_employee_excel, name='report_generate_employee_excel'),
    path('report-generate-employee-pdf/', views.report_generate_employee_pdf, name='report_generate_employee_pdf'),
    
    path('get_locations_filter/', views.get_locations_filter, name='get_locations_filter'),
    path('report-generate-location-csv/', views.report_generate_location_csv, name='report_generate_location_csv'),
    path('report-generate-location-excel/', views.report_generate_location_excel, name='report_generate_location_excel'),
    path('report-generate-location-pdf/', views.report_generate_location_pdf, name='report_generate_location_pdf'),

    path('get-companies-filter/', views.get_companies_filter, name='get_companies_filter'),
    path('report-generate-company-pdf/', views.report_generate_company_pdf, name='report_generate_company_pdf'),
    path('report-generate-company-csv/', views.report_generate_company_csv, name='report_generate_company_csv'),
    path('report-generate-company-excel/', views.report_generate_company_excel, name='report_generate_company_excel'),


    path('get_exhibitions_filter/', views.get_exhibitions_filter, name='get_exhibitions_filter'),
    path('get_locations_exhibition_filter/', views.get_locations_exhibition_filter, name='get_locations_exhibition_filter'),
    path('report-generate-exhibition-pdf/', views.report_generate_exhibition_pdf, name='report_generate_exhibition_pdf'),
    path('report-generate-exhibition-csv/', views.report_generate_exhibition_csv, name='report_generate_exhibition_csv'),
    path('report-generate-exhibition-excel/', views.report_generate_exhibition_excel, name='report_generate_exhibition_excel'),
    
    path('get_customers_filter/', views.get_customers_filter, name='get_customers_filter'),
    path('report-generate-customer-pdf/', views.report_generate_customer_pdf, name='report_generate_customer_pdf'),
    path('report-generate-customer-csv/', views.report_generate_customer_csv, name='report_generate_customer_csv'),
    path('report-generate-customer-excel/', views.report_generate_customer_excel, name='report_generate_customer_excel'),
    
    
    path('get_suppliers_filter/', views.get_suppliers_filter, name='get_suppliers_filter'),
    path('report-generate-supplier-pdf/', views.report_generate_supplier_pdf, name='report_generate_supplier_pdf'),
    path('report-generate-supplier-csv/', views.report_generate_supplier_csv, name='report_generate_supplier_csv'),
    path('report-generate-supplier-excel/', views.report_generate_supplier_excel, name='report_generate_supplier_excel'),
    
    path('get_products_filter/', views.get_products_filter, name='get_products_filter'),
    path('get_categories_filter/', views.get_categories_filter, name='get_categories_filter'),
    path('get_subcategories_filter/', views.get_subcategories_filter, name='get_subcategories_filter'),
    path('report-generate-product-csv/', views.report_generate_product_csv, name='report_generate_product_csv'),
    path('report-generate-product-excel/', views.report_generate_product_excel, name='report_generate_product_excel'),
    path('report-generate-product-pdf/', views.report_generate_product_pdf, name='report_generate_product_pdf'),
    
    path('user_profile_page', views.user_profile_page, name='user-profile-page'),
    path('get-user-data/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('update-user-profile/<int:user_id>/', views.update_user_profile, name='update_user_profile'),   

    path('save_expense/', views.save_expense, name='save_expense'),
    path('get_employee_details/', views.get_employee_details, name='get_employee_details'),











] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




