import re
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Q

# Create your models here.

# class Organization(models.Model):
#     name = models.CharField("First name", max_length=255, blank = True, null = True)
#     code = models.CharField("First name", max_length=255, unique=True)
#     phone_regex = RegexValidator(regex=r'^\+?\d{9,16}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
#     phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)


class Department(models.Model):
    name = models.CharField(max_length=32, unique=True)
    # charfield and textfield not require null=True
    location = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f'{self.name.capitalize()}'
    @property
    def repr(self):
        return self.__str__()


class Permission(models.Model):
    VIEW = 10
    ADD = 11
    EDIT = 12
    DELETE = 13

    Actions = (
        (VIEW, 'смотреть',),
        (ADD, 'добавлять',),
        (EDIT, 'изменять',),
        (DELETE, 'удалять')
    )

    PROFILES = 20
    ROLES = 21
    INVENTORY = 22
    RECEIPTS =23
    PRODUCTS = 24
    CATEGORIES = 25
    DEPARTMENTS = 26
    
    Subjects= (
        (PROFILES, 'Пользователи'),
        (ROLES, 'Роли'),
        (INVENTORY, 'Остатки'),
        (RECEIPTS,'Накладные'),
        (PRODUCTS, 'Номенклатура'),
        (CATEGORIES, 'Категории'),
        (DEPARTMENTS, 'Отделения')
    )

    action = models.IntegerField(choices=Actions)
    subject = models.IntegerField(choices=Subjects,blank=True,null=True)

    class Meta:
        unique_together = ('action', 'subject')

    def __str__(self):
        return f'{self.get_action_display()} {self.get_subject_display()}'
    @property
    def repr(self):
        return self.__str__()

    



class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return f'{self.name.capitalize()}'
    @property
    def repr(self):
        return self.__str__()



class Profile(models.Model):
    phone_regex = RegexValidator(
        regex=r'^\+?\d{9,16}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, blank=True)

    def __str__(self):
        
        return f'{self.name}: {self.role}'
    @property
    def repr(self):
        #NAME_PATTERN = r'([А-Я]?[а-я]+)+'
        if self.name:
            group = self.name.split()#re.split(NAME_PATTERN,self.name)
            name = group.pop(0)
            if group:
                for each in group:
                    name += ' {}.'.format(each[0])
            return name
        else:
            return self.phone_number


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __str__(self):
        return f'{self.name}'
    @property
    def repr(self):
        return self.__str__()


class Product(models.Model):
    vendor_code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128, unique=True)
    units = models.CharField(max_length=32, default='шт')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    def __str__(self):
        return f'{self.vendor_code}: {self.name}'
    @property
    def repr(self):
        return self.__str__()


class Receipt(models.Model):
    date = models.DateField()
    # type = models.IntegerField(choices=Types)
    from_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True, related_name='from_department')
    to_department = models.ForeignKey(Department, on_delete=models.PROTECT, blank=True, null=True, related_name='to_department')
    made_by = models.ForeignKey(Profile, on_delete=models.PROTECT)
    #provider = models.CharField(max_length=128, blank=True)
    #customer = models.CharField(max_length=128, blank=True)
    note = models.CharField(max_length=256, blank=True)
    def __str__(self):
        return '{}: {} {}'.format(self.id, self.type, self.date)
    @property
    def repr(self):
        return self.__str__()
    @property
    def type(self):
        if self.from_department and self.to_department:
            return 'Перемещение'
        elif self.from_department:
            return 'Расходная'
        else:
            return 'Приходная'

    

class ReceiptProduct(models.Model):
    #Удаление Receipt рассматривается как отмена операции по накладной
    receipt = models.ForeignKey(Receipt,on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, default = 0)
    quantity = models.IntegerField()
    class Meta:
        unique_together = ('receipt', 'product','price')

class Inventory(models.Model):
    JAN = 1
    FEB = 2
    MAR = 3
    APR = 4
    MAY = 5
    JUN = 6
    JUL = 7
    AUG = 8
    SEP = 9
    OCT = 10
    NOV = 11
    DEC = 12
    Months= (
        (JAN, 'Январь'),
        (FEB, 'Февраль'),
        (MAR, 'Март'),
        (APR, 'Апрель'),
        (MAY, 'Май'),
        (JUN, 'Июнь'),
        (JUL, 'Июль'),
        (AUG, 'Август'),
        (SEP, 'Сентябрь'),
        (OCT, 'Октябрь'),
        (NOV, 'Ноябрь'),
        (DEC, 'Декабрь')
    )
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    year = models.IntegerField()
    month = models.IntegerField(choices=Months)
    #day = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    #month_start = models.IntegerField(default = 0)
    goods_received = models.IntegerField(default = 0)
    goods_issued = models.IntegerField(default = 0)
    class Meta:
        unique_together = ('department', 'year','month','product')
    @property
    def month_start(self):
        previous_months = Inventory.objects.filter(department=self.department, year=self.year,
                                                       month__lt=self.month, product=self.product).order_by('-year', '-month').first()
        
        if previous_months:
            return previous_months.month_start + previous_months.goods_received - previous_months.goods_issued
        else:
            previous_years = Inventory.objects.filter(department=self.department, year__lt=self.year,
                                                       product=self.product).order_by('-year', '-month').first()
            if previous_years:
                return previous_years.month_start + previous_years.goods_received - previous_years.goods_issued
            else:
                return 0


# class Profile(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     full_name = models.CharField(max_length=255, blank=True, null=True)
#     login = models.CharField(max_length=255, unique=True)
#     # role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     password = models.CharField(max_length=255)


# class ProfileRole(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
#     roles = models.ManyToManyField(Role)
#     # Access to all departments
#     full_access = models.BooleanField(default=False)
#     departments = models.ManyToManyField(Department)


# class Chat(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     chat_id = models.IntegerField(unique=True)
#     profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
