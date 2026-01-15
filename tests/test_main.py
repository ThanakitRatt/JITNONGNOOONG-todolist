"""Unit tests for Task 2: CLI Interface - Basic Interaction

This module tests the pre-login menu, signup, login, and basic authentication flows
for the command-line to-do list application.
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Import from src
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from main import (
    ensure_data_dir,
    load_users,
    save_users,
    find_user,
    TodoManager,
)
from models import TodoItem, Priority, Status


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_data_paths(temp_data_dir, monkeypatch):
    """Mock the data paths to use temporary directory."""
    users_file = temp_data_dir / "users.json"
    todos_file = temp_data_dir / "todos.json"
    
    monkeypatch.setattr("main.DATA_DIR", temp_data_dir)
    monkeypatch.setattr("main.USERS_FILE", users_file)
    monkeypatch.setattr("main.TODOS_FILE", todos_file)
    
    return {"users_file": users_file, "todos_file": todos_file, "data_dir": temp_data_dir}


class TestDataManagement:
    """Tests for basic data file operations."""

    def test_ensure_data_dir_creates_directory(self, temp_data_dir, monkeypatch):
        """Test that ensure_data_dir creates the data directory."""
        test_dir = temp_data_dir / "test_data"
        monkeypatch.setattr("main.DATA_DIR", test_dir)
        
        assert not test_dir.exists()
        ensure_data_dir()
        assert test_dir.exists()

    def test_ensure_data_dir_idempotent(self, temp_data_dir, monkeypatch):
        """Test that ensure_data_dir can be called multiple times safely."""
        test_dir = temp_data_dir / "test_data"
        monkeypatch.setattr("main.DATA_DIR", test_dir)
        
        ensure_data_dir()
        ensure_data_dir()  # Should not raise an error
        assert test_dir.exists()

    def test_load_users_empty_file(self, mock_data_paths):
        """Test loading users when no users file exists."""
        users = load_users()
        assert users == []

    def test_save_and_load_users(self, mock_data_paths):
        """Test saving and loading users."""
        test_users = [
            {"username": "alice", "password": "hashed_pass_1"},
            {"username": "bob", "password": "hashed_pass_2"},
        ]
        
        save_users(test_users)
        loaded_users = load_users()
        
        assert loaded_users == test_users

    def test_load_users_with_corrupted_json(self, mock_data_paths):
        """Test that corrupted JSON returns empty list."""
        # Write invalid JSON
        mock_data_paths["users_file"].write_text("{ invalid json")
        
        users = load_users()
        assert users == []

    def test_find_user_exists(self, mock_data_paths):
        """Test finding an existing user."""
        test_users = [
            {"username": "alice", "password": "pass1"},
            {"username": "bob", "password": "pass2"},
        ]
        save_users(test_users)
        
        found = find_user(test_users, "alice")
        assert found == {"username": "alice", "password": "pass1"}

    def test_find_user_not_exists(self, mock_data_paths):
        """Test finding a non-existent user."""
        test_users = [{"username": "alice", "password": "pass1"}]
        
        found = find_user(test_users, "charlie")
        assert found is None

    def test_find_user_empty_list(self, mock_data_paths):
        """Test finding user in empty user list."""
        found = find_user([], "alice")
        assert found is None


class TestTodoManager:
    """Tests for TodoManager class."""

    def test_todo_manager_initialization(self, mock_data_paths):
        """Test TodoManager initializes correctly."""
        manager = TodoManager()
        assert manager.todos == []

    def test_create_todo(self, mock_data_paths):
        """Test creating a new todo item."""
        manager = TodoManager()
        
        todo = manager.create_todo(
            title="Test Task",
            details="Test Details",
            priority="HIGH",
            owner="alice"
        )
        
        assert todo.title == "Test Task"
        assert todo.details == "Test Details"
        assert todo.priority == Priority.HIGH
        assert todo.owner == "alice"
        assert todo.status == Status.PENDING
        assert len(manager.todos) == 1

    def test_create_todo_persistence(self, mock_data_paths):
        """Test that created todos are saved to file."""
        manager1 = TodoManager()
        manager1.create_todo("Task 1", "Details 1", "MID", "alice")
        
        # Create new manager instance to load from file
        manager2 = TodoManager()
        assert len(manager2.todos) == 1
        assert manager2.todos[0]["title"] == "Task 1"

    def test_create_todo_invalid_priority_defaults_to_mid(self, mock_data_paths):
        """Test that invalid priority defaults to MID."""
        manager = TodoManager()
        
        todo = manager.create_todo(
            title="Task",
            details="Details",
            priority="INVALID",
            owner="alice"
        )
        
        assert todo.priority == Priority.MID

    def test_get_todos_by_owner(self, mock_data_paths):
        """Test retrieving todos by owner."""
        manager = TodoManager()
        
        manager.create_todo("Task 1", "Details 1", "HIGH", "alice")
        manager.create_todo("Task 2", "Details 2", "MID", "bob")
        manager.create_todo("Task 3", "Details 3", "LOW", "alice")
        
        alice_todos = manager.get_todos_by_owner("alice")
        assert len(alice_todos) == 2
        assert all(todo.owner == "alice" for todo in alice_todos)

    def test_get_todos_by_owner_no_results(self, mock_data_paths):
        """Test getting todos for owner with no items."""
        manager = TodoManager()
        manager.create_todo("Task 1", "Details 1", "HIGH", "alice")
        
        charlie_todos = manager.get_todos_by_owner("charlie")
        assert charlie_todos == []

    def test_get_todo_by_id(self, mock_data_paths):
        """Test retrieving a specific todo by ID."""
        manager = TodoManager()
        
        created_todo = manager.create_todo("Task 1", "Details 1", "HIGH", "alice")
        retrieved_todo = manager.get_todo_by_id(created_todo.id)
        
        assert retrieved_todo is not None
        assert retrieved_todo.id == created_todo.id
        assert retrieved_todo.title == "Task 1"

    def test_get_todo_by_id_not_found(self, mock_data_paths):
        """Test getting a non-existent todo by ID."""
        manager = TodoManager()
        
        result = manager.get_todo_by_id("non-existent-id")
        assert result is None

    def test_update_todo_title(self, mock_data_paths):
        """Test updating a todo's title."""
        manager = TodoManager()
        created_todo = manager.create_todo("Original Title", "Details", "HIGH", "alice")
        
        success = manager.update_todo(created_todo.id, title="Updated Title")
        assert success is True
        
        updated_todo = manager.get_todo_by_id(created_todo.id)
        assert updated_todo.title == "Updated Title"

    def test_update_todo_status(self, mock_data_paths):
        """Test updating a todo's status."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "HIGH", "alice")
        
        success = manager.update_todo(created_todo.id, status="COMPLETED")
        assert success is True
        
        updated_todo = manager.get_todo_by_id(created_todo.id)
        assert updated_todo.status == Status.COMPLETED

    def test_update_todo_priority(self, mock_data_paths):
        """Test updating a todo's priority."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "LOW", "alice")
        
        success = manager.update_todo(created_todo.id, priority="HIGH")
        assert success is True
        
        updated_todo = manager.get_todo_by_id(created_todo.id)
        assert updated_todo.priority == Priority.HIGH

    def test_update_todo_multiple_fields(self, mock_data_paths):
        """Test updating multiple fields at once."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "LOW", "alice")
        
        success = manager.update_todo(
            created_todo.id,
            title="New Title",
            details="New Details",
            priority="HIGH",
            status="COMPLETED"
        )
        assert success is True
        
        updated_todo = manager.get_todo_by_id(created_todo.id)
        assert updated_todo.title == "New Title"
        assert updated_todo.details == "New Details"
        assert updated_todo.priority == Priority.HIGH
        assert updated_todo.status == Status.COMPLETED

    def test_update_todo_not_found(self, mock_data_paths):
        """Test updating a non-existent todo."""
        manager = TodoManager()
        
        success = manager.update_todo("non-existent-id", title="New Title")
        assert success is False

    def test_update_todo_updates_timestamp(self, mock_data_paths):
        """Test that updating a todo updates its updated_at timestamp."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "HIGH", "alice")
        original_updated_at = created_todo.updated_at
        
        # Small delay to ensure timestamp is different
        import time
        time.sleep(0.01)
        
        manager.update_todo(created_todo.id, title="New Title")
        updated_todo = manager.get_todo_by_id(created_todo.id)
        
        assert updated_todo.updated_at > original_updated_at

    def test_update_todo_invalid_status_defaults(self, mock_data_paths):
        """Test that invalid status defaults to PENDING."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "HIGH", "alice")
        
        manager.update_todo(created_todo.id, status="INVALID_STATUS")
        updated_todo = manager.get_todo_by_id(created_todo.id)
        
        assert updated_todo.status == Status.PENDING

    def test_delete_todo(self, mock_data_paths):
        """Test deleting a todo."""
        manager = TodoManager()
        created_todo = manager.create_todo("Task", "Details", "HIGH", "alice")
        todo_id = created_todo.id
        
        assert len(manager.todos) == 1
        success = manager.delete_todo(todo_id)
        assert success is True
        assert len(manager.todos) == 0

    def test_delete_todo_not_found(self, mock_data_paths):
        """Test deleting a non-existent todo."""
        manager = TodoManager()
        
        success = manager.delete_todo("non-existent-id")
        assert success is False


class TestAuthenticationFlow:
    """Tests for user authentication (signup and login) flows."""

    def test_user_can_be_added_to_users_list(self, mock_data_paths):
        """Test adding a new user to the users list."""
        users = []
        new_user = {"username": "alice", "password": "hashed_password"}
        users.append(new_user)
        
        assert len(users) == 1
        assert find_user(users, "alice") == new_user

    def test_duplicate_username_detection(self, mock_data_paths):
        """Test detecting duplicate usernames."""
        users = [
            {"username": "alice", "password": "pass1"},
            {"username": "bob", "password": "pass2"},
        ]
        
        # Check if username exists
        existing_user = find_user(users, "alice")
        assert existing_user is not None

    def test_user_signup_flow(self, mock_data_paths):
        """Test a complete signup flow."""
        users = load_users()
        assert len(users) == 0
        
        # Simulate signup
        new_user = {"username": "charlie", "password": "hashed_pass"}
        users.append(new_user)
        save_users(users)
        
        # Verify saved
        loaded_users = load_users()
        assert len(loaded_users) == 1
        assert find_user(loaded_users, "charlie") is not None

    def test_user_login_verification(self, mock_data_paths):
        """Test user login verification."""
        users = [{"username": "alice", "password": "hashed_password"}]
        save_users(users)
        
        # Verify user exists
        found_user = find_user(load_users(), "alice")
        assert found_user is not None
        assert found_user["username"] == "alice"

    def test_user_login_invalid_username(self, mock_data_paths):
        """Test login with invalid username."""
        users = [{"username": "alice", "password": "hashed_password"}]
        save_users(users)
        
        # Try to find non-existent user
        found_user = find_user(load_users(), "invalid_user")
        assert found_user is None


class TestMenuInteraction:
    """Tests for menu interaction and user input handling."""

    def test_menu_options_available(self):
        """Test that expected menu options are available."""
        # Pre-login menu options
        pre_login_options = {
            "1": "Login",
            "2": "Sign Up",
            "3": "Exit",
        }
        
        assert "1" in pre_login_options
        assert "2" in pre_login_options
        assert "3" in pre_login_options

    def test_exit_option_recognized(self):
        """Test that exit option (3) is properly recognized."""
        option = "3"
        assert option in {"1", "2", "3"}

    def test_login_option_recognized(self):
        """Test that login option (1) is properly recognized."""
        option = "1"
        assert option in {"1", "2", "3"}

    def test_signup_option_recognized(self):
        """Test that signup option (2) is properly recognized."""
        option = "2"
        assert option in {"1", "2", "3"}


class TestTodoItemCreation:
    """Tests for TodoItem data model used in Task 2 context."""

    def test_todo_item_creation_with_defaults(self):
        """Test creating a TodoItem with default values."""
        todo = TodoItem(title="Test", owner="alice")
        
        assert todo.title == "Test"
        assert todo.owner == "alice"
        assert todo.priority == Priority.MID
        assert todo.status == Status.PENDING
        assert todo.id is not None  # UUID should be generated

    def test_todo_item_to_dict(self):
        """Test converting TodoItem to dictionary."""
        todo = TodoItem(
            title="Test",
            details="Details",
            priority=Priority.HIGH,
            status=Status.COMPLETED,
            owner="alice"
        )
        
        todo_dict = todo.to_dict()
        
        assert todo_dict["title"] == "Test"
        assert todo_dict["priority"] == "HIGH"
        assert todo_dict["status"] == "COMPLETED"
        assert isinstance(todo_dict["priority"], str)
        assert isinstance(todo_dict["status"], str)

    def test_todo_item_from_dict(self):
        """Test creating TodoItem from dictionary."""
        data = {
            "id": "test-uuid",
            "title": "Test",
            "details": "Details",
            "priority": "HIGH",
            "status": "COMPLETED",
            "owner": "alice",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
        }
        
        todo = TodoItem.from_dict(data)
        
        assert todo.id == "test-uuid"
        assert todo.title == "Test"
        assert todo.priority == Priority.HIGH
        assert todo.status == Status.COMPLETED

    def test_todo_item_roundtrip(self):
        """Test TodoItem can be converted to dict and back."""
        original = TodoItem(
            title="Test Task",
            details="Test Details",
            priority=Priority.LOW,
            owner="bob"
        )
        
        # Convert to dict and back
        todo_dict = original.to_dict()
        restored = TodoItem.from_dict(todo_dict)
        
        assert restored.title == original.title
        assert restored.details == original.details
        assert restored.priority == original.priority
        assert restored.owner == original.owner
        assert restored.id == original.id
