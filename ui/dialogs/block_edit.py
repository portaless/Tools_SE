"""
Block Edit Dialog
Comprehensive block property editor
"""

import tkinter as tk
from tkinter import ttk, messagebox
from models.entities import BlockType

class BlockEditDialog:
    """Dialog for editing block properties"""
    
    def __init__(self, parent, controller, block_id):
        self.controller = controller
        self.block_id = block_id
        self.block = controller.model.blocks[block_id]
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"✏️ Edit Block: {self.block.name}")
        self.dialog.geometry("500x700")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.center_dialog()
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (700 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        # Header
        header = tk.Canvas(self.dialog, height=50, 
                          bg="#4A90E2" if self.block.type == BlockType.LOGICAL else "#2ECC71",
                          highlightthickness=0)
        header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        icon = "🔷" if self.block.type == BlockType.LOGICAL else "🟢"
        header.create_text(250, 25, text=f"{icon} {self.block.name}",
                          font=("Arial", 14, "bold"), fill="white")
        
        # Scrollable content
        content_frame = self.create_scrollable_frame()
        
        # Basic properties
        row = self.add_section(content_frame, "📋 Basic Properties", 0)
        row = self.add_basic_properties(content_frame, row)
        
        # Position & Size
        row = self.add_section(content_frame, "📐 Position & Size", row)
        row = self.add_position_size(content_frame, row)
        
        # Layout settings
        row = self.add_section(content_frame, "⚙️ Layout Settings", row)
        row = self.add_layout_settings(content_frame, row)
        
        # Ports management
        row = self.add_section(content_frame, "🔌 Ports Management", row)
        row = self.add_ports_section(content_frame, row)
        
        # Info
        self.add_info_section(content_frame, row)
        
        # Buttons
        self.add_buttons()
    
    def create_scrollable_frame(self):
        """Create scrollable content frame"""
        canvas_frame = ttk.Frame(self.dialog)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        return self.scrollable_frame
    
    def add_section(self, parent, title, row):
        """Add section header"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(10 if row > 0 else 0, 10))
        
        ttk.Label(frame, text=title, font=("Arial", 10, "bold")).pack(anchor="w")
        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(5, 0))
        
        return row + 1
    
    def add_basic_properties(self, parent, row):
        """Add basic property fields"""
        # Name
        ttk.Label(parent, text="Name:").grid(row=row, column=0, sticky="w", pady=5, padx=(10, 5))
        self.name_var = tk.StringVar(value=self.block.name)
        name_entry = ttk.Entry(parent, textvariable=self.name_var, width=35)
        name_entry.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        # Type
        ttk.Label(parent, text="Type:").grid(row=row, column=0, sticky="w", pady=5, padx=(10, 5))
        self.type_var = tk.StringVar(value=self.block.type.value)
        type_combo = ttk.Combobox(parent, textvariable=self.type_var,
                                 values=["logical", "functional"], state="readonly", width=33)
        type_combo.grid(row=row, column=1, sticky="ew", pady=5)
        row += 1
        
        return row
    
    def add_position_size(self, parent, row):
        """Add position and size fields"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Position
        ttk.Label(frame, text="Position:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        ttk.Label(frame, text="X:").grid(row=1, column=0, sticky="w", padx=(10, 5))
        self.x_var = tk.IntVar(value=int(self.block.x))
        ttk.Spinbox(frame, from_=0, to=5000, textvariable=self.x_var, width=12).grid(row=1, column=1, sticky="w")
        
        ttk.Label(frame, text="Y:").grid(row=1, column=2, sticky="w", padx=(20, 5))
        self.y_var = tk.IntVar(value=int(self.block.y))
        ttk.Spinbox(frame, from_=0, to=5000, textvariable=self.y_var, width=12).grid(row=1, column=3, sticky="w")
        
        # Size
        ttk.Label(frame, text="Size:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky="w", pady=(10, 5))
        
        ttk.Label(frame, text="Width:").grid(row=3, column=0, sticky="w", padx=(10, 5))
        self.width_var = tk.IntVar(value=int(self.block.width))
        ttk.Spinbox(frame, from_=100, to=1000, textvariable=self.width_var, width=12).grid(row=3, column=1, sticky="w")
        
        ttk.Label(frame, text="Height:").grid(row=3, column=2, sticky="w", padx=(20, 5))
        self.height_var = tk.IntVar(value=int(self.block.height))
        ttk.Spinbox(frame, from_=100, to=1000, textvariable=self.height_var, width=12).grid(row=3, column=3, sticky="w")
        
        return row + 1
    
    def add_layout_settings(self, parent, row):
        """Add layout setting fields"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        ttk.Label(frame, text="Header Height:").grid(row=0, column=0, sticky="w", pady=5)
        self.header_var = tk.IntVar(value=self.block.header_height)
        ttk.Spinbox(frame, from_=30, to=80, textvariable=self.header_var, width=12).grid(row=0, column=1, sticky="w", padx=(5, 20))
        
        ttk.Label(frame, text="Port Width:").grid(row=0, column=2, sticky="w")
        self.port_width_var = tk.IntVar(value=self.block.port_section_width)
        ttk.Spinbox(frame, from_=15, to=50, textvariable=self.port_width_var, width=12).grid(row=0, column=3, sticky="w", padx=5)
        
        ttk.Label(frame, text="Padding:").grid(row=1, column=0, sticky="w", pady=5)
        self.padding_var = tk.IntVar(value=self.block.padding)
        ttk.Spinbox(frame, from_=5, to=30, textvariable=self.padding_var, width=12).grid(row=1, column=1, sticky="w", padx=(5, 20))
        
        ttk.Label(frame, text="Child Spacing:").grid(row=1, column=2, sticky="w")
        self.spacing_var = tk.IntVar(value=self.block.child_spacing)
        ttk.Spinbox(frame, from_=2, to=20, textvariable=self.spacing_var, width=12).grid(row=1, column=3, sticky="w", padx=5)
        
        return row + 1
    
    def add_ports_section(self, parent, row):
        """Add ports management section"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=10, pady=5)
        
        # Ports list
        self.ports_listbox = tk.Listbox(frame, height=5, width=50, selectmode=tk.SINGLE)
        self.ports_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_ports_list()
        
        # Buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row+1, column=0, columnspan=2, pady=(5, 10))
        
        ttk.Button(btn_frame, text="➕ Add", command=self.add_port, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="✏️ Edit", command=self.edit_port, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(btn_frame, text="🗑️ Delete", command=self.delete_port, width=12).pack(side=tk.LEFT, padx=3)
        
        return row + 2
    
    def add_info_section(self, parent, row):
        """Add info section"""
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=10, padx=10)
        
        info_canvas = tk.Canvas(frame, height=40, bg="#ECF0F1", highlightthickness=0)
        info_canvas.pack(fill=tk.X)
        
        info_text = f"ℹ️  Children: {len(self.block.children)}  |  "
        info_text += f"Connections: {len([c for c in self.controller.model.connections if c.from_block == self.block_id or c.to_block == self.block_id])}  |  "
        info_text += f"Level: {self.controller.model.get_nesting_level(self.block_id)}"
        
        info_canvas.create_text(10, 20, text=info_text, anchor="w", font=("Arial", 9), fill="#7F8C8D")
    
    def add_buttons(self):
        """Add action buttons"""
        btn_container = ttk.Frame(self.dialog)
        btn_container.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        btn_frame = ttk.Frame(btn_container)
        btn_frame.pack()
        
        apply_btn = tk.Button(btn_frame, text="✓ Apply Changes", command=self.apply_changes,
                             bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
                             padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="✗ Cancel", command=self.cancel,
                              bg="#95A5A6", fg="white", font=("Arial", 10, "bold"),
                              padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def refresh_ports_list(self):
        """Refresh ports listbox"""
        self.ports_listbox.delete(0, tk.END)
        for port in self.block.ports:
            side_icon = {"left": "⬅️", "right": "➡️", "top": "⬆️", "bottom": "⬇️"}.get(port.side, "•")
            self.ports_listbox.insert(tk.END, f"{side_icon} {port.name} ({port.side}, {int(port.offset*100)}%)")
    
    def add_port(self):
        """Add new port"""
        from ui.dialogs.port_edit import PortAddDialog
        self.dialog.grab_release()
        PortAddDialog(self.dialog, self.controller, self.block_id)
        self.dialog.grab_set()
        self.refresh_ports_list()
    
    def edit_port(self):
        """Edit selected port"""
        selection = self.ports_listbox.curselection()
        if not selection:
            return
        
        port = self.block.ports[selection[0]]
        from ui.dialogs.port_edit import PortEditDialog
        self.dialog.grab_release()
        PortEditDialog(self.dialog, self.controller, self.block_id, port.id)
        self.dialog.grab_set()
        self.refresh_ports_list()
        self.controller.redraw()
    
    def delete_port(self):
        """Delete selected port"""
        selection = self.ports_listbox.curselection()
        if not selection:
            return
        
        port = self.block.ports[selection[0]]
        if messagebox.askyesno("Delete Port", f"Delete port '{port.name}'?"):
            self.controller.model.delete_port(self.block_id, port.id)
            self.refresh_ports_list()
            self.controller.redraw()
    
    def apply_changes(self):
        """Apply changes to block"""
        try:
            new_name = self.name_var.get().strip()
            if not new_name:
                messagebox.showerror("Error", "Name cannot be empty")
                return
            
            # Apply changes
            self.block.name = new_name
            self.block.type = BlockType(self.type_var.get())
            self.block.x = float(self.x_var.get())
            self.block.y = float(self.y_var.get())
            self.block.width = float(self.width_var.get())
            self.block.height = float(self.height_var.get())
            self.block.header_height = self.header_var.get()
            self.block.port_section_width = self.port_width_var.get()
            self.block.padding = self.padding_var.get()
            self.block.child_spacing = self.spacing_var.get()
            
            # Re-layout if needed
            if self.block.children and self.block.show_content:
                self.controller.model.auto_layout_children(self.block_id)
            
            self.dialog.grab_release()
            self.dialog.destroy()
            
            self.controller.redraw()
            self.controller.props_panel.update()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {str(e)}")
    
    def cancel(self):
        """Cancel and close"""
        self.dialog.grab_release()
        self.dialog.destroy()