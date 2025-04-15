import phonenumbers

def validate_tel_number(tel_number):
    if not tel_number:
        raise ValueError("Укажите номер телефона")
    if not tel_number.startswith('+'):
        raise ValueError("Номер телефона должен начинаться с '+'")
    
    try:
        parsed_number = phonenumbers.parse(tel_number, "BY")
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Неверный формат номера телефона для Беларуси.")
    except Exception as e:
        raise ValueError(f"Ошибка при указании номера телефона: {e}")
    
    return tel_number