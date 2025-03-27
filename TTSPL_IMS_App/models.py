from django.db import models
from django.utils.timezone import now
import uuid

# Create your models here.
PRODUCT_STATUS_CHOICES = (
        ('ASSIGN', 'assign'),
        ('FIXED_ASSET','fixed_asset'),
        ('RETURN', 'return'),
        ('SELL','sell'),
        ('DEMO', 'demo'),
        ('INSPECTION', 'inspection'),
        ('INSTOCK','instock'),
    )

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
    product_status = models.CharField(max_length=30, choices=PRODUCT_STATUS_CHOICES, default='INSTOCK')
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

class AssignProduct(models.Model):
    stock_id = models.ForeignKey('StockEntry', on_delete=models.CASCADE, null=True, blank=True)
    assign_id = models.CharField(max_length=100, unique=True)
    assign_product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    assign_employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)
    assign_company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)
    assign_exhibition = models.ForeignKey('Exhibition', on_delete=models.CASCADE, null=True, blank=True)
    assign_customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True)
    assign_mode = models.CharField(max_length=30)
    assign_quantity = models.IntegerField(default=0)
    assign_customer_details = models.CharField(max_length=200)
    assign_at = models.DateTimeField(auto_now_add=True)

class ReturnProductHistory(models.Model):
    return_stock_id = models.ForeignKey('StockEntry', on_delete=models.CASCADE, null=True, blank=True)
    return_id = models.CharField(max_length=100,null=True)
    assign_return_id = models.CharField(max_length=100)
    return_product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    return_employee = models.ForeignKey('Employee', on_delete=models.CASCADE, null=True, blank=True)
    return_company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True, blank=True)
    return_exhibition = models.ForeignKey('Exhibition', on_delete=models.CASCADE, null=True, blank=True)
    return_customer = models.ForeignKey('Customer', on_delete=models.CASCADE, null=True, blank=True)
    return_mode = models.CharField(max_length=30)
    return_quantity = models.IntegerField(default=0)
    return_customer_details = models.CharField(max_length=200)
    return_product_status = models.CharField(max_length=255, blank=True, null=True)
    reuturn_assign_at = models.CharField(max_length=255, blank=True, null=True)
    return_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    reuturn_status = models.CharField(max_length=255, blank=True, null=True)
