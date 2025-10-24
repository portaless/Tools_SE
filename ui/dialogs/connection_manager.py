"""
Connection Manager Dialog
Manages all connections in the model
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ConnectionManagerDialog:
    """Dialog for managing connections"""
    
    def __init__(self, parent, controller):
        self.controller = controller
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔗 Connection Manager")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.center_dialog()
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_container = ttk.Frame(self.dialog)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_canvas = tk.Canvas(main_container, height=50, bg="#3498DB", highlightthickness=0)
        header_canvas.pack(fill=tk.X)
        header_canvas.create_text(
            350, 25,
            text=f"🔗 Manage Connections ({len(self.controller.model.connections)} total)",
            font=("Arial", 14, "bold"),
            fill="white"
        )
        
        # Connections list
        list_frame = ttk.LabelFrame(main_container, text="Connections List", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 10))
        
        # Treeview
        columns = ("From", "From Port", "To", "To Port")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=15)
        
        self.tree.heading("#0", text="ID")
        self.tree.heading("From", text="From Block")
        self.tree.heading("From Port", text="From Port")
        self.tree.heading("To", text="To Block")
        self.tree.heading("To Port", text="To Port")
        
        self.tree.column("#0", width=80)
        self.tree.column("From", width=150)
        self.tree.column("From Port", width=120)
        self.tree.column("To", width=150)
        self.tree.column("To Port", width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bindings
        self.tree.bind("<Double-Button-1>", lambda e: self.edit_connection())
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.highlight_connection())
        
        # Populate tree
        self.refresh_list()
        
        # Buttons
        btn_frame = ttk.Frame(main_container)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="✏️ Edit Connection", 
                  command=self.edit_connection, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Connection", 
                  command=self.delete_connection, width=20).pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = tk.Button(btn_frame, text="✓ Close", command=self.close,
                             bg="#3498DB", fg="white", font=("Arial", 10, "bold"),
                             padx=20, pady=8, relief=tk.FLAT, cursor="hand2")
        close_btn.pack(side=tk.RIGHT, padx=5)
    
    def refresh_list(self):
        """Refresh connections list"""
        self.tree.delete(*self.tree.get_children())
        
        for conn in self.controller.model.connections:
            from_block = self.controller.model.blocks.get(conn.from_block)
            to_block = self.controller.model.blocks.get(conn.to_block)
            
            if not from_block or not to_block:
                continue
            
            # Get port names
            from_port_name = "Block"
            if conn.from_port:
                from_port = self.controller.model.get_port_by_id(conn.from_block, conn.from_port)
                if from_port:
                    from_port_name = from_port.name
            
            to_port_name = "Block"
            if conn.to_port:
                to_port = self.controller.model.get_port_by_id(conn.to_block, conn.to_port)
                if to_port:
                    to_port_name = to_port.name
            
            self.tree.insert("", tk.END, text=conn.id,
                           values=(from_block.name, from_port_name, to_block.name, to_port_name),
                           tags=(conn.id,))
    
    def edit_connection(self):
        """Edit selected connection"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a connection to edit")
            return
        
        conn_id = self.tree.item(selection[0])["tags"][0]
        conn = next((c for c in self.controller.model.connections if c.id == conn_id), None)
        
        if not conn:
            return
        
        self.dialog.grab_release()
        ConnectionEditDialog(self.dialog, self.controller, conn)
        self.dialog.grab_set()
        self.refresh_list()
        self.controller.redraw()
    
    def delete_connection(self):
        """Delete selected connection"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a connection to delete")
            return
        
        conn_id = self.tree.item(selection[0])["tags"][0]
        conn = next((c for c in self.controller.model.connections if c.id == conn_id), None)
        
        if not conn:
            return
        
        from_block = self.controller.model.blocks.get(conn.from_block)
        to_block = self.controller.model.blocks.get(conn.to_block)
        
        message = f"Delete connection from '{from_block.name}' to '{to_block.name}'?"
        
        if messagebox.askyesno("Delete Connection", message):
            self.controller.model.delete_connection(conn.id)
            self.refresh_list()
            self.controller.redraw()
            self.controller.props_panel.update()
    
    def highlight_connection(self):
        """Highlight blocks involved in selected connection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        conn_id = self.tree.item(selection[0])["tags"][0]
        conn = next((c for c in self.controller.model.connections if c.id == conn_id), None)
        
        if not conn:
            return
        
        self.controller.selected_block = conn.from_block
        self.controller.selected_blocks = [conn.from_block, conn.to_block]
        self.controller.redraw()
    
    def close(self):
        """Close dialog"""
        self.dialog.grab_release()
        self.dialog.destroy()


class ConnectionEditDialog:
    """Dialog for editing connection endpoints"""
    
    def __init__(self, parent, controller, connection):
        self.controller = controller
        self.connection = connection
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"✏️ Edit Connection: {connection.id}")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.center_dialog()
        self.setup_ui()
    
    def center_dialog(self):
        """Center dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (400 // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_canvas = tk.Canvas(main_frame, height=40, bg="#9B59B6", highlightthickness=0)
        header_canvas.pack(fill=tk.X)
        header_canvas.create_text(250, 20, text="🔗 Edit Connection",
                                 font=("Arial", 12, "bold"), fill="white")
        
        # Source section
        ttk.Label(main_frame, text="Source", font=("Arial", 10, "bold")).pack(anchor="w", pady=(15, 5))
        
        source_frame = ttk.Frame(main_frame)
        source_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(source_frame, text="From Block:").grid(row=0, column=0, sticky="w", pady=5)
        self.from_block_var = tk.StringVar(value=f"{self.connection.from_block} - {self.controller.model.blocks[self.connection.from_block].name}")
        from_block_combo = ttk.Combobox(source_frame, textvariable=self.from_block_var,
                                       values=[f"{b.id} - {b.name}" for b in self.controller.model.blocks.values()],
                                       state="readonly", width=35)
        from_block_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        ttk.Label(source_frame, text="From Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.from_port_var = tk.StringVar(value=self.connection.from_port or "Block")
        self.from_port_combo = ttk.Combobox(source_frame, textvariable=self.from_port_var, width=35)
        self.from_port_combo.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        self.from_block_var.trace_add("write", self.update_from_ports)
        self.update_from_ports()
        
        # Destination section
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=15)
        ttk.Label(main_frame, text="Destination", font=("Arial", 10, "bold")).pack(anchor="w", pady=(5, 5))
        
        dest_frame = ttk.Frame(main_frame)
        dest_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dest_frame, text="To Block:").grid(row=0, column=0, sticky="w", pady=5)
        self.to_block_var = tk.StringVar(value=f"{self.connection.to_block} - {self.controller.model.blocks[self.connection.to_block].name}")
        to_block_combo = ttk.Combobox(dest_frame, textvariable=self.to_block_var,
                                     values=[f"{b.id} - {b.name}" for b in self.controller.model.blocks.values()],
                                     state="readonly", width=35)
        to_block_combo.grid(row=0, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        ttk.Label(dest_frame, text="To Port:").grid(row=1, column=0, sticky="w", pady=5)
        self.to_port_var = tk.StringVar(value=self.connection.to_port or "Block")
        self.to_port_combo = ttk.Combobox(dest_frame, textvariable=self.to_port_var, width=35)
        self.to_port_combo.grid(row=1, column=1, sticky="ew", pady=5, padx=(10, 0))
        
        self.to_block_var.trace_add("write", self.update_to_ports)
        self.update_to_ports()
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=(20, 0))
        
        apply_btn = tk.Button(btn_frame, text="✓ Apply", command=self.apply_changes,
                             bg="#27AE60", fg="white", font=("Arial", 10, "bold"),
                             padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        apply_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(btn_frame, text="✗ Cancel", command=self.cancel,
                              bg="#95A5A6", fg="white", font=("Arial", 10, "bold"),
                              padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        source_frame.columnconfigure(1, weight=1)
        dest_frame.columnconfigure(1, weight=1)
    
    def update_from_ports(self, *args):
        """Update from ports list"""
        try:
            block_id = self.from_block_var.get().split(" - ")[0]
            if block_id in self.controller.model.blocks:
                block = self.controller.model.blocks[block_id]
                ports = ["Block"] + [f"{p.id} - {p.name}" for p in block.ports]
                self.from_port_combo['values'] = ports
        except:
            pass
    
    def update_to_ports(self, *args):
        """Update to ports list"""
        try:
            block_id = self.to_block_var.get().split(" - ")[0]
            if block_id in self.controller.model.blocks:
                block = self.controller.model.blocks[block_id]
                ports = ["Block"] + [f"{p.id} - {p.name}" for p in block.ports]
                self.to_port_combo['values'] = ports
        except:
            pass
    
    def apply_changes(self):
        """Apply changes to connection"""
        try:
            from_block_id = self.from_block_var.get().split(" - ")[0]
            to_block_id = self.to_block_var.get().split(" - ")[0]
            
            from_port_val = self.from_port_var.get()
            from_port_id = None if from_port_val == "Block" else from_port_val.split(" - ")[0]
            
            to_port_val = self.to_port_var.get()
            to_port_id = None if to_port_val == "Block" else to_port_val.split(" - ")[0]
            
            if from_block_id not in self.controller.model.blocks or \
               to_block_id not in self.controller.model.blocks:
                messagebox.showerror("Error", "Invalid block selection")
                return
            
            # Apply changes
            self.connection.from_block = from_block_id
            self.connection.to_block = to_block_id
            self.connection.from_port = from_port_id
            self.connection.to_port = to_port_id
            
            self.dialog.grab_release()
            self.dialog.destroy()
            
            self.controller.redraw()
            self.controller.props_panel.update()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update connection: {str(e)}")
    
    def cancel(self):
        """Cancel and close"""
        self.dialog.grab_release()
        self.dialog.destroy()