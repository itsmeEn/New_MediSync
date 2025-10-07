"""
Async database utilities for MediSync backend.
This module provides async wrappers for database operations to prevent blocking.
"""

import asyncio
from functools import wraps
from typing import Any, Callable, Optional
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

def async_db_operation(func: Callable) -> Callable:
    """
    Decorator to convert synchronous database operations to async.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await sync_to_async(func)(*args, **kwargs)
        except Exception as e:
            logger.error(f"Async DB operation failed: {str(e)}")
            raise
    return wrapper

class AsyncModelManager:
    """
    Async wrapper for Django model operations.
    """
    
    @staticmethod
    async def get_object_or_none(model_class: models.Model, **kwargs) -> Optional[models.Model]:
        """
        Async version of get_object_or_404 that returns None instead of raising.
        """
        try:
            return await sync_to_async(model_class.objects.get)(**kwargs)
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting object: {str(e)}")
            raise

    @staticmethod
    async def create_object(model_class: models.Model, **kwargs) -> models.Model:
        """
        Async object creation.
        """
        try:
            return await sync_to_async(model_class.objects.create)(**kwargs)
        except Exception as e:
            logger.error(f"Error creating object: {str(e)}")
            raise

    @staticmethod
    async def update_object(instance: models.Model, **kwargs) -> models.Model:
        """
        Async object update.
        """
        try:
            for key, value in kwargs.items():
                setattr(instance, key, value)
            await sync_to_async(instance.save)()
            return instance
        except Exception as e:
            logger.error(f"Error updating object: {str(e)}")
            raise

    @staticmethod
    async def delete_object(instance: models.Model) -> bool:
        """
        Async object deletion.
        """
        try:
            await sync_to_async(instance.delete)()
            return True
        except Exception as e:
            logger.error(f"Error deleting object: {str(e)}")
            raise

    @staticmethod
    async def filter_objects(model_class: models.Model, **kwargs) -> list:
        """
        Async queryset filtering.
        """
        try:
            queryset = model_class.objects.filter(**kwargs)
            return await sync_to_async(list)(queryset)
        except Exception as e:
            logger.error(f"Error filtering objects: {str(e)}")
            raise

    @staticmethod
    async def count_objects(model_class: models.Model, **kwargs) -> int:
        """
        Async object count.
        """
        try:
            return await sync_to_async(model_class.objects.filter(**kwargs).count)()
        except Exception as e:
            logger.error(f"Error counting objects: {str(e)}")
            raise

class AsyncTransactionManager:
    """
    Async transaction management.
    """
    
    @staticmethod
    async def atomic_operation(operations: list[Callable]) -> Any:
        """
        Execute multiple database operations atomically.
        """
        from django.db import transaction
        
        async def execute_operations():
            results = []
            for operation in operations:
                if asyncio.iscoroutinefunction(operation):
                    result = await operation()
                else:
                    result = await sync_to_async(operation)()
                results.append(result)
            return results
        
        try:
            return await sync_to_async(transaction.atomic)()(execute_operations)()
        except Exception as e:
            logger.error(f"Atomic operation failed: {str(e)}")
            raise

# Async decorators for common operations
def async_safe(timeout: int = 30):
    """
    Decorator to add timeout and error handling to async operations.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
            except asyncio.TimeoutError:
                logger.error(f"Operation {func.__name__} timed out after {timeout} seconds")
                raise
            except Exception as e:
                logger.error(f"Operation {func.__name__} failed: {str(e)}")
                raise
        return wrapper
    return decorator