from django.core.exceptions import ValidationError


def validate_phone(phone_number):
    # 998936039020
    if not (len(phone_number) == 12 and phone_number.isdigit()):
        raise ValidationError(
            "Telefon number to'g'ri emas 998992339900 shu shakilda yuboring",
            params={'value': phone_number},
        )


def validate_barcode(barcode):
    # only integer

    if not barcode.isdigit():
        raise ValidationError(
            "Shtrix kod son bo'lishi kerak",
            params={'value': barcode},
        )
