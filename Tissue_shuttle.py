import tkinter as tk
from tkinter import ttk, messagebox

from startup import djlab, djanimal, djtissue
from tissue_dj import retina_tissue, brainSlice_tissue

class AnimalDataGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Animal Data Collection")
        self.root.geometry("500x600")

        # Variables to store input values
        self.animal_id = tk.StringVar()
        self.user_name = tk.StringVar()
        self.brain_slice_thickness = tk.StringVar()
        self.slicing_orientation = tk.StringVar()
        self.retina_side = tk.StringVar()

        # Validation status for each field
        self.validation_status = {
            'animal_id': False,
            'user_name': False,
            'brain_slice_thickness': False,
            'slicing_orientation': False,
            'retina_side': False
        }

        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Title
        title_label = ttk.Label(main_frame, text="Tissue Data Collection",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Animal ID
        ttk.Label(main_frame, text="Animal ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.animal_id_entry = ttk.Entry(main_frame, textvariable=self.animal_id, width=25)
        self.animal_id_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.animal_id_entry.bind('<KeyRelease>', lambda e: self.validate_field('animal_id'))

        # User Name
        ttk.Label(main_frame, text="User Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.user_name_entry = ttk.Entry(main_frame, textvariable=self.user_name, width=25)
        self.user_name_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.user_name_entry.bind('<KeyRelease>', lambda e: self.validate_field('user_name'))

        # Brain Slice Thickness
        ttk.Label(main_frame, text="Brain Slice Thickness:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.thickness_entry = ttk.Entry(main_frame, textvariable=self.brain_slice_thickness, width=25)
        self.thickness_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.thickness_entry.bind('<KeyRelease>', lambda e: self.validate_field('brain_slice_thickness'))

        # Slicing Orientation
        ttk.Label(main_frame, text="Slicing Orientation:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.orientation_combo = ttk.Combobox(main_frame, textvariable=self.slicing_orientation,
                                              values=["Sagittal", "Coronal", "Horizontal"],
                                              state="readonly", width=22)
        self.orientation_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.orientation_combo.bind('<<ComboboxSelected>>', lambda e: self.validate_field('slicing_orientation'))

        # Retina Side
        ttk.Label(main_frame, text="Retina Side:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.retina_combo = ttk.Combobox(main_frame, textvariable=self.retina_side,
                                         values=["Left", "Right", "Both"],
                                         state="readonly", width=22)
        self.retina_combo.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        self.retina_combo.bind('<<ComboboxSelected>>', lambda e: self.validate_field('retina_side'))

        # Feedback text box
        ttk.Label(main_frame, text="Validation Feedback:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.feedback_text = tk.Text(main_frame, height=10, width=60, wrap=tk.WORD)
        self.feedback_text.grid(row=7, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Scrollbar for feedback text
        feedback_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.feedback_text.yview)
        feedback_scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S), pady=5)
        self.feedback_text.config(yscrollcommand=feedback_scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=(20, 0))

        # Validate All button
        self.validate_button = ttk.Button(button_frame, text="Validate All",
                                          command=self.validate_all_fields)
        self.validate_button.grid(row=0, column=0, padx=(0, 10))

        # Confirm button
        self.confirm_button = ttk.Button(button_frame, text="Confirm",
                                         command=self.confirm_data, state="disabled")
        self.confirm_button.grid(row=0, column=1, padx=(10, 0))

        # Clear button
        self.clear_button = ttk.Button(button_frame, text="Clear All",
                                       command=self.clear_all_fields)
        self.clear_button.grid(row=0, column=2, padx=(10, 0))

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Initial feedback
        self.update_feedback("Ready for input. Please fill in all fields.")

#todo this function needs a lot of reworking
    def validate_field(self, field_name):

        """Validate individual field - placeholder for your custom validation"""
        if field_name == 'animal_id':
            value = self.animal_id.get().strip()
            if value and value.isdigit():
                self.validation_status[field_name] = True
                self.update_feedback(f"✓ Animal ID: Valid ({value})")
            else:
                self.validation_status[field_name] = False
                self.update_feedback(f"✗ Animal ID: Must be a number")

        elif field_name == 'user_name':
            value = self.user_name.get().strip()
            user = {'user_name': value}
            queryresult = djlab.User & user
            result = queryresult.fetch('user_name')
            if result.size>0:
                self.validation_status[field_name] = True
                self.update_feedback(f"✓ User Name: Valid ({value})")
            else:
                self.validation_status[field_name] = False
                self.update_feedback(f"✗ User Name: Check if name spelling is right, or if you are in lab's DJ!")

        elif field_name == 'brain_slice_thickness':
            value = self.brain_slice_thickness.get().strip()
            try:
                thickness = float(value)
                if thickness > 0:
                    self.validation_status[field_name] = True
                    self.update_feedback(f"✓ Brain Slice Thickness: Valid ({thickness})")
                else:
                    self.validation_status[field_name] = False
                    self.update_feedback(f"✗ Brain Slice Thickness: Must be positive")
            except ValueError:
                self.validation_status[field_name] = False
                self.update_feedback(f"✗ Brain Slice Thickness: Must be a number")

        elif field_name == 'slicing_orientation':
            value = self.slicing_orientation.get()

            if value:
                self.validation_status[field_name] = True
                self.update_feedback(f"✓ Slicing Orientation: Valid ({value})")
            else:
                self.validation_status[field_name] = False
                self.update_feedback(f"✗ Slicing Orientation: Please select an option")

        elif field_name == 'retina_side':
            value = self.retina_side.get()
            if value:
                self.validation_status[field_name] = True
                self.update_feedback(f"✓ Retina Side: Valid ({value})")
            else:
                self.validation_status[field_name] = False
                self.update_feedback(f"✗ Retina Side: Please select an option")

        # Enable/disable confirm button based on validation
        self.update_confirm_button()

    def validate_all_fields(self):
        """Validate all fields at once"""
        self.clear_feedback()
        self.update_feedback("Validating all fields...\n")

        for field in ['animal_id', 'user_name', 'brain_slice_thickness', 'slicing_orientation', 'retina_side']:
            self.validate_field(field)

        if all(self.validation_status.values()):
            self.update_feedback("\n✓ All fields are valid! You can now confirm.")
        else:
            self.update_feedback("\n✗ Some fields need attention. Please fix the errors above.")

    def update_confirm_button(self):
        """Enable/disable confirm button based on validation status"""
        if all(self.validation_status.values()):
            self.confirm_button.config(state="normal")
        else:
            self.confirm_button.config(state="disabled")

    def update_feedback(self, message):
        """Update feedback text box"""
        self.feedback_text.insert(tk.END, message + "\n")
        self.feedback_text.see(tk.END)

    def clear_feedback(self):
        """Clear feedback text box"""
        self.feedback_text.delete(1.0, tk.END)

    def clear_all_fields(self):
        """Clear all input fields"""
        self.animal_id.set("")
        self.user_name.set("")
        self.brain_slice_thickness.set("")
        self.slicing_orientation.set("")
        self.retina_side.set("")

        # Reset validation status
        for key in self.validation_status:
            self.validation_status[key] = False

        self.clear_feedback()
        self.update_feedback("All fields cleared. Ready for new input.")
        self.update_confirm_button()

    def confirm_data(self):
        """Handle confirm button click - replace this with your custom logic"""
        if all(self.validation_status.values()):
            # Get all the validated data
            data = {
                'animal_id': int(self.animal_id.get()),
                'user_name': self.user_name.get().strip(),
                'brain_slice_thickness': float(self.brain_slice_thickness.get()),
                'slicing_orientation': self.slicing_orientation.get(),
                'retina_side': self.retina_side.get()
            }

            # TODO: Replace this section with your custom processing logic
            self.update_feedback(f"\n✓ Data confirmed and ready for processing:")
            self.update_feedback(f"  Animal ID: {data['animal_id']}")
            self.update_feedback(f"  User Name: {data['user_name']}")
            self.update_feedback(f"  Brain Slice Thickness: {data['brain_slice_thickness']}")
            self.update_feedback(f"  Slicing Orientation: {data['slicing_orientation']}")
            self.update_feedback(f"  Retina Side: {data['retina_side']}")

            # Your custom processing code goes here
            self.uploading(data)

        else:
            messagebox.showerror("Validation Error", "Please fix all validation errors before confirming.")


    def get_data(self):
        """Get current data as dictionary (useful for external access)"""
        return {
            'animal_id': self.animal_id.get(),
            'user_name': self.user_name.get(),
            'brain_slice_thickness': self.brain_slice_thickness.get(),
            'slicing_orientation': self.slicing_orientation.get(),
            'retina_side': self.retina_side.get()
        }

    def uploading(self, data = None):
        if data is None:
            data = self.get_data()
        retina = retina_tissue(data['animal_id'], data['retina_side'])
        retina_id = retina.uploader(data['user_name'])
        message_retina = 'Retina tissue id: ' + str(retina_id) + '\n'


        brainslice = brainSlice_tissue(data['animal_id'], data['brain_slice_thickness'], data['slicing_orientation'])
        brain_id = brainslice.uploader(data['user_name'])
        mesaage_brain = 'Brain slice tissue id: ' + str(brain_id) + '\n'

        total_message = message_retina + mesaage_brain
        self.update_feedback(total_message)
        return


def main():
    root = tk.Tk()
    app = AnimalDataGUI(root)
    root.mainloop()




if __name__ == "__main__":
    main()