"""
MBSE Block Modeler - Main Entry Point
Architecture: MVC pattern with clear separation of concerns
"""

import tkinter as tk
from ui.main_window import MainWindow

def main():
    """Initialize and run the MBSE Modeler application"""
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()