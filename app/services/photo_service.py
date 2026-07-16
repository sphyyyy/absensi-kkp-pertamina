import os
import uuid
from io import BytesIO

from PIL import Image
from flask import current_app


def validate_photo(photo_data):
    """Validate that the uploaded photo is a real image.

    Args:
        photo_data: File-like object or bytes.

    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    try:
        if isinstance(photo_data, bytes):
            img = Image.open(BytesIO(photo_data))
        else:
            img = Image.open(photo_data)

        img.verify()
        return True, None
    except Exception:
        return False, 'File yang dikirim bukan gambar yang valid.'


def save_photo(photo_data, user_id, attendance_type):
    """Save and resize a selfie photo to the upload directory.

    Args:
        photo_data: File-like object or bytes of the image.
        user_id: ID of the user for filename generation.
        attendance_type: 'check_in' or 'check_out'.

    Returns:
        str: Relative path to the saved file.
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    try:
        os.makedirs(upload_folder, exist_ok=True)
    except OSError:
        pass


    # Generate unique filename
    unique_id = uuid.uuid4().hex[:8]
    filename = f'{user_id}_{attendance_type}_{unique_id}.jpg'
    filepath = os.path.join(upload_folder, filename)

    # Open, resize, and save as JPEG
    if isinstance(photo_data, bytes):
        img = Image.open(BytesIO(photo_data))
    else:
        img = Image.open(photo_data)

    # Convert to RGB (in case of PNG with alpha)
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Resize to max 800px width while maintaining aspect ratio
    max_width = 800
    if img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.LANCZOS)

    img.save(filepath, 'JPEG', quality=85, optimize=True)
    return filename
