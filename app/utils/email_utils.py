"""
Email utilities for RCM SaaS Application
"""

import re
from typing import List, Dict, Any
from datetime import datetime


def validate_email_format(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def format_email_template(template: str, data: Dict[str, Any]) -> str:
    """Format email template with data"""
    try:
        return template.format(**data)
    except KeyError as e:
        raise ValueError(f"Missing template variable: {e}")


def extract_email_domain(email: str) -> str:
    """Extract domain from email address"""
    if '@' in email:
        return email.split('@')[1]
    return ""


def is_business_email(email: str) -> bool:
    """Check if email is from a business domain (not common personal email providers)"""
    personal_domains = [
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
        'aol.com', 'icloud.com', 'protonmail.com'
    ]
    
    domain = extract_email_domain(email).lower()
    return domain not in personal_domains


def generate_email_verification_token() -> str:
    """Generate email verification token"""
    import secrets
    return secrets.token_urlsafe(32)


def format_email_address(name: str, email: str) -> str:
    """Format email address with name"""
    if name and email:
        return f"{name} <{email}>"
    return email


def parse_email_address(email_str: str) -> Dict[str, str]:
    """Parse email address string into name and email"""
    if '<' in email_str and '>' in email_str:
        # Format: "Name <email@domain.com>"
        name_part = email_str.split('<')[0].strip()
        email_part = email_str.split('<')[1].split('>')[0].strip()
        return {'name': name_part, 'email': email_part}
    else:
        # Format: "email@domain.com"
        return {'name': '', 'email': email_str.strip()}
