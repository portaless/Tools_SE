"""
Port Edit Dialogs
Dialogs for adding and editing ports
"""

import tkinter as tk
from tkinter import ttk, simpledialog, messagebox

class PortAddDialog:
    """Dialog for adding a new port"""
    
    def __init__(self, parent, controller, block_id):
        self.controller = controller
        self.block_id = block_id
        
        # Get port name
        port_name = simpledialog.askstring("Add Port", "Enter port name:")
        if not port_name or not port_name.strip():
            return
        
        self.port_name = port_name.strip()
        
        # Side selection dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Port Side")
        self.dialog.geometry("250x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.center_dialog()
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (250 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        ttk.Label(self.dialog, text="Select port position:", 
                 font=("Arial", 10)).pack(pady=15)
        
        ttk.Button(self.dialog, text="⬅️ Left", 
                   command=lambda: self.create_port("left")).pack(fill=tk.X, padx=30, pady=3)
        ttk.Button(self.dialog, text="➡️ Right", 
                   command=lambda: self.create_port("right")).pack(fill=tk.X, padx=30, pady=3)
        ttk.Button(self.dialog, text="⬆️ Top", 
                   command=lambda: self.create_port("top")).pack(fill=tk.X, padx=30, pady=3)
        ttk.Button(self.dialog, text="⬇️ Bottom", 
                   command=lambda: self.create_port("bottom")).pack(fill=tk.X, padx=30, pady=3)
    
    def create_port(self, side: str):
        """Create port with selected side"""
        try:
            port_id = self.controller.model.create_port(self.block_id, self.port_name, side)
            print(f"✓ Port added: '{self.port_name}' on {side} side")
            
            self.dialog.grab_release()
            self.dialog.destroy()
            
            self.controller.redraw()
            self.controller.props_panel.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create port: {str(e)}")


class PortEditDialog:
    """Dialog for editing port properties"""
    
    def __init__(self, parent, controller, block_id, port_id):
        self.controller = controller
        self.block_id = block_id
        self.port_id = port_id
        
        block = controller.model.blocks[block_id]
        self.port = controller.model.get_port_by_id(block_id, port_id)
        
        if not self.port:
            return
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Edit Port: {self.port.name}")
        self.dialog.geometry("350x280")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.center_dialog()
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (280 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Port name
        ttk.Label(main_frame, text="Port Name:").grid(row=0, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar(value=self.port.name)
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=25)
        name_entry.grid(row=0, column=1, sticky="ew", pady=5)
        
        # Port side
        ttk.Label(main_frame, text="Side:").grid(row=1, column=0, sticky="w", pady=5)
        self.side_var = tk.StringVar(value=self.port.side)
        side_combo = ttk.Combobox(main_frame, textvariable=self.side_var,
                                 values=["left", "right", "top", "bottom"],
                                 state="readonly", width=23)
        side_combo.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Port offset
        ttk.Label(main_frame, text="Position (%):").grid(row=2, column=0, sticky="w", pady=5)
        self.offset_var = tk.IntVar(value=int(self.port.offset * 100))
        offset_scale = ttk.Scale(main_frame, from_=10, to=90, variable=self.offset_var, 
                                orient=tk.HORIZONTAL)
        offset_scale.grid(row=2, column=1, sticky="ew", pady=5)
        
        self.offset_label = ttk.Label(main_frame, text=f"{self.offset_var.get()}%")
        self.offset_label.grid(row=3, column=1, sticky="w")
        
        self.offset_var.trace_add("write", self.update_offset_label)
        
        # Connection info
        port_conns = len([c for c in self.controller.model.connections
                         if c.from_port == self.port.id or c.to_port == self.port.id])
        
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=2,
                                                             sticky="ew", pady=15)
        ttk.Label(main_frame, text=f"Connections: {port_conns}",
                 foreground="gray").grid(row=5, column=0, columnspan=2, sticky="w")
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(btn_frame, text="✓ Apply", command=self.apply_changes, 
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✗ Cancel", command=self.cancel, 
                  width=15).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
        
        name_entry.focus_set()
        name_entry.select_range(0, tk.END)
    
    def update_offset_label(self, *args):
        """Update offset label"""
        self.offset_label.config(text=f"{self.offset_var.get()}%")
    
    def apply_changes(self):
        """Apply changes to port"""
        new_name = self.name_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Port name cannot be empty")
            return
        
        old_name = self.port.name
        self.port.name = new_name
        self.port.side = self.side_var.get()
        self.port.offset = self.offset_var.get() / 100.0
        
        print(f"✓ Port updated: '{old_name}' → '{self.port.name}'")
        print(f"  Side: {self.port.side}, Position: {int(self.port.offset*100)}%")
        
        self.dialog.grab_release()
        self.dialog.destroy()
        
        self.controller.redraw()
        self.controller.props_panel.update()
    
    def cancel(self):
        """Cancel and close"""
        self.dialog.grab_release()
        self.dialog.destroy()