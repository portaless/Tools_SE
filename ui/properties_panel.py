"""
Properties Panel Component
Displays selected block properties and hierarchy tree
"""

import tkinter as tk
from tkinter import ttk

class PropertiesPanel(ttk.Frame):
    """Panel showing properties and hierarchy"""
    
    def __init__(self, parent, controller):
        super().__init__(parent, width=320)
        self.controller = controller
        self.pack_propagate(False)
        self.setup_widgets()
    
    def setup_widgets(self):
        """Create panel widgets"""
        # Properties section
        props_frame = ttk.LabelFrame(self, text="Properties & Hierarchy")
        props_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.props_text = tk.Text(props_frame, wrap=tk.WORD, height=12, width=38)
        self.props_text.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Hierarchy tree
        tree_frame = ttk.LabelFrame(self, text="Block Hierarchy")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.tree = ttk.Treeview(tree_frame, height=15)
        tree_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.config(yscrollcommand=tree_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.update()
    
    def update(self):
        """Update properties display"""
        self.update_properties()
        self.update_tree()
    
    def update_properties(self):
        """Update properties text"""
        self.props_text.delete(1.0, tk.END)
        
        if not self.controller.selected_block or \
           self.controller.selected_block not in self.controller.model.blocks:
            self.show_help_text()
            return
        
        block = self.controller.model.blocks[self.controller.selected_block]
        
        props = f"""Type: {block.type.value.title()}
Name: {block.name}
ID: {block.id}

Position: ({int(block.x)}, {int(block.y)})
Size: {int(block.width)} x {int(block.height)}

Parent: {block.parent_id or "Root"}
Children: {len(block.children)}
Ports: {len(block.ports)}
Nesting Level: {self.controller.model.get_nesting_level(block.id)}

State: {"Collapsed" if block.collapsed else "Expanded"}

Connections:
  Out: {len([c for c in self.controller.model.connections if c.from_block == block.id])}
  In: {len([c for c in self.controller.model.connections if c.to_block == block.id])}
"""
        
        if len(self.controller.selected_blocks) > 1:
            props += f"\n✓ Multi-selection: {len(self.controller.selected_blocks)} blocks\n"
        
        if block.ports:
            props += "\nPorts:\n"
            for port in block.ports:
                port_conns = len([c for c in self.controller.model.connections 
                                if (c.from_port == port.id or c.to_port == port.id)])
                props += f"  • {port.name} ({port.side}, {int(port.offset*100)}%) [{port_conns} conn]\n"
        
        self.props_text.insert(tk.END, props)
    
    def show_help_text(self):
        """Show help text when nothing selected"""
        help_text = """No block selected

SHORTCUTS:
• F2: Rename block
• Ctrl+E: Edit block
• Delete: Delete block
• Ctrl+A: Select all
• Escape: Clear selection
• Ctrl+Click: Multi-select

ACTIONS:
• Double-click header: Collapse/Expand
• Double-click block: Edit
• Double-click port: Edit port
• Right-click: Context menu
• Drag port: Reposition
• Drag handles: Resize

TIPS:
• Uncheck '🔗 Move with children' to move block alone
• Use Auto Layout for clean arrangement
"""
        self.props_text.insert(tk.END, help_text)
        
        if len(self.controller.selected_blocks) > 1:
            self.props_text.insert(tk.END, 
                f"\n✓ {len(self.controller.selected_blocks)} blocks selected\n")
    
    def update_tree(self):
        """Update hierarchy tree"""
        self.tree.delete(*self.tree.get_children())
        
        def add_to_tree(block_id, parent=""):
            block = self.controller.model.blocks[block_id]
            type_icon = "🔷" if block.type.value == "logical" else "🟢"
            collapse_icon = "▼" if block.show_content else "▶"
            
            display = f"{type_icon} {block.name}"
            if block.children:
                display += f" {collapse_icon} [{len(block.children)}]"
            if block.ports:
                display += f" 🔌{len(block.ports)}"
            
            item = self.tree.insert(parent, "end", text=display, values=(block_id,))
            
            if block.show_content:
                for child_id in block.children:
                    if child_id in self.controller.model.blocks:
                        add_to_tree(child_id, item)
        
        for block_id, block in self.controller.model.blocks.items():
            if not block.parent_id:
                add_to_tree(block_id)
    
    def on_tree_select(self, event):
        """Handle tree selection"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            values = self.tree.item(item, "values")
            if values:
                self.controller.selected_block = values[0]
                self.controller.redraw()
                self.update_properties()