"""Tests for validation utilities."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from anyrun.utils import validate_model
from anyrun.utils.validation import ValidationError


class TestModel(BaseModel):
    """Test model for validation."""

    name: str = Field(min_length=3, max_length=50)
    age: int = Field(ge=0, le=120)
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    optional_field: Optional[str] = None


async def test_validate_model_success() -> None:
    """Test successful model validation."""
    data: Dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
    }
    result = await validate_model(TestModel, data)
    assert result.name == "John Doe"
    assert result.age == 30
    assert result.email == "john@example.com"


async def test_validate_model_invalid_name() -> None:
    """Test model validation with invalid name."""
    data: Dict[str, Any] = {
        "name": "Jo",  # Too short
        "age": 30,
        "email": "john@example.com",
    }
    try:
        await validate_model(TestModel, data)
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        assert "String should have at least 3 characters" in str(e)


async def test_validate_model_invalid_age() -> None:
    """Test model validation with invalid age."""
    data: Dict[str, Any] = {
        "name": "John Doe",
        "age": -1,  # Invalid age
        "email": "john@example.com",
    }
    try:
        await validate_model(TestModel, data)
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        assert "Input should be greater than or equal to 0" in str(e)


async def test_validate_model_invalid_email() -> None:
    """Test model validation with invalid email."""
    data: Dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "email": "invalid-email",  # Invalid email
    }
    try:
        await validate_model(TestModel, data)
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        assert "String should match pattern" in str(e)


async def test_validate_model_missing_field() -> None:
    """Test model validation with missing required field."""
    data: Dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        # Missing email field
    }
    try:
        await validate_model(TestModel, data)
        assert False, "Should raise ValidationError"
    except ValidationError as e:
        assert "Field required" in str(e)


async def test_validate_model_extra_field() -> None:
    """Test model validation with extra field."""
    data: Dict[str, Any] = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "extra_field": "value",  # Extra field
    }
    result = await validate_model(TestModel, data)
    assert not hasattr(result, "extra_field")
