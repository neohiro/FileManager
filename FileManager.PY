import os
import shutil
import sys
import string
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class GUIFileManager(tk.Tk):
    """
    A simple graphical file manager with a directory tree and file list.
    """
    def __init__(self):
        super().__init__()
        self.title("GUI File Manager")
        self.geometry("800x600")

        # Set up styles for a more modern look
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('Treeview', font=('Arial', 10), rowheight=22)
        style.map('Treeview',
                  background=[('selected', '#347083')],
                  foreground=[('selected', 'white')])

        # Store the current directory, starting at the user's home folder
        self.current_path = os.path.expanduser('~')

        # Create main frames
        self.main_frame = ttk.Frame(self, padding="5 5 5 5")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Shortcuts, Directory Tree, and File List frames
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))

        self.shortcuts_frame = ttk.LabelFrame(self.left_panel, text="Shortcuts", padding="5 5 5 5")
        self.shortcuts_frame.pack(fill=tk.X, pady=(0, 5))

        self.drives_frame = ttk.LabelFrame(self.left_panel, text="Drives", padding="5 5 5 5")
        self.drives_frame.pack(fill=tk.X, pady=5)

        self.tree_frame = ttk.Frame(self.left_panel)
        self.tree_frame.pack(side=tk.LEFT, fill=tk.Y, expand=True)

        self.list_frame = ttk.Frame(self.main_frame)
        self.list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Populate shortcuts and drives
        self.add_shortcuts()
        self.add_drives()

        # Directory Treeview
        self.tree = ttk.Treeview(self.tree_frame, selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.heading("#0", text="Directory Tree", anchor=tk.W)

        # File Listbox
        self.file_listbox = tk.Listbox(self.list_frame, selectmode=tk.EXTENDED, font=('Arial', 10))
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<Double-1>', self.on_file_double_click)

        # Path label
        self.path_label = ttk.Label(self, text=f"Current Path: {self.current_path}", font=('Arial', 10, 'bold'))
        self.path_label.pack(fill=tk.X, padx=5, pady=(0, 5))

        # Action buttons
        self.button_frame = ttk.Frame(self)
        self.button_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # New "Up" button added here
        ttk.Button(self.button_frame, text="Up", command=self.go_up).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="New Folder", command=self.create_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="New File", command=self.create_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Delete", command=self.delete_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Rename", command=self.rename_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Copy", command=self.copy_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Move", command=self.move_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.button_frame, text="Refresh", command=self.refresh).pack(side=tk.RIGHT, padx=5)

        # Populate the tree
        self.populate_tree()
        self.update_file_list()

    def add_shortcuts(self):
        """Adds buttons for common locations to the shortcuts frame."""
        home_path = os.path.expanduser('~')
        desktop_path = os.path.join(home_path, "Desktop")
        docs_path = os.path.join(home_path, "Documents")

        ttk.Button(self.shortcuts_frame, text="Home", command=lambda: self.go_to_path(home_path)).pack(fill=tk.X, pady=2)
        ttk.Button(self.shortcuts_frame, text="Desktop", command=lambda: self.go_to_path(desktop_path)).pack(fill=tk.X, pady=2)
        ttk.Button(self.shortcuts_frame, text="Documents", command=lambda: self.go_to_path(docs_path)).pack(fill=tk.X, pady=2)

    def add_drives(self):
        """Adds buttons for system drives to the drives frame."""
        if sys.platform == "win32":
            for letter in string.ascii_uppercase:
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    ttk.Button(self.drives_frame, text=f"Drive {letter}", command=lambda d=drive: self.go_to_path(d)).pack(fill=tk.X, pady=2)
        else:
            # On Linux/macOS, use the root directory as a shortcut
            ttk.Button(self.drives_frame, text="Root", command=lambda: self.go_to_path("/")).pack(fill=tk.X, pady=2)

    def go_up(self):
        """Moves to the parent directory."""
        parent_path = os.path.dirname(self.current_path)
        self.go_to_path(parent_path)

    def go_to_path(self, path):
        """Updates the current path and refreshes the display."""
        if os.path.isdir(path):
            self.current_path = path
            self.path_label.config(text=f"Current Path: {self.current_path}")
            self.populate_tree(parent_path=self.current_path)
            self.update_file_list()
        else:
            messagebox.showerror("Error", f"Path not found: {path}")

    def refresh(self):
        """Refreshes the file list and tree view."""
        self.populate_tree(parent_path=self.current_path)
        self.update_file_list()

    def populate_tree(self, parent_id='', parent_path=None):
        """Populates the directory tree starting from the specified path."""
        if not parent_path:
            parent_path = self.current_path

        self.tree.delete(*self.tree.get_children())
        self.tree.insert('', 'end', parent_path, text=parent_path, open=True)
        self._insert_children(parent_path, parent_path)

    def _insert_children(self, parent_id, parent_path):
        """Helper function to insert child directories."""
        try:
            for item in os.listdir(parent_path):
                full_path = os.path.join(parent_path, item)
                if os.path.isdir(full_path):
                    self.tree.insert(parent_id, 'end', full_path, text=item)
        except PermissionError:
            pass # Ignore directories we don't have permission to access

    def on_tree_select(self, event):
        """Handles directory selection in the Treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            return
        
        path = selected_item[0]
        self.go_to_path(path)


    def on_file_double_click(self, event):
        """Opens a selected file or directory."""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        file_name = self.file_listbox.get(selection[0])
        full_path = os.path.join(self.current_path, file_name)

        if os.path.isdir(full_path):
            self.go_to_path(full_path)
        else:
            messagebox.showinfo("File Selected", f"You double-clicked on: {full_path}")
            # You could add logic here to open the file with the default program

    def update_file_list(self):
        """Updates the listbox with files and directories in the current path."""
        self.file_listbox.delete(0, tk.END)
        try:
            for item in sorted(os.listdir(self.current_path)):
                self.file_listbox.insert(tk.END, item)
        except FileNotFoundError:
            messagebox.showerror("Error", "Directory not found.")
        except PermissionError:
            messagebox.showerror("Permission Error", "You do not have permission to access this directory.")

    def create_folder(self):
        """Creates a new folder."""
        new_name = filedialog.askstring("New Folder", "Enter new folder name:")
        if new_name:
            try:
                os.mkdir(os.path.join(self.current_path, new_name))
                self.update_file_list()
                self.populate_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create folder: {e}")

    def create_file(self):
        """Creates a new file."""
        new_name = filedialog.askstring("New File", "Enter new file name:")
        if new_name:
            try:
                with open(os.path.join(self.current_path, new_name), 'w') as f:
                    f.write("")
                self.update_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Could not create file: {e}")

    def delete_item(self):
        """Deletes selected file(s) or folder(s)."""
        selected_items = self.file_listbox.curselection()
        if not selected_items:
            messagebox.showinfo("Info", "No item selected to delete.")
            return

        if not messagebox.askyesno("Delete", "Are you sure you want to delete the selected items?"):
            return

        for index in selected_items:
            item_name = self.file_listbox.get(index)
            full_path = os.path.join(self.current_path, item_name)
            try:
                if os.path.isdir(full_path):
                    shutil.rmtree(full_path)
                else:
                    os.remove(full_path)
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete '{item_name}': {e}")
        self.update_file_list()
        self.populate_tree()

    def rename_item(self):
        """Renames a selected file or folder."""
        selection = self.file_listbox.curselection()
        if len(selection) != 1:
            messagebox.showinfo("Info", "Please select exactly one item to rename.")
            return

        old_name = self.file_listbox.get(selection[0])
        new_name = filedialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if new_name and new_name != old_name:
            try:
                old_path = os.path.join(self.current_path, old_name)
                new_path = os.path.join(self.current_path, new_name)
                os.rename(old_path, new_path)
                self.update_file_list()
                self.populate_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Could not rename '{old_name}': {e}")

    def copy_item(self):
        """Copies selected items."""
        selected_items = self.file_listbox.curselection()
        if not selected_items:
            messagebox.showinfo("Info", "No item selected to copy.")
            return
        
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if not destination:
            return

        for index in selected_items:
            item_name = self.file_listbox.get(index)
            source_path = os.path.join(self.current_path, item_name)
            try:
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, os.path.join(destination, item_name))
                else:
                    shutil.copy(source_path, destination)
            except Exception as e:
                messagebox.showerror("Error", f"Could not copy '{item_name}': {e}")
        
        self.update_file_list()
        self.populate_tree()

    def move_item(self):
        """Moves selected items."""
        selected_items = self.file_listbox.curselection()
        if not selected_items:
            messagebox.showinfo("Info", "No item selected to move.")
            return
        
        destination = filedialog.askdirectory(title="Select Destination Folder")
        if not destination:
            return

        for index in selected_items:
            item_name = self.file_listbox.get(index)
            source_path = os.path.join(self.current_path, item_name)
            try:
                shutil.move(source_path, destination)
            except Exception as e:
                messagebox.showerror("Error", f"Could not move '{item_name}': {e}")
        
        self.update_file_list()
        self.populate_tree()

if __name__ == "__main__":
    app = GUIFileManager()
    app.mainloop()
