"""Tests for validation utilities."""

import pytest
from pydantic import BaseModel, Field

from anyrun.utils.validation import ValidationError, validate_model


class TestModel(BaseModel):
    """Test model for validation."""

    name: str = Field(min_length=1, max_length=64)
    age: int = Field(ge=0, le=150)
    email: str = Field(pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def test_validate_model_success() -> None:
    """Test successful model validation."""
    data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
    }
    result = validate_model(TestModel, data)
    assert result.name == "John Doe"
    assert result.age == 30
    assert result.email == "john@example.com"


def test_validate_model_invalid_name() -> None:
    """Test model validation with invalid name."""
    data = {
        "name": "",  # Empty name
        "age": 30,
        "email": "john@example.com",
    }
    with pytest.raises(ValidationError):
        validate_model(TestModel, data)


def test_validate_model_invalid_age() -> None:
    """Test model validation with invalid age."""
    data = {
        "name": "John Doe",
        "age": -1,  # Negative age
        "email": "john@example.com",
    }
    with pytest.raises(ValidationError):
        validate_model(TestModel, data)


def test_validate_model_invalid_email() -> None:
    """Test model validation with invalid email."""
    data = {
        "name": "John Doe",
        "age": 30,
        "email": "invalid-email",  # Invalid email format
    }
    with pytest.raises(ValidationError):
        validate_model(TestModel, data)


def test_validate_model_missing_field() -> None:
    """Test model validation with missing field."""
    data = {
        "name": "John Doe",
        "age": 30,
        # Missing email field
    }
    with pytest.raises(ValidationError):
        validate_model(TestModel, data)


def test_validate_model_extra_field() -> None:
    """Test model validation with extra field."""
    data = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "extra": "field",  # Extra field
    }
    result = validate_model(TestModel, data)
    assert not hasattr(result, "extra")  # Extra field should be ignored 