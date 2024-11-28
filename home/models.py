from django.core.validators import RegexValidator
from django.db import models
from datetime import date
import phonenumbers


class Department(models.Model):
    name = models.CharField(max_length=32, unique=True)
    # charfield and textfield not require null=True
    location = models.CharField(max_length=128, blank=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name.capitalize()}"

    @property
    def repr(self):
        return self.__str__()

    @property
    def receipts_count(self):
        from_d = len(Receipt.objects.filter(from_department=self.id))  # type: ignore
        to_d = len(Receipt.objects.filter(to_department=self.id))  # type: ignore
        return from_d + to_d

    def save(self, *args, **kwargs):
        if self.location == "Skip":
            self.location = ""

        super().save(*args, **kwargs)


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    is_protected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name.capitalize()}"

    @property
    def repr(self):
        return self.__str__()


class RolePermission(models.Model):
    VIEW = 10
    ADD = 11
    EDIT = 12
    DELETE = 13
    Actions = (
        (
            VIEW,
            "view",
        ),
        (
            ADD,
            "add",
        ),
        (
            EDIT,
            "edit",
        ),
        (DELETE, "delete"),
    )
    PROFILES = 20
    ROLES = 21
    INVENTORY = 22
    RECEIPTS = 23
    PRODUCTS = 24
    CATEGORIES = 25
    DEPARTMENTS = 26
    Subjects = (
        (PROFILES, "Profiles"),
        (ROLES, "Roles"),
        (INVENTORY, "Inventory"),
        (RECEIPTS, "Receipts"),
        (PRODUCTS, "Products"),
        (CATEGORIES, "Categories"),
        (DEPARTMENTS, "Departments"),
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    action = models.IntegerField(choices=Actions)
    subject = models.IntegerField(choices=Subjects, blank=True, null=True)

    class Meta:
        unique_together = ("role", "action", "subject")

    def __str__(self):
        # type: ignore
        return f"{self.role.repr}: {self.get_action_display()} {self.get_subject_display()}"  # type: ignore

    @property
    def repr(self):
        return self.__str__()


class Profile(models.Model):
    name = models.CharField(max_length=64, blank=True)
    phone_number = models.CharField(max_length=20, unique=True)
    user_id = models.CharField(max_length=32, unique=True, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    departments = models.ManyToManyField(Department, blank=True)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):

        return f"{self.name}: {self.role}"

    @property
    def repr(self):
        if self.name:
            group = self.name.split()
            name = group.pop(0)
            if group:
                for each in group:
                    name += " {}.".format(each[0])
            return name
        else:
            return self.phone_number

    def save(self, *args, **kwargs):
        if self.phone_number:
            parsed_number = phonenumbers.parse(self.phone_number)
            self.phone_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
            )
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.name}"

    @property
    def repr(self):
        return self.__str__()


class Product(models.Model):
    vendor_code = models.CharField(max_length=32, blank=True)
    name = models.CharField(max_length=128)
    units = models.CharField(max_length=32, default="шт")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, blank=True, null=True
    )

    class Meta:
        unique_together = ("name", "category")

    def __str__(self):
        vendor_code = f"{self.vendor_code}:" if self.vendor_code else ""
        category = f"{self.category.repr}: " if self.category else ""
        return vendor_code + category + self.name

    @property
    def repr(self):
        return self.__str__()

    def save(self, *args, **kwargs):
        if self.vendor_code == "Пропустить":
            self.vendor_code = ""
        super().save(*args, **kwargs)


class Receipt(models.Model):
    # date = models.DateField()
    # date now:
    date = models.DateField(default=date.today)  # auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    from_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="from_department",
    )
    to_department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="to_department",
    )
    made_by = models.ForeignKey(Profile, on_delete=models.PROTECT)
    note = models.CharField(max_length=256, blank=True)

    def __str__(self):
        # type: ignore
        return "{}: {} {} {}".format(
            self.id,  # type: ignore
            self.type,
            self.date.strftime("%d/%m/%Y"),
            self.time.strftime("%H:%M"),
        )

    @property
    def repr(self):
        return self.__str__()

    @property
    def type(self):
        if self.from_department and self.to_department:
            return "Transfer"
        elif self.from_department:
            return "Outgoing"
        else:
            return "Incoming"


class ReceiptProduct(models.Model):
    # Удаление Receipt рассматривается как отмена операции по накладной
    # Товары накладной должны быть удалены отдельно
    # Можно удалить только последнюю накладную
    receipt = models.ForeignKey(Receipt, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # type: ignore
    quantity = models.IntegerField()

    class Meta:
        unique_together = ("receipt", "product", "price")


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
    Months = (
        (JAN, "Январь"),
        (FEB, "Февраль"),
        (MAR, "Март"),
        (APR, "Апрель"),
        (MAY, "Май"),
        (JUN, "Июнь"),
        (JUL, "Июль"),
        (AUG, "Август"),
        (SEP, "Сентябрь"),
        (OCT, "Октябрь"),
        (NOV, "Ноябрь"),
        (DEC, "Декабрь"),
    )
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField(choices=Months)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    goods_received = models.IntegerField(default=0)
    goods_issued = models.IntegerField(default=0)

    class Meta:
        unique_together = ("department", "year", "month", "product")

    @property
    def month_start(self) -> int:
        """
        Calculate the starting quantity of a product in the current month.

        This property calculates the starting quantity of a product in the current month by summing the ending quantity
        of the previous month and subtracting the quantity issued in the previous month. If there are no previous
        months or years, the starting quantity is set to 0.

        Returns:
            int: The starting quantity of the product in the current month.
        """
        # note: may require optimization of queries if performance is an issue
        prev_months = (
            Inventory.objects.filter(
                department=self.department,
                year=self.year,
                month__lt=self.month,
                product=self.product,
            )
            .order_by("-year", "-month")
            .first()
        )
        if prev_months:
            return (
                prev_months.month_start
                + prev_months.goods_received
                - prev_months.goods_issued
            )
        else:
            prev_years = (
                Inventory.objects.filter(
                    department=self.department, year__lt=self.year, product=self.product
                )
                .order_by("-year", "-month")
                .first()
            )
            if prev_years:
                return (
                    prev_years.month_start
                    + prev_years.goods_received
                    - prev_years.goods_issued
                )
            else:
                return 0
