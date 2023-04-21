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
    units = models.CharField(max_length=32, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    @property
    def repr(self):
        return self.__str__()



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
