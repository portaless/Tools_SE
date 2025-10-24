"""
Toolbar Component
Provides buttons and controls for main actions
"""

import tkinter as tk
from tkinter import ttk

class Toolbar(ttk.Frame):
    """Application toolbar with action buttons"""
    
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_widgets()
    
    def setup_widgets(self):
        """Create toolbar widgets"""
        # Block creation
        ttk.Button(self, text="➕ Logical", 
                   command=lambda: self.controller.set_mode("add_logical")).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="➕ Functional", 
                   command=lambda: self.controller.set_mode("add_functional")).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Connection mode
        self.connect_btn = ttk.Button(self, text="🔗 Connect", 
                                      command=self.controller.toggle_connect_mode)
        self.connect_btn.pack(side=tk.LEFT, padx=2)
        
        # Port management
        ttk.Button(self, text="🔌 Add Port", 
                   command=self.add_port).pack(side=tk.LEFT, padx=2)
        
        # Edit and delete
        ttk.Button(self, text="✏️ Edit", 
                   command=self.controller.edit_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="🗑️ Delete", 
                   command=self.controller.delete_selected).pack(side=tk.LEFT, padx=2)
        
        # Connections manager
        ttk.Button(self, text="🔗 Connections", 
                   command=self.manage_connections).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Layout
        ttk.Button(self, text="📐 Auto Layout", 
                   command=self.controller.auto_layout_selected).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="⬆️ Expand All", 
                   command=self.controller.expand_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="⬇️ Collapse All", 
                   command=self.controller.collapse_all).pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # Move mode toggle
        self.move_mode_var = tk.BooleanVar(value=True)
        self.move_check = ttk.Checkbutton(
            self, 
            text="🔗 Move with children",
            variable=self.move_mode_var,
            command=self.controller.toggle_move_mode
        )
        self.move_check.pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)
        
        # File operations
        ttk.Button(self, text="💾 Save", 
                   command=self.controller.save_model).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="📂 Load", 
                   command=self.controller.load_model).pack(side=tk.LEFT, padx=2)
        
        # Mode indicator
        self.mode_label = ttk.Label(self, text="Mode: Select", 
                                    font=("Arial", 10, "bold"))
        self.mode_label.pack(side=tk.RIGHT, padx=10)
    
    def update_mode_display(self, mode: str):
        """Update mode label"""
        mode_text = {
            "select": "Select",
            "connect": "Connect",
            "add_logical": "Add Logical Block",
            "add_functional": "Add Functional Block"
        }
        self.mode_label.config(text=f"Mode: {mode_text.get(mode, mode)}")
        
        # Update connect button
        if mode == "connect":
            self.connect_btn.config(text="✓ Connecting...")
        else:
            self.connect_btn.config(text="🔗 Connect")
    
    def add_port(self):
        """Add port to selected block"""
        if not self.controller.selected_block:
            from tkinter import messagebox
            messagebox.showwarning("Warning", "Please select a block first")
            return
        
        from ui.dialogs.port_edit import PortAddDialog
        dialog = PortAddDialog(self.winfo_toplevel(), self.controller, 
                              self.controller.selected_block)
    
    def manage_connections(self):
        """Open connections manager"""
        from ui.dialogs.connection_manager import ConnectionManagerDialog
        dialog = ConnectionManagerDialog(self.winfo_toplevel(), self.controller)