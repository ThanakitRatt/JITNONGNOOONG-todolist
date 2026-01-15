"""Unit tests for Task 3: Models

This module tests the TodoItem data model, including creation, serialization,
deserialization, and enum handling.
"""

import pytest
import uuid
from pathlib import Path

# Import from src
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models import TodoItem, Priority, Status


class TestPriorityEnum:
    """Tests for the Priority enum."""

    def test_priority_values(self):
        """Test that Priority enum has correct values."""
        assert Priority.HIGH.value == "HIGH"
        assert Priority.MID.value == "MID"
        assert Priority.LOW.value == "LOW"

    def test_priority_from_string(self):
        """Test creating Priority enum from string values."""
        assert Priority("HIGH") == Priority.HIGH
        assert Priority("MID") == Priority.MID
        assert Priority("LOW") == Priority.LOW

    def test_priority_invalid_value(self):
        """Test that invalid priority values raise ValueError."""
        with pytest.raises(ValueError):
            Priority("INVALID")

    def test_priority_enum_members(self):
        """Test that all expected priority members exist."""
        assert hasattr(Priority, "HIGH")
        assert hasattr(Priority, "MID")
        assert hasattr(Priority, "LOW")


class TestStatusEnum:
    """Tests for the Status enum."""

    def test_status_values(self):
        """Test that Status enum has correct values."""
        assert Status.PENDING.value == "PENDING"
        assert Status.COMPLETED.value == "COMPLETED"

    def test_status_from_string(self):
        """Test creating Status enum from string values."""
        assert Status("PENDING") == Status.PENDING
        assert Status("COMPLETED") == Status.COMPLETED

    def test_status_invalid_value(self):
        """Test that invalid status values raise ValueError."""
        with pytest.raises(ValueError):
            Status("INVALID")

    def test_status_enum_members(self):
        """Test that all expected status members exist."""
        assert hasattr(Status, "PENDING")
        assert hasattr(Status, "COMPLETED")


class TestTodoItemCreation:
    """Tests for TodoItem creation and initialization."""

    def test_create_todo_with_defaults(self):
        """Test creating a TodoItem with default values."""
        todo = TodoItem()

        assert todo.title == ""
        assert todo.details == ""
        assert todo.priority == Priority.MID
        assert todo.status == Status.PENDING
        assert todo.owner == ""
        assert todo.id is not None
        assert todo.created_at is not None
        assert todo.updated_at is not None

    def test_create_todo_with_all_fields(self):
        """Test creating a TodoItem with all fields specified."""
        todo_id = str(uuid.uuid4())
        created = "2026-01-15T10:00:00"
        updated = "2026-01-15T11:00:00"

        todo = TodoItem(
            id=todo_id,
            title="Test Task",
            details="Test Details",
            priority=Priority.HIGH,
            status=Status.COMPLETED,
            owner="alice",
            created_at=created,
            updated_at=updated,
        )

        assert todo.id == todo_id
        assert todo.title == "Test Task"
        assert todo.details == "Test Details"
        assert todo.priority == Priority.HIGH
        assert todo.status == Status.COMPLETED
        assert todo.owner == "alice"
        assert todo.created_at == created
        assert todo.updated_at == updated

    def test_todo_id_is_unique(self):
        """Test that each TodoItem gets a unique ID."""
        todo1 = TodoItem()
        todo2 = TodoItem()

        assert todo1.id != todo2.id
        assert len(todo1.id) > 0
        assert len(todo2.id) > 0

    def test_todo_timestamps_are_generated(self):
        """Test that created_at and updated_at are set automatically."""
        todo = TodoItem()

        assert todo.created_at is not None
        assert todo.updated_at is not None
        assert len(todo.created_at) > 0
        assert len(todo.updated_at) > 0

    def test_create_todo_with_partial_fields(self):
        """Test creating a TodoItem with some fields specified."""
        todo = TodoItem(title="My Task", priority=Priority.LOW, owner="bob")

        assert todo.title == "My Task"
        assert todo.priority == Priority.LOW
        assert todo.owner == "bob"
        assert todo.status == Status.PENDING
        assert todo.details == ""


class TestTodoItemSerialization:
    """Tests for TodoItem serialization to dictionary."""

    def test_to_dict_basic(self):
        """Test converting a TodoItem to dictionary."""
        todo = TodoItem(
            id="test-id",
            title="Test",
            details="Test Details",
            priority=Priority.HIGH,
            status=Status.PENDING,
            owner="alice",
            created_at="2026-01-15T10:00:00",
            updated_at="2026-01-15T11:00:00",
        )

        result = todo.to_dict()

        assert result["id"] == "test-id"
        assert result["title"] == "Test"
        assert result["details"] == "Test Details"
        assert result["priority"] == "HIGH"
        assert result["status"] == "PENDING"
        assert result["owner"] == "alice"
        assert result["created_at"] == "2026-01-15T10:00:00"
        assert result["updated_at"] == "2026-01-15T11:00:00"

    def test_to_dict_enum_conversion(self):
        """Test that enums are converted to strings in to_dict."""
        todo = TodoItem(title="Test", priority=Priority.MID, status=Status.COMPLETED)

        result = todo.to_dict()

        assert isinstance(result["priority"], str)
        assert isinstance(result["status"], str)
        assert result["priority"] == "MID"
        assert result["status"] == "COMPLETED"

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict includes all TodoItem fields."""
        todo = TodoItem()
        result = todo.to_dict()

        required_fields = [
            "id",
            "title",
            "details",
            "priority",
            "status",
            "owner",
            "created_at",
            "updated_at",
        ]

        for field in required_fields:
            assert field in result


class TestTodoItemDeserialization:
    """Tests for TodoItem deserialization from dictionary."""

    def test_from_dict_basic(self):
        """Test creating a TodoItem from a dictionary."""
        data = {
            "id": "test-id",
            "title": "Test Task",
            "details": "Test Details",
            "priority": "HIGH",
            "status": "COMPLETED",
            "owner": "alice",
            "created_at": "2026-01-15T10:00:00",
            "updated_at": "2026-01-15T11:00:00",
        }

        todo = TodoItem.from_dict(data)

        assert todo.id == "test-id"
        assert todo.title == "Test Task"
        assert todo.details == "Test Details"
        assert todo.priority == Priority.HIGH
        assert todo.status == Status.COMPLETED
        assert todo.owner == "alice"
        assert todo.created_at == "2026-01-15T10:00:00"
        assert todo.updated_at == "2026-01-15T11:00:00"

    def test_from_dict_with_missing_fields(self):
        """Test from_dict with missing optional fields."""
        data = {"title": "Test Task", "owner": "alice"}

        todo = TodoItem.from_dict(data)

        assert todo.title == "Test Task"
        assert todo.owner == "alice"
        assert todo.details == ""
        assert todo.priority == Priority.MID
        assert todo.status == Status.PENDING
        assert todo.id is not None

    def test_from_dict_enum_conversion(self):
        """Test that string values are converted to enums in from_dict."""
        data = {"title": "Test", "priority": "LOW", "status": "PENDING"}

        todo = TodoItem.from_dict(data)

        assert isinstance(todo.priority, Priority)
        assert isinstance(todo.status, Status)
        assert todo.priority == Priority.LOW
        assert todo.status == Status.PENDING

    def test_from_dict_with_empty_dict(self):
        """Test from_dict with an empty dictionary."""
        todo = TodoItem.from_dict({})

        assert todo.title == ""
        assert todo.details == ""
        assert todo.priority == Priority.MID
        assert todo.status == Status.PENDING
        assert todo.owner == ""
        assert todo.id is not None

    def test_from_dict_preserves_id(self):
        """Test that from_dict preserves the ID from data."""
        specific_id = "custom-id-123"
        data = {"id": specific_id}

        todo = TodoItem.from_dict(data)

        assert todo.id == specific_id


class TestTodoItemRoundTrip:
    """Tests for serialization and deserialization round trips."""

    def test_to_dict_from_dict_roundtrip(self):
        """Test that to_dict and from_dict are inverse operations."""
        original = TodoItem(
            id="test-id",
            title="Test Task",
            details="Details",
            priority=Priority.HIGH,
            status=Status.COMPLETED,
            owner="alice",
            created_at="2026-01-15T10:00:00",
            updated_at="2026-01-15T11:00:00",
        )

        # Convert to dict and back
        data = original.to_dict()
        restored = TodoItem.from_dict(data)

        # Verify all fields match
        assert restored.id == original.id
        assert restored.title == original.title
        assert restored.details == original.details
        assert restored.priority == original.priority
        assert restored.status == original.status
        assert restored.owner == original.owner
        assert restored.created_at == original.created_at
        assert restored.updated_at == original.updated_at

    def test_multiple_roundtrips(self):
        """Test that multiple roundtrips maintain data integrity."""
        original = TodoItem(title="Test", priority=Priority.MID, owner="bob")

        # Multiple roundtrips
        todo = original
        for _ in range(3):
            todo = TodoItem.from_dict(todo.to_dict())

        assert todo.title == original.title
        assert todo.priority == original.priority
        assert todo.owner == original.owner


class TestTodoItemDataTypes:
    """Tests for TodoItem field data types."""

    def test_field_types(self):
        """Test that TodoItem fields have correct types."""
        todo = TodoItem(title="Test", priority=Priority.LOW, status=Status.PENDING)

        assert isinstance(todo.id, str)
        assert isinstance(todo.title, str)
        assert isinstance(todo.details, str)
        assert isinstance(todo.priority, Priority)
        assert isinstance(todo.status, Status)
        assert isinstance(todo.owner, str)
        assert isinstance(todo.created_at, str)
        assert isinstance(todo.updated_at, str)

    def test_enum_type_validation(self):
        """Test that priority and status are enum types."""
        todo = TodoItem(priority=Priority.HIGH, status=Status.COMPLETED)

        # Verify they are enum instances, not strings
        assert not isinstance(todo.priority, str)
        assert not isinstance(todo.status, str)
        assert hasattr(todo.priority, "value")
        assert hasattr(todo.status, "value")
