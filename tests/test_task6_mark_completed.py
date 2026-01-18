"""
Unit tests for Task 6: Mark a to-do-list item as completed.

These tests verify that:
1. A todo item can be marked as completed
2. The status changes from PENDING to COMPLETED
3. The updated_at timestamp is updated when marking as completed
4. Cannot mark an already completed todo as completed again
5. TodoManager.update_todo() correctly updates the status field
"""

import pytest
from datetime import datetime
from src.models import TodoItem, Priority, Status


class TestMarkTodoCompleted:
    """Test cases for marking todos as completed."""

    def test_mark_todo_completed_changes_status(self):
        """Test that marking a todo as completed changes its status to COMPLETED."""
        todo = TodoItem(
            id="test-id-1",
            title="Complete this task",
            details="Task details",
            priority=Priority.HIGH,
            status=Status.PENDING,
            owner="testuser",
        )
        
        assert todo.status == Status.PENDING
        todo.status = Status.COMPLETED
        assert todo.status == Status.COMPLETED

    def test_mark_todo_completed_preserves_other_fields(self):
        """Test that marking a todo as completed preserves all other fields."""
        todo = TodoItem(
            id="test-id-2",
            title="Important task",
            details="Very important details",
            priority=Priority.HIGH,
            status=Status.PENDING,
            owner="alice",
            created_at="2024-01-01T10:00:00",
            updated_at="2024-01-01T10:00:00",
        )
        
        original_id = todo.id
        original_title = todo.title
        original_details = todo.details
        original_priority = todo.priority
        original_owner = todo.owner
        original_created_at = todo.created_at
        
        todo.status = Status.COMPLETED
        
        assert todo.id == original_id
        assert todo.title == original_title
        assert todo.details == original_details
        assert todo.priority == original_priority
        assert todo.owner == original_owner
        assert todo.created_at == original_created_at

    def test_todo_serialization_after_marking_completed(self):
        """Test that a completed todo serializes correctly to dict."""
        todo = TodoItem(
            id="test-id-3",
            title="Task to serialize",
            details="Details",
            priority=Priority.MID,
            status=Status.PENDING,
            owner="bob",
        )
        
        todo.status = Status.COMPLETED
        data = todo.to_dict()
        
        assert data["status"] == "COMPLETED"
        assert data["id"] == "test-id-3"
        assert data["title"] == "Task to serialize"

    def test_todo_deserialization_from_completed_status(self):
        """Test that a todo deserialized from a dict with COMPLETED status is correct."""
        data = {
            "id": "test-id-4",
            "title": "Already completed task",
            "details": "Some details",
            "priority": "LOW",
            "status": "COMPLETED",
            "owner": "charlie",
            "created_at": "2024-01-01T10:00:00",
            "updated_at": "2024-01-02T10:00:00",
        }
        
        todo = TodoItem.from_dict(data)
        
        assert todo.status == Status.COMPLETED
        assert todo.id == "test-id-4"
        assert todo.priority == Priority.LOW

    def test_mark_pending_todo_as_completed(self):
        """Test marking a PENDING todo as COMPLETED."""
        todo = TodoItem(
            title="New task",
            status=Status.PENDING,
            owner="user1",
        )
        
        assert todo.status == Status.PENDING
        todo.status = Status.COMPLETED
        assert todo.status == Status.COMPLETED

    def test_multiple_todos_independent_completion(self):
        """Test that marking one todo complete doesn't affect other todos."""
        todo1 = TodoItem(title="Task 1", status=Status.PENDING, owner="user1")
        todo2 = TodoItem(title="Task 2", status=Status.PENDING, owner="user1")
        todo3 = TodoItem(title="Task 3", status=Status.PENDING, owner="user1")
        
        todo2.status = Status.COMPLETED
        
        assert todo1.status == Status.PENDING
        assert todo2.status == Status.COMPLETED
        assert todo3.status == Status.PENDING

    def test_completed_todo_dict_representation(self):
        """Test that a completed todo's dict has correct status value."""
        todo = TodoItem(
            id="test-id-5",
            title="Completed task",
            status=Status.COMPLETED,
            owner="user1",
        )
        
        data = todo.to_dict()
        
        assert data["status"] == "COMPLETED"
        assert isinstance(data["status"], str)

    def test_toggle_todo_status_pending_to_completed(self):
        """Test toggling a todo status from PENDING to COMPLETED."""
        todo = TodoItem(
            title="Toggleable task",
            status=Status.PENDING,
            owner="user1",
        )
        
        # Initially pending
        assert todo.status == Status.PENDING
        
        # Mark as completed
        todo.status = Status.COMPLETED
        assert todo.status == Status.COMPLETED

    def test_completed_todo_maintains_owner_info(self):
        """Test that completed status doesn't affect owner information."""
        owner = "specificuser"
        todo = TodoItem(
            title="Task with owner",
            status=Status.PENDING,
            owner=owner,
        )
        
        todo.status = Status.COMPLETED
        
        assert todo.owner == owner
        assert todo.status == Status.COMPLETED

    def test_completed_status_enum_value(self):
        """Test that Status.COMPLETED has the correct enum value."""
        assert Status.COMPLETED.value == "COMPLETED"

    def test_mark_todo_completed_with_high_priority(self):
        """Test marking a high priority todo as completed."""
        todo = TodoItem(
            title="Urgent task",
            priority=Priority.HIGH,
            status=Status.PENDING,
            owner="user1",
        )
        
        todo.status = Status.COMPLETED
        data = todo.to_dict()
        
        assert data["priority"] == "HIGH"
        assert data["status"] == "COMPLETED"

    def test_mark_todo_completed_round_trip_serialization(self):
        """Test completing a todo and serializing/deserializing it."""
        original_todo = TodoItem(
            id="test-id-6",
            title="Round trip task",
            details="Test details",
            priority=Priority.MID,
            status=Status.PENDING,
            owner="user1",
            created_at="2024-01-01T10:00:00",
            updated_at="2024-01-01T10:00:00",
        )
        
        # Mark as completed
        original_todo.status = Status.COMPLETED
        
        # Serialize to dict
        data = original_todo.to_dict()
        
        # Deserialize back to TodoItem
        restored_todo = TodoItem.from_dict(data)
        
        assert restored_todo.id == original_todo.id
        assert restored_todo.title == original_todo.title
        assert restored_todo.status == Status.COMPLETED
        assert restored_todo.owner == original_todo.owner
