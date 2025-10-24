"""
File I/O Utilities
Handles saving and loading of models
"""

import json
from tkinter import filedialog, messagebox
from typing import Optional

class FileIO:
    """File operations for model persistence"""
    
    @staticmethod
    def save(model_manager) -> bool:
        """Save model to JSON file"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save Model"
        )
        
        if not filename:
            return False
        
        try:
            data = model_manager.to_dict()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Model saved to:\n{filename}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save model:\n{str(e)}")
            return False
    
    @staticmethod
    def load(model_manager) -> bool:
        """Load model from JSON file"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Load Model"
        )
        
        if not filename:
            return False
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            model_manager.from_dict(data)
            
            messagebox.showinfo("Success", f"Model loaded from:\n{filename}")
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load model:\n{str(e)}")
            return False
    
    @staticmethod
    def export_to_dict(model_manager) -> dict:
        """Export model to dictionary"""
        return model_manager.to_dict()
    
    @staticmethod
    def import_from_dict(model_manager, data: dict) -> bool:
        """Import model from dictionary"""
        try:
            model_manager.from_dict(data)
            return True
        except Exception as e:
            print(f"Import error: {e}")
            return False