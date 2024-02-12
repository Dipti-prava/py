import os

from django.utils import timezone


def get_file_extension(mimetype):
    extension = ''
    if mimetype == 'data:application/pdf':
        extension = 'pdf'
    elif mimetype == 'data:application/vnd.ms-powerpoint':
        extension = 'ppt'
    elif mimetype == 'data:application/vnd.openxmlformats-officedocument.presentationml.presentation':
        extension = 'pptx'
    elif mimetype in ['data:application/vnd.ms-excel', 'data:application/msexcel']:
        extension = 'xls'
    elif mimetype == 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        extension = 'xlsx'
    elif mimetype == 'data:application/msword':
        extension = 'doc'
    elif mimetype == 'data:application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        extension = 'docx'
    elif mimetype == 'data:image/jpg':
        extension = 'jpg'
    elif mimetype == 'data:image/jpeg':
        extension = 'jpeg'
    elif mimetype == 'data:image/png':
        extension = 'png'
    else:
        extension = '0'
    return extension


def get_allowed_extension(doctype):
    allowed_extensions = []
    if doctype == 'pdf':
        allowed_extensions = ['pdf']
    elif doctype == 'ppt':
        allowed_extensions = ['ppt', 'pptx']
    elif doctype == 'word':
        allowed_extensions = ['doc', 'docx']
    elif doctype == 'excel':
        allowed_extensions = ['xls', 'xlsx']
    elif doctype == 'image':
        allowed_extensions = ['jpg', 'jpeg', 'png']
    return allowed_extensions


def convert_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} KB"
    elif 1024 <= size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.0f} KB"
    elif 1024 ** 2 <= size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.0f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.0f} GB"


def size_multiplier(unit):
    units = {'KB': 1024, 'MB': 1024 * 1024, 'GB': 1024 * 1024 * 1024}  # Add more units if needed
    return units.get(unit, 1)  # Default to 1 for unknown units


def create_unique_name(name):
    now = timezone.now()
    unique_name = f"{name}_{now.year}{now.month}{now.day}_{now.hour}{now.minute}{now.second}"
    return unique_name


def document_upload_path(instance, filename):
    # Get the file extension
    extension = os.path.splitext(filename)[1][1:].lower()  # Get the file extension without '.'

    # Determine the sub folder based on the file extension
    if extension == 'pdf':
        return f'documents/pdf/{filename}'
    elif extension == 'xlsx' or extension == 'xls':
        return f'documents/excel/{filename}'
    elif extension in ['jpg', 'jpeg', 'png']:
        return f'documents/images/{filename}'
    elif extension == 'doc' or extension == 'docx':
        return f'documents/word/{filename}'
    elif extension == 'ppt' or extension == 'pptx':
        return f'documents/ppt/{filename}'
    else:
        return f'documents/others/{filename}'

