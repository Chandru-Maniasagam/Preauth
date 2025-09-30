"""
Validation utilities for RCM SaaS Application
"""

import re
from datetime import datetime, date
from typing import Any, List, Optional, Union
import phonenumbers
from phonenumbers import NumberParseException


def validate_email(email: str) -> bool:
    """Validate email address format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str, country_code: str = 'IN') -> bool:
    """Validate phone number format"""
    if not phone:
        return False
    
    try:
        parsed_number = phonenumbers.parse(phone, country_code)
        return phonenumbers.is_valid_number(parsed_number)
    except NumberParseException:
        return False


def validate_indian_phone_number(phone: str) -> bool:
    """Validate Indian phone number format"""
    if not phone:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Indian mobile numbers are 10 digits and start with 6, 7, 8, or 9
    if len(digits_only) == 10:
        return digits_only[0] in '6789'
    
    # With country code +91
    if len(digits_only) == 12 and digits_only.startswith('91'):
        return digits_only[2] in '6789'
    
    return False


def validate_aadhaar_number(aadhaar: str) -> bool:
    """Validate Aadhaar number format"""
    if not aadhaar:
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', aadhaar)
    
    # Aadhaar number should be 12 digits
    if len(digits_only) != 12:
        return False
    
    # Basic checksum validation (Verhoeff algorithm)
    return _verhoeff_checksum(digits_only)


def validate_pan_number(pan: str) -> bool:
    """Validate PAN number format"""
    if not pan:
        return False
    
    # PAN format: 5 letters, 4 digits, 1 letter
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    return bool(re.match(pattern, pan.upper()))


def validate_date_format(date_string: str, format: str = '%Y-%m-%d') -> bool:
    """Validate date string format"""
    if not date_string:
        return False
    
    try:
        datetime.strptime(date_string, format)
        return True
    except ValueError:
        return False


def validate_age(birth_date: Union[str, date], min_age: int = 0, max_age: int = 150) -> bool:
    """Validate age based on birth date"""
    if not birth_date:
        return False
    
    if isinstance(birth_date, str):
        try:
            birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
        except ValueError:
            return False
    
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    return min_age <= age <= max_age


def validate_blood_group(blood_group: str) -> bool:
    """Validate blood group format"""
    if not blood_group:
        return False
    
    valid_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_group.upper() in valid_groups


def validate_gender(gender: str) -> bool:
    """Validate gender value"""
    if not gender:
        return False
    
    valid_genders = ['male', 'female', 'other', 'prefer_not_to_say']
    return gender.lower() in valid_genders


def validate_currency_amount(amount: Union[str, int, float], min_amount: float = 0) -> bool:
    """Validate currency amount"""
    if amount is None:
        return False
    
    try:
        amount_float = float(amount)
        return amount_float >= min_amount
    except (ValueError, TypeError):
        return False


def validate_pincode(pincode: str, country: str = 'IN') -> bool:
    """Validate postal/pin code format"""
    if not pincode:
        return False
    
    if country == 'IN':
        # Indian pincode is 6 digits
        return bool(re.match(r'^[1-9][0-9]{5}$', pincode))
    
    return True  # Add other country validations as needed


def validate_insurance_policy_number(policy_number: str) -> bool:
    """Validate insurance policy number format"""
    if not policy_number:
        return False
    
    # Basic validation - alphanumeric, 6-20 characters
    pattern = r'^[A-Za-z0-9]{6,20}$'
    return bool(re.match(pattern, policy_number))


def validate_medical_code(code: str, code_type: str = 'icd10') -> bool:
    """Validate medical codes (ICD-10, CPT, etc.)"""
    if not code:
        return False
    
    if code_type == 'icd10':
        # ICD-10 codes: Letter followed by 2-3 digits, optional decimal and 1-4 more digits
        pattern = r'^[A-Z][0-9]{2,3}(\.[0-9]{1,4})?$'
        return bool(re.match(pattern, code.upper()))
    
    elif code_type == 'cpt':
        # CPT codes: 5 digits, optional 2-digit modifier
        pattern = r'^[0-9]{5}(-[0-9]{2})?$'
        return bool(re.match(pattern, code))
    
    return True


def validate_hospital_registration_number(reg_number: str) -> bool:
    """Validate hospital registration number format"""
    if not reg_number:
        return False
    
    # Basic validation - alphanumeric, 8-20 characters
    pattern = r'^[A-Za-z0-9]{8,20}$'
    return bool(re.match(pattern, reg_number))


def validate_license_number(license_number: str, license_type: str = 'medical') -> bool:
    """Validate professional license number"""
    if not license_number:
        return False
    
    if license_type == 'medical':
        # Medical license: alphanumeric, 6-15 characters
        pattern = r'^[A-Za-z0-9]{6,15}$'
        return bool(re.match(pattern, license_number))
    
    return True


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """Validate file size"""
    max_size_bytes = max_size_mb * 1024 * 1024
    return 0 < file_size <= max_size_bytes


def validate_json_schema(data: dict, schema: dict) -> tuple[bool, List[str]]:
    """Validate data against JSON schema"""
    import jsonschema
    from jsonschema import ValidationError
    
    try:
        jsonschema.validate(data, schema)
        return True, []
    except ValidationError as e:
        return False, [e.message]


def _verhoeff_checksum(number: str) -> bool:
    """Verhoeff algorithm for Aadhaar validation"""
    # Verhoeff multiplication table
    d = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]
    
    # Verhoeff permutation table
    p = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]
    
    # Verhoeff inverse table
    inv = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
    
    c = 0
    n = len(number)
    
    for i in range(n - 1, -1, -1):
        c = d[c][p[((n - i) % 8)][int(number[i])]]
    
    return c == 0


def sanitize_string(text: str) -> str:
    """Sanitize string input"""
    if not text:
        return ''
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags and javascript
    text = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    # Remove dangerous attributes
    text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
    
    # Trim whitespace
    return text.strip()


def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one number")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors
