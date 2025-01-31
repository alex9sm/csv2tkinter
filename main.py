import tkinter as tk
from pathlib import Path
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd

class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Viewer")
        self.main_frame = tk.Frame(self)
        self.main_frame.pack(fill="both", expand="true")
        self.geometry("1400x800")
        self.search_page = SearchPage(parent=self.main_frame)
        
class DataTable(ttk.Treeview):
    def __init__(self, parent):
        super().__init__(parent)
        scroll_Y = tk.Scrollbar(self, orient="vertical", command=self.yview)
        scroll_X = tk.Scrollbar(self, orient="horizontal", command=self.xview)
        self.configure(yscrollcommand=scroll_Y.set, xscrollcommand=scroll_X.set)
        scroll_Y.pack(side="right", fill="y")
        scroll_X.pack(side="bottom", fill="x")
        self.stored_dataframe = pd.DataFrame()
        
        
    def set_datatable(self, dataframe):
        self.stored_dataframe = dataframe
        self._draw_table(dataframe)
    
    def _draw_table(self, dataframe):
        self.delete(*self.get_children())
        columns = list(dataframe.columns)
        self.__setitem__("column", columns)
        self.__setitem__("show", "headings")
        
        for col in columns:
            self.heading(col, text=col)
            
        rows = dataframe.to_numpy().tolist()
        for row in rows:
            self.insert("", "end", values=row)
        return None
    
    def reset_table(self):
        self._draw_table(self.stored_dataframe)
        
    def find_value(self, pairs):
        new_df = self.stored_dataframe
        for col, value in pairs.items():
            query_string = f"{col}.str.contains('{value}')"
            new_df = new_df.query(query_string, engine="python")
        self._draw_table(new_df)
        
class SearchPage(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.files_listbox = tk.Listbox(parent, selectmode=tk.SINGLE, background="darkgray")
        self.files_listbox.place(relheight=1, relwidth=0.25)
        self.files_listbox.drop_target_register(DND_FILES)
        self.files_listbox.dnd_bind("<<Drop>>", self.drop_file)
        self.files_listbox.bind("<Double-1>", self._display_file)
        
        self.search_entrybox = tk.Entry(parent)
        self.search_entrybox.place(relx=0.25, relwidth=0.75)
        self.search_entrybox.bind("<Return>", self.search_table)
        
        self.data_table = DataTable(parent)
        self.data_table.place(rely=0.05, relx=0.25, relwidth=0.75, relheight=0.95)
        
        self.path_map = {}
        
    def drop_file(self, event):
        file_paths = self._parse_files(event.data)
        current_listbox_items = set(self.files_listbox.get(0, "end"))
        for file_path in file_paths:
            if file_path.endswith(".csv"):
                path_object = Path(file_path)
                file_name = path_object.name
                if file_name not in current_listbox_items:
                    self.files_listbox.insert("end", file_name)
                    self.path_map[file_name] = file_path
    
    def _display_file(self, event):
        file_name = self.files_listbox.get(self.files_listbox.curselection())
        path = self.path_map[file_name]
        df = pd.read_csv(path)
        self.data_table.set_datatable(dataframe=df)
        
    def _parse_files(self, filename):
        size = len(filename)
        filepaths = []
        name = ""
        index = 0
        while index<size:
            if filename[index] == "{":
                i = index + 1
                while filename[i] != "}":
                    name+= filename[i]
                    i+=1
                filepaths.append(name)
                name=""
                index = i
            elif filename[index]== " " and name != "":
                filepaths.append(name)
                name = ""
            elif filename[index] != " ":
                name += filename[index]
            index += 1
        if name != "":
            filepaths.append(name)
        return filepaths
        
    def search_table(self, event):
        entry = self.search_entrybox.get()
        if entry == "":
            self.data_table.reset_table()
        else:
            # convert all columns to string type for easy searching
            df = self.data_table.stored_dataframe.astype(str)
            mask = df.apply(lambda x: x.str.contains(entry, case=False, na=False)).any(axis=1)
            filtered_df = self.data_table.stored_dataframe[mask]
            self.data_table._draw_table(filtered_df)
            
        
        
if __name__ == "__main__":
    root = App()
    root.mainloop()