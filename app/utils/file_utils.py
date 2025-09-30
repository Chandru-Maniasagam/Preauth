"""
File utilities for RCM SaaS Application
"""

import os
import mimetypes
from typing import List, Dict, Any, Optional
from pathlib import Path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return Path(filename).suffix.lower()


def get_mime_type(filename: str) -> str:
    """Get MIME type for file"""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return get_file_extension(filename) in image_extensions


def is_document_file(filename: str) -> bool:
    """Check if file is a document"""
    doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'}
    return get_file_extension(filename) in doc_extensions


def is_spreadsheet_file(filename: str) -> bool:
    """Check if file is a spreadsheet"""
    spreadsheet_extensions = {'.xls', '.xlsx', '.csv', '.ods'}
    return get_file_extension(filename) in spreadsheet_extensions


def get_file_size_mb(filepath: str) -> float:
    """Get file size in MB"""
    if os.path.exists(filepath):
        size_bytes = os.path.getsize(filepath)
        return size_bytes / (1024 * 1024)
    return 0.0


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing invalid characters"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = 'unnamed_file'
    
    return filename


def create_directory_if_not_exists(directory_path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except OSError:
        return False


def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get comprehensive file information"""
    if not os.path.exists(filepath):
        return {}
    
    stat = os.stat(filepath)
    
    return {
        'filename': os.path.basename(filepath),
        'size_bytes': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'extension': get_file_extension(filepath),
        'mime_type': get_mime_type(filepath),
        'is_image': is_image_file(filepath),
        'is_document': is_document_file(filepath),
        'is_spreadsheet': is_spreadsheet_file(filepath),
        'created_at': stat.st_ctime,
        'modified_at': stat.st_mtime
    }


def validate_file_size(filepath: str, max_size_mb: float) -> bool:
    """Validate file size against maximum allowed size"""
    size_mb = get_file_size_mb(filepath)
    return size_mb <= max_size_mb


def get_safe_filename(original_filename: str, directory: str = "") -> str:
    """Get a safe filename that doesn't conflict with existing files"""
    base_name = Path(original_filename).stem
    extension = get_file_extension(original_filename)
    
    if directory:
        full_path = os.path.join(directory, f"{base_name}{extension}")
    else:
        full_path = f"{base_name}{extension}"
    
    counter = 1
    while os.path.exists(full_path):
        if directory:
            full_path = os.path.join(directory, f"{base_name}_{counter}{extension}")
        else:
            full_path = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return os.path.basename(full_path)
