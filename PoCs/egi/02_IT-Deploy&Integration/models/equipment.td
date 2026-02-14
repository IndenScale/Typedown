# Model: Equipment

> IT 设备建模：服务器、网络设备、PDU 等。

## EquipmentType

设备类型。

```model:EquipmentType
class EquipmentType(BaseModel):
    category: str = Field(..., pattern=r'^(server|switch|router|storage|pdu|kvm|blank|other)$')
    vendor: str
    model: str
```

## Port

设备端口定义。

```model:Port
class Port(BaseModel):
    port_id: str
    port_type: str = Field(..., pattern=r'^(rj45|sfp|sfp\+|sfp28|qsfp\+|qsfp28|power_c13|power_c14|power_c15|power_c19|power_c20|console|usb)$')
    status: str = Field(default="available", pattern=r'^(available|occupied|reserved|disabled)$')
    max_speed_gbps: Optional[float] = None
```

## PowerSpec

功耗规格。

```model:PowerSpec
class PowerSpec(BaseModel):
    rated_power: float = Field(..., gt=0)  # W
    typical_power: float = Field(..., gt=0)  # W
    max_power: float = Field(..., gt=0)  # W
    voltage: str = Field(default="AC220", pattern=r'^(AC110|AC220|AC240|DC48)$')
    redundancy: str = Field(default="none", pattern=r'^(none|n\+1|2n)$')
    
    @model_validator(mode='after')
    def check_power_consistency(self):
        assert self.typical_power <= self.rated_power, "典型功率不能超过额定功率"
        assert self.rated_power <= self.max_power, "额定功率不能超过最大功率"
        return self
```

## Equipment

通用设备模型。

```model:Equipment
class Equipment(BaseModel):
    asset_id: str = Field(..., pattern=r'^[A-Z]{2,4}-\d{4,6}$')
    name: str
    equipment_type: EquipmentType
    
    # 物理规格
    rack_units: int = Field(..., ge=0, le=50)  # U 数（PDU 可能为 0）
    mounting_depth: float = Field(..., ge=0, le=1000)  # mm（PDU 可能为 0）
    weight: float = Field(..., ge=0)  # kg
    
    # 功耗
    power: PowerSpec
    
    # 端口
    network_ports: List[Port] = Field(default_factory=list)
    power_ports: List[Port] = Field(default_factory=list)
    management_ports: List[Port] = Field(default_factory=list)
    
    # 部署位置
    deployed_in: Optional[Ref["Cabinet"]] = None
    start_u: Optional[int] = Field(None, ge=1, le=48)
```

## Server

服务器专用模型。

```model:Server
class Server(Equipment):
    cpu_model: str
    cpu_cores: int = Field(..., ge=1)
    cpu_count: int = Field(..., ge=1)
    memory_total_gb: int = Field(..., ge=1)
    storage_type: str = Field(..., pattern=r'^(hdd|ssd|nvme)$')
    storage_capacity_gb: int = Field(..., ge=1)
```

## NetworkSwitch

交换机专用模型。

```model:NetworkSwitch
class NetworkSwitch(Equipment):
    switch_type: str = Field(..., pattern=r'^(access|aggregation|core|tor)$')
    layer: int = Field(..., ge=2, le=3)
    total_ports: int = Field(..., ge=1)
    uplink_ports: int = Field(default=0)
```

## PDU

电源分配单元。

```model:PDU
class PDU(Equipment):
    pdu_type: str = Field(..., pattern=r'^(vertical|horizontal)$')
    phases: int = Field(..., ge=1, le=3)
    
    input_connector: str = Field(..., pattern=r'^(iec_60309|nema_l6-30|nema_l21-30)$')
    input_current_a: float = Field(..., gt=0)
    input_voltage_v: float = Field(..., gt=0)
    
    c13_outlets: int = Field(default=0)
    c19_outlets: int = Field(default=0)
    
    current_load_a: float = Field(default=0, ge=0)
    
    # 计算属性
    @property
    def input_power_va(self) -> float:
        power = self.input_voltage_v * self.input_current_a * self.phases
        if self.phases == 3:
            power *= 1.732  # √3
        return power
    
    @property
    def load_percentage(self) -> float:
        return (self.current_load_a / self.input_current_a) * 100 if self.input_current_a > 0 else 0
```
