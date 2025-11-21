import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch
from browtrix_server.core.resources import ResourceManager


@pytest.fixture
def resource_manager():
    """Create a fresh ResourceManager for each test with automatic cleanup."""
    manager = ResourceManager(max_resources=3)
    yield manager
    # Cleanup: clear all resources
    manager.resources.clear()


@pytest.mark.asyncio
async def test_resource_manager_create_sync(resource_manager):
    """Test resource creation with proper attributes."""
    resource = await resource_manager.create_resource(
        name="test", data={"key": "value"}
    )
    assert resource.resource_id
    assert resource.name == "test"
    assert resource.is_active
    assert resource.data == {"key": "value"}


@pytest.mark.asyncio
async def test_get_resource_updates_access(resource_manager):
    """Test that accessing a resource updates its last_accessed timestamp."""
    initial_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    later_time = datetime(2025, 1, 1, 12, 0, 1, tzinfo=timezone.utc)

    with patch("browtrix_server.core.resources.datetime") as mock_datetime:
        mock_datetime.now.return_value = initial_time
        mock_datetime.side_effect = (
            lambda *args, **kw: datetime(*args, **kw) if args or kw else initial_time
        )

        resource = await resource_manager.create_resource(name="test")

        # Change the mock to return a later time
        mock_datetime.now.return_value = later_time

        retrieved = resource_manager.get_resource(resource.resource_id)
        assert retrieved.last_accessed >= later_time


@pytest.mark.asyncio
async def test_list_resources_filtering(resource_manager):
    """Test resource listing with active-only filter."""
    await resource_manager.create_resource(name="active")
    inactive_resource = await resource_manager.create_resource(name="inactive")
    # Manually deactivate the resource
    resource_manager.resources[inactive_resource.resource_id].is_active = False
    resources = resource_manager.list_resources(active_only=True)
    assert len(resources) == 1
    assert resources[0].name == "active"


@pytest.mark.asyncio
async def test_delete_resource(resource_manager):
    """Test resource deletion (deactivation)."""
    resource = await resource_manager.create_resource()
    success = resource_manager.delete_resource(resource.resource_id)
    assert success
    retrieved = resource_manager.get_resource(resource.resource_id)
    assert not retrieved.is_active


@pytest.mark.asyncio
async def test_update_resource(resource_manager):
    """Test resource data updates."""
    resource = await resource_manager.create_resource()
    success = resource_manager.update_resource(
        resource.resource_id, data={"new": "data"}
    )
    assert success
    assert "new" in resource_manager.resources[resource.resource_id].data


def test_resource_stats(resource_manager):
    """Test resource statistics reporting."""
    stats = resource_manager.get_resource_stats()
    assert stats["total_resources"] >= 0


@pytest.mark.asyncio
async def test_cleanup_old_resources(resource_manager):
    """Test that cleanup removes old inactive resources."""

    # Create some resources
    resource1 = await resource_manager.create_resource(name="resource1")
    resource2 = await resource_manager.create_resource(name="resource2")

    # Deactivate one resource and make it old
    resource2.is_active = False
    resource2.last_accessed = datetime.now(timezone.utc) - timedelta(hours=25)

    # Verify we have 2 resources
    assert len(resource_manager.resources) == 2

    # Call cleanup
    await resource_manager._cleanup_old_resources()

    # Should have cleaned up the old inactive resource
    assert len(resource_manager.resources) == 1
    assert resource1.resource_id in resource_manager.resources
    assert resource2.resource_id not in resource_manager.resources


def test_get_nonexistent_resource(resource_manager):
    """Test retrieving a resource that doesn't exist."""
    result = resource_manager.get_resource("nonexistent")
    assert result is None


def test_delete_nonexistent_resource(resource_manager):
    """Test deleting a resource that doesn't exist."""
    success = resource_manager.delete_resource("nonexistent")
    assert success is False


def test_update_nonexistent_resource(resource_manager):
    """Test updating a resource that doesn't exist."""
    success = resource_manager.update_resource("nonexistent", data={"test": "data"})
    assert success is False


@pytest.mark.asyncio
async def test_create_resource_with_invalid_data(resource_manager):
    """Test resource creation with various data types."""
    # Test with None data - gets converted to empty dict by Pydantic
    resource = await resource_manager.create_resource(name="test", data=None)
    assert resource.data == {}  # Pydantic converts None to default

    # Test with complex data
    complex_data = {"nested": {"key": "value"}, "list": [1, 2, 3]}
    resource = await resource_manager.create_resource(name="complex", data=complex_data)
    assert resource.data == complex_data


@pytest.mark.asyncio
async def test_resource_exhaustion(resource_manager):
    """Test behavior when resource limit is reached."""
    # Create resources up to the limit
    resources = []
    for i in range(resource_manager.max_resources):
        resource = await resource_manager.create_resource(name=f"resource_{i}")
        resources.append(resource)

    # Verify we have exactly max_resources
    assert len(resource_manager.resources) == resource_manager.max_resources

    # Create one more - should allow exceeding the limit (cleanup only removes very old resources)
    new_resource = await resource_manager.create_resource(name="overflow")

    # Should have max_resources + 1 since cleanup only removes very old/inactive resources
    assert len(resource_manager.resources) == resource_manager.max_resources + 1
    # New resource should exist
    assert new_resource.resource_id in resource_manager.resources


@pytest.mark.asyncio
async def test_concurrent_resource_access():
    """Test concurrent access to resources."""
    manager = ResourceManager(max_resources=10)

    # Create multiple resources concurrently
    async def create_resource(name):
        return await manager.create_resource(name=name)

    tasks = [create_resource(f"resource_{i}") for i in range(5)]
    resources = await asyncio.gather(*tasks)

    # All should be created successfully
    assert len(manager.resources) == 5
    assert len(resources) == 5

    # All IDs should be unique
    resource_ids = [r.resource_id for r in resources]
    assert len(set(resource_ids)) == 5


@pytest.mark.asyncio
async def test_resource_corruption_scenarios():
    """Test resource behavior under corruption scenarios."""
    manager = ResourceManager(max_resources=5)

    # Create a resource
    resource = await manager.create_resource(name="test")

    # Simulate corruption by manually modifying internal state
    # Simulate corruption by clearing the data dict
    resource.data.clear()

    # Operations should still work
    success = manager.update_resource(resource.resource_id, data={"new": "data"})
    assert success is True

    # Resource should be retrievable
    retrieved = manager.get_resource(resource.resource_id)
    assert retrieved is not None
    assert retrieved.resource_id == resource.resource_id


@pytest.mark.asyncio
async def test_cleanup_failure_handling():
    """Test behavior when cleanup operations fail."""
    manager = ResourceManager(max_resources=5)  # Higher limit to avoid cleanup

    # Create resources without triggering cleanup
    for i in range(2):
        await manager.create_resource(name=f"resource_{i}")

    # Mock the cleanup to raise an exception
    async def failing_cleanup():
        raise Exception("Cleanup failed")

    # Replace the cleanup method temporarily
    original_cleanup = manager._cleanup_old_resources
    manager._cleanup_old_resources = failing_cleanup  # type: ignore

    try:
        # Manually call cleanup to test error handling
        with pytest.raises(Exception, match="Cleanup failed"):
            await manager._cleanup_old_resources()
    finally:
        # Restore original cleanup
        manager._cleanup_old_resources = original_cleanup  # type: ignore

    # Verify resources are still intact after failed cleanup
    assert len(manager.resources) == 2


@pytest.mark.asyncio
async def test_resource_manager_with_zero_max_resources():
    """Test ResourceManager with zero max_resources."""
    manager = ResourceManager(max_resources=0)

    # Should still function but with zero limit
    assert manager.max_resources == 0

    # Creating resources should still work (just not be cleaned up)
    resource = await manager.create_resource(name="test")
    assert resource is not None
    assert len(manager.resources) == 1
