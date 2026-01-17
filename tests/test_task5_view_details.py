"""
Unit tests for Task 5: View to-do-list item details.

These tests simulate retrieving a single todo item (by id or owner)
and asserting that all required fields are present and correctly typed/valued.
"""

from datetime import datetime
from uuid import UUID

from src.models import TodoItem, Priority, Status


def test_view_todo_details_includes_all_fields():
    todo = TodoItem(
        id="detail-test-uuid",
        title="Detail Task",
        details="Detailed description",
        priority=Priority.HIGH,
        status=Status.PENDING,
        owner="viewer",
        created_at="2024-02-01T12:00:00",
        updated_at="2024-02-02T13:30:00",
    )

    data = todo.to_dict()

    # Ensure all expected keys exist
    expected_keys = {
        "id",
        "title",
        "details",
        "priority",
        "status",
        "owner",
        "created_at",
        "updated_at",
    }

    assert expected_keys.issubset(set(data.keys()))

    # Values preserved and types/format as expected
    assert data["id"] == "detail-test-uuid"
    assert data["title"] == "Detail Task"
    assert data["details"] == "Detailed description"
    assert data["priority"] == "HIGH"
    assert data["status"] == "PENDING"
    assert data["owner"] == "viewer"
    # ISO format parseable
    datetime.fromisoformat(data["created_at"])
    datetime.fromisoformat(data["updated_at"])


def test_view_todo_details_retrieve_by_id_from_list():
    todo1 = TodoItem(title="A", owner="user1")
    todo2 = TodoItem(id="target-id-123", title="Target", owner="user2")
    todo3 = TodoItem(title="C", owner="user3")

    todos_data = [todo1.to_dict(), todo2.to_dict(), todo3.to_dict()]

    # Simulate lookup by id as a view-details operation
    found = [t for t in todos_data if t.get("id") == "target-id-123"]
    assert len(found) == 1

    item = TodoItem.from_dict(found[0])
    assert item.id == "target-id-123"
    assert item.title == "Target"


def test_view_todo_details_defaults_when_missing_fields():
    # Simulate stored minimal record (e.g., some fields missing)
    minimal = {"id": "min-id-1", "title": "Minimal"}
    todo = TodoItem.from_dict(minimal)

    assert todo.id == "min-id-1"
    assert todo.title == "Minimal"
    # Defaults should apply
    assert todo.details == ""
    assert todo.priority == Priority.MID
    assert todo.status == Status.PENDING
    assert todo.owner == ""


def test_view_todo_details_timestamp_and_uuid_valid():
    todo = TodoItem(title="CheckTS")
    data = todo.to_dict()

    # id should be a valid UUID string
    UUID(data["id"])

    # timestamps parseable as ISO
    datetime.fromisoformat(data["created_at"])
    datetime.fromisoformat(data["updated_at"])
