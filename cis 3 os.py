import tkinter as tk
from tkinter import messagebox, simpledialog  # Import simpledialog

class SimpleBankers:
    def __init__(self, total, max_demand, allocated):
        if len(total) != len(max_demand[0]) or len(max_demand) != len(allocated) or len(allocated[0]) != len(total):
            raise ValueError("Mismatch in number of resources between total, max_demand, and allocated lists.")
        
        self.total = total
        self.max_demand = max_demand
        self.allocated = allocated

        self.need = [[self.max_demand[i][j] - self.allocated[i][j] 
                      for j in range(len(total))] for i in range(len(max_demand))]

    def is_safe(self):
        work = self.total[:]
        finish = [False] * len(self.max_demand)
        safe_sequence = []

        for _ in range(len(self.max_demand)):
            for i in range(len(self.max_demand)):
                if not finish[i] and all(self.need[i][j] <= work[j] for j in range(len(work))):
                    for j in range(len(work)):
                        work[j] += self.allocated[i][j]
                    finish[i] = True
                    safe_sequence.append(i)
                    break
            else:
                return False, []
        return True, safe_sequence

    def request(self, dept, req):
        if any(req[j] > self.need[dept][j] for j in range(len(req))) or any(req[j] > self.total[j] for j in range(len(req))):
            return False
        
        for j in range(len(req)):
            self.total[j] -= req[j]
            self.allocated[dept][j] += req[j]
            self.need[dept][j] -= req[j]

        safe, sequence = self.is_safe()
        if safe:
            return True, sequence
        else:
            for j in range(len(req)):
                self.total[j] += req[j]
                self.allocated[dept][j] -= req[j]
                self.need[dept][j] += req[j]
            return False

    def display_current_state(self):
        print("\nCurrent Resource Allocation:")
        for i, alloc in enumerate(self.allocated):
            print(f"Department {i} (Allocated): {alloc}")
        
        print("Need Matrix:")
        for i, need in enumerate(self.need):
            print(f"Department {i} (Need): {need}")

        print(f"Available Resources: {self.total}")

class HospitalResourceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hospital Resource Manager")
        
        # Center the window
        self.center_window(400, 300)  # Width and Height of the window

        # Total Resources
        self.total_label = tk.Label(root, text="Enter total resources (space-separated):")
        self.total_label.grid(row=0, column=0)
        self.total_entry = tk.Entry(root)
        self.total_entry.grid(row=0, column=1)

        # Number of Departments
        self.dept_label = tk.Label(root, text="Enter number of departments:")
        self.dept_label.grid(row=1, column=0)
        self.dept_entry = tk.Entry(root)
        self.dept_entry.grid(row=1, column=1)

        # Button to initialize the system
        self.initialize_button = tk.Button(root, text="Initialize", command=self.initialize_system)
        self.initialize_button.grid(row=2, column=0, columnspan=2)

        # Buttons for the operations
        self.safe_state_button = tk.Button(root, text="Check Safe State", command=self.check_safe_state, state=tk.DISABLED)
        self.safe_state_button.grid(row=3, column=0, columnspan=2)

        self.request_button = tk.Button(root, text="Request Resources", command=self.request_resources, state=tk.DISABLED)
        self.request_button.grid(row=4, column=0, columnspan=2)

        self.display_button = tk.Button(root, text="Display Current State", command=self.display_current_state, state=tk.DISABLED)
        self.display_button.grid(row=5, column=0, columnspan=2)

    def center_window(self, width, height):
        # Get screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Calculate the position of the window
        position_x = (screen_width // 2) - (width // 2)
        position_y = (screen_height // 2) - (height // 2)

        # Set the geometry of the window
        self.root.geometry(f'{width}x{height}+{position_x}+{position_y}')

    def initialize_system(self):
        try:
            # Get total resources
            total_resources = list(map(int, self.total_entry.get().split()))
            num_departments = int(self.dept_entry.get())

            # Create entry fields for each department
            self.max_demand_entries = []
            self.allocated_entries = []
            for i in range(num_departments):
                tk.Label(self.root, text=f"Department {i} Max Demand:").grid(row=6 + i, column=0)
                max_demand_entry = tk.Entry(self.root)
                max_demand_entry.grid(row=6 + i, column=1)
                self.max_demand_entries.append(max_demand_entry)

                tk.Label(self.root, text=f"Department {i} Allocated:").grid(row=6 + num_departments + i, column=0)
                allocated_entry = tk.Entry(self.root)
                allocated_entry.grid(row=6 + num_departments + i, column=1)
                self.allocated_entries.append(allocated_entry)

            # Button to confirm input and initialize system
            self.confirm_button = tk.Button(self.root, text="Confirm Input", command=lambda: self.confirm_input(total_resources, num_departments))
            self.confirm_button.grid(row=6 + 2 * num_departments, column=0, columnspan=2)

        except ValueError:
            messagebox.showerror("Input Error", "Please provide valid inputs.")

    def confirm_input(self, total_resources, num_departments):
        try:
            max_demand = []
            allocated = []

            # Collect max demand and allocated resources from entries
            for i in range(num_departments):
                max_demand.append(list(map(int, self.max_demand_entries[i].get().split())))
                allocated.append(list(map(int, self.allocated_entries[i].get().split())))

            # Initialize the Banker's algorithm system
            self.hospital = SimpleBankers(total_resources, max_demand, allocated)
            messagebox.showinfo("Success", "System initialized successfully.")

            # Enable the action buttons
            self.safe_state_button.config(state=tk.NORMAL)
            self.request_button.config(state=tk.NORMAL)
            self.display_button.config(state=tk.NORMAL)

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")

    def check_safe_state(self):
        is_safe, safe_sequence = self.hospital.is_safe()
        if is_safe:
            messagebox.showinfo("Safe State", f"System is in a safe state. Safe sequence: {safe_sequence}")
        else:
            messagebox.showerror("Unsafe State", "System is not in a safe state.")

    def request_resources(self):
        dept = int(simpledialog.askstring("Request", "Enter department number:"))
        req = list(map(int, simpledialog.askstring("Request", "Enter resources requested:").split()))
        
        granted, safe_sequence = self.hospital.request(dept, req)
        if granted:
            messagebox.showinfo("Request Granted", f"Resources allocated successfully. Safe sequence: {safe_sequence}")
        else:
            messagebox.showerror("Request Denied", "Request denied due to unsafe state.")

    def display_current_state(self):
        self.hospital.display_current_state()

if __name__ == "__main__":
    root = tk.Tk()
    app = HospitalResourceManagerApp(root)
    root.mainloop()
