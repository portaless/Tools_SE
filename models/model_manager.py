"""
Model Manager - Business logic for MBSE models
Handles block/connection operations, validation, and state management
"""

from typing import Dict, List, Optional, Tuple
from models.entities import Block, Port, Connection, BlockType

class ModelManager:
    """Manages the model state and business logic"""
    
    def __init__(self):
        self.blocks: Dict[str, Block] = {}
        self.connections: List[Connection] = []
        self.block_counter = 0
        self.connection_counter = 0
        self.port_counter = 0
    
    # === Block Operations ===
    
    def create_block(self, block_type: BlockType, x: float, y: float, 
                    parent_id: Optional[str] = None) -> str:
        """Create new block and return its ID"""
        block_id = f"block_{self.block_counter}"
        self.block_counter += 1
        
        type_name = "Logical" if block_type == BlockType.LOGICAL else "Functional"
        name = f"{type_name} {self.block_counter}"
        
        block = Block(
            id=block_id,
            type=block_type,
            name=name,
            x=x,
            y=y,
            width=220,
            height=150,
            parent_id=parent_id
        )
        
        self.blocks[block_id] = block
        
        if parent_id and parent_id in self.blocks:
            self.blocks[parent_id].children.append(block_id)
        
        return block_id
    
    def delete_block(self, block_id: str):
        """Delete block and all its children"""
        if block_id not in self.blocks:
            return
        
        block = self.blocks[block_id]
        
        # Delete children recursively
        for child_id in block.children[:]:
            self.delete_block(child_id)
        
        # Remove from parent
        if block.parent_id and block.parent_id in self.blocks:
            parent = self.blocks[block.parent_id]
            if block_id in parent.children:
                parent.children.remove(block_id)
        
        # Remove connections
        self.connections = [c for c in self.connections 
                          if c.from_block != block_id and c.to_block != block_id]
        
        del self.blocks[block_id]
    
    def move_block(self, block_id: str, dx: float, dy: float, 
                  move_children: bool = True):
        """Move block by offset"""
        if block_id not in self.blocks:
            return
        
        block = self.blocks[block_id]
        block.x += dx
        block.y += dy
        
        if move_children:
            self._move_children_recursive(block_id, dx, dy)
    
    def _move_children_recursive(self, parent_id: str, dx: float, dy: float):
        """Move all descendants by offset"""
        parent = self.blocks[parent_id]
        for child_id in parent.children:
            if child_id in self.blocks:
                child = self.blocks[child_id]
                child.x += dx
                child.y += dy
                self._move_children_recursive(child_id, dx, dy)
    
    def get_block_at(self, x: float, y: float) -> Optional[str]:
        """Get deepest visible block at position"""
        candidates = []
        for block_id, block in self.blocks.items():
            if block.contains_point(x, y) and self.is_block_visible(block_id):
                candidates.append((block_id, self.get_nesting_level(block_id)))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        return None
    
    def is_block_visible(self, block_id: str) -> bool:
        """Check if block is visible (not inside collapsed parent)"""
        block = self.blocks[block_id]
        if not block.parent_id:
            return True
        
        parent = self.blocks[block.parent_id]
        if not parent.show_content:
            return False
        
        return self.is_block_visible(parent.id)
    
    def get_nesting_level(self, block_id: str) -> int:
        """Get nesting depth of block"""
        level = 0
        current = self.blocks[block_id]
        while current.parent_id:
            level += 1
            current = self.blocks[current.parent_id]
        return level
    
    # === Port Operations ===
    
    def create_port(self, block_id: str, name: str, side: str) -> str:
        """Create new port on block"""
        if block_id not in self.blocks:
            raise ValueError(f"Block {block_id} not found")
        
        port_id = f"port_{self.port_counter}"
        self.port_counter += 1
        
        port = Port(port_id, name, side, offset=0.5)
        self.blocks[block_id].ports.append(port)
        
        return port_id
    
    def delete_port(self, block_id: str, port_id: str):
        """Delete port and its connections"""
        if block_id not in self.blocks:
            return
        
        block = self.blocks[block_id]
        port = self.get_port_by_id(block_id, port_id)
        
        if not port:
            return
        
        # Remove connections
        self.connections = [c for c in self.connections 
                          if c.from_port != port_id and c.to_port != port_id]
        
        block.ports.remove(port)
    
    def get_port_by_id(self, block_id: str, port_id: str) -> Optional[Port]:
        """Get port by ID"""
        if not port_id or block_id not in self.blocks:
            return None
        block = self.blocks[block_id]
        return next((p for p in block.ports if p.id == port_id), None)
    
    def get_port_at(self, block_id: str, x: float, y: float) -> Optional[Port]:
        """Get port at position"""
        if block_id not in self.blocks:
            return None
        
        block = self.blocks[block_id]
        port_size = 12
        
        for i, port in enumerate(block.ports):
            px, py = self.get_port_position(block, port, i)
            if abs(x - px) < port_size and abs(y - py) < port_size:
                return port
        
        return None
    
    def get_port_position(self, block: Block, port: Port, index: int) -> Tuple[float, float]:
        """Calculate port position"""
        if port.side == "left":
            x = block.x
            y = block.y + block.header_height + (block.height - block.header_height) * port.offset
        elif port.side == "right":
            x = block.x + block.width
            y = block.y + block.header_height + (block.height - block.header_height) * port.offset
        elif port.side == "top":
            x = block.x + block.width * port.offset
            y = block.y + block.header_height
        else:  # bottom
            x = block.x + block.width * port.offset
            y = block.y + block.height
        
        return (x, y)
    
    # === Connection Operations ===
    
    def create_connection(self, from_block: str, to_block: str,
                         from_port: Optional[str] = None,
                         to_port: Optional[str] = None) -> str:
        """Create new connection"""
        conn_id = f"conn_{self.connection_counter}"
        self.connection_counter += 1
        
        conn = Connection(conn_id, from_block, to_block, from_port, to_port)
        self.connections.append(conn)
        
        return conn_id
    
    def delete_connection(self, conn_id: str):
        """Delete connection by ID"""
        self.connections = [c for c in self.connections if c.id != conn_id]
    
    def get_connection_at(self, x: float, y: float, tolerance: float = 10) -> Optional[Connection]:
        """Get connection near point"""
        for conn in self.connections:
            if conn.from_block not in self.blocks or conn.to_block not in self.blocks:
                continue
            
            from_block = self.blocks[conn.from_block]
            to_block = self.blocks[conn.to_block]
            
            # Get connection points
            x1, y1 = self._get_connection_point(from_block, to_block, conn.from_port, True)
            x2, y2 = self._get_connection_point(to_block, from_block, conn.to_port, False)
            
            # Check distance to line
            distance = self._point_to_line_distance(x, y, x1, y1, x2, y2)
            if distance < tolerance:
                return conn
        
        return None
    
    def _get_connection_point(self, block: Block, other_block: Block, 
                            port_id: Optional[str], is_source: bool) -> Tuple[float, float]:
        """Get connection point for block/port"""
        if port_id:
            port = self.get_port_by_id(block.id, port_id)
            if port:
                idx = block.ports.index(port)
                return self.get_port_position(block, port, idx)
        
        return self.get_block_edge_point(block, other_block)
    
    def get_block_edge_point(self, block: Block, target_block: Block) -> Tuple[float, float]:
        """Get point on block edge closest to target"""
        cx = block.x + block.width / 2
        cy = block.y + block.height / 2
        
        tx = target_block.x + target_block.width / 2
        ty = target_block.y + target_block.height / 2
        
        dx = tx - cx
        dy = ty - cy
        
        intersections = []
        
        # Check all edges
        if dx != 0:
            t = (block.x - cx) / dx
            y = cy + t * dy
            if 0 <= t <= 1 and block.y <= y <= block.y + block.height:
                intersections.append((block.x, y, abs(t)))
            
            t = (block.x + block.width - cx) / dx
            y = cy + t * dy
            if 0 <= t <= 1 and block.y <= y <= block.y + block.height:
                intersections.append((block.x + block.width, y, abs(t)))
        
        if dy != 0:
            t = (block.y - cy) / dy
            x = cx + t * dx
            if 0 <= t <= 1 and block.x <= x <= block.x + block.width:
                intersections.append((x, block.y, abs(t)))
            
            t = (block.y + block.height - cy) / dy
            x = cx + t * dx
            if 0 <= t <= 1 and block.x <= x <= block.x + block.width:
                intersections.append((x, block.y + block.height, abs(t)))
        
        if intersections:
            intersections.sort(key=lambda p: ((p[0]-tx)**2 + (p[1]-ty)**2))
            return (intersections[0][0], intersections[0][1])
        
        return (cx, cy)
    
    def _point_to_line_distance(self, px: float, py: float, 
                               x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate distance from point to line segment"""
        dx = x2 - x1
        dy = y2 - y1
        
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        
        t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
        
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        return ((px - closest_x) ** 2 + (py - closest_y) ** 2) ** 0.5
    
    # === Layout Operations ===
    
    def auto_layout_children(self, parent_id: str):
        """Auto-layout children in compartment"""
        if parent_id not in self.blocks:
            return
        
        parent = self.blocks[parent_id]
        if not parent.children or not parent.show_content:
            return
        
        cx, cy, cw, ch = parent.get_content_area()
        children = [self.blocks[cid] for cid in parent.children if cid in self.blocks]
        
        if not children:
            return
        
        num_children = len(children)
        child_height = (ch - parent.child_spacing * (num_children - 1)) / num_children
        child_height = max(60, child_height)
        
        y = cy
        for child in children:
            child.x = cx + parent.padding
            child.y = y
            child.width = cw - 2 * parent.padding
            child.height = child_height
            y += child_height + parent.child_spacing
            
            if child.children and child.show_content:
                self.auto_layout_children(child.id)
        
        # Adjust parent height
        total_height = num_children * child_height + (num_children - 1) * parent.child_spacing
        min_parent_height = total_height + parent.header_height + parent.port_section_width + 2 * parent.padding
        if parent.height < min_parent_height:
            parent.height = min_parent_height
    
    def expand_all(self):
        """Expand all blocks"""
        for block in self.blocks.values():
            block.show_content = True
            block.collapsed = False
    
    def collapse_all(self):
        """Collapse all blocks with children"""
        for block in self.blocks.values():
            if block.children:
                block.show_content = False
                block.collapsed = True
    
    # === Persistence ===
    
    def to_dict(self):
        """Export model to dictionary"""
        return {
            "blocks": [block.to_dict() for block in self.blocks.values()],
            "connections": [conn.to_dict() for conn in self.connections]
        }
    
    def from_dict(self, data):
        """Import model from dictionary"""
        self.blocks = {b['id']: Block.from_dict(b) for b in data['blocks']}
        self.connections = [Connection(**c) for c in data['connections']]
        
        self.block_counter = max([int(b.id.split('_')[1]) 
                                 for b in self.blocks.values()], default=0) + 1
        self.connection_counter = max([int(c.id.split('_')[1]) 
                                      for c in self.connections], default=0) + 1