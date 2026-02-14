# Model: Cabinet

> 机柜建模：槽位管理、承重、功耗预算、散热。

## CabinetSpec

机柜规格。

```model:CabinetSpec
class CabinetSpec(BaseModel):
    standard: str = Field(default="19-inch", pattern=r'^(19-inch|23-inch|etsi)$')
    total_units: int = Field(default=42, ge=42, le=48)
    
    # 物理尺寸
    width_mm: float = Field(default=600, gt=0)
    depth_mm: float = Field(default=1200, gt=0)
    
    # 承重能力
    max_static_load_kg: float = Field(..., gt=0)
    max_dynamic_load_kg: float = Field(..., gt=0)
    
    # 电力容量
    power_capacity_kw: float = Field(..., gt=0)
    pdu_count: int = Field(default=2, ge=1, le=4)
```

## CabinetSlot

机柜槽位状态。

```model:CabinetSlot
class CabinetSlot(BaseModel):
    unit_number: int = Field(..., ge=1)
    status: str = Field(default="empty", pattern=r'^(empty|occupied|reserved|blocked)$')
    occupied_by: Optional[Ref["Equipment"]] = None
```

## Cabinet

机柜实体。

```model:Cabinet
class Cabinet(BaseModel):
    cabinet_id: str = Field(..., pattern=r'^[A-Z]\d{2}-\d{2}$')  # 如 A01-05
    name: str
    room: str
    row: str
    position: int
    
    spec: CabinetSpec
    slots: List[CabinetSlot] = Field(default_factory=list)
    equipments: List[Ref["Equipment", "Server", "NetworkSwitch"]] = Field(default_factory=list)
    pdus: List[Ref["PDU"]] = Field(default_factory=list)
    
    # 散热
    airflow: str = Field(default="front-to-back", pattern=r'^(front-to-back|back-to-front|side-to-side)$')
    max_heat_dissipation_w: float = Field(default=12000, gt=0)
    
    # 计算当前重量
    @property
    def current_weight_kg(self) -> float:
        total = sum(resolve(e).weight for e in self.equipments)
        total += sum(resolve(p).weight for p in self.pdus)
        return total
    
    # 计算当前功率
    @property
    def current_power_w(self) -> float:
        return sum(resolve(e).power.rated_power for e in self.equipments)
    
    @model_validator(mode='after')
    def check_slot_count(self):
        if len(self.slots) != self.spec.total_units:
            raise ValueError(f"槽位数量 {len(self.slots)} 与规格 {self.spec.total_units} 不匹配")
        return self
    
    @model_validator(mode='after')
    def check_weight_limit(self):
        """验证机柜总重量不超过静态承重限制"""
        total_weight = self.current_weight_kg
        max_load = self.spec.max_static_load_kg
        if total_weight > max_load:
            raise ValueError(f"机柜 {self.cabinet_id} 总重量 {total_weight:.1f}kg 超过静态承重限制 {max_load}kg")
        return self
    
    @model_validator(mode='after')
    def check_collision(self):
        """验证机柜内设备位置不重叠"""
        occupied_ranges = []
        
        for equip_ref in self.equipments:
            equip = resolve(equip_ref)
            if equip.start_u is None or equip.rack_units is None:
                continue
            
            start = equip.start_u
            end = equip.start_u + equip.rack_units - 1
            
            # 检查是否超出机柜范围
            if end > self.spec.total_units:
                raise ValueError(f"设备 {equip.name} 占用 U{start}-{end}，超出机柜最大 U 位 {self.spec.total_units}")
            
            # 检查与已有设备的碰撞
            for other_start, other_end, other_name in occupied_ranges:
                if not (end < other_start or start > other_end):
                    raise ValueError(f"设备位置重叠: {equip.name} (U{start}-{end}) 与 {other_name} (U{other_start}-{other_end})")
            
            occupied_ranges.append((start, end, equip.name))
        
        return self
    
    @model_validator(mode='after')
    def check_power_budget(self):
        """验证机柜总功耗不超过供电容量预算"""
        total_power = self.current_power_w  # W
        capacity_w = self.spec.power_capacity_kw * 1000  # kW -> W
        
        # 计算 PDU 总供电能力
        pdu_capacity_total = sum(resolve(p).input_power_va for p in self.pdus)
        
        # 使用更严格的限制
        effective_limit = min(capacity_w, pdu_capacity_total) if pdu_capacity_total > 0 else capacity_w
        
        if total_power > effective_limit:
            raise ValueError(f"机柜 {self.cabinet_id} 总功耗 {total_power/1000:.2f}kW 超过供电限制 {effective_limit/1000:.2f}kW")
        return self
```
