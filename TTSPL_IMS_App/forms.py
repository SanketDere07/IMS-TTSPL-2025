from django import forms
from .models import Role, User, Profile, UserRole, UserPermission, Permission, DefaultRolePermission

# from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email',]

    password = forms.CharField(widget=forms.PasswordInput)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'mobile_no', 'company', 'location', 'role']


class UserRoleForm(forms.ModelForm):
    class Meta:
        model = UserRole
        fields = ['role']


class UserPermissionForm(forms.ModelForm):
    class Meta:
        model = UserPermission
        fields = ['permission']


class RoleForm(forms.ModelForm):
    users_permission = forms.BooleanField(required=False, label="Users")
    create_users_page_permission = forms.BooleanField(
        required=False, label="Create Users Page")
    create_users_add_permission = forms.BooleanField(
        required=False, label="Add Users Button")
    create_users_view_permission = forms.BooleanField(
        required=False, label="View Users Button")
    create_users_update_permission = forms.BooleanField(
        required=False, label="Update Users Button")
    create_users_delete_permission = forms.BooleanField(
        required=False, label="Delete Users Button")

    create_role_page_permission = forms.BooleanField(
        required=False, label="Create Role Page")
    create_role_add_permission = forms.BooleanField(
        required=False, label="Add Role Button")
    create_role_view_permission = forms.BooleanField(
        required=False, label="View Role Button")
    create_role_update_permission = forms.BooleanField(
        required=False, label="Update Role Button")
    create_role_delete_permission = forms.BooleanField(
        required=False, label="Delete Role Button")

    users_audit_log_permission = forms.BooleanField(
        required=False, label="Audit Logs Page")

    dashboard_permission = forms.BooleanField(required=False, label="Dashboard")
    dashboard_analytics_permission = forms.BooleanField(required=False, label="Dashboard Analytics")
    
    masters_permission = forms.BooleanField(required=False, label="Masters")
    employee_page_permission = forms.BooleanField(required=False, label="Employee Master")
    location_page_permission = forms.BooleanField(required=False, label="Location Master")
    company_page_permission = forms.BooleanField(required=False, label="Company Master")
    category_page_permission = forms.BooleanField(required=False, label="Category Master")
    subcategory_page_permission = forms.BooleanField(required=False, label="Subcategory Master")
    box_page_permission = forms.BooleanField(required=False, label="Box Master")
    rack_page_permission = forms.BooleanField(required=False, label="Rack Master")
    product_page_permission = forms.BooleanField(required=False, label="Product Master")
    customer_page_permission = forms.BooleanField(required=False, label="Customer Master")
    supplier_page_permission = forms.BooleanField(required=False, label="Supplier Master")
    exhibition_page_permission = forms.BooleanField(required=False, label="Exhibition Master")
    
    exhibition_permission = forms.BooleanField(required=False, label="Exhibition")
    exhibition_entry_permission = forms.BooleanField(required=False, label="Exhibition Entry")
    exhibition_return_page_permission = forms.BooleanField(required=False, label="Exhibition Return")
    
    operations_permission = forms.BooleanField(required=False, label="Exhibition")
    stock_entry_permission = forms.BooleanField(required=False, label="Stock Permission")
    scan_stock_page_permission = forms.BooleanField(required=False, label="Scan Stock")
    assign_stock_page_permission = forms.BooleanField(required=False, label="Assign Stock")
    process_stock_page_permission = forms.BooleanField(required=False, label="Process Stock")
    print_barcode_page_permission = forms.BooleanField(required=False, label="Print Stock")
    
    expense_permission = forms.BooleanField(required=False, label="Expense")
    add_expense_permission = forms.BooleanField(required=False, label="Add Expense")
    track_expense_permission = forms.BooleanField(required=False, label="Track Expense")
    verify_process_expense_permission = forms.BooleanField(required=False, label="Verify Expense")
    finance_process_expense_permission = forms.BooleanField(required=False, label="Finance Expense")
    
    report_permission = forms.BooleanField(required=False, label="Report")
    masters_report_permission = forms.BooleanField(required=False, label="Masters Report")
    operations_report_permission = forms.BooleanField(required=False, label="Operations Report")

    settings_permission = forms.BooleanField(required=False, label="Settings")
    general_setting_page_permission = forms.BooleanField(
        required=False, label="General Settings Page")
    backup_recovery_page_permission = forms.BooleanField(
        required=False, label="Backup Recovery Page")
    backup_recovery_import_permission = forms.BooleanField(
        required=False, label="Import Database")
    backup_recovery_export_permission = forms.BooleanField(
        required=False, label="Export Database")
    backup_recovery_scheduled_database_permission = forms.BooleanField(
        required=False, label="Scheduled Database")
    backup_recovery_add_scheduled_database_permission = forms.BooleanField(
        required=False, label="Add Scheduled Database")

    class Meta:
        model = Role
        fields = ['role_name', 'role_description']

    def __init__(self, *args, **kwargs):
        self.created_by = kwargs.pop('created_by', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        role = super().save(commit=False)
        if commit:
            role.save()
            role_permissions = {
                'Users': self.cleaned_data['users_permission'],
                'Create Users Page': self.cleaned_data['create_users_page_permission'],
                'Add Users Button': self.cleaned_data['create_users_add_permission'],
                'View Users Button': self.cleaned_data['create_users_view_permission'],
                'Update Users Button': self.cleaned_data['create_users_update_permission'],
                'Delete Users Button': self.cleaned_data['create_users_delete_permission'],

                'Create Role Page': self.cleaned_data['create_role_page_permission'],
                'Add Role Button': self.cleaned_data['create_role_add_permission'],
                'View Role Button': self.cleaned_data['create_role_view_permission'],
                'Update Role Button': self.cleaned_data['create_role_update_permission'],
                'Delete Role Button': self.cleaned_data['create_role_delete_permission'],

                'Audit Logs Page': self.cleaned_data['users_audit_log_permission'],

                'Dashboard': self.cleaned_data['dashboard_permission'],
                'Dashboard Analytics': self.cleaned_data['dashboard_analytics_permission'],
                
                'Masters': self.cleaned_data['masters_permission'],
                'Employee Master': self.cleaned_data['employee_page_permission'],
                'Location Master': self.cleaned_data['location_page_permission'],
                'Company Master': self.cleaned_data['company_page_permission'],
                'Category Master': self.cleaned_data['category_page_permission'],
                'Subcategory Master': self.cleaned_data['subcategory_page_permission'],
                'Box Master': self.cleaned_data['box_page_permission'],
                'Rack Master': self.cleaned_data['rack_page_permission'],
                'Product Master': self.cleaned_data['product_page_permission'],
                'Customer Master': self.cleaned_data['customer_page_permission'],
                'Supplier Master': self.cleaned_data['supplier_page_permission'],
                'Exhibition Master': self.cleaned_data['exhibition_page_permission'],
                
                'Exhibition': self.cleaned_data['exhibition_permission'],
                'Exhibition Entry': self.cleaned_data['exhibition_entry_permission'],
                'Exhibition Return': self.cleaned_data['exhibition_return_page_permission'],
                
                'Operations': self.cleaned_data['operations_permission'],
                'Stock Permission': self.cleaned_data['stock_entry_permission'],
                'Scan Stock': self.cleaned_data['scan_stock_page_permission'],
                'Assign Stock': self.cleaned_data['assign_stock_page_permission'],
                'Process Stock': self.cleaned_data['process_stock_page_permission'],
                'Print Stock': self.cleaned_data['print_barcode_page_permission'],
                
                'Expense': self.cleaned_data['expense_permission'],
                'Add Expense': self.cleaned_data['add_expense_permission'],
                'Track Expense': self.cleaned_data['track_expense_permission'],
                'Verify Expense': self.cleaned_data['verify_process_expense_permission'],
                'Finance Expense': self.cleaned_data['finance_process_expense_permission'],
                
                'Report': self.cleaned_data['report_permission'],
                'Masters Report': self.cleaned_data['masters_report_permission'],
                'Operations Report': self.cleaned_data['operations_report_permission'],

                'Settings': self.cleaned_data['settings_permission'],
                'General Settings Page': self.cleaned_data['general_setting_page_permission'],
                'Backup Recovery Page': self.cleaned_data['backup_recovery_page_permission'],
                'Import Database': self.cleaned_data['backup_recovery_import_permission'],
                'Export Database': self.cleaned_data['backup_recovery_export_permission'],
                'Scheduled Database': self.cleaned_data['backup_recovery_scheduled_database_permission'],
                'Add Scheduled Database': self.cleaned_data['backup_recovery_add_scheduled_database_permission'],

            }
            created_permissions = []
            for module_name, is_active in role_permissions.items():
                if is_active:
                    permission, created = Permission.objects.get_or_create(
                        module_name=module_name,
                        permission_name=f"View {module_name}",
                        defaults={'created_by': self.created_by}
                    )
                    DefaultRolePermission.objects.get_or_create(
                        role=role, permission=permission)
                    created_permissions.append(permission.permission_name)
            self.created_permissions = created_permissions
        return role
