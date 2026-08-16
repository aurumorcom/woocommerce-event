"""Unit tests for system status schemas."""

from woocommerce_event.modules.system_status.schemas import (
    DatabaseInfo,
    EnvironmentInfo,
    SecurityInfo,
    SystemStatus,
    SystemStatusSampled,
)


def test_system_status_validation():
    """Test validating sample system status structure."""
    status = SystemStatus(
        environment=EnvironmentInfo(version="8.5.0", wp_version="6.4.2"),
        database=DatabaseInfo(wc_database_version="8.5.0"),
        security=SecurityInfo(secure_connection=True),
    )
    assert status.environment is not None
    assert status.environment.version == "8.5.0"
    assert status.database is not None
    assert status.database.wc_database_version == "8.5.0"


def test_system_status_sampled_cloudevent():
    """Test SystemStatusSampled CloudEvent schema."""
    status = SystemStatus(
        environment=EnvironmentInfo(version="8.5.0"),
    )
    event = SystemStatusSampled(
        id="evt-health-1",
        source="woocommerce://101/system_status",
        subject="101",
        tenant_id=1,
        data=status,
    )
    assert event.type == "woocommerce.system_status.sampled"
    assert event.subject == "101"
    assert event.tenant_id == 1
    assert event.data.environment is not None
