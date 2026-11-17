import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

DB_NAME = "students.db"


def initialize_database():
    """Create the students table if it does not already exist."""
    with sqlite3.connect(DB_NAME) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                course TEXT
            )
        """)


class StudentTrackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Tracking")
        self.root.geometry("950x560")
        self.root.minsize(780, 450)

        self.fields = {}
        self.build_interface()
        self.load_students()

    def build_interface(self):
        title = ttk.Label(
            self.root, text="Student Tracking",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=(15, 10))

        form = ttk.LabelFrame(self.root, text="Student Information", padding=12)
        form.pack(fill="x", padx=18, pady=8)

        field_names = [
            ("First name", "first_name"),
            ("Last name", "last_name"),
            ("Phone number", "phone"),
            ("Email", "email"),
            ("Current course", "course"),
        ]

        for index, (label_text, key) in enumerate(field_names):
            row, column = divmod(index, 2)
            ttk.Label(form, text=label_text + ":").grid(
                row=row, column=column * 2, sticky="w", padx=(5, 8), pady=7
            )
            entry = ttk.Entry(form, width=32)
            entry.grid(row=row, column=column * 2 + 1, sticky="ew", padx=(0, 15), pady=7)
            self.fields[key] = entry

        form.columnconfigure(1, weight=1)
        form.columnconfigure(3, weight=1)

        ttk.Button(form, text="Submit", command=self.add_student).grid(
            row=2, column=3, sticky="e", padx=5, pady=(8, 2)
        )

        listing = ttk.LabelFrame(self.root, text="Student List", padding=10)
        listing.pack(fill="both", expand=True, padx=18, pady=(8, 18))

        columns = ("first_name", "last_name", "phone", "email", "course")
        self.tree = ttk.Treeview(listing, columns=columns, show="headings", selectmode="extended")

        headings = {
            "first_name": "First name",
            "last_name": "Last name",
            "phone": "Phone number",
            "email": "Email",
            "course": "Current course",
        }
        widths = {"first_name": 120, "last_name": 120, "phone": 130, "email": 190, "course": 170}

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], minwidth=85)

        scrollbar = ttk.Scrollbar(listing, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        ttk.Button(
            listing, text="Delete selected student(s)", command=self.delete_students
        ).pack(anchor="e", pady=(10, 0))

    def add_student(self):
        values = {key: entry.get().strip() for key, entry in self.fields.items()}

        if not values["first_name"] or not values["last_name"]:
            messagebox.showwarning(
                "Missing information", "Please enter at least a first name and last name."
            )
            return

        with sqlite3.connect(DB_NAME) as connection:
            connection.execute("""
                INSERT INTO students (first_name, last_name, phone, email, course)
                VALUES (?, ?, ?, ?, ?)
            """, (
                values["first_name"], values["last_name"], values["phone"],
                values["email"], values["course"]
            ))

        for entry in self.fields.values():
            entry.delete(0, tk.END)

        self.load_students()
        messagebox.showinfo("Student added", "The student was saved successfully.")

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        with sqlite3.connect(DB_NAME) as connection:
            rows = connection.execute("""
                SELECT id, first_name, last_name, phone, email, course
                FROM students ORDER BY last_name, first_name
            """).fetchall()

        for student_id, first_name, last_name, phone, email, course in rows:
            self.tree.insert(
                "", tk.END, iid=str(student_id),
                values=(first_name, last_name, phone, email, course)
            )

    def delete_students(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select one or more students to delete.")
            return

        confirmed = messagebox.askyesno(
            "Confirm deletion",
            f"Delete {len(selected)} selected student(s)? This cannot be undone."
        )
        if not confirmed:
            return

        with sqlite3.connect(DB_NAME) as connection:
            connection.executemany(
                "DELETE FROM students WHERE id = ?",
                [(student_id,) for student_id in selected]
            )

        self.load_students()


if __name__ == "__main__":
    initialize_database()
    root = tk.Tk()
    app = StudentTrackingApp(root)
    root.mainloop()
