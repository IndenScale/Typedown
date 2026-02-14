# Model: Cable

> 线缆建模：类型、长度、端口连接。

## CableType

线缆类型定义。

```model:CableType
class CableType(BaseModel):
    category: str = Field(..., pattern=r'^(power|network|fiber|console|kvm|dac|aoc)$')
    type_name: str
    gauge: Optional[str] = None  # 线规，如 "24AWG"
    max_length_m: float = Field(..., gt=0)
    bandwidth_gbps: Optional[float] = None
```

## CableConnector

线缆连接器。

```model:CableConnector
class CableConnector(BaseModel):
    connector_type: str = Field(..., pattern=r'^(rj45|lc|sc|fc|c13|c14|c15|c19|c20|usb_a|usb_c|qsfp|qsfp28|sfp|sfp\+)$')
    gender: str = Field(default="none", pattern=r'^(male|female|none)$')
```

## CableEndpoint

线缆端点。

```model:CableEndpoint
class CableEndpoint(BaseModel):
    equipment: Ref["Equipment"]
    port_id: str
    connector: CableConnector
```

## Cable

线缆实体。

```model:Cable
class Cable(BaseModel):
    cable_id: str
    name: str
    cable_type: Ref["CableType"]
    length_m: float = Field(..., gt=0)
    
    endpoint_a: CableEndpoint
    endpoint_b: CableEndpoint
    
    status: str = Field(default="planned", pattern=r'^(planned|installed|testing|active|decommissioned)$')
```
