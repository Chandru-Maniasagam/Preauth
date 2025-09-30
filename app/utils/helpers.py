"""
Helper utilities for RCM SaaS Application
"""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, date
from typing import Any, Dict, List, Optional, Union
import re
import json


def generate_id(prefix: str = '') -> str:
    """Generate a unique ID with optional prefix"""
    unique_id = str(uuid.uuid4())
    return f"{prefix}_{unique_id}" if prefix else unique_id


def generate_short_id(length: int = 8) -> str:
    """Generate a short unique ID"""
    return secrets.token_urlsafe(length)


def generate_patient_id(hospital_id: str) -> str:
    """Generate patient ID for hospital"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f"PAT_{hospital_id[:4]}_{timestamp}_{random_part}"


def generate_preauth_id(hospital_id: str) -> str:
    """Generate preauth ID for hospital"""
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = secrets.token_hex(4).upper()
    return f"PA_{hospital_id[:4]}_{timestamp}_{random_part}"


def generate_claim_id(hospital_id: str) -> str:
    """Generate a unique claim ID in format CSHLS-YYYYMMDD-001"""
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Get the next sequence number for the day
    # In a real implementation, this would be atomic
    sequence = get_next_claim_sequence(hospital_id, date_str)
    
    return f"CSHLS-{date_str}-{sequence:03d}"


def get_next_claim_sequence(hospital_id: str, date_str: str) -> int:
    """Get next sequence number for claim ID"""
    # This is a simplified implementation
    # In production, use a proper counter or database sequence
    import random
    return random.randint(1, 999)


def calculate_age_detailed(dob_str: str) -> Dict[str, int]:
    """Calculate detailed age in years, months, and days"""
    try:
        dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
        today = date.today()
        
        years = today.year - dob.year
        months = today.month - dob.month
        days = today.day - dob.day
        
        if days < 0:
            months -= 1
            days += 30  # Approximate
        
        if months < 0:
            years -= 1
            months += 12
        
        return {
            'years': years,
            'months': months,
            'days': days
        }
    except Exception:
        return {'years': 0, 'months': 0, 'days': 0}


def generate_reference_number(prefix: str = 'REF') -> str:
    """Generate reference number"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(3).upper()
    return f"{prefix}_{timestamp}_{random_part}"


def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}:{password_hash}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, password_hash = hashed_password.split(':')
        return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
    except ValueError:
        return False


def format_currency(amount: Union[int, float], currency: str = 'INR') -> str:
    """Format currency amount"""
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    elif currency == 'USD':
        return f"${amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_phone_number(phone: str, country_code: str = '+91') -> str:
    """Format phone number with country code"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"{country_code} {digits[:5]} {digits[5:]}"
    elif len(digits) == 12 and digits.startswith('91'):
        return f"+{digits[:2]} {digits[2:7]} {digits[7:]}"
    else:
        return phone


def format_date(date_obj: Union[str, datetime, date], format: str = '%d-%m-%Y') -> str:
    """Format date object to string"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format)
    elif isinstance(date_obj, date):
        return date_obj.strftime(format)
    else:
        return str(date_obj)


def parse_date(date_string: str, format: str = '%Y-%m-%d') -> Optional[datetime]:
    """Parse date string to datetime object"""
    try:
        return datetime.strptime(date_string, format)
    except ValueError:
        return None


def calculate_age(birth_date: Union[str, datetime, date]) -> Optional[int]:
    """Calculate age from birth date"""
    if isinstance(birth_date, str):
        birth_date = parse_date(birth_date)
    
    if not birth_date:
        return None
    
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return max(0, age)


def get_time_ago(datetime_obj: datetime) -> str:
    """Get human-readable time ago string"""
    now = datetime.utcnow()
    diff = now - datetime_obj
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_initial_letters(text: str, max_letters: int = 2) -> str:
    """Extract initial letters from text"""
    if not text:
        return ''
    
    words = text.split()
    initials = ''.join([word[0].upper() for word in words[:max_letters]])
    return initials


def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data like phone numbers, emails, etc."""
    if not data or len(data) <= visible_chars:
        return data
    
    if '@' in data:  # Email
        local, domain = data.split('@', 1)
        if len(local) <= 2:
            return f"{local[0]}{mask_char * (len(local) - 1)}@{domain}"
        else:
            return f"{local[0]}{mask_char * (len(local) - 2)}{local[-1]}@{domain}"
    else:  # Phone number or other data
        return f"{data[:visible_chars//2]}{mask_char * (len(data) - visible_chars)}{data[-visible_chars//2:]}"


def convert_to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase"""
    components = snake_str.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


def convert_to_snake_case(camel_str: str) -> str:
    """Convert camelCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', camel_str)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """Flatten nested dictionary"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def group_by_key(items: List[Dict], key: str) -> Dict[Any, List[Dict]]:
    """Group list of dictionaries by key"""
    grouped = {}
    for item in items:
        group_key = item.get(key)
        if group_key not in grouped:
            grouped[group_key] = []
        grouped[group_key].append(item)
    return grouped


def sort_dict_by_key(d: Dict, reverse: bool = False) -> Dict:
    """Sort dictionary by keys"""
    return dict(sorted(d.items(), reverse=reverse))


def sort_dict_by_value(d: Dict, reverse: bool = False) -> Dict:
    """Sort dictionary by values"""
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))


def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List) -> List:
    """Remove duplicates from list while preserving order"""
    seen = set()
    return [x for x in lst if not (x in seen or seen.add(x))]


def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely load JSON string"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def safe_json_dumps(obj: Any, default: str = '{}') -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''


def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size from bytes to MB"""
    return round(file_size_bytes / (1024 * 1024), 2)


def is_valid_url(url: str) -> bool:
    """Check if string is a valid URL"""
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(pattern.match(url))


def generate_random_string(length: int = 32) -> str:
    """Generate random string of specified length"""
    return secrets.token_urlsafe(length)


def calculate_percentage(part: Union[int, float], total: Union[int, float]) -> float:
    """Calculate percentage"""
    if total == 0:
        return 0.0
    return round((part / total) * 100, 2)


def round_to_nearest(value: Union[int, float], nearest: Union[int, float] = 1) -> Union[int, float]:
    """Round value to nearest specified number"""
    return round(value / nearest) * nearest


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.utcnow().isoformat()


def get_timestamp_from_datetime(dt: datetime) -> str:
    """Get timestamp string from datetime object"""
    return dt.isoformat()


def parse_timestamp_to_datetime(timestamp: str) -> Optional[datetime]:
    """Parse timestamp string to datetime object"""
    try:
        return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    except ValueError:
        return None
