from enum import Enum
from typing import List, Optional
from pydantic import Field
from ..core.primitives import BaseEntity

class RackType(str, Enum):
    STANDARD_42U = "42U Standard"
    NETWORK_24U = "24U Network"

class Rack(BaseEntity):
    """机柜定义"""
    room_code: str
    code: str
    type: RackType
    location_grid: str # e.g. "A-01"

class DeviceStatus(str, Enum):
    PROVISIONING = "Provisioning"
    ONLINE = "Online"
    MAINTENANCE = "Maintenance"
    OFFLINE = "Offline"

class NetworkDevice(BaseEntity):
    """网络设备/服务器"""
    rack_id: str
    u_position: int = Field(..., description="U位起始", ge=1, le=42)
    u_height: int = Field(default=1)
    hostname: str
    ip_address: Optional[str] = None
    brand_model: str
    status: DeviceStatus = DeviceStatus.PROVISIONING

class PortType(str, Enum):
    RJ45 = "RJ45"
    SFP_PLUS = "SFP+"
    FIBER_LC = "Fiber-LC"

class CablingRecord(BaseEntity):
    """跳线/连接记录"""
    source_device_id: str
    source_port: str
    target_device_id: str
    target_port: str
    cable_type: str = "Cat6"
    cable_id: Optional[str] = None
    installer_id: str
    connected_at: str
