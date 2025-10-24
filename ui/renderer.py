"""
Canvas Renderer - Handles all drawing operations
Separates rendering logic from business logic
"""

import tkinter as tk
from typing import Optional, Tuple, List
from models.entities import Block, Port, Connection, BlockType

class CanvasRenderer:
    """Renders blocks, ports, and connections on canvas"""
    
    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        
        # Visual settings
        self.colors = {
            'logical': '#4A90E2',
            'logical_header': '#357ABD',
            'logical_border': '#2C5AA0',
            'functional': '#2ECC71',
            'functional_header': '#27AE60',
            'functional_border': '#1E8449',
            'selection': '#F39C12',
            'multi_selection': '#E74C3C',
            'connection': '#2C3E50',
            'connection_preview': '#9B59B6',
            'port': '#34495E',
            'port_dragging': '#E67E22',
            'resize_handle': '#F39C12'
        }
    
    def clear(self):
        """Clear canvas"""
        self.canvas.delete("all")
    
    def draw_block(self, block: Block, is_selected: bool = False, 
                  is_multi_selected: bool = False, is_connection_source: bool = False):
        """Draw block in compartment style"""
        color = self.colors['logical'] if block.type == BlockType.LOGICAL else self.colors['functional']
        header_color = self.colors['logical_header'] if block.type == BlockType.LOGICAL else self.colors['functional_header']
        border_color = self.colors['logical_border'] if block.type == BlockType.LOGICAL else self.colors['functional_border']
        
        # Selection highlighting
        if is_connection_source:
            border_width = 3
            border_color = self.colors['connection_preview']
        elif is_multi_selected:
            border_width = 3
            border_color = self.colors['multi_selection']
        elif is_selected:
            border_width = 3
            border_color = self.colors['selection']
        else:
            border_width = 2
        
        # Main rectangle
        self.canvas.create_rectangle(
            block.x, block.y,
            block.x + block.width, block.y + block.height,
            fill="white", outline=border_color, width=border_width
        )
        
        # Header
        self.canvas.create_rectangle(
            block.x, block.y,
            block.x + block.width, block.y + block.header_height,
            fill=header_color, outline=""
        )
        
        # Stereotype
        type_text = "«Logical»" if block.type == BlockType.LOGICAL else "«Functional»"
        self.canvas.create_text(
            block.x + block.width / 2, block.y + 12,
            text=type_text, fill="white",
            font=("Arial", 8, "italic")
        )
        
        # Name
        self.canvas.create_text(
            block.x + block.width / 2, block.y + 28,
            text=block.name, fill="white",
            font=("Arial", 10, "bold")
        )
        
        # Collapse indicator
        if block.children:
            indicator = "▼" if block.show_content else "▶"
            self.canvas.create_text(
                block.x + 10, block.y + block.header_height // 2,
                text=indicator, fill="white", font=("Arial", 10)
            )
            
            # Children count
            self.canvas.create_text(
                block.x + block.width - 10, block.y + 12,
                text=f"[{len(block.children)}]", fill="white",
                font=("Arial", 8), anchor="e"
            )
            
            # Show contents when collapsed
            if not block.show_content:
                self._draw_collapsed_contents(block)
        
        # Port sections
        if block.ports:
            self.canvas.create_rectangle(
                block.x, block.y + block.header_height,
                block.x + block.port_section_width, block.y + block.height,
                fill="#ECF0F1", outline=""
            )
            
            self.canvas.create_rectangle(
                block.x + block.width - block.port_section_width, block.y + block.header_height,
                block.x + block.width, block.y + block.height,
                fill="#ECF0F1", outline=""
            )
        
        # Content separator
        if block.show_content and block.children:
            self.canvas.create_line(
                block.x, block.y + block.header_height,
                block.x + block.width, block.y + block.header_height,
                fill="#BDC3C7", width=1
            )
    
    def _draw_collapsed_contents(self, block: Block):
        """Draw list of children when collapsed"""
        cx, cy, cw, ch = block.get_content_area()
        list_y = cy + 5
        
        self.canvas.create_text(
            cx + 5, list_y,
            text="Contents:", fill="#7F8C8D",
            font=("Arial", 8, "italic"), anchor="nw"
        )
        list_y += 15
        
        from models.model_manager import ModelManager  # Avoid circular import
        
        for i, child_id in enumerate(block.children):
            # This assumes we have access to blocks dict - needs to be passed
            icon = "🔷"  # Placeholder
            child_name = f"Child {i+1}"
            
            self.canvas.create_text(
                cx + 10, list_y,
                text=f"{icon} {child_name}", fill="#2C3E50",
                font=("Arial", 8), anchor="nw"
            )
            list_y += 14
            
            if i >= 8 and i < len(block.children) - 1:
                remaining = len(block.children) - i - 1
                self.canvas.create_text(
                    cx + 10, list_y,
                    text=f"... and {remaining} more", fill="#95A5A6",
                    font=("Arial", 7, "italic"), anchor="nw"
                )
                break
    
    def draw_port(self, block: Block, port: Port, position: Tuple[float, float], 
                 is_dragging: bool = False):
        """Draw port on block"""
        px, py = position
        port_size = 10
        
        color = self.colors['port_dragging'] if is_dragging else self.colors['port']
        outline_width = 3 if is_dragging else 2
        
        # Port rectangle
        self.canvas.create_rectangle(
            px - port_size//2, py - port_size//2,
            px + port_size//2, py + port_size//2,
            fill=color, outline="white", width=outline_width
        )
        
        # Label
        if port.side in ["left", "right"]:
            anchor = "w" if port.side == "right" else "e"
            label_x = px + 15 if port.side == "right" else px - 15
            label_y = py
        else:
            anchor = "n" if port.side == "bottom" else "s"
            label_x = px
            label_y = py + 10 if port.side == "bottom" else py - 10
        
        self.canvas.create_text(
            label_x, label_y,
            text=port.name, fill="#2C3E50",
            font=("Arial", 7), anchor=anchor
        )
    
    def draw_connection(self, x1: float, y1: float, x2: float, y2: float):
        """Draw connection line"""
        # Line
        self.canvas.create_line(
            x1, y1, x2, y2,
            width=2, fill=self.colors['connection'],
            smooth=False, capstyle=tk.ROUND
        )
        
        # Endpoints
        radius = 4
        # Source
        self.canvas.create_oval(
            x1 - radius, y1 - radius, x1 + radius, y1 + radius,
            fill="#3498DB", outline="#2980B9", width=2
        )
        # Target
        self.canvas.create_oval(
            x2 - radius, y2 - radius, x2 + radius, y2 + radius,
            fill="#2ECC71", outline="#27AE60", width=2
        )
    
    def draw_connection_preview(self, x1: float, y1: float, x2: float, y2: float):
        """Draw preview line during connection creation"""
        self.canvas.create_line(
            x1, y1, x2, y2,
            width=2, fill=self.colors['connection_preview'], dash=(5, 3),
            capstyle=tk.ROUND
        )
        
        self.canvas.create_oval(
            x1 - 5, y1 - 5, x1 + 5, y1 + 5,
            fill=self.colors['connection_preview'], outline="#8E44AD", width=2
        )
    
    def draw_resize_handles(self, block: Block):
        """Draw resize handles on selected block"""
        handle_size = 8
        color = self.colors['resize_handle']
        
        # Corners
        corners = [
            (block.x, block.y),
            (block.x + block.width - handle_size, block.y),
            (block.x, block.y + block.height - handle_size),
            (block.x + block.width - handle_size, block.y + block.height - handle_size)
        ]
        
        for x, y in corners:
            self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill=color, outline="white", width=1
            )
        
        # Edge midpoints
        mid_handles = [
            (block.x + block.width//2 - handle_size//2, block.y),
            (block.x + block.width//2 - handle_size//2, block.y + block.height - handle_size),
            (block.x, block.y + block.height//2 - handle_size//2),
            (block.x + block.width - handle_size, block.y + block.height//2 - handle_size//2)
        ]
        
        for x, y in mid_handles:
            self.canvas.create_rectangle(
                x, y, x + handle_size, y + handle_size,
                fill=color, outline="white", width=1
            )