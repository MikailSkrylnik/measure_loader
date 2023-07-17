import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import json
import zipfile
import snowflake.connector


# Place for bind params
# --------

# --------

class MeasureLoaderApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Measure Loader")

        # Create main frame
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Header - Selected file button
        self.selected_file = tk.StringVar()
        self.selected_file.set("Select file")

        self.file_name = ""

        self.file_button = tk.Button(self.main_frame, textvariable=self.selected_file, command=self.load_file)
        self.file_button.pack(pady=10, fill=tk.X)

        # Middle - Measure details table
        self.measure_table_frame = ttk.Frame(self.main_frame)
        self.measure_table_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.style = ttk.Style()
        self.style.map("Treeview",
                       foreground=self.fixed_map("foreground"),
                       background=self.fixed_map("background"))

        self.measures = []

        self.measure_treeview = ttk.Treeview(self.measure_table_frame, selectmode="none")
        self.measure_treeview.pack(side="left", fill=tk.BOTH, expand=True)

        self.measure_treeview["columns"] = ("name", "expression", "description", "load")

        self.measure_treeview.column("#0", width=0, stretch=tk.NO)
        self.measure_treeview.column("name", width=150)
        self.measure_treeview.column("expression", width=300)
        self.measure_treeview.column("description", width=300)
        self.measure_treeview.column("load", width=50, anchor="center")

        self.measure_treeview.heading("#0", text="")
        self.measure_treeview.heading("name", text="Name")
        self.measure_treeview.heading("expression", text="Expression")
        self.measure_treeview.heading("description", text="Description")
        self.measure_treeview.heading("load", text="Load")

        self.measure_scrollbar = ttk.Scrollbar(self.measure_table_frame, orient="vertical",
                                               command=self.measure_treeview.yview)
        self.measure_scrollbar.pack(side="right", fill="y")

        self.measure_treeview.configure(yscrollcommand=self.measure_scrollbar.set)

        self.measure_treeview.tag_configure("load_True_even", background="darkolivegreen3")
        self.measure_treeview.tag_configure("load_False_even", background="snow2")
        self.measure_treeview.tag_configure("load_True_odd", background="darkolivegreen1")
        self.measure_treeview.tag_configure("load_False_odd", background="white")

        self.log_text = tk.Text(self.main_frame, height=5, width=50)
        self.log_text.pack(pady=10, fill=tk.BOTH, expand=True)

        self.load_button = tk.Button(self.main_frame, text="Load to Snowflake", command=self.load_to_snowflake)
        self.load_button.pack(pady=10, fill=tk.X)

        # Configure grid weights for resizing
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)

        self.measure_treeview.bind("<ButtonRelease-1>", self.toggle_load)
        self.measure_treeview.bind("<Double-Button-1>", self.edit_cell_content)

    # Row color solution by: https://stackoverflow.com/a/60949800
    def fixed_map(self, option):
        # Returns the style map for 'option' with any styles starting with
        # ("!disabled", "!selected", ...) filtered out

        # style.map() returns an empty list for missing options, so this should
        # be future-safe
        return [elm for elm in self.style.map("Treeview", query_opt=option)
                if elm[:2] != ("!disabled", "!selected")]

    def update_row_colors(self):
        for index, item in enumerate(self.measure_treeview.get_children()):
            values = self.measure_treeview.item(item)['values']
            if values:
                load_value = values[-1]
                if index % 2 == 0:
                    self.measure_treeview.item(item, tags=("load_" + load_value + "_even",))
                else:
                    self.measure_treeview.item(item, tags=("load_" + load_value + "_odd",))

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("PowerBI Template Files", "*.pbit")])
        self.file_name = os.path.splitext(os.path.basename(file_path))[0]
        if file_path:
            self.selected_file.set(file_path)
            self.load_measures_from_file(file_path)

    def load_measures_from_file(self, file_path):
        # Extract measures from the DataModelSchema file in the .pbit archive
        with zipfile.ZipFile(file_path, 'r') as archive:
            try:
                data_model_schema = archive.read("DataModelSchema")
                self.measures = self.extract_measures_from_data_model_schema(data_model_schema)
                self.display_measures()
            except KeyError:
                # DataModelSchema file not found in the .pbit archive
                messagebox.showerror("Error", "DataModelSchema file not found in the .pbit archive.")

    def extract_measures_from_data_model_schema(self, data_model_schema):
        # Convert the string to a Python data structure
        try:
            data = json.loads(data_model_schema)
        except json.JSONDecodeError:
            # If there's an error, try removing non-printable characters from the string
            clean_data = ''.join(char for char in data_model_schema if char.isprintable())
            data = json.loads(clean_data)

        tables = data['model']['tables']
        measures = []

        for table in tables:
            if 'measures' in table:
                for measure in table['measures']:
                    measure_name = measure['name']
                    if isinstance(measure['expression'], list):
                        measure['expression'] = "".join(measure['expression']).strip()
                    measure_expression = measure['expression']
                    try:
                        measure_description = measure['description']
                    except KeyError:
                        measure_description = ""
                    measures.append({
                        'name': measure_name,
                        'expression': measure_expression,
                        'description': measure_description
                    })

        return measures

    def toggle_load(self, event):
        column = self.measure_treeview.identify_column(event.x)  # Identify the column clicked
        if column == "#4":  # Check if the clicked column is the "Load" column
            item = self.measure_treeview.focus()
            item_index = self.measure_treeview.index(item)
            values = self.measure_treeview.item(item)['values']
            if values:
                load_value = values[-1]
                if load_value == "True":
                    new_value = "False"
                else:
                    new_value = "True"
                self.measure_treeview.set(item, "load", new_value)
                self.measures[item_index]['load'] = new_value
                self.update_row_colors()  # Update the row color

    def edit_cell_content(self, event):
        column = self.measure_treeview.identify_column(event.x)  # Identify the column clicked
        if column in ("#2", "#3"):  # Check if the clicked column is either "Expression" or "Description"
            item = self.measure_treeview.focus()
            cell_value = self.measure_treeview.set(item, column)  # Get the current cell value

            # Create a dialog frame with a multiline text box
            dialog = tk.Toplevel(self)
            dialog.title("Edit Cell Content")

            text_box = tk.Text(dialog, height=10, width=50)
            text_box.insert(tk.END, cell_value)
            text_box.pack(padx=10, pady=(10, 0), fill=tk.BOTH, expand=True)

            # Frame to hold the buttons
            button_frame = tk.Frame(dialog)
            button_frame.pack(pady=(0, 10))

            # Save button to update the cell value
            save_button = tk.Button(button_frame, text="Save",
                                    command=lambda: self.update_cell_value(dialog, item, column,
                                                                           text_box.get("1.0", tk.END)))
            save_button.pack(side=tk.LEFT, padx=5)

            # Cancel button to close the dialog without saving changes
            cancel_button = tk.Button(button_frame, text="Cancel", command=dialog.destroy)
            cancel_button.pack(side=tk.LEFT, padx=5)

    def update_cell_value(self, dialog, item, column, new_value):
        self.measure_treeview.set(item, column, new_value)
        item_index = self.measure_treeview.index(item)
        if column == "#2":
            self.measures[item_index]['expression'] = new_value
        elif column == "#3":
            self.measures[item_index]['description'] = new_value
        dialog.destroy()

    def display_measures(self):
        # Clear existing measure rows
        self.measure_treeview.delete(*self.measure_treeview.get_children())

        # Display measure rows
        for index, measure in enumerate(self.measures):
            name = measure['name']
            expression = measure['expression']
            description = measure['description']
            measure['load'] = "True" if description else "False"
            load = measure['load']
            # Determine the background color based on whether the row index is odd or even
            if index % 2 == 0:
                state = "_even"
            else:
                state = "_odd"

            # Insert the measure row with the specified background color
            self.measure_treeview.insert("", tk.END, values=(name, expression, description, load),
                                         tags=("load_" + load + state,))

    def load_to_snowflake(self):
        selected_measures = [measure for measure in self.measures if measure['load'] == "True"]
        self.log_text.delete('1.0', tk.END)
        if len(selected_measures) > 0:
            self.insert_measures_into_snowflake(selected_measures)
        else:
            self.log_text.insert(tk.END, f"No rows to insert\n")

    def insert_measures_into_snowflake(self, measures):
        # Snowflake connection
        try:
            connection = snowflake.connector.connect(**snowflake_config)

            self.log_text.insert(tk.END, f"Snowflake connection established\n")

            connection.cursor().execute(
                "DELETE FROM " + snowflake_config["target_table"] + " WHERE RPT_NAM_DSC='" + self.file_name + "';")

            flag = True

            # Insert selected measures into Snowflake table
            for measure in measures:
                name = measure['name']
                expression = measure['expression']
                description = measure['description'] if measure['description'] != "" else "#"

                try:
                    # Execute SQL query to insert the measure
                    sql = "INSERT INTO " + snowflake_config["target_table"] \
                          + " (RPT_NAM_DSC, MEA_NAM_DSC, MEA_COD_TXT, MEA_CMT_TXT) VALUES (%s, %s, %s, %s)"
                    values = (self.file_name, name, expression, description)
                    # Execute the SQL statement
                    connection.cursor().execute(sql, values)
                    self.log_text.insert(tk.END, f"Inserted measure '{name}'\n")
                except Exception as e:
                    flag = False
                    self.log_text.insert(tk.END, f"Error inserting measure '{name}': {str(e)}\n")

            if flag:
                self.log_text.insert(tk.END, f"All selected measures have been loaded\n")
            else:
                self.log_text.insert(tk.END, f"Errors occurred while loading measures\n")

            # Commit the changes and close the connection
            connection.commit()
            connection.close()

        except snowflake.connector.errors.ProgrammingError:
            self.log_text.insert(tk.END, f"Invalid credentials or .env file\n")
        except snowflake.connector.errors.DatabaseError as e:
            self.log_text.insert(tk.END, f"{str(e)}\n")


if __name__ == '__main__':
    app = MeasureLoaderApp()
    app.mainloop()
