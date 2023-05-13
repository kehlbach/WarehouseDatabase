from config.settings import env
from datetime import date
from random import randint, choice as randchoice
import environ
import os
from pathlib import Path
from django.contrib.auth.models import User
from home.models import *
from home.serializers import ReceiptProductSerializer, ReceiptSerializer
from django.core.exceptions import ValidationError
databases = ['db1']


def run():
    subjects = dict(RolePermission.Subjects).keys()
    actions = dict(RolePermission.Actions).keys()
    admin = Role.objects.get_or_create(
        name='Администратор', is_protected=True)[0]
    for subject in subjects:
        for action in actions:
            obj, created = RolePermission.objects.get_or_create(
                role=admin,
                action=action,
                subject=subject
            )

    Role.objects.get_or_create(name='Без прав', is_protected=True)[0]
    Role.objects.get_or_create(name='Тест')[0]
    admin.save()
    adm1 = Profile.objects.get_or_create(
        name='Valentin',
        phone_number='+7 747 930 9084',
        role=admin,
    )[0]
    n = 15
    categories = []
    for i in range(n):
        if i < 6:
            categories.append(None)
        else:
            categories.append(Category.objects.get_or_create(
                name=f'Категория {i+1}')[0])
    departments = []
    for i in range(n):
        departments.append(Department.objects.get_or_create(
            name=f'Отделение {i+1}')[0])
    products = []
    for i in range(n):
        product, created = Product.objects.get_or_create(
            vendor_code=i+1, name=f'Продукт {i+1}')
        if created:
            product.category = randchoice(categories)
            product.save()
        products.append(product)

    # receipt_data_1 = {
    #     "date": date(2015, 1, 1),
    #     "to_department": 1,
    #     "made_by": adm1
    # }
    # receipt_data_2 = {
    #     "date": date(2015, 2, 2),
    #     "from_department": 1,
    #     "to_department": 2,
    #     "made_by": adm1
    # }

    # receipt1 = Receipt.objects.get_or_create(
    #                     **receipt_data_1)[0]
    # receipt2 = Receipt.objects.get_or_create(
    #                     **receipt_data_2)[0]

    # receipt_product_data1 = {
    #     'receipt': receipt1.id,  # type: ignore
    #     'product': 1,
    #     'quantity': 10
    # }
    # receipt_product_serializer1 = ReceiptProductSerializer(
    #     data=receipt_product_data1)  # type: ignore
    # receipt_product_serializer1.is_valid(
    #     raise_exception=True)
    # receipt_product = receipt_product_serializer1.save()
    # receipt_product_data2 = {
    #     'receipt': receipt1.id,  # type: ignore
    #     'product': 1,
    #     'quantity': 10
    # }
    # receipt_product_serializer2 = ReceiptProductSerializer(
    #     data=receipt_product_data2)  # type: ignore
    # receipt_product_serializer2.is_valid(
    #     raise_exception=True)
    # receipt_product = receipt_product_serializer2.save()
    

    if False:
        for year in (2020, 2021, 2022):
            for _ in range(3):
                month = randint(1, 12)
                for i in range(3):
                    day = randint(1, 27)
                    receipt_data = dict()
                    receipt_data_1 = {
                        "date": date(year, month, day),
                        "to_department": randchoice(departments),
                        "made_by": adm1
                    }

                    receipt_data_2 = {
                        "date": date(year, month, day),
                        "from_department": randchoice(departments),
                        "to_department": randchoice(departments),
                        "made_by": adm1
                    }
                    receipt_data_3 = {
                        "date": date(year, month, day),
                        "from_department": randchoice(departments),
                        "made_by": adm1
                    }
                    # receipt = Receipt.objects.get_or_create(**receipt_data)[0]
                    receipt1 = Receipt.objects.get_or_create(
                        **receipt_data_1)[0]
                    receipt2 = Receipt.objects.get_or_create(
                        **receipt_data_2)[0]
                    receipt3 = Receipt.objects.get_or_create(
                        **receipt_data_3)[0]
                    receipts = [receipt1, receipt2, receipt3]

                    for _ in range(3):

                        product = randchoice(products)
                        receipt_product = ReceiptProduct.objects.filter(
                            receipt=receipt1,
                            product=product
                        )

                        if receipt_product:
                            pass
                        else:
                            receipt_product_data = {
                                'receipt': receipt1.id,  # type: ignore
                                'product': product.id,
                                'quantity': randint(5, 16)
                            }
                            receipt_product_serializer1 = ReceiptProductSerializer(
                                data=receipt_product_data)  # type: ignore
                            try:
                                receipt_product_serializer1.is_valid(
                                    raise_exception=True)
                                receipt_product = receipt_product_serializer1.save()
                            except ValidationError:
                                pass
                    for _ in range(3):
                        _receipt = randchoice((receipt2, receipt3))
                        product = randchoice(products)
                        receipt_product = ReceiptProduct.objects.filter(
                            receipt=_receipt,
                            product=product
                        )

                        if receipt_product:
                            pass
                        else:
                            receipt_product_data = {
                                'receipt': _receipt.id,  # type: ignore
                                'product': product.id,
                                'quantity': randint(1, 9)
                            }
                            receipt_product_serializer1 = ReceiptProductSerializer(
                                data=receipt_product_data)  # type: ignore
                            try:
                                receipt_product_serializer1.is_valid(
                                    raise_exception=True)
                                receipt_product = receipt_product_serializer1.save()
                            except ValidationError:
                                pass
                    # receipt_serializer = ReceiptSerializer(
                    #     data=receipt_data)  # type: ignore
                    # try:
                    #     receipt_serializer.is_valid(raise_exception=False)

                    #     receipt = receipt_serializer.create(receipt_data)
                    #     receipt_product_data = [
                    #         {
                    #             "receipt": receipt,
                    #             "product": randchoice(products).id,
                    #             "quantity": randint(1, 15)
                    #         },
                    #         {
                    #             "receipt": receipt,
                    #             "product": randchoice(products).id,
                    #             "quantity": randint(1, 15)
                    #         }
                    #     ]
                    #     receipt_product_serializer = ReceiptProductSerializer(
                    #         data=receipt_product_data,  # type: ignore
                    #         many=True,
                    #         #context={"receipt": receipt}
                    #     )
                    #     receipt_product_serializer.is_valid(
                    #         raise_exception=False)
                    #     receipt_product_serializer.save()
                    # except Exception as error:
                    #     pass

        # for year in (2020,2021,2022):
        #     for _ in range(3):
        #         month = randint(1,12)
        #         for _ in range(3):
        #             day = randint(1,27)
        #             dec = randint(1,3)
        #             if dec ==1:
        #                 try:
        #                     receipt = Receipt.objects.create(
        #                         date = date(year,month,day),
        #                         from_department = department1,
        #                         to_department = department2,
        #                         made_by = adm1
        #                     )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1-15)
        #                     )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1-15)
        #                     )
        #                 except Exception:
        #                     pass
        #             elif dec ==2:
        #                 try:
        #                     receipt = Receipt.objects.create(
        #                             date = date(year,month,day),
        #                             to_department = randchoice((department1,department2)),
        #                             made_by = adm1
        #                         )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1,15)
        #                     )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1,15)
        #                     )
        #                 except Exception:
        #                     pass
        #             elif dec ==3:
        #                 try:
        #                     receipt = Receipt.objects.create(
        #                             date = date(year,month,day),
        #                             from_department = randchoice((department1,department2)),
        #                             made_by = adm1
        #                         )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1,15)
        #                     )
        #                     ReceiptProduct.objects.create(
        #                         receipt = receipt,
        #                         product = randchoice(products),
        #                         quantity = randint(1,15)
        #                     )
        #                 except Exception:
        #                     pass

    # Profile.objects.filter
