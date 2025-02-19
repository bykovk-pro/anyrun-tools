"""Validation utilities for ANY.RUN Tools."""

import os
import re
from typing import Any, Type, TypeVar, Union, cast

from loguru import logger
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError

T = TypeVar("T", bound=BaseModel)


class ValidationError(Exception):
    """Validation error."""


def validate_api_key(api_key: str) -> None:
    """Validate ANY.RUN API key format.

    Args:
        api_key: API key to validate

    Raises:
        ValidationError: If API key is invalid
    """
    if not api_key:
        raise ValidationError("API key is required")

    # API key format: 32 hex characters
    if not re.match(r"^[a-f0-9]{32}$", api_key.lower()):
        raise ValidationError("Invalid API key format. Expected 32 hexadecimal characters.")


def validate_file_size(
    file_path: Union[str, bytes], max_size: int = 100 * 1024 * 1024  # 100MB
) -> None:
    """Validate file size.

    Args:
        file_path: Path to file or file content as bytes
        max_size: Maximum allowed file size in bytes

    Raises:
        ValidationError: If file size exceeds maximum
        FileNotFoundError: If file does not exist
    """
    try:
        if isinstance(file_path, str):
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            size = os.path.getsize(file_path)
        else:
            size = len(file_path)

        if size > max_size:
            raise ValidationError(
                f"File size ({size} bytes) exceeds maximum allowed size " f"({max_size} bytes)"
            )

        if size == 0:
            raise ValidationError("File is empty")

    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        logger.error(f"File validation error: {str(e)}")
        raise ValidationError(f"File validation failed: {str(e)}")


async def validate_model(model_class: Type[T], data: Any) -> T:
    """Validate data against Pydantic model.

    Args:
        model_class: Pydantic model class
        data: Data to validate

    Returns:
        T: Validated model instance

    Raises:
        ValidationError: If validation fails
    """
    try:
        return cast(T, model_class.model_validate(data))
    except PydanticValidationError as e:
        # Convert Pydantic validation error to our own ValidationError
        raise ValidationError(str(e)) from e
    except Exception as e:
        # Wrap other errors
        logger.error(f"Model validation error: {str(e)}")
        raise ValidationError(f"Model validation failed: {str(e)}") from e
