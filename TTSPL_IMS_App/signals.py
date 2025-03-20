from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from .models import User, Permission 

DEFAULT_PERMISSIONS = [
    'Users',
    'Create Users Page',
    'Add Users Button',
    'View Users Button',
    'Update Users Button',
    'Delete Users Button',
    'Create Role Page',
    'Add Role Button',
    'View Role Button',
    'Update Role Button',
    'Delete Role Button',
    'Audit Logs Page',
    
    'Dashboard',
    'Dashboard Analytics',

    'Masters',
    'Employee Master',
    'Location Master',
    'Company Master',
    'Category Master',
    'Subcategory Master',
    'Box Master',
    'Rack Master',
    'Product Master',
    'Customer Master',
    'Supplier Master',
    'Exhibition Master',

    'Exhibition',
    'Exhibition Entry',
    'Exhibition Return',

    'Operations',
    'Stock Permission',
    'Scan Stock',
    'Assign Stock',
    'Process Stock',
    'Print Stock',

    'Expense',
    'Add Expense',
    'Track Expense',
    'Verify Expense',
    'Finance Expense',

    'Report',
    'Masters Report',
    'Operations Report',
   
    'Settings',
    'General Settings Page',
    'Backup Recovery Page',
    'Import Database',
    'Export Database',
    'Scheduled Database',
    'Add Scheduled Database',
    'Others Settings Page',
]

def create_default_permissions(sender, **kwargs):
    try:
        superuser = User.objects.get(is_superuser=True)
    except User.DoesNotExist:
        print("No superuser found!")
        return

    for permission_name in DEFAULT_PERMISSIONS:
        permission, created = Permission.objects.get_or_create(
            module_name=permission_name,
            permission_name=f"View {permission_name}",
            defaults={
                'is_active': True,
                'created_at': timezone.now(),  # Set created_at to current time
                'created_by': superuser  # Set created_by to the superuser
            }
        )
        
        if created:
            print(f'Permission "{permission.permission_name}" created.')
        else:
            print(f'Permission "{permission.permission_name}" already exists.')

@receiver(post_migrate)
def setup_permissions(sender, **kwargs):
    if sender.name == 'TTSPL_IMS_App': 
        create_default_permissions(sender)
