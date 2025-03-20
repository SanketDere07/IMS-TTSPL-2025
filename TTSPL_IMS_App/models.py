from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

# Create your models here.

# ----------------------- User, Role, Permission ------------------------------------------------------------------------------------------------

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email,
                          username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)  # Store OTP
    otp_generated_time = models.DateTimeField(
        null=True, blank=True)  # Store OTP generation time

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Add any additional required fields here

    def __str__(self):
        return self.email

    def has_permission(self, permission_name):
        """Check if the user has a specific permission."""
        if self.is_superuser:
            return True

        # Get all roles for this user
        user_roles = self.userrole_set.values_list('role_id', flat=True)

        # Check if any of the user's roles have the permission
        return DefaultRolePermission.objects.filter(
            role_id__in=user_roles,
            permission__permission_name=permission_name
        ).exists()

    def has_role(self, role_name):
        """Check if the user has a specific role."""
        return self.userrole_set.filter(role__role_name=role_name).exists()

# ------------------------------UserLog----------------------------------------------------------#


class UserAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    username = models.CharField(max_length=150)
    date = models.DateField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # Update last_login and log the login action
    user_audit_log = UserAuditLog.objects.create(
        user=user,
        action='Login',
        details='User logged in',
        username=user.username,
        last_login=user.last_login,
    )
    user_audit_log.save()


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    # Log the logout action
    user_audit_log = UserAuditLog.objects.create(
        user=user,
        action='Logout',
        details='User logged out',
        username=user.username,
        last_login=user.last_login,
    )
    user_audit_log.save()


class Permission(models.Model):
    module_name = models.CharField(max_length=255, null=True, blank=True)
    permission_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_permissions')

    def __str__(self):
        return self.permission_name

    def save(self, *args, **kwargs):
        if not self.permission_name and self.module_name:
            self.permission_name = f"View {self.module_name}"
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser


class Role(models.Model):
    role_name = models.CharField(max_length=255)
    role_description = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_roles')
    permissions = models.ManyToManyField(Permission, related_name='roles')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.role_name


class Profile(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15, null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, related_name='profiles')
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.user.email


class UserAddress(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='addresses')
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address1}, {self.city}, {self.state}, {self.zip_code}"


class UserSession(models.Model):
    user = models.OneToOneField(
        'User', on_delete=models.CASCADE, related_name='user_session')
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.session_key}'


class UserRole(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.user.email} - {self.role.name}'


class UserPermission(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.user.email} - {self.permission.name}'


class DefaultRolePermission(models.Model):
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now, editable=False)


class RolePermissionAuditLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()
    date = models.DateField(auto_now_add=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    permission = models.CharField(max_length=4024, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f'{self.user.username} - {self.action} - {self.role or ""} - {self.permission or ""} - {self.timestamp}'
    

class SecondaryEmailConfig(models.Model):
    host = models.CharField(max_length=255)
    port = models.PositiveIntegerField()
    use_tls = models.BooleanField(default=False)
    host_user = models.EmailField()
    host_password = models.CharField(max_length=255)
    default_from_email = models.EmailField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)


    def __str__(self):
        return f'Secondary Email Config: {self.host_user}'
    

    
class Location(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    )

    name = models.CharField(max_length=255)
    details = models.TextField()
    shortcode = models.CharField(max_length=10, unique=True)  # New field for shortcodes
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.shortcode})"


    
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)  # Auto-generate Employee ID
    employee_code = models.CharField(max_length=10, unique=True)  # Employee code (auto-generated or manual)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    address = models.TextField()
    location = models.CharField(max_length=100)
    work_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, null=True, related_name='employee_work_location'
    ) 
    date_of_birth = models.DateField()
    mobile_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    aadhaar_card = models.CharField(max_length=12, unique=True)
    pan_card = models.CharField(max_length=10, blank=True, null=True)    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.name}"
    
    
class Company(models.Model):
    company_id = models.AutoField(primary_key=True) 
    company_name = models.CharField(max_length=150)
    CIN_number = models.CharField(max_length=21, unique=True) 
    GST_number = models.CharField(max_length=15, unique=True)  
    location = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.company_id} - {self.company_name}"
    
    
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=150, unique=True)
    details = models.TextField()
    shortcode = models.CharField(max_length=10, unique=True, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category_id} - {self.category_name}"
    
    
class SubCategory(models.Model):
    subcategory_id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='subcategories')
    subcategory_name = models.CharField(max_length=150, unique=True)
    shortcode = models.CharField(max_length=4, unique=True)  
    details = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subcategory_id} - {self.subcategory_name} (Category: {self.category.category_name})"
    
    
class Box(models.Model):
    box_id = models.AutoField(primary_key=True)
    box_name = models.CharField(max_length=150, unique=True)
    details = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.box_id} - {self.box_name}"
    
    
class Rank(models.Model):
    rank_id = models.AutoField(primary_key=True)
    rank_name = models.CharField(max_length=150, unique=True)
    details = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rank_id} - {self.rank_name}"
    

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_code = models.CharField(max_length=20, unique=True)  # Add this field
    product_name = models.CharField(max_length=150)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    date_of_entry = models.DateField(auto_now_add=True)
    product_size_length = models.DecimalField(max_digits=10, decimal_places=2)
    product_size_breadth = models.DecimalField(max_digits=10, decimal_places=2)
    product_size_height = models.DecimalField(max_digits=10, decimal_places=2)
    product_weight = models.DecimalField(max_digits=10, decimal_places=2)
    manufacture_name = models.CharField(max_length=150)
    description = models.TextField()
    product_images = models.ManyToManyField('ProductImage', related_name='products')
    vendor = models.CharField(max_length=150)
    barcode = models.CharField(max_length=50, unique=True)
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)
    purchase_date = models.DateField()
    purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"


class ProductImage(models.Model):
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image {self.id}"
    

class Exhibition(models.Model):
    exhibition_id = models.AutoField(primary_key=True)
    exhibition_name = models.CharField(max_length=150)
    location = models.CharField(max_length=150)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=6)
    start_date = models.DateField()
    end_date = models.DateField()
    details = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exhibition_id} - {self.exhibition_name}"
    
    
class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    customer_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='customers')
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    details = models.TextField()

    def __str__(self):
        return f"{self.customer_name} ({self.customer_id})"
    
    
class Supplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)
    supplier_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='suppliers')
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    details = models.TextField()

    def __str__(self):
        return f"{self.supplier_name} ({self.supplier_id})"
    
    
class StockEntry(models.Model):
    stock_id = models.AutoField(primary_key=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    subcategory = models.ForeignKey('SubCategory', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    rack = models.ForeignKey('Rank', on_delete=models.CASCADE)  
    box = models.ForeignKey('Box', on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField(default=1)
    serial_number = models.CharField(max_length=255, blank=True, null=True)  
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stock Entry: {self.product.product_name} - {self.quantity} units"

class StockBarcode(models.Model):
    """ Stores multiple barcode images for each Stock Entry """
    stock_entry = models.ForeignKey(StockEntry, on_delete=models.CASCADE, related_name="barcodes")
    barcode_text = models.CharField(max_length=255, unique=True)
    barcode_image = models.ImageField(upload_to='stock_barcodes/')

    def __str__(self):
        return f"Barcode: {self.barcode_text} for {self.stock_entry.product.product_name}"


class TempStockBarcode(models.Model):
    """ Temporarily stores barcode images before final stock entry """
    barcode_text = models.CharField(max_length=255, unique=True)
    barcode_image = models.ImageField(upload_to='temp_barcodes/')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='temp_barcodes')  
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name='temp_barcodes') 
    serial_number = models.CharField(max_length=255, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Temp Barcode: {self.barcode_text}"
    

class ScheduledBackup(models.Model):
    BACKUP_CHOICES = [
        ('backup', 'Backup'),
        ('cleanup', 'Cleanup'),
        ('backup_cleanup', 'Backup & Cleanup'),
        ('never', 'Never')
    ]

    table_name = models.CharField(max_length=1000)
    backup_interval_days = models.IntegerField()
    next_backup = models.DateTimeField(default=timezone.now)
    last_backup = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='scheduledbackup'
    )
    operation = models.CharField(max_length=20, choices=BACKUP_CHOICES, default='backup')

    def __str__(self):
        return f"{self.table_name} - every {self.backup_interval_days} days ({self.operation})"
    

class ScheduledBackupDetails(models.Model):
    backup_name = models.CharField(max_length=255)
    sql_file_name = models.CharField(max_length=255)
    txt_file_name = models.CharField(max_length=255)
    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    scheduled_operation = models.CharField(max_length=50)
    file_size = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"Backup: {self.backup_name} - {self.scheduled_operation}"