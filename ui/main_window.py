"""
Main Window - Application Controller
Coordinates between UI components and business logic
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, Tuple
import json

from models.entities import BlockType
from models.model_manager import ModelManager
from ui.renderer import CanvasRenderer
from ui.toolbar import Toolbar
from ui.properties_panel import PropertiesPanel
from ui.dialogs.block_edit import *
from ui.dialogs.connection_manager import *
from ui.dialogs.port_edit import *
from utils.file_io import FileIO

class MainWindow:
    """Main application window and controller"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("MBSE Block Modeler - Compartment Layout")
        self.root.geometry("1500x900")
        
        # Model
        self.model = ModelManager()
        
        # State
        self.selected_block: Optional[str] = None
        self.selected_blocks = []
        self.dragging_block: Optional[str] = None
        self.drag_offset = (0, 0)
        self.mode = "select"
        self.connection_start: Optional[Tuple[str, Optional[str]]] = None
        self.move_with_children = True
        
        # Resize state
        self.resizing_block: Optional[str] = None
        self.resize_corner: Optional[str] = None
        self.resize_start_pos = (0, 0)
        self.resize_start_size = (0, 0)
        
        # Port drag state
        self.dragging_port: Optional[Tuple[str, str]] = None
        
        # Mouse state
        self.mouse_x = 0
        self.mouse_y = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI components"""
        # Toolbar
        self.toolbar = Toolbar(self.root, self)
        self.toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Canvas with scrollbars
        canvas_frame = self.create_canvas_frame(main_container)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Initialize renderer
        self.renderer = CanvasRenderer(self.canvas)
        
        # Properties panel
        self.props_panel = PropertiesPanel(main_container, self)
        self.props_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        
        # Setup bindings
        self.setup_bindings()
    
    def create_canvas_frame(self, parent):
        """Create canvas with scrollbars"""
        frame = ttk.Frame(parent)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Canvas
        self.canvas = tk.Canvas(frame, bg="#F8F9FA", highlightthickness=1,
                               highlightbackground="gray",
                               scrollregion=(0, 0, 3000, 3000))
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure scrollbars
        v_scroll.config(command=self.canvas.yview)
        h_scroll.config(command=self.canvas.xview)
        self.canvas.config(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        return frame
    
    def setup_bindings(self):
        """Setup event bindings"""
        # Canvas events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # Keyboard shortcuts
        self.root.bind("<Delete>", lambda e: self.delete_selected())
        self.root.bind("<F2>", lambda e: self.rename_selected())
        self.root.bind("<Control-e>", lambda e: self.edit_selected())
        self.root.bind("<Control-a>", lambda e: self.select_all())
        self.root.bind("<Escape>", lambda e: self.clear_selection())
        
        # Mouse wheel
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self.on_shift_mousewheel)
    
    # === Mode Management ===
    
    def set_mode(self, mode: str):
        """Set interaction mode"""
        self.mode = mode
        self.connection_start = None
        cursor = "crosshair" if mode in ["add_logical", "add_functional"] else "arrow"
        self.canvas.config(cursor=cursor)
        self.toolbar.update_mode_display(mode)
    
    def toggle_connect_mode(self):
        """Toggle connection mode"""
        if self.mode == "connect":
            self.set_mode("select")
        else:
            self.set_mode("connect")
    
    def toggle_move_mode(self):
        """Toggle move with children"""
        self.move_with_children = not self.move_with_children
    
    # === Event Handlers ===
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.mode == "add_logical":
            self.add_block(BlockType.LOGICAL, x - 110, y - 75)
            self.set_mode("select")
        
        elif self.mode == "add_functional":
            self.add_block(BlockType.FUNCTIONAL, x - 110, y - 75)
            self.set_mode("select")
        
        elif self.mode == "connect":
            self.handle_connection_click(x, y)
        
        else:  # select mode
            self.handle_select_click(x, y, event)
    
    def handle_connection_click(self, x: float, y: float):
        """Handle click in connection mode"""
        block_id = self.model.get_block_at(x, y)
        if not block_id:
            if self.connection_start:
                self.connection_start = None
                self.redraw()
            return
        
        port = self.model.get_port_at(block_id, x, y)
        
        if not self.connection_start:
            self.connection_start = (block_id, port.id if port else None)
            self.redraw()
        else:
            start_block, start_port = self.connection_start
            self.model.create_connection(start_block, block_id, start_port, 
                                       port.id if port else None)
            self.connection_start = None
            self.redraw()
            self.props_panel.update()
    
    def handle_select_click(self, x: float, y: float, event):
        """Handle click in select mode"""
        block_id = self.model.get_block_at(x, y)
        
        if not block_id:
            self.selected_blocks = []
            self.selected_block = None
            self.redraw()
            self.props_panel.update()
            return
        
        # Check for port drag
        port = self.model.get_port_at(block_id, x, y)
        if port:
            self.dragging_port = (block_id, port.id)
            self.selected_block = block_id
            self.redraw()
            self.props_panel.update()
            return
        
        # Check for resize
        corner = self.get_resize_corner(block_id, x, y)
        if corner:
            self.resizing_block = block_id
            self.resize_corner = corner
            self.resize_start_pos = (x, y)
            block = self.model.blocks[block_id]
            self.resize_start_size = (block.width, block.height)
            self.selected_block = block_id
            self.redraw()
            self.props_panel.update()
            return
        
        # Regular selection
        self.selected_block = block_id
        block = self.model.blocks[block_id]
        self.dragging_block = block_id
        self.drag_offset = (x - block.x, y - block.y)
        
        # Multi-select with Ctrl
        if event.state & 0x4:
            if block_id in self.selected_blocks:
                self.selected_blocks.remove(block_id)
            else:
                self.selected_blocks.append(block_id)
        else:
            self.selected_blocks = [block_id] if block_id else []
        
        self.redraw()
        self.props_panel.update()
    
    def on_canvas_drag(self, event):
        """Handle canvas drag"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.dragging_port and self.mode == "select":
            self.handle_port_drag(x, y)
        elif self.resizing_block and self.mode == "select":
            self.handle_resize_drag(x, y)
        elif self.dragging_block and self.mode == "select":
            self.handle_block_drag(x, y)
    
    def handle_port_drag(self, x: float, y: float):
        """Handle port dragging"""
        block_id, port_id = self.dragging_port
        block = self.model.blocks[block_id]
        port = self.model.get_port_by_id(block_id, port_id)
        
        if port.side in ["left", "right"]:
            rel_y = (y - block.y - block.header_height) / (block.height - block.header_height)
            port.offset = max(0.1, min(0.9, rel_y))
        else:
            rel_x = (x - block.x) / block.width
            port.offset = max(0.1, min(0.9, rel_x))
        
        self.redraw()
    
    def handle_resize_drag(self, x: float, y: float):
        """Handle block resizing"""
        block = self.model.blocks[self.resizing_block]
        dx = x - self.resize_start_pos[0]
        dy = y - self.resize_start_pos[1]
        
        corner = self.resize_corner
        min_width, min_height = 150, 100
        
        new_width = block.width
        new_height = block.height
        new_x = block.x
        new_y = block.y
        
        if 'e' in corner:
            new_width = max(min_width, self.resize_start_size[0] + dx)
        if 'w' in corner:
            potential_width = max(min_width, self.resize_start_size[0] - dx)
            if potential_width >= min_width:
                new_width = potential_width
                new_x = self.resize_start_pos[0] - self.drag_offset[0] + dx
        if 's' in corner:
            new_height = max(min_height, self.resize_start_size[1] + dy)
        if 'n' in corner:
            potential_height = max(min_height, self.resize_start_size[1] - dy)
            if potential_height >= min_height:
                new_height = potential_height
                new_y = self.resize_start_pos[1] - self.drag_offset[1] + dy
        
        # Apply changes
        dx_move = new_x - block.x
        dy_move = new_y - block.y
        
        block.x = new_x
        block.y = new_y
        block.width = new_width
        block.height = new_height
        
        if dx_move != 0 or dy_move != 0:
            self.model._move_children_recursive(self.resizing_block, dx_move, dy_move)
        
        if block.children and block.show_content:
            self.model.auto_layout_children(self.resizing_block)
        
        self.redraw()
    
    def handle_block_drag(self, x: float, y: float):
        """Handle block dragging"""
        blocks_to_move = self.selected_blocks if len(self.selected_blocks) > 1 else [self.dragging_block]
        
        for block_id in blocks_to_move:
            if block_id not in self.model.blocks:
                continue
            
            block = self.model.blocks[block_id]
            
            if block_id == self.dragging_block:
                new_x = x - self.drag_offset[0]
                new_y = y - self.drag_offset[1]
            else:
                dx = (x - self.drag_offset[0]) - self.model.blocks[self.dragging_block].x
                dy = (y - self.drag_offset[1]) - self.model.blocks[self.dragging_block].y
                new_x = block.x + dx
                new_y = block.y + dy
            
            # Constrain to parent
            if block.parent_id and block.parent_id in self.model.blocks:
                parent = self.model.blocks[block.parent_id]
                cx, cy, cw, ch = parent.get_content_area()
                new_x = max(cx, min(new_x, cx + cw - block.width))
                new_y = max(cy, min(new_y, cy + ch - block.height))
            
            dx = new_x - block.x
            dy = new_y - block.y
            
            self.model.move_block(block_id, dx, dy, self.move_with_children)
        
        self.redraw()
    
    def on_canvas_release(self, event):
        """Handle mouse release"""
        self.dragging_block = None
        self.resizing_block = None
        self.dragging_port = None
    
    def on_canvas_double_click(self, event):
        """Handle double click"""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        block_id = self.model.get_block_at(x, y)
        if not block_id:
            return
        
        block = self.model.blocks[block_id]
        
        # Toggle collapse on header
        if y < block.y + block.header_height:
            if block.children:
                block.show_content = not block.show_content
                block.collapsed = not block.collapsed
                self.redraw()
            return
        
        # Edit port
        port = self.model.get_port_at(block_id, x, y)
        if port:
            dialog = PortEditDialog(self.root, self, block_id, port.id)
            return
        
        # Edit block
        dialog = BlockEditDialog(self.root, self, block_id)
    
    def on_right_click(self, event):
        """Handle right click - context menu"""
        # TODO: Implement context menu
        pass
    
    def on_mouse_move(self, event):
        """Handle mouse movement - update cursor"""
        self.mouse_x = self.canvas.canvasx(event.x)
        self.mouse_y = self.canvas.canvasy(event.y)
        
        if self.mode == "connect":
            block_id = self.model.get_block_at(self.mouse_x, self.mouse_y)
            if block_id and self.model.get_port_at(block_id, self.mouse_x, self.mouse_y):
                self.canvas.config(cursor="hand2")
            else:
                self.canvas.config(cursor="crosshair")
        elif self.mode == "select":
            self.update_cursor_for_select_mode()
        
        if self.connection_start:
            self.redraw()
    
    def update_cursor_for_select_mode(self):
        """Update cursor in select mode"""
        block_id = self.model.get_block_at(self.mouse_x, self.mouse_y)
        
        if block_id and not self.resizing_block and not self.dragging_block:
            if self.model.get_port_at(block_id, self.mouse_x, self.mouse_y):
                self.canvas.config(cursor="hand2")
                return
        
        if block_id:
            corner = self.get_resize_corner(block_id, self.mouse_x, self.mouse_y)
            if corner:
                cursor_map = {
                    "se": "bottom_right_corner", "ne": "top_right_corner",
                    "sw": "bottom_left_corner", "nw": "top_left_corner",
                    "e": "sb_h_double_arrow", "w": "sb_h_double_arrow",
                    "n": "sb_v_double_arrow", "s": "sb_v_double_arrow"
                }
                self.canvas.config(cursor=cursor_map.get(corner, "arrow"))
                return
        
        self.canvas.config(cursor="arrow")
    
    def on_mousewheel(self, event):
        """Vertical scroll"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def on_shift_mousewheel(self, event):
        """Horizontal scroll"""
        self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # === Helper Methods ===
    
    def get_resize_corner(self, block_id: str, x: float, y: float) -> Optional[str]:
        """Get resize corner/edge at position"""
        if block_id not in self.model.blocks:
            return None
        
        block = self.model.blocks[block_id]
        corner_size = 15
        edge_size = 8
        
        # Check corners first
        corners = {
            "se": (block.x + block.width - corner_size, block.y + block.height - corner_size,
                   block.x + block.width, block.y + block.height),
            "ne": (block.x + block.width - corner_size, block.y,
                   block.x + block.width, block.y + corner_size),
            "sw": (block.x, block.y + block.height - corner_size,
                   block.x + corner_size, block.y + block.height),
            "nw": (block.x, block.y,
                   block.x + corner_size, block.y + corner_size),
        }
        
        for corner, (x1, y1, x2, y2) in corners.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return corner
        
        # Check edges
        edges = {
            "e": (block.x + block.width - edge_size, block.y + corner_size,
                  block.x + block.width, block.y + block.height - corner_size),
            "w": (block.x, block.y + corner_size,
                  block.x + edge_size, block.y + block.height - corner_size),
            "n": (block.x + corner_size, block.y,
                  block.x + block.width - corner_size, block.y + edge_size),
            "s": (block.x + corner_size, block.y + block.height - edge_size,
                  block.x + block.width - corner_size, block.y + block.height)
        }
        
        for edge, (x1, y1, x2, y2) in edges.items():
            if x1 <= x <= x2 and y1 <= y <= y2:
                return edge
        
        return None
    
    # === Action Methods ===
    
    def add_block(self, block_type: BlockType, x: float, y: float):
        """Add new block"""
        parent_id = self.model.get_block_at(x, y)
        block_id = self.model.create_block(block_type, x, y, parent_id)
        
        if parent_id:
            self.model.auto_layout_children(parent_id)
        
        self.redraw()
        self.props_panel.update_tree()
    
    def delete_selected(self):
        """Delete selected block"""
        if not self.selected_block:
            return
        
        block = self.model.blocks[self.selected_block]
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete block '{block.name}' and its children?"):
            parent_id = block.parent_id
            self.model.delete_block(self.selected_block)
            self.selected_block = None
            
            if parent_id and parent_id in self.model.blocks:
                self.model.auto_layout_children(parent_id)
            
            self.redraw()
            self.props_panel.update()
    
    def rename_selected(self):
        """Rename selected block"""
        if not self.selected_block:
            return
        
        block = self.model.blocks[self.selected_block]
        from tkinter import simpledialog
        new_name = simpledialog.askstring("Rename", "New name:", 
                                         initialvalue=block.name)
        if new_name:
            block.name = new_name
            self.redraw()
            self.props_panel.update()
    
    def edit_selected(self):
        """Edit selected block"""
        if not self.selected_block:
            return
        dialog = BlockEditDialog(self.root, self, self.selected_block)
    
    def select_all(self):
        """Select all root blocks"""
        self.selected_blocks = [bid for bid, b in self.model.blocks.items() 
                               if not b.parent_id]
        if self.selected_blocks:
            self.selected_block = self.selected_blocks[0]
        self.redraw()
        self.props_panel.update()
    
    def clear_selection(self):
        """Clear selection"""
        self.selected_blocks = []
        self.selected_block = None
        self.redraw()
        self.props_panel.update()
    
    def expand_all(self):
        """Expand all blocks"""
        self.model.expand_all()
        self.redraw()
    
    def collapse_all(self):
        """Collapse all blocks"""
        self.model.collapse_all()
        self.redraw()
    
    def auto_layout_selected(self):
        """Auto-layout selected block's children"""
        if self.selected_block:
            self.model.auto_layout_children(self.selected_block)
            self.redraw()
    
    def save_model(self):
        """Save model to file"""
        FileIO.save(self.model)
    
    def load_model(self):
        """Load model from file"""
        if FileIO.load(self.model):
            self.selected_block = None
            self.redraw()
            self.props_panel.update()
    
    # === Rendering ===
    
    def redraw(self):
        """Redraw entire canvas"""
        self.renderer.clear()
        
        # Draw blocks
        drawn = set()
        
        def draw_hierarchy(bid):
            if bid in drawn:
                return
            block = self.model.blocks[bid]
            
            is_selected = (self.selected_block == bid)
            is_multi = (bid in self.selected_blocks and len(self.selected_blocks) > 1)
            is_conn_src = (self.connection_start and self.connection_start[0] == bid)
            
            self.renderer.draw_block(block, is_selected, is_multi, is_conn_src)
            drawn.add(bid)
            
            # Draw ports
            for i, port in enumerate(block.ports):
                pos = self.model.get_port_position(block, port, i)
                is_dragging = (self.dragging_port and 
                             self.dragging_port[0] == bid and 
                             self.dragging_port[1] == port.id)
                self.renderer.draw_port(block, port, pos, is_dragging)
            
            if block.show_content:
                for cid in block.children:
                    if cid in self.model.blocks:
                        draw_hierarchy(cid)
        
        for bid, block in self.model.blocks.items():
            if not block.parent_id:
                draw_hierarchy(bid)
        
        # Draw connections
        for conn in self.model.connections:
            if conn.from_block not in self.model.blocks or conn.to_block not in self.model.blocks:
                continue
            
            from_block = self.model.blocks[conn.from_block]
            to_block = self.model.blocks[conn.to_block]
            
            if not self.model.is_block_visible(conn.from_block) or not self.model.is_block_visible(conn.to_block):
                continue
            
            x1, y1 = self.model._get_connection_point(from_block, to_block, conn.from_port, True)
            x2, y2 = self.model._get_connection_point(to_block, from_block, conn.to_port, False)
            
            self.renderer.draw_connection(x1, y1, x2, y2)
        
        # Draw connection preview
        if self.connection_start and self.mode == "connect":
            start_block_id, start_port_id = self.connection_start
            if start_block_id in self.model.blocks:
                start_block = self.model.blocks[start_block_id]
                x1, y1 = self.model._get_connection_point(start_block, start_block, 
                                                         start_port_id, True)
                self.renderer.draw_connection_preview(x1, y1, self.mouse_x, self.mouse_y)
        
        # Draw resize handles
        if self.selected_block and self.selected_block in self.model.blocks:
            self.renderer.draw_resize_handles(self.model.blocks[self.selected_block])