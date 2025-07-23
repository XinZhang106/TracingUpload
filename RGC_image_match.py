import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import csv


class ImageMatcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Matcher - Manual 1:1 Matching")
        self.root.geometry("1200x800")

        # Data storage
        self.list1_files = []  # File paths for list 1
        self.list2_files = []  # File paths for list 2
        self.matches = {}  # Dictionary: {list1_index: list2_index}

        # Selected items
        self.selected_list1 = None
        self.selected_list2 = None
        self.confirmed_list1 = None  # Confirmed selection for matching
        self.confirmed_list2 = None  # Confirmed selection for matching

        # Image display variables
        self.current_image1 = None
        self.current_image2 = None

        self.setup_ui()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="Image Matching Tool", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))

        # File list frames
        self.setup_file_lists(main_frame)

        # Image display frame
        self.setup_image_display(main_frame)

        # Control buttons
        self.setup_controls(main_frame)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load images to begin")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))

    def setup_file_lists(self, parent):
        # List 1 frame
        list1_frame = ttk.LabelFrame(parent, text="Image List 1", padding="5")
        list1_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        list1_frame.columnconfigure(0, weight=1)
        list1_frame.rowconfigure(1, weight=1)

        # List 1 load button
        load1_btn = ttk.Button(list1_frame, text="Load Images (List 1)",
                               command=lambda: self.load_images(1))
        load1_btn.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))

        # List 1 listbox with scrollbar
        list1_scroll_frame = ttk.Frame(list1_frame)
        list1_scroll_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list1_scroll_frame.columnconfigure(0, weight=1)
        list1_scroll_frame.rowconfigure(0, weight=1)

        self.list1_listbox = tk.Listbox(list1_scroll_frame, selectmode=tk.SINGLE)
        self.list1_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.list1_listbox.bind('<<ListboxSelect>>', lambda e: self.on_list_select(1))

        list1_scrollbar = ttk.Scrollbar(list1_scroll_frame, orient=tk.VERTICAL,
                                        command=self.list1_listbox.yview)
        list1_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.list1_listbox.configure(yscrollcommand=list1_scrollbar.set)

        # Select button for List 1
        self.select1_btn = ttk.Button(list1_frame, text="Select for Matching",
                                      command=lambda: self.confirm_selection(1), state=tk.DISABLED)
        self.select1_btn.grid(row=2, column=0, pady=(5, 0), sticky=(tk.W, tk.E))

        # Selected item label for List 1
        self.selected1_var = tk.StringVar()
        self.selected1_var.set("No image selected for matching")
        selected1_label = ttk.Label(list1_frame, textvariable=self.selected1_var,
                                    font=("Arial", 8), foreground="blue")
        selected1_label.grid(row=3, column=0, pady=(2, 0))

        # List 2 frame
        list2_frame = ttk.LabelFrame(parent, text="Image List 2", padding="5")
        list2_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        list2_frame.columnconfigure(0, weight=1)
        list2_frame.rowconfigure(1, weight=1)

        # List 2 load button
        load2_btn = ttk.Button(list2_frame, text="Load Images (List 2)",
                               command=lambda: self.load_images(2))
        load2_btn.grid(row=0, column=0, pady=(0, 5), sticky=(tk.W, tk.E))

        # List 2 listbox with scrollbar
        list2_scroll_frame = ttk.Frame(list2_frame)
        list2_scroll_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list2_scroll_frame.columnconfigure(0, weight=1)
        list2_scroll_frame.rowconfigure(0, weight=1)

        self.list2_listbox = tk.Listbox(list2_scroll_frame, selectmode=tk.SINGLE)
        self.list2_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.list2_listbox.bind('<<ListboxSelect>>', lambda e: self.on_list_select(2))

        list2_scrollbar = ttk.Scrollbar(list2_scroll_frame, orient=tk.VERTICAL,
                                        command=self.list2_listbox.yview)
        list2_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.list2_listbox.configure(yscrollcommand=list2_scrollbar.set)

        # Select button for List 2
        self.select2_btn = ttk.Button(list2_frame, text="Select for Matching",
                                      command=lambda: self.confirm_selection(2), state=tk.DISABLED)
        self.select2_btn.grid(row=2, column=0, pady=(5, 0), sticky=(tk.W, tk.E))

        # Selected item label for List 2
        self.selected2_var = tk.StringVar()
        self.selected2_var.set("No image selected for matching")
        selected2_label = ttk.Label(list2_frame, textvariable=self.selected2_var,
                                    font=("Arial", 8), foreground="blue")
        selected2_label.grid(row=3, column=0, pady=(2, 0))

    def setup_image_display(self, parent):
        # Image display frame
        image_frame = ttk.LabelFrame(parent, text="Image Preview", padding="5")
        image_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        image_frame.columnconfigure(0, weight=1)
        image_frame.columnconfigure(2, weight=1)

        # Image 1 display
        self.image1_label = ttk.Label(image_frame, text="Select an image from List 1",
                                      relief=tk.SUNKEN, anchor=tk.CENTER)
        self.image1_label.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))

        # Separator
        separator = ttk.Separator(image_frame, orient=tk.VERTICAL)
        separator.grid(row=0, column=1, sticky=(tk.N, tk.S), padx=10)

        # Image 2 display
        self.image2_label = ttk.Label(image_frame, text="Select an image from List 2",
                                      relief=tk.SUNKEN, anchor=tk.CENTER)
        self.image2_label.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))

    def setup_controls(self, parent):
        # Control frame
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, columnspan=3, pady=10)

        # Match button
        self.match_btn = ttk.Button(control_frame, text="Create Match",
                                    command=self.create_match, state=tk.DISABLED)
        self.match_btn.grid(row=0, column=0, padx=5)

        # Remove match button
        self.remove_match_btn = ttk.Button(control_frame, text="Remove Match",
                                           command=self.remove_match, state=tk.DISABLED)
        self.remove_match_btn.grid(row=0, column=1, padx=5)

        # Export button
        export_btn = ttk.Button(control_frame, text="Export Matches to CSV",
                                command=self.export_matches)
        export_btn.grid(row=0, column=2, padx=5)

        # Clear all button
        clear_btn = ttk.Button(control_frame, text="Clear All Matches",
                               command=self.clear_matches)
        clear_btn.grid(row=0, column=3, padx=5)

        # Match counter
        self.match_count_var = tk.StringVar()
        self.match_count_var.set("Matches: 0")
        match_count_label = ttk.Label(control_frame, textvariable=self.match_count_var)
        match_count_label.grid(row=0, column=4, padx=20)

    def load_images(self, list_num):
        """Load images into the specified list"""
        filetypes = [
            ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
            ("All files", "*.*")
        ]

        files = filedialog.askopenfilenames(
            title=f"Select images for List {list_num}",
            filetypes=filetypes
        )

        if files:
            if list_num == 1:
                self.list1_files = list(files)
                self.list1_listbox.delete(0, tk.END)
                for file_path in self.list1_files:
                    filename = os.path.basename(file_path)
                    self.list1_listbox.insert(tk.END, filename)
                self.status_var.set(f"Loaded {len(self.list1_files)} images into List 1")
            else:
                self.list2_files = list(files)
                self.list2_listbox.delete(0, tk.END)
                for file_path in self.list2_files:
                    filename = os.path.basename(file_path)
                    self.list2_listbox.insert(tk.END, filename)
                self.status_var.set(f"Loaded {len(self.list2_files)} images into List 2")

            self.update_match_display()

    def on_list_select(self, list_num):
        """Handle selection in image lists"""
        try:
            if list_num == 1:
                selection = self.list1_listbox.curselection()
                if selection:
                    self.selected_list1 = selection[0]
                    self.display_image(self.list1_files[self.selected_list1], 1)
                    self.select1_btn.configure(state=tk.NORMAL)
                else:
                    self.selected_list1 = None
                    self.select1_btn.configure(state=tk.DISABLED)
            else:
                selection = self.list2_listbox.curselection()
                if selection:
                    self.selected_list2 = selection[0]
                    self.display_image(self.list2_files[self.selected_list2], 2)
                    self.select2_btn.configure(state=tk.NORMAL)
                else:
                    self.selected_list2 = None
                    self.select2_btn.configure(state=tk.DISABLED)

            self.update_button_states()

        except Exception as e:
            messagebox.showerror("Error", f"Error selecting image: {str(e)}")

    def confirm_selection(self, list_num):
        """Confirm selection for matching"""
        if list_num == 1 and self.selected_list1 is not None:
            self.confirmed_list1 = self.selected_list1
            filename = os.path.basename(self.list1_files[self.confirmed_list1])
            self.selected1_var.set(f"Selected: {filename}")
            self.status_var.set(f"List 1 selection confirmed: {filename}")
        elif list_num == 2 and self.selected_list2 is not None:
            self.confirmed_list2 = self.selected_list2
            filename = os.path.basename(self.list2_files[self.confirmed_list2])
            self.selected2_var.set(f"Selected: {filename}")
            self.status_var.set(f"List 2 selection confirmed: {filename}")

        self.update_button_states()

    def display_image(self, file_path, display_num):
        """Display image in the preview area"""
        try:
            # Open and resize image
            image = Image.open(file_path)

            # Calculate size maintaining aspect ratio
            max_size = (300, 200)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Display image
            if display_num == 1:
                self.current_image1 = photo  # Keep reference
                self.image1_label.configure(image=photo, text="")
            else:
                self.current_image2 = photo  # Keep reference
                self.image2_label.configure(image=photo, text="")

            # Update status with filename
            filename = os.path.basename(file_path)
            self.status_var.set(f"Displaying: {filename}")

        except Exception as e:
            if display_num == 1:
                self.image1_label.configure(image="", text=f"Error loading image:\n{str(e)}")
                self.current_image1 = None
            else:
                self.image2_label.configure(image="", text=f"Error loading image:\n{str(e)}")
                self.current_image2 = None

    def update_button_states(self):
        """Update button states based on current selection"""
        can_match = (self.confirmed_list1 is not None and
                     self.confirmed_list2 is not None and
                     len(self.list1_files) > 0 and
                     len(self.list2_files) > 0)

        can_remove = (self.confirmed_list1 is not None and
                      self.confirmed_list1 in self.matches)

        self.match_btn.configure(state=tk.NORMAL if can_match else tk.DISABLED)
        self.remove_match_btn.configure(state=tk.NORMAL if can_remove else tk.DISABLED)

    def create_match(self):
        """Create a match between selected images"""
        if self.confirmed_list1 is not None and self.confirmed_list2 is not None:
            # Check if list1 item is already matched
            if self.confirmed_list1 in self.matches:
                old_match = self.matches[self.confirmed_list1]
                old_filename = os.path.basename(self.list2_files[old_match])
                result = messagebox.askyesno("Match Exists",
                                             f"Image from List 1 is already matched to '{old_filename}'.\n"
                                             f"Do you want to replace this match?")
                if not result:
                    return

            # Create the match
            self.matches[self.confirmed_list1] = self.confirmed_list2

            # Update display
            self.update_match_display()
            self.update_button_states()

            # Update status
            file1 = os.path.basename(self.list1_files[self.confirmed_list1])
            file2 = os.path.basename(self.list2_files[self.confirmed_list2])
            self.status_var.set(f"Match created: {file1} ↔ {file2}")

            # Clear confirmed selections after successful match
            self.confirmed_list1 = None
            self.confirmed_list2 = None
            self.selected1_var.set("No image selected for matching")
            self.selected2_var.set("No image selected for matching")
            self.update_button_states()

    def remove_match(self):
        """Remove match for selected list1 item"""
        if self.confirmed_list1 is not None and self.confirmed_list1 in self.matches:
            matched_index = self.matches[self.confirmed_list1]
            file1 = os.path.basename(self.list1_files[self.confirmed_list1])
            file2 = os.path.basename(self.list2_files[matched_index])

            result = messagebox.askyesno("Remove Match",
                                         f"Remove match between:\n'{file1}' and '{file2}'?")

            if result:
                del self.matches[self.confirmed_list1]
                self.update_match_display()
                self.update_button_states()
                self.status_var.set(f"Match removed: {file1}")

                # Clear confirmed selections after removal
                self.confirmed_list1 = None
                self.confirmed_list2 = None
                self.selected1_var.set("No image selected for matching")
                self.selected2_var.set("No image selected for matching")
                self.update_button_states()

    def update_match_display(self):
        """Update the visual indicators for matches"""
        # Update match counter
        self.match_count_var.set(f"Matches: {len(self.matches)}")

        # Clear existing background colors
        for i in range(self.list1_listbox.size()):
            self.list1_listbox.itemconfig(i, bg='white')
        for i in range(self.list2_listbox.size()):
            self.list2_listbox.itemconfig(i, bg='white')

        # Highlight matched items
        for list1_idx, list2_idx in self.matches.items():
            if list1_idx < self.list1_listbox.size():
                self.list1_listbox.itemconfig(list1_idx, bg='lightgreen')
            if list2_idx < self.list2_listbox.size():
                self.list2_listbox.itemconfig(list2_idx, bg='lightgreen')

    def clear_matches(self):
        """Clear all matches"""
        if self.matches:
            result = messagebox.askyesno("Clear Matches",
                                         f"Are you sure you want to clear all {len(self.matches)} matches?")
            if result:
                self.matches.clear()
                self.update_match_display()
                self.update_button_states()
                self.status_var.set("All matches cleared")
        else:
            messagebox.showinfo("No Matches", "No matches to clear.")

    def export_matches(self):
        """Export matches to CSV file"""
        if not self.matches and not self.list1_files and not self.list2_files:
            messagebox.showwarning("No Data", "No images or matches to export.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save matches as CSV"
        )

        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)

                    # Write header
                    writer.writerow(['List1_Index', 'List1_Filename', 'List1_Path',
                                     'List2_Index', 'List2_Filename', 'List2_Path', 'Matched'])

                    # Write all list1 items
                    for i, file1_path in enumerate(self.list1_files):
                        file1_name = os.path.basename(file1_path)

                        if i in self.matches:
                            # This item is matched
                            j = self.matches[i]
                            file2_path = self.list2_files[j] if j < len(self.list2_files) else ""
                            file2_name = os.path.basename(file2_path) if file2_path else ""
                            writer.writerow([i, file1_name, file1_path, j, file2_name, file2_path, 'Yes'])
                        else:
                            # This item is not matched
                            writer.writerow([i, file1_name, file1_path, '', '', '', 'No'])

                messagebox.showinfo("Export Successful",
                                    f"Matches exported successfully to:\n{filename}\n\n"
                                    f"Total items: {len(self.list1_files)}\n"
                                    f"Matched items: {len(self.matches)}")

                self.status_var.set(f"Exported {len(self.matches)} matches to CSV")

            except Exception as e:
                messagebox.showerror("Export Error", f"Error exporting matches:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageMatcherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()