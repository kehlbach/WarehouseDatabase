from django.db import models
from django.core.validators import RegexValidator
# Create your models here.

# class Organization(models.Model):
#     name = models.CharField("First name", max_length=255, blank = True, null = True)
#     code = models.CharField("First name", max_length=255, unique=True)
#     phone_regex = RegexValidator(regex=r'^\+?\d{9,16}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
#     phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    # charfield and textfield not require null=True
    location = models.CharField(max_length=128, blank=True)

    def __str__(self):
        return f'{self.id}: {self.name.capitalize()}'


class Permission(models.Model):
    id = models.BigAutoField(primary_key=True)
    action = models.CharField(max_length=32)  # add, change
    subject = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return f'{self.id}: {self.action} {self.subject.capitalize()}'


class Role(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=32, unique=True)
    perms = models.ManyToManyField(Permission, blank=True)

    def __str__(self):
        return f'{self.id}: {self.name.capitalize()}'


class Profile(models.Model):
    id = models.BigAutoField(primary_key=True)
    phone_regex = RegexValidator(
        regex=r'^\+?\d{9,16}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], max_length=17, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    departments = models.ManyToManyField(Department, blank=True)

    def __str__(self):
        return f'{self.id}: {self.phone_number}'


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)


class Product(models.Model):
    vendor_code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=128, unique=True)
    units = models.CharField(max_length=32, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


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
