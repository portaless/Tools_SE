"""
Data models for MBSE Modeler
Contains all entity definitions (Block, Port, Connection)
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional, Tuple
from enum import Enum

class BlockType(Enum):
    """Type of block in the model"""
    LOGICAL = "logical"
    FUNCTIONAL = "functional"

@dataclass
class Port:
    """Port for connections between blocks"""
    id: str
    name: str
    side: str  # 'left', 'right', 'top', 'bottom'
    offset: float = 0.5  # Position on side (0.0 to 1.0)
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Block:
    """Block entity with compartment layout"""
    id: str
    type: BlockType
    name: str
    x: float
    y: float
    width: float = 200
    height: float = 100
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    ports: List[Port] = field(default_factory=list)
    collapsed: bool = False
    show_content: bool = True
    
    # Layout settings
    header_height: int = 40
    port_section_width: int = 25
    padding: int = 10
    child_spacing: int = 8
    
    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside block"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
    
    def get_content_area(self) -> Tuple[float, float, float, float]:
        """Get content compartment area (x, y, width, height)"""
        return (
            self.x + self.port_section_width,
            self.y + self.header_height,
            self.width - 2 * self.port_section_width,
            self.height - self.header_height - self.port_section_width
        )
    
    def to_dict(self):
        d = asdict(self)
        d['type'] = self.type.value
        d['ports'] = [p.to_dict() for p in self.ports]
        return d
    
    @classmethod
    def from_dict(cls, data):
        data['type'] = BlockType(data['type'])
        ports_data = data.pop('ports', [])
        block = cls(**data)
        block.ports = [Port(**p) for p in ports_data]
        return block

@dataclass
class Connection:
    """Connection between blocks/ports"""
    id: str
    from_block: str
    to_block: str
    from_port: Optional[str] = None
    to_port: Optional[str] = None
    
    def to_dict(self):
        return asdict(self)