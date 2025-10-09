"""
Image utility functions for profile picture handling.
Provides validation, optimization, and secure processing of uploaded images.
"""

import os
import uuid
from io import BytesIO
from typing import Tuple, Optional, Dict, Any
from PIL import Image, ImageOps, ExifTags
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError
from django.conf import settings
import hashlib


class ImageProcessor:
    """
    Comprehensive image processing class for profile pictures.
    Handles validation, optimization, and secure storage.
    """
    
    # Supported image formats
    ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
    ALLOWED_MIME_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']
    
    # Size constraints
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    MIN_FILE_SIZE = 1024  # 1KB
    MAX_DIMENSIONS = (2000, 2000)  # Max width, height
    MIN_DIMENSIONS = (50, 50)  # Min width, height
    
    # Optimization settings
    THUMBNAIL_SIZES = {
        'small': (150, 150),
        'medium': (300, 300),
        'large': (600, 600)
    }
    JPEG_QUALITY = 85
    PNG_OPTIMIZE = True
    
    @staticmethod
    def validate_image_file(uploaded_file) -> Dict[str, Any]:
        """
        Comprehensive validation of uploaded image file.
        
        Args:
            uploaded_file: Django UploadedFile object
            
        Returns:
            Dict with validation results and metadata
            
        Raises:
            ValidationError: If validation fails
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # Check if file exists
        if not uploaded_file:
            raise ValidationError("No file provided.")
        
        # File size validation
        if uploaded_file.size > ImageProcessor.MAX_FILE_SIZE:
            size_mb = uploaded_file.size / (1024 * 1024)
            raise ValidationError(
                f"File size ({size_mb:.2f}MB) exceeds maximum allowed size "
                f"({ImageProcessor.MAX_FILE_SIZE / (1024 * 1024)}MB)."
            )
        
        if uploaded_file.size < ImageProcessor.MIN_FILE_SIZE:
            raise ValidationError("File is too small. Please upload a valid image.")
        
        # MIME type validation
        if uploaded_file.content_type not in ImageProcessor.ALLOWED_MIME_TYPES:
            raise ValidationError(
                f"Unsupported file type: {uploaded_file.content_type}. "
                f"Allowed types: {', '.join(ImageProcessor.ALLOWED_MIME_TYPES)}"
            )
        
        # File extension validation
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension not in ImageProcessor.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"Unsupported file extension: {file_extension}. "
                f"Allowed extensions: {', '.join(ImageProcessor.ALLOWED_EXTENSIONS)}"
            )
        
        # Try to open and validate the image
        try:
            with Image.open(uploaded_file) as img:
                # Verify it's a valid image
                img.verify()
                
                # Re-open for further processing (verify() closes the file)
                uploaded_file.seek(0)
                with Image.open(uploaded_file) as img:
                    # Format validation
                    if img.format not in ImageProcessor.ALLOWED_FORMATS:
                        raise ValidationError(
                            f"Unsupported image format: {img.format}. "
                            f"Allowed formats: {', '.join(ImageProcessor.ALLOWED_FORMATS)}"
                        )
                    
                    # Dimension validation
                    width, height = img.size
                    if width < ImageProcessor.MIN_DIMENSIONS[0] or height < ImageProcessor.MIN_DIMENSIONS[1]:
                        raise ValidationError(
                            f"Image dimensions ({width}x{height}) are too small. "
                            f"Minimum size: {ImageProcessor.MIN_DIMENSIONS[0]}x{ImageProcessor.MIN_DIMENSIONS[1]} pixels."
                        )
                    
                    if width > ImageProcessor.MAX_DIMENSIONS[0] or height > ImageProcessor.MAX_DIMENSIONS[1]:
                        validation_result['warnings'].append(
                            f"Image dimensions ({width}x{height}) are large and will be resized to "
                            f"{ImageProcessor.MAX_DIMENSIONS[0]}x{ImageProcessor.MAX_DIMENSIONS[1]} pixels."
                        )
                    
                    # Store metadata
                    validation_result['metadata'] = {
                        'format': img.format,
                        'mode': img.mode,
                        'size': img.size,
                        'file_size': uploaded_file.size,
                        'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
                    }
                    
        except Exception as e:
            raise ValidationError(f"Invalid image file: {str(e)}")
        
        # Reset file pointer
        uploaded_file.seek(0)
        return validation_result
    
    @staticmethod
    def optimize_image(uploaded_file, max_size: Tuple[int, int] = None) -> InMemoryUploadedFile:
        """
        Optimize uploaded image for storage and performance.
        
        Args:
            uploaded_file: Django UploadedFile object
            max_size: Optional tuple of (width, height) for resizing
            
        Returns:
            Optimized InMemoryUploadedFile
        """
        if max_size is None:
            max_size = ImageProcessor.MAX_DIMENSIONS
        
        try:
            with Image.open(uploaded_file) as img:
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Convert to RGB if necessary (for JPEG compatibility)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background for transparency
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if necessary
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save optimized image
                output = BytesIO()
                
                # Determine format and quality
                original_format = img.format or 'JPEG'
                if original_format == 'PNG' and not hasattr(img, 'transparency'):
                    # Convert PNG to JPEG if no transparency
                    img.save(output, format='JPEG', quality=ImageProcessor.JPEG_QUALITY, optimize=True)
                    file_extension = '.jpg'
                    content_type = 'image/jpeg'
                elif original_format == 'PNG':
                    img.save(output, format='PNG', optimize=ImageProcessor.PNG_OPTIMIZE)
                    file_extension = '.png'
                    content_type = 'image/png'
                else:
                    img.save(output, format='JPEG', quality=ImageProcessor.JPEG_QUALITY, optimize=True)
                    file_extension = '.jpg'
                    content_type = 'image/jpeg'
                
                output.seek(0)
                
                # Generate secure filename
                original_name = os.path.splitext(uploaded_file.name)[0]
                secure_filename = f"{original_name}_{uuid.uuid4().hex[:8]}{file_extension}"
                
                # Create optimized file object
                optimized_file = InMemoryUploadedFile(
                    output,
                    'ImageField',
                    secure_filename,
                    content_type,
                    output.getbuffer().nbytes,
                    None
                )
                
                return optimized_file
                
        except Exception as e:
            raise ValidationError(f"Failed to optimize image: {str(e)}")
    
    @staticmethod
    def generate_secure_filename(original_filename: str, user_id: int) -> str:
        """
        Generate a secure filename for uploaded images.
        
        Args:
            original_filename: Original filename from upload
            user_id: User ID for uniqueness
            
        Returns:
            Secure filename string
        """
        # Extract extension
        _, ext = os.path.splitext(original_filename)
        if not ext:
            ext = '.jpg'  # Default extension
        
        # Create hash from user_id and timestamp
        timestamp = str(uuid.uuid4().int)
        hash_input = f"{user_id}_{timestamp}_{original_filename}"
        file_hash = hashlib.md5(hash_input.encode()).hexdigest()[:12]
        
        # Generate secure filename
        secure_name = f"profile_{user_id}_{file_hash}{ext.lower()}"
        return secure_name
    
    @staticmethod
    def get_upload_path(instance, filename: str) -> str:
        """
        Generate upload path for profile pictures with date-based organization.
        
        Args:
            instance: Model instance
            filename: Original filename
            
        Returns:
            Upload path string
        """
        from datetime import datetime
        
        # Generate secure filename
        secure_filename = ImageProcessor.generate_secure_filename(filename, instance.id or 0)
        
        # Create date-based path
        now = datetime.now()
        path = f"profile_pictures/{now.year}/{now.month:02d}/{now.day:02d}/{secure_filename}"
        
        return path


def get_upload_path(instance, filename: str) -> str:
    """
    Standalone function for Django model upload_to parameter.
    """
    return ImageProcessor.get_upload_path(instance, filename)
    
    @staticmethod
    def create_thumbnails(image_file, sizes: Dict[str, Tuple[int, int]] = None) -> Dict[str, InMemoryUploadedFile]:
        """
        Create multiple thumbnail sizes from an image.
        
        Args:
            image_file: Source image file
            sizes: Dictionary of size names and dimensions
            
        Returns:
            Dictionary of thumbnail files
        """
        if sizes is None:
            sizes = ImageProcessor.THUMBNAIL_SIZES
        
        thumbnails = {}
        
        try:
            with Image.open(image_file) as img:
                # Handle EXIF orientation
                img = ImageOps.exif_transpose(img)
                
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                for size_name, dimensions in sizes.items():
                    # Create thumbnail
                    thumb = img.copy()
                    thumb.thumbnail(dimensions, Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    output = BytesIO()
                    thumb.save(output, format='JPEG', quality=ImageProcessor.JPEG_QUALITY, optimize=True)
                    output.seek(0)
                    
                    # Create filename
                    original_name = os.path.splitext(image_file.name)[0]
                    thumb_filename = f"{original_name}_{size_name}.jpg"
                    
                    # Create file object
                    thumb_file = InMemoryUploadedFile(
                        output,
                        'ImageField',
                        thumb_filename,
                        'image/jpeg',
                        output.getbuffer().nbytes,
                        None
                    )
                    
                    thumbnails[size_name] = thumb_file
                    
        except Exception as e:
            raise ValidationError(f"Failed to create thumbnails: {str(e)}")
        
        return thumbnails


def validate_profile_picture(uploaded_file):
    """
    Django validator function for profile pictures.
    
    Args:
        uploaded_file: Django UploadedFile object
        
    Raises:
        ValidationError: If validation fails
    """
    ImageProcessor.validate_image_file(uploaded_file)


def process_profile_picture(uploaded_file, user_id: int = None) -> InMemoryUploadedFile:
    """
    Complete processing pipeline for profile pictures.
    
    Args:
        uploaded_file: Django UploadedFile object
        user_id: Optional user ID for secure naming
        
    Returns:
        Processed and optimized image file
    """
    # Validate the image
    ImageProcessor.validate_image_file(uploaded_file)
    
    # Optimize the image
    optimized_file = ImageProcessor.optimize_image(uploaded_file)
    
    return optimized_file