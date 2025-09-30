"""
Data formatting utilities for RCM SaaS Application
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import re


def format_patient_name(first_name: str, last_name: str, middle_name: str = '') -> str:
    """Format patient full name"""
    name_parts = [first_name, middle_name, last_name]
    return ' '.join([part for part in name_parts if part])


def format_doctor_name(prefix: str, first_name: str, last_name: str, suffix: str = '') -> str:
    """Format doctor name with prefix and suffix"""
    name_parts = [prefix, first_name, last_name, suffix]
    return ' '.join([part for part in name_parts if part])


def format_address(address_dict: Dict[str, str]) -> str:
    """Format address dictionary to string"""
    if not address_dict:
        return ''
    
    address_parts = [
        address_dict.get('street', ''),
        address_dict.get('area', ''),
        address_dict.get('city', ''),
        address_dict.get('state', ''),
        address_dict.get('pincode', ''),
        address_dict.get('country', '')
    ]
    
    return ', '.join([part for part in address_parts if part])


def format_contact_info(contact_dict: Dict[str, str]) -> str:
    """Format contact information"""
    if not contact_dict:
        return ''
    
    contact_parts = []
    
    if contact_dict.get('phone'):
        contact_parts.append(f"Phone: {contact_dict['phone']}")
    
    if contact_dict.get('email'):
        contact_parts.append(f"Email: {contact_dict['email']}")
    
    if contact_dict.get('website'):
        contact_parts.append(f"Website: {contact_dict['website']}")
    
    return ' | '.join(contact_parts)


def format_medical_code(code: str, code_type: str = 'icd10') -> str:
    """Format medical code for display"""
    if not code:
        return ''
    
    if code_type == 'icd10':
        # Format ICD-10 code: A00.0
        return code.upper()
    elif code_type == 'cpt':
        # Format CPT code: 12345-50
        return code
    else:
        return code.upper()


def format_currency_indian(amount: Union[int, float]) -> str:
    """Format currency in Indian format (lakhs, crores)"""
    if amount < 100000:  # Less than 1 lakh
        return f"₹{amount:,.2f}"
    elif amount < 10000000:  # Less than 1 crore
        lakhs = amount / 100000
        return f"₹{lakhs:.2f} L"
    else:  # Crores
        crores = amount / 10000000
        return f"₹{crores:.2f} Cr"


def format_percentage(value: Union[int, float], total: Union[int, float] = 100) -> str:
    """Format percentage value"""
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    elif seconds < 86400:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"
    else:
        days = seconds // 86400
        remaining_hours = (seconds % 86400) // 3600
        return f"{days}d {remaining_hours}h"


def format_phone_display(phone: str, country_code: str = '+91') -> str:
    """Format phone number for display"""
    if not phone:
        return ''
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) == 10:
        return f"{country_code} {digits[:5]} {digits[5:]}"
    elif len(digits) == 12 and digits.startswith('91'):
        return f"+{digits[:2]} {digits[2:7]} {digits[7:]}"
    else:
        return phone


def format_date_display(date_obj: Union[str, datetime, date], format_type: str = 'short') -> str:
    """Format date for display"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
        except ValueError:
            return date_obj
    
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    if format_type == 'short':
        return date_obj.strftime('%d-%m-%Y')
    elif format_type == 'long':
        return date_obj.strftime('%d %B %Y')
    elif format_type == 'time':
        return date_obj.strftime('%d-%m-%Y %H:%M')
    else:
        return str(date_obj)


def format_datetime_display(datetime_obj: Union[str, datetime], format_type: str = 'short') -> str:
    """Format datetime for display"""
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        except ValueError:
            return datetime_obj
    
    if format_type == 'short':
        return datetime_obj.strftime('%d-%m-%Y %H:%M')
    elif format_type == 'long':
        return datetime_obj.strftime('%d %B %Y at %I:%M %p')
    elif format_type == 'time_only':
        return datetime_obj.strftime('%H:%M')
    elif format_type == 'date_only':
        return datetime_obj.strftime('%d-%m-%Y')
    else:
        return str(datetime_obj)


def format_relative_time(datetime_obj: Union[str, datetime]) -> str:
    """Format relative time (e.g., '2 hours ago')"""
    if isinstance(datetime_obj, str):
        try:
            datetime_obj = datetime.fromisoformat(datetime_obj.replace('Z', '+00:00'))
        except ValueError:
            return datetime_obj
    
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


def format_status_badge(status: str) -> str:
    """Format status as HTML badge"""
    status_colors = {
        'active': 'success',
        'inactive': 'secondary',
        'pending': 'warning',
        'approved': 'success',
        'rejected': 'danger',
        'expired': 'dark',
        'cancelled': 'secondary',
        'completed': 'info',
        'urgent': 'danger',
        'normal': 'primary',
        'high': 'warning',
        'low': 'secondary'
    }
    
    color = status_colors.get(status.lower(), 'secondary')
    return f'<span class="badge badge-{color}">{status.title()}</span>'


def format_priority_badge(priority: str) -> str:
    """Format priority as HTML badge"""
    priority_colors = {
        'urgent': 'danger',
        'high': 'warning',
        'normal': 'primary',
        'low': 'secondary'
    }
    
    color = priority_colors.get(priority.lower(), 'secondary')
    return f'<span class="badge badge-{color}">{priority.title()}</span>'


def format_table_data(data: List[Dict], columns: List[str]) -> List[List[str]]:
    """Format data for table display"""
    formatted_data = []
    
    for row in data:
        formatted_row = []
        for col in columns:
            value = row.get(col, '')
            if isinstance(value, (int, float)):
                if 'amount' in col.lower() or 'cost' in col.lower():
                    formatted_row.append(format_currency_indian(value))
                elif 'percentage' in col.lower() or 'rate' in col.lower():
                    formatted_row.append(format_percentage(value))
                else:
                    formatted_row.append(str(value))
            elif isinstance(value, datetime):
                formatted_row.append(format_datetime_display(value))
            elif isinstance(value, date):
                formatted_row.append(format_date_display(value))
            else:
                formatted_row.append(str(value))
        formatted_data.append(formatted_row)
    
    return formatted_data


def format_json_pretty(data: Any) -> str:
    """Format JSON data with pretty printing"""
    import json
    return json.dumps(data, indent=2, default=str)


def format_csv_row(data: Dict, headers: List[str]) -> str:
    """Format data as CSV row"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    row = [data.get(header, '') for header in headers]
    writer.writerow(row)
    
    return output.getvalue().strip()


def format_xml_element(tag: str, content: str, attributes: Dict[str, str] = None) -> str:
    """Format XML element"""
    if attributes:
        attr_str = ' '.join([f'{k}="{v}"' for k, v in attributes.items()])
        return f'<{tag} {attr_str}>{content}</{tag}>'
    else:
        return f'<{tag}>{content}</{tag}>'


def format_html_list(items: List[str], list_type: str = 'ul') -> str:
    """Format list as HTML"""
    if list_type == 'ul':
        return f"<ul>{''.join([f'<li>{item}</li>' for item in items])}</ul>"
    elif list_type == 'ol':
        return f"<ol>{''.join([f'<li>{item}</li>' for item in items])}</ol>"
    else:
        return '\n'.join([f'• {item}' for item in items])


def format_markdown_table(data: List[Dict], headers: List[str]) -> str:
    """Format data as Markdown table"""
    if not data:
        return ''
    
    # Create header row
    header_row = '| ' + ' | '.join(headers) + ' |'
    separator_row = '| ' + ' | '.join(['---'] * len(headers)) + ' |'
    
    # Create data rows
    data_rows = []
    for row in data:
        row_data = [str(row.get(header, '')) for header in headers]
        data_rows.append('| ' + ' | '.join(row_data) + ' |')
    
    return '\n'.join([header_row, separator_row] + data_rows)


def format_export_filename(prefix: str, file_type: str, timestamp: datetime = None) -> str:
    """Format export filename"""
    if timestamp is None:
        timestamp = datetime.now()
    
    timestamp_str = timestamp.strftime('%Y%m%d_%H%M%S')
    return f"{prefix}_{timestamp_str}.{file_type}"


def format_error_message(error: Exception) -> str:
    """Format error message for display"""
    error_type = type(error).__name__
    error_message = str(error)
    
    return f"{error_type}: {error_message}"


def format_validation_errors(errors: List[str]) -> str:
    """Format validation errors for display"""
    if not errors:
        return ''
    
    if len(errors) == 1:
        return errors[0]
    else:
        return f"Multiple errors: {'; '.join(errors)}"


def format_success_message(message: str, details: str = '') -> str:
    """Format success message for display"""
    if details:
        return f"✅ {message}: {details}"
    else:
        return f"✅ {message}"


def format_warning_message(message: str, details: str = '') -> str:
    """Format warning message for display"""
    if details:
        return f"⚠️ {message}: {details}"
    else:
        return f"⚠️ {message}"


def format_info_message(message: str, details: str = '') -> str:
    """Format info message for display"""
    if details:
        return f"ℹ️ {message}: {details}"
    else:
        return f"ℹ️ {message}"
