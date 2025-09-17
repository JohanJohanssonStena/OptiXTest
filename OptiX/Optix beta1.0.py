import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as tkFont
import numpy as np
import pandas as pd
import os
import re
import shutil
from scipy.optimize import linprog
from scipy.linalg import block_diag
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.stats import norm
from datetime import datetime

def main():
    app = Application()
    app.mainloop()

#Huvudapplikation, förskapar alla fönster och tar hand om byte mellan 
class Application(tk.Tk): 
    def __init__(self):
        super().__init__()
        self.title('OptiX')
        self.geometry("1024x720")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.page1 = Window1(self.container, self)
        self.page2 = Window2(self.container, self)
        self.page3 = Window3(self.container, self)

        self.page1.place(relwidth=1, relheight=1)
        self.page2.place(relwidth=1, relheight=1)
        self.page3.place(relwidth=1, relheight=1)

        self.show_page(self.page1)

    def show_page(self,page):
        page.tkraise()

class Window1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1, uniform='group1')
        self.rowconfigure(1, weight=1, uniform='group1')
        self.rowconfigure(2, weight=1, uniform='group1')

        frame_choosefile1 = FileLoader(self, controller, df_key='df1', label_text='Lager')
        frame_choosefile1.grid(row=0, column=0)

        frame_choosefile2 = FileLoader(self, controller, df_key='df2', label_text='Styrplaner')
        frame_choosefile2.grid(row=1, column=0)

        frame_choosefile3 = FileLoader(self, controller, df_key='df3', label_text='Provugnsprotokoll (valfritt)')
        frame_choosefile3.grid(row=2, column=0)

        frame_listbox1 = InputForm(self, controller, 'frame1')
        frame_listbox1.grid(row=0, column=1, sticky='nsew', rowspan=2)

        frame_listbox2 = InputForm(self, controller, 'frame2')
        frame_listbox2.grid(row=0, column=2, sticky='nsew', rowspan=2)

        frame_checkboxsimulation = CheckBoxSimulation(self, controller)
        frame_checkboxsimulation.grid(row=2, column=2, sticky='se')

        frame_start = Start(self, controller, rec_key='rec_', mode='start')
        frame_start.grid(row=2, column=1)

        controller.text_list1 = frame_listbox1.text_list
        controller.text_list2 = frame_listbox2.text_list

        controller.df1 = frame_choosefile1.df
        controller.df2 = frame_choosefile2.df
        controller.df3 = frame_choosefile3.df

        controller.rec_ = frame_start.rec_

class InputForm(tk.Frame):
    def __init__(self, parent, controller, mode):
        super().__init__(parent)
        self.controller = controller
        self.mode = mode
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self.entry = tk.Entry(self, font=tkFont.Font(size=12))
        self.entry.grid(row=0, column=0, pady=(25, 0), padx=(5, 0), sticky='ew')

        self.entry.bind('<Return>', self.add_to_list)

        self.entry_btn = tk.Button(self, text='Add', font=tkFont.Font(size=12), command=self.add_to_list)
        self.entry_btn.grid(row=0, column=1, pady=(25, 0))

        self.entry_btn2 = tk.Button(self, text='Clear', font=tkFont.Font(size=12), command=self.clear_list)
        self.entry_btn2.grid(row=0, column=2, pady=(25, 0), padx=(0, 5))

        self.text_list = tk.Listbox(self, font=tkFont.Font(size=12))
        self.text_list.grid(row=1, column=0, columnspan=3, pady=(0, 80), padx=5, sticky='nsew')

        self.valid_second_words = ['MIN', 'MAX', 'COST0', '=', 'ALLOW'] #godkända funktioner, skrivs i caps

        self.controller.set_styrplaner = []
        self.controller.artiklar = []

        self.controller.lr_dict = {}
    def validate_input(self):

        def is_float(value: str) -> bool:
            # Byt ut komma till punkt för enhetlig hantering
            normalized = value.replace(',', '.')
            
            # Kontrollera att det är ett positivt heltal eller decimaltal med max en punkt
            pattern = r'^(0|[1-9]\d*)(\.\d+)?$'
            
            return bool(re.match(pattern, normalized))

        elem = ['Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Ni', 'Zn', 'Ti', 'Pb', 'Sn', 'Cr', 'Na', 'Sr','Sb', 'P', 'Bi', 'Ca', 'Cd', 'Zr', 'Be', 'B', 'Li', 'Al', 'Hg']
        elem = [e.upper() for e in elem]
        if self.mode == 'frame2' or self.mode == 'frame3':
            parts = self.text.strip().split()
            if len(parts) < 2 or len(parts) > 3:
                return False

            first = parts[0].upper()
            second = parts[1].upper()
            value = parts[2] if len(parts) == 3 else ''

            if self.mode == 'frame3' and first in elem and is_float(second):
                return True

            if first not in self.controller.artiklar:
                return False

            if second not in self.valid_second_words:
                return False

            rule = second
            if rule == 'MAX' or rule == 'MIN' or rule == '=':
                return value.isdigit()
            elif rule == 'COST0':
                return len(parts) == 2
            elif self.mode == 'frame3' and rule == 'ALLOW':
                return len(parts) == 2

        if self.mode == 'frame1':
            if self.text in self.controller.set_styrplaner:
                return True
            else:
                return False
            
    def local_rules(self):
        if self.mode == 'frame3':
            if self.controller.index not in self.controller.lr_dict:
                self.controller.lr_dict[self.controller.index] = [self.text]
            else:
                self.controller.lr_dict[self.controller.index].append(self.text)

    def add_to_list(self, _event=None):
        self.text = self.entry.get()
        if self.validate_input():
            self.text_list.insert(tk.END, self.text)
            self.entry.delete(0, tk.END)
            self.local_rules()
            
    def clear_list(self):
        selected = self.text_list.curselection()
        if selected:
            self.text_list.delete(selected[0])
            if self.mode == 'frame3':
                self.controller.lr_dict[self.controller.index].remove(self.controller.lr_dict[self.controller.index][selected[0]])

class FileLoader(tk.Frame):
    def __init__(self, parent, controller, df_key, label_text):
        super().__init__(parent)
        self.controller = controller
        self.df_key = df_key
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight=1)
        self.frame = tk.LabelFrame(self, text=label_text, labelanchor='n', font=tkFont.Font(size=12))
        self.frame.grid(row=0, column=0, sticky='ew')
        
        self.choose_btn = tk.Button(self.frame, text='Choose file', anchor='center',command=self.choose_file, font=tkFont.Font(size=12))
        self.choose_btn.grid(row=1,column=0, pady=(10,5), padx=65)

        self.file_name_label = tk.Label(self.frame, text="No file selected", anchor='center')
        self.file_name_label.grid(row=2, column=0, sticky='ew')
        self.df = pd.DataFrame()

    def choose_file(self, _event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")], title="Choose an Excel file")

        if file_path:
            error_message = True
            try:
                self.df = pd.read_excel(file_path)
            except PermissionError:
                messagebox.showerror("Permission Denied", "The file is open in another program or you don't have permission to access it.")
                error_message = False

            setattr(self.controller, self.df_key, self.df)
            if self.validate_file():
                self.file_name = os.path.basename(file_path)
                self.file_name_label.config(text=self.file_name)

                if self.df_key == 'df1' and self.df.columns[:3].tolist() == ['Part No', 'Part Description', 'Estimated Material Cost']:
                    artiklar = self.df['Part No'].tolist()
                    self.controller.artiklar = list(set(artiklar    ))

                if self.df_key == 'df2' and self.df.columns[:3].tolist() == ['Part No', 'Mearsurement Spec', 'Si']:
                    styrplaner = self.df['Part No'].tolist()
                    self.controller.set_styrplaner = styrplaner[0:len(styrplaner):  6]

                if self.df.columns[:5].tolist() == ['Leverantör', 'Inköpt råvara', 'Klassad råvara', 'Klassad variant', 'Provdatum']:
                    appdata_local = os.getenv('LOCALAPPDATA')
                    folder1 = 'OptiX'
                    folder2 = 'Data'
                    folder3 = 'Provugn'
                    full_path = os.path.join(appdata_local, folder1, folder2, folder3)
                    file = os.listdir(full_path)
                    full_path = os.path.join(appdata_local, folder1, folder2, folder3, file[0])
                    shutil.copy2(file_path, full_path)
            elif error_message:
                messagebox.showerror('Error', 'Wrong File')

            
    def validate_file(self):
        if self.df_key == 'df1' and self.df.columns[:3].tolist() == ['Part No', 'Part Description', 'Estimated Material Cost']:
            return True
        elif self.df_key == 'df2' and self.df.columns[:3].tolist() == ['Part No', 'Mearsurement Spec', 'Si']:
            return True
        elif self.df_key == 'df3' and self.df.columns[:5].tolist() == ['Leverantör', 'Inköpt råvara', 'Klassad råvara', 'Klassad variant', 'Provdatum']:
            return True
        else:
            return False
class CheckBoxSimulation(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.checkbox_var = tk.BooleanVar()
        checkbox = tk.Checkbutton(self, text="Simulation", variable=self.controller.checkbox_var, font=tkFont.Font(size=12))
        checkbox.grid(row=0, column=0, padx=20, pady=20, sticky='se')

class Start(tk.Frame):
    def __init__(self, parent, controller, rec_key, mode):
        super().__init__(parent)
        self.controller = controller
        self.rec_key = rec_key
        self.mode = mode
        self.first_run = True
        self.columnconfigure(0, weight = 1)
        self.rowconfigure(0, weight=1)
        if self.mode == 'start':
            self.start_button = tk.Button(self, width=20, height=4, bg='green', text='Start', font=tkFont.Font(size=16), command=self.start_combined)
            self.start_button.grid(row=0, column=0)
        if self.mode == 'remake':
            self.remake_button = tk.Button(self, width=20, height=4, bg='green', text='Återskapa', font=tkFont.Font(size=14), command=self.start_combined)
            self.remake_button.grid(row=0, column=0, padx=5, pady=5, sticky='ne')
        self.rec_ = {'artnum':np.empty((0,)), 'amount':np.empty((0,))}

    def read_control_plan(self, _event=None):
        df = self.controller.df2 #läsa in styrplan
        r = 0.5

        elem = ['Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Ni', 'Zn', 'Ti', 'Pb', 'Sn', 'Cr', 'Na', 'Sr','Sb', 'P', 'Bi', 'Ca', 'Cd', 'Zr', 'Be', 'B', 'Li', 'Al', 'Hg']

        sales_article = np.array(df['Part No'].tolist())
        set_sales_article = sales_article[0:len(sales_article):6]

        all_tolerance=np.empty((len(sales_article),0))
        for i in elem:
            temp_list = np.array(df[i].tolist())
            temp_list = temp_list[:, np.newaxis]
            all_tolerance = np.hstack((all_tolerance, temp_list))

        outer_min = all_tolerance[0:len(sales_article):6]
        outer_max = all_tolerance[1:len(sales_article):6]
        inner_min = all_tolerance[2:len(sales_article):6]
        inner_max = all_tolerance[3:len(sales_article):6]
        dec_min = all_tolerance[4:len(sales_article):6]
        dec_max = all_tolerance[5:len(sales_article):6]
        dec_min[np.isnan(dec_min)] = 0
        tol_min = outer_min.copy()
        tol_min[~np.isnan(inner_min)] = inner_min[~np.isnan(inner_min)]
        tol_min = tol_min - r * np.power(10, dec_min*(-1))
        dec_max[np.isnan(dec_max)] = 0
        tol_max = outer_max.copy()
        tol_max[~np.isnan(inner_max)] = inner_max[~np.isnan(inner_max)]
        tol_max = tol_max + r * np.power(10, (dec_max-1)*(-1))

        outer_min = outer_min - r * np.power(10, (dec_max-1)*(-1))
        outer_max = outer_max + r * np.power(10, (dec_max-1)*(-1))

        tol_max[tol_max > 100] = 100
        tol_min[tol_min < 0] = 0

        outer_max[outer_max > 100] = 100
        outer_min[outer_min < 0] = 0
        
        tol_max = np.squeeze(tol_max)
        tol_min = np.squeeze(tol_min)
        recipe_list = self.controller.text_list1.get(0, tk.END)
        temp_min = []
        temp_max = []
        temp_omin = []
        temp_omax = []
        for i in recipe_list:
            p = np.where(i == set_sales_article)[0][0]
            temp_min.append(tol_min[p])
            temp_max.append(tol_max[p])
            temp_omin.append(outer_min[p])
            temp_omax.append(outer_max[p])

        for i in range(len(tol_max)):
            tol_max[i][4] += 1
        
        weight_in = [35000 for _ in range(len(self.controller.text_list1.get(0, tk.END)))]
        weight_out = [28500 for _ in range(len(self.controller.text_list1.get(0, tk.END)))]

        self.controller.cp_dict = {'outer_min': temp_omin, 'outer_max': temp_omax, 'tol_min': temp_min, 'tol_max': temp_max, 'elem': elem, 'weight_in': weight_in, 'weight_out': weight_out}

        self.tol_max = temp_max
        self.tol_min = temp_min       
        self.set_sales_article = set_sales_article
    def read_testing(self, _event=None):
        # skapar list från excelfil
        df = self.controller.df3

        if df.equals(pd.DataFrame()):

            appdata_local = os.getenv('LOCALAPPDATA')
            folder1 = 'OptiX'
            folder2 = 'Data'
            folder3 = 'Provugn'
            full_path = os.path.join(appdata_local, folder1, folder2, folder3)
            file = os.listdir(full_path)
            full_path = os.path.join(appdata_local, folder1, folder2, folder3, file[0])
            df = pd.read_excel(full_path)

        ikr = np.array(df['Inköpt råvara'].tolist())
        klr = np.array(df['Klassad råvara'].tolist())
        obv = np.array(df['Anmärkning'].tolist())
        #tar de n senaste proverna
        n = 5000
        obv = np.delete(obv, range(n, len(ikr)))
        ikr = np.delete(ikr, range(n, len(ikr)))
        klr = np.delete(klr, range(n, len(klr)))
        #bytar inköpt råvara till klassad råvara
        klr[klr == '-'] = 'nan'
        ikr[klr != 'nan'] = klr[klr != 'nan']
        #alla ämnen
        elem = ['Si%', 'Fe%', 'Cu%', 'Mn%', 'Mg%', 'Ni%', 'Zn%', 'Ti%', 'Pb%', 'Sn%', 'Cr%', 'Na%', 'Sr%','Sb%', 'P%', 'Bi%', 'Ca%', 'Cd%', 'Zr%', 'Be%', 'B%', 'Li%', 'Al%', 'Hg%']

        all_tests=np.empty((n,0))
        for i in elem:
            temp_list = np.array(df[i].tolist())
            temp_list = np.delete(temp_list, range(n, len(temp_list)))
            temp_list = temp_list[:, np.newaxis]
            all_tests = np.hstack((all_tests, temp_list))

        #filtrering av dokumenet, toma tester, tar bort P, sätter in uträknat Hg och Al värde
        p = np.where(all_tests[:,0] == '-')
        all_tests = np.delete(all_tests, p, axis=0)
        ikr = np.delete(ikr, p)
        klr = np.delete(klr, p)
        obv = np.delete(obv, p)

        pattern = re.compile(r'^\d{3}[Pp]?$')
        p = [i for i, val in enumerate(ikr) if not pattern.match(val)]
        all_tests = np.delete(all_tests, p, axis=0)
        ikr = np.delete(ikr, p)
        klr = np.delete(klr, p)
        obv = np.delete(obv, p)

        ikr = np.char.replace(ikr, 'P', '')
        ikr = np.char.replace(ikr, 'p', '')
        set_artnum = np.array(list(set(ikr)))
        artnum = ikr

        flame = artnum[obv == 'Mycket brand3']
        flame = np.array(list(set(flame)))

        all_tests[:,23][all_tests[:,23] == '-'] = 0
        p = np.where(all_tests[:,22] == '-')
        all_tests[p,22] = 100-np.sum(np.squeeze((all_tests[p,0:22].astype(np.float64))),axis=1)
        all_tests = all_tests.astype(np.float64)
        #färdig filtrerat
        #beräkning på medelvärde och standardavvikelse
        imp_elem = [1, 2, 6]
        imp_tests = all_tests[:, imp_elem]
        mean_c = np.mean(imp_tests, axis=0)
        imp_tests = imp_tests / mean_c.reshape(1, -1)

        imp_tests = np.power(np.sum(np.power(imp_tests, 2), axis=1), 1/2)
        set_std = np.empty(0)
        set_mean = np.empty(0)
        for i in set_artnum:
            p = np.where(i == artnum)
            set_std = np.hstack((set_std, np.std(imp_tests[p])))
            set_mean = np.hstack((set_mean, np.mean(imp_tests[p])))
        #kontrollerar vilka värden som är utanför toleransen och tar bort dessa

        amount_test = np.empty(0)
        for i in set_artnum:
            amount_test = np.hstack((amount_test, len(np.where(i == artnum)[0])))


        std_multiplier = 1.645 #1.645 tar bort de sämsta 10 % av mätningarna
        p2 = np.empty(0)
        for i in range(0,len(set_artnum)):
            p = (np.where(set_artnum[i] == artnum))[0]
            for j in p:
                if (imp_tests[j] > set_mean[i]+set_std[i]*std_multiplier or imp_tests[j] < set_mean[i]-set_std[i]*std_multiplier) and amount_test[i] > 3:
                    p2 = np.hstack((p2, j))

        p2 = p2.astype(np.int32)
        all_tests = np.delete(all_tests, p2, axis=0)
        artnum = np.delete(artnum, p2)
        #räknar ut medelvärdet med utan de dåliga testerna
        set_mean_final = np.empty((0,24))
        for i in set_artnum:
            p = np.where(i == artnum)[0]
            set_mean_final = np.vstack((set_mean_final, np.mean(all_tests[p,:], axis=0)))

        
        #manuellt dokument
        appdata_local = os.getenv('LOCALAPPDATA')
        folder1 = 'OptiX'
        folder2 = 'Data'
        file = 'Saknade analyser.xlsx'
        full_path = os.path.join(appdata_local, folder1, folder2, file)
        manual_df = pd.read_excel(full_path)
        manual_artnum = np.array(manual_df['Klassad råvara'].tolist())

        #tar bort dubbletter, prioriterar manuella listan 
        mask = ~np.isin(set_artnum, manual_artnum)
        set_mean_final = set_mean_final[mask, :]
        set_artnum = set_artnum[mask]
        

        manual_tests = np.empty((len(manual_artnum),0))
        for i in elem:
            temp_list = np.array(manual_df[i].tolist())
            temp_list = temp_list[:, np.newaxis]
            manual_tests = np.hstack((manual_tests, temp_list))

        p = np.isnan(manual_tests[:, 0])
        manual_tests = manual_tests[~p]
        manual_artnum = manual_artnum[~p]

        p = np.isnan(manual_tests[:,22])

        manual_tests[np.isnan(manual_tests)] = 0

        manual_tests[p,22] = 100-np.sum(np.squeeze((manual_tests[p,0:22].astype(np.float64))),axis=1)
        manual_tests = manual_tests.astype(np.float64)

        #slår ihop båda.

        set_mean_final = np.vstack((set_mean_final, manual_tests))
        set_artnum = np.hstack((set_artnum, manual_artnum))
        set_artnum_p = set_artnum.copy()

        # Läser in åalistan
        def aa_list():
            appdata_local = os.getenv('LOCALAPPDATA')
            folder1 = 'OptiX'
            folder2 = 'Data'
            file = 'AALISTAN.csv'
            full_path = os.path.join(appdata_local, folder1, folder2, file)

            aa_df = pd.read_csv(full_path, encoding="latin1", sep=";")
            aa_df.columns = aa_df.iloc[0]
            aa_df = aa_df.iloc[1:].reset_index(drop=True)

            all_artnum = np.array(aa_df['Artikelnummer'].tolist())
            all_artnum = all_artnum[all_artnum != '0']
        
        aa_df = self.controller.df1
        all_artnum = np.array(list(set(aa_df['Part No'].tolist())))

        #Sätter ett P bakom de artikelnummer som ska ha ett
        p_list = np.empty(0, dtype=int)
        for i in all_artnum:
            p = np.where(i + 'P' == all_artnum)[0]
            if len(p) > 0:
                p_list = np.hstack((p_list, p))
        list_ = np.char.replace(all_artnum[p_list], 'P','')
        for i in range(0,len(list_)):
            p = np.where(list_[i] == set_artnum_p)[0]
            if len(p) > 0:
                set_artnum_p[p] = all_artnum[p_list][i]

        self.set_artnum_p = set_artnum_p
        self.set_mean_final = set_mean_final
        self.set_artnum = set_artnum
        self.controller.testing_dict = {'set_artnum_p': set_artnum_p, 'set_mean_final': set_mean_final, 'set_artnum': set_artnum}

        #ta fram standard deviation
        all_test_std = np.empty((0, 24))
        for i in set_artnum:
            p = np.where(i == artnum)[0]
            if len(p) > 0:
                all_test_std = np.vstack((all_test_std, np.std(all_tests[p, :], axis=0)))
        col_mean = np.mean(all_test_std, axis=0) * 1.5
        a = all_test_std.shape[0]
        for i in range(a, len(set_artnum_p)):
            all_test_std = np.vstack((all_test_std, col_mean))

        for i in range(all_test_std.shape[0]):
            if np.all(all_test_std[i,:] == 0):
                all_test_std[i,:] = col_mean

        for i, value in enumerate(set_artnum.astype(float)):
            if value >= 800:
                all_test_std[i,:] = 0
        self.controller.all_test_std = all_test_std
    def read_rules(self, _event=None):
        appdata_local = os.getenv('LOCALAPPDATA')
        folder1 = 'OptiX'
        folder2 = 'Data'
        file = 'Regler.xlsx'
        full_path = os.path.join(appdata_local, folder1, folder2, file)

        df = pd.read_excel(full_path)
        col_names = df.columns
        amount = df.iloc[0].tolist()
        df = df.iloc[1:].reset_index(drop=True)

        A_add_on = np.empty((0,len(self.set_artnum_p)))
        for i in col_names:
            A_add = np.zeros((1, len(self.set_artnum_p)))[0]
            col = np.array(df[i].tolist())
            if col.dtype == np.dtype('float'):
                col = col[~np.isnan(col)]
                col = col.astype(int)
                col = col.astype(str)
            for j in col:
                A_add[j == self.set_artnum_p] = 1
            A_add_on = np.vstack((A_add_on, A_add))

        self.A_add_on = A_add_on
        self.b_add_on = amount
    def read_inventory(self, _event=None):
        df = self.controller.df1
        artnum = np.array(df['Part No'].tolist())
        cost = np.array(df['Estimated Material Cost'].tolist())
        exchange = np.array(df['Utbyte (Exchange)'].tolist())
        quantity = np.array(df['Available Qty'].tolist())
        spot = np.array(df['Warehouse'].tolist())
        exact_spot = np.array(df['Location No'].tolist())
        description = np.array(df['Part Description'].tolist())

        self.controller.boxes = {}

        p1 = np.where(spot == 'BOX')[0]
        
        artnum_box = artnum[p1]
        set_artnum_box = np.array(list(set(list(artnum_box))))
        quantity_box = quantity[p1]#*exchange[p1]

        for i, value in enumerate(set_artnum_box):
            p = np.where(value == artnum_box)[0]
            temp = quantity_box[p]
            self.controller.boxes[value] = temp[np.argsort(-temp)]

        set_artnum = np.array(list(set(list(artnum))))
        set_exchange = np.zeros(len(set_artnum))
        set_cost = np.zeros(len(set_artnum))
        set_description = np.full(len(set_artnum), '', dtype='U100')
        sum_quantity = np.zeros(len(set_artnum))
        if not self.controller.checkbox_var.get():
            for i in range(len(set_artnum)):
                p = np.where(set_artnum[i] == artnum)[0]
                p = np.delete(p, spot[p] == 'FLAK' )
                p = np.delete(p, spot[p] == 'nan' )
                p = np.delete(p, [i for i, val in enumerate(exact_spot[p]) if 'FLAK' in val])
                p = np.delete(p, [i for i, val in enumerate(exact_spot[p]) if 'VÅG' in val])

                # p = np.delete(p, spot[p] == 'PALL' )
                # p = np.delete(p, spot[p] == 'BOX' )
                if p.size > 0:
                    set_exchange[i] = exchange[p[0]]
                    set_cost[i] = cost[p[0]]
                    set_description[i] = description[p[0]]
                    sum_quantity[i] = np.sum(quantity[p])
            set_artnum = np.delete(set_artnum, sum_quantity==0)
            set_exchange = np.delete(set_exchange, sum_quantity==0)
            set_cost = np.delete(set_cost, sum_quantity==0)
            set_description = np.delete(set_description, sum_quantity==0)
            sum_quantity = np.delete(sum_quantity, sum_quantity==0)

            for value in list(self.controller.boxes.keys()): #lägger in resten av material i boxlager
                self.controller.boxes[f'{value}rest'] = sum_quantity[set_artnum == value]- np.sum(self.controller.boxes[value])
        else:
            for i in range(len(set_artnum)):
                p = np.where(set_artnum[i] == artnum)[0]
                p = np.delete(p, cost[p] == 0)
                if p.size > 0:
                    set_exchange[i] = exchange[p[0]]
                    set_cost[i] = cost[p[0]]
                    set_description[i] = description[p[0]]

            set_artnum = np.delete(set_artnum, set_exchange==0)
            set_cost = np.delete(set_cost, set_exchange==0)
            set_description = np.delete(set_description, set_exchange==0)
            set_exchange = np.delete(set_exchange, set_exchange==0)
            sum_quantity = np.full(len(set_artnum), 1e10)
            
        self.set_artnum_inventory = set_artnum
        self.set_exchange = set_exchange
        self.set_cost = set_cost
        self.set_description = set_description
        self.sum_quantity = sum_quantity
    def compare(self, _event=None):
        shared_artnum = np.intersect1d(self.set_artnum_p, self.set_artnum_inventory)

        b1 = np.isin(self.set_artnum_p, shared_artnum)
        b2 = np.isin(self.set_artnum_inventory, shared_artnum)

        self.set_artnum_inventory = self.set_artnum_inventory[b2]
        self.set_exchange = self.set_exchange[b2]
        self.set_cost = self.set_cost [b2]
        self.set_description = self.set_description[b2]
        self.sum_quantity = self.sum_quantity[b2]

        self.set_artnum_p = self.set_artnum_p[b1]
        self.set_artnum = self.set_artnum[b1]

        sort_index = np.argsort([np.where(self.set_artnum_p == x)[0][0] for x in self.set_artnum_inventory]) #tar fram i vilken ordning det ska sorteras enligt set_artnum_p

        self.set_artnum_inventory = self.set_artnum_inventory[sort_index]
        self.set_exchange = self.set_exchange[sort_index]
        self.set_cost = self.set_cost[sort_index]
        self.set_description = self.set_description[sort_index]
        self.sum_quantity = self.sum_quantity[sort_index]

        self.set_cost = self.set_cost / self.set_exchange
        self.sum_quantity = self.sum_quantity * self.set_exchange

        self.set_mean_final = self.set_mean_final[b1, :]
        self.A_add_on = self.A_add_on[:, b1]
        self.controller.all_test_std = self.controller.all_test_std[b1, :]

    def prepare(self, _event=None):
        #fördimensionerar listor där data per recept sätts in i varje posistion i listan
        n = len(self.controller.text_list1.get(0, tk.END))
        A = [None] * n
        b = [None] * n
        f = [None] * n
        Aeq = [None] * n
        beq = [None] * n
        bound = [None] * n

        #läser in och strukturerar manuella globala regler 
        mr_A_add_on = np.empty((0,len(self.set_artnum_p)))
        mr_b_add_on = np.empty(0)
        mr_Aeq_add_on = np.empty((0,len(self.set_artnum_p)))
        mr_beq_add_on = np.empty(0)
        modified_cost = self.set_cost.copy()

        if len(self.controller.text_list2.get(0, tk.END)) > 0:
            mr_artnum = []
            mr_command = []
            mr_amount = []
            manual_rule = self.controller.text_list2.get(0, tk.END)
            for i in range(0,len(manual_rule)):
                mr_artnum.append(manual_rule[i].strip().split()[0].upper())
                mr_command.append(manual_rule[i].strip().split()[1].upper())
                if len(manual_rule[i].strip().split()) > 2:
                    mr_amount.append(manual_rule[i].strip().split()[2].upper())
                else:
                    mr_amount.append(0)
            mr_amount = [float(x) if x != '' else 0.0 for x in mr_amount]            
            for i in range(0,len(mr_artnum)):
                if mr_command[i] == 'MAX' or mr_command[i] == 'MIN':
                    mr_A_add = np.zeros(len(self.set_artnum_p))
                    mr_A_add[mr_artnum[i] == self.set_artnum_p] = 1
                    mr_b_add = np.array([mr_amount[i]])
                    if np.any(mr_A_add == 1):
                        mr_A_add = mr_A_add * (-1) if mr_command[i] == 'MIN' else mr_A_add
                        mr_b_add = mr_b_add * (-1) if mr_command[i] == 'MIN' else mr_b_add
                        mr_A_add_on = np.vstack((mr_A_add_on, mr_A_add))
                        mr_b_add_on = np.concatenate((mr_b_add_on, mr_b_add))
                if mr_command[i] == '=':
                    mr_Aeq_add = np.zeros(len(self.set_artnum_p))
                    mr_beq_add = np.array([mr_amount[i]])
                    mr_Aeq_add[mr_artnum[i] == self.set_artnum_p] = 1
                    if np.any(mr_Aeq_add == 1):
                        mr_Aeq_add_on = np.vstack((mr_Aeq_add_on, mr_Aeq_add))
                        mr_beq_add_on = np.concatenate((mr_beq_add_on, mr_beq_add))
                if mr_command[i] == 'COST0':
                    modified_cost[mr_artnum[i] == self.set_artnum_p] = 0

        max_amount_A = np.ones((1, len(self.set_artnum_p)))/self.set_exchange
        #läser in och strukturerar manuella lokala regler
        lmr_A_add_on = [np.empty((0,len(self.set_artnum_p))) for _ in range(n)]
        lmr_b_add_on = [np.empty(0) for _ in range(n)]
        lmr_Aeq_add_on = [np.empty((0,len(self.set_artnum_p))) for _ in range(n)]
        lmr_beq_add_on = [np.empty(0) for _ in range(n)]
        temp = modified_cost
        modified_cost = [temp.copy() for _ in range(n)]
        rule_override = [np.full(len(self.set_artnum_p), False) for _ in range(n)]
        choose_std = [np.empty(0, dtype=int) for _ in range(n)]
        choose_std_value = [np.empty(0) for _ in range(n)]
        if self.controller.lr_dict:
            for i in range(0,n):
                if i in self.controller.lr_dict:
                    lmr_artnum = []
                    lmr_command = []
                    lmr_amount = []
                    lmr = self.controller.lr_dict[i]
                    elem = ['Si', 'Fe', 'Cu', 'Mn', 'Mg', 'Ni', 'Zn', 'Ti', 'Pb', 'Sn', 'Cr', 'Na', 'Sr','Sb', 'P', 'Bi', 'Ca', 'Cd', 'Zr', 'Be', 'B', 'Li', 'Al', 'Hg']
                    elem = [e.upper() for e in elem]
                    for j in range(0,len(lmr)):
                        lmr_artnum.append(lmr[j].strip().split()[0].upper())
                        lmr_command.append(lmr[j].strip().split()[1].upper())
                        if len(lmr[j].strip().split()) > 2:
                            lmr_amount.append(lmr[j].strip().split()[2].upper())
                        else:
                            lmr_amount.append(0)
                    lmr_A_add_on[i] = np.zeros((len(lmr_artnum), len(self.set_artnum_p)))
                    lmr_b_add_on[i] = np.zeros(len(lmr_artnum))

                    lmr_Aeq_add_on[i] = np.zeros((len(lmr_artnum), len(self.set_artnum_p)))
                    lmr_beq_add_on[i] = np.zeros(len(lmr_artnum)) 

                    for k in range(0,len(lmr_artnum)):
                        lmr_amount = [float(x) if x != '' else 0.0 for x in lmr_amount]
                        if lmr_command[k] == 'MAX' or lmr_command[k] == 'MIN':
                            p = np.where(lmr_artnum[k] == self.set_artnum_p)
                            lmr_A_add_on[i][k][p] = 1 if lmr_command[k] == 'MAX' else -1
                            lmr_b_add_on[i][k] = lmr_amount[k] if lmr_command[k] == 'MAX' else lmr_amount[k]*(-1)
                        if lmr_command[k] == '=':
                            p = np.where(lmr_artnum[k] == self.set_artnum_p)
                            lmr_Aeq_add_on[i][k][p] = 1
                            lmr_beq_add_on[i][k] = lmr_amount[k]
                        if lmr_command[k] == 'COST0':
                            modified_cost[i][lmr_artnum[k] == self.set_artnum_p] = 0
                        if lmr_command[k] == 'ALLOW':
                            rule_override[i][lmr_artnum[k] == self.set_artnum_p] = True
                        if lmr_artnum[k] in elem:
                            p = np.where(lmr_artnum[k] == np.array(elem))[0]
                            temp = lmr_command[k].replace(',', '.')
                            choose_std[i] = np.hstack((choose_std[i], p))
                            choose_std_value[i] = np.hstack((choose_std_value[i], float(temp)/100))

        A_add_on_i = [self.A_add_on.copy() for _ in range(n)]
        for i in range(n):
            A_add_on_i[i][:, rule_override[i]] = 0
        #sätter max lager för flera recept
        inventory_A_addon = np.empty((len(self.set_artnum_p), 0))
        inventory_A_add = np.eye(len(self.set_artnum_p))
        inventory_b_addon = self.sum_quantity.copy()
        for i in range(n):
            inventory_A_addon = np.hstack((inventory_A_addon, inventory_A_add))
    
        selected_test_std = [np.empty((0,len(self.set_artnum_p))) for _ in range(n)]
        selected_test_std_value = [np.empty(0) for _ in range(n)]
        for i in range(n):
            for j in range(choose_std[i].shape[0]):
                selected_test_std[i] = np.vstack((selected_test_std[i], np.power(self.controller.all_test_std[:,choose_std[i][j]], 2)))
                selected_test_std_value[i] = np.hstack((selected_test_std_value[i], np.power(choose_std_value[i][j]*100/2, 2) * self.controller.cp_dict['weight_out'][i]))

        tol_max_multiplier = np.full(24, 0.1645)
        tol_max_multiplier[[4, 22, 23]] = 1e10

        for i in range(0,n): #bygger listor med ett recept per position
            A[i] = np.transpose(self.set_mean_final) 
            A[i] = np.vstack((A[i], A[i]*(-1)))
            A[i] = np.vstack((A[i], selected_test_std[i]))
            A[i] = np.vstack((A[i], A_add_on_i[i]))
            A[i] = np.vstack((A[i], mr_A_add_on/self.set_exchange))
            A[i] = np.vstack((A[i], lmr_A_add_on[i]/self.set_exchange))
            A[i] = np.vstack((A[i], max_amount_A))
            b[i] = self.controller.cp_dict['tol_max'][i] * self.controller.cp_dict['weight_out'][i]
            b[i] = np.hstack((b[i], self.controller.cp_dict['tol_min'][i] *(-1) * self.controller.cp_dict['weight_out'][i]))
            b[i] = np.hstack((b[i], selected_test_std_value[i]))
            b[i] = np.hstack((b[i], self.b_add_on))
            b[i] = np.hstack((b[i], mr_b_add_on))
            b[i] = np.hstack((b[i], lmr_b_add_on[i]))
            b[i] = np.hstack((b[i], np.array([self.controller.cp_dict['weight_in'][i]])))
            Aeq[i] = np.ones((1, (len(self.set_artnum_p))))
            Aeq[i] = np.vstack((Aeq[i], mr_Aeq_add_on/self.set_exchange))
            Aeq[i] = np.vstack((Aeq[i], lmr_Aeq_add_on[i]/self.set_exchange))
            beq[i] = np.array([self.controller.cp_dict['weight_out'][i]])
            beq[i] = beq[i] = np.hstack((beq[i], mr_beq_add_on))
            beq[i] = np.hstack((beq[i], lmr_beq_add_on[i]))
            f[i] = modified_cost[i]
            bound[i] = [(0, None)] * len(self.set_mean_final)
        
        #utformar arrayerna för linprog
        A_ub = block_diag(*A)
        A_eq = block_diag(*Aeq)
        b_ub = np.concatenate(b)
        b_eq = np.concatenate(beq)
        func = np.concatenate(f)
        bounds = np.concatenate(bound)
        A_ub = np.vstack((A_ub, inventory_A_addon))
        b_ub = np.concatenate((b_ub, inventory_b_addon))

        #skapar exceldokument för felsökning
        # L = [A_ub, A_eq, b_ub, b_eq, func, bounds]
        # for i, arr in enumerate(L, start=1):
        #     if arr.ndim == 1:
        #         arr = arr.reshape(-1, 1) # Gör om 1D till kolumn
        #     df = pd.DataFrame(arr)
        #     df.to_excel(f"array_{i}.xlsx", index=False)

        result = linprog(func, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        
        if not result.success:
            result_bol = np.zeros(n, dtype=bool)  
            for i in range(0,n): #bygger listor med ett recept per position
                result_test = linprog(f[i], A_ub=np.vstack((A[i], inventory_A_add)), b_ub=np.concatenate((b[i], inventory_b_addon)), A_eq=Aeq[i], b_eq=beq[i], bounds=bound[i])
                result_bol[i] = result_test.success
            non_possible = np.array(list(range(n)))[~result_bol]
            if False in result_bol:
                messagebox.showerror('Error', f'Index {", ".join(map(str, non_possible))} can not be created.')
            else:
                messagebox.showerror('Error', 'The combination can not be created')



        #box
        def box_func(self):
            artnum_box = list(self.boxes.keys())
            artnum_result = np.array(list(self.set_artnum_p) * n)
            box_A_add_on = np.empty((0, len(self.set_artnum)*n))
            box_b_add_on = np.empty(0)
            for i, value in enumerate(artnum_box):
                p1 = np.where(value == artnum_result)[0]
                p2 = np.where(result.x > 0)[0]
                p = np.intersect1d(p1, p2)
                sorti = np.argsort([np.where(np.sort(result.x[p])[::-1] == x)[0][0] for x in result.x[p]])

                for j in p[sorti]:

                    bin_mat = np.empty((0,len(self.boxes[value])+1))
                    for i in (range(2**len(self.boxes[value])+1,2**(len(self.boxes[value])+1))):
                        temp = np.array([int(digit) for digit in str(bin(i)[2:])], np.newaxis)
                        bin_mat = np.vstack((bin_mat, temp))
                    bin_mat = np.delete(bin_mat, 0, axis=1)
                    s_bin_mat = np.sum(bin_mat*self.boxes[value][np.newaxis,:], axis=1)
                    sort_index = np.argsort([np.where(np.sort(s_bin_mat)[::-1] == x)[0][0] for x in s_bin_mat])

                    for i in s_bin_mat[sort_index]:
                        if result.x[j] >= i:
                            box_A_add = np.zeros((1, len(self.set_artnum)*n))
                            box_A_add[0,j] = 1
                            box_A_add_on = np.vstack((box_A_add_on, box_A_add))

                            # box_A_add = np.ones((1, len(self.set_artnum)*n))
                            # box_A_add[0,j] = 0
                            # box_A_add_on = np.vstack((box_A_add_on, box_A_add))
                            box_b_add_on = np.hstack((box_b_add_on, np.array([i])))
                            break
                            # box_b_add_on = np.hstack((box_b_add_on, np.array([0])))
                

            A_eq = np.vstack((A_eq, box_A_add_on))
            b_eq = np.hstack((b_eq, box_b_add_on))

            # #skapar exceldokument för felsökning
            # L = [A_ub, A_eq, b_ub, b_eq, f, bound]
            # for i, arr in enumerate(L, start=1):
            #     if arr.ndim == 1:
            #         arr = arr.reshape(-1, 1) # Gör om 1D till kolumn
            #     df = pd.DataFrame(arr)
            #     df.to_excel(f"array_{i}.xlsx", index=False)
            result = linprog(f, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bound)

        if result.success:
            rec_artnum = [None] * n
            rec_amount = [None] * n
            rec_scrap_amount = [None] * n
            rec_alloy = [None] * n
            rec_result_x = [None] * n
            rec_scrap_result_x = [None] * n
            rec_description = [None] * n

            for i in range(0,n):
                p = np.where(result.x[i*len(self.set_artnum_p):(i+1)*len(self.set_artnum_p)] != 0)
                rec_artnum[i] = self.set_artnum_p[p]
                rec_description[i] = self.set_description[p]
                rec_amount[i] = (result.x[i*len(self.set_artnum_p):(i+1)*len(self.set_artnum_p)])[p]
                rec_scrap_amount[i] = (result.x[i*len(self.set_artnum_p):(i+1)*len(self.set_artnum_p)]/self.set_exchange)[p]
                rec_scrap_result_x[i] = result.x[i*len(self.set_artnum_p):(i+1)*len(self.set_artnum_p)]/self.set_exchange 
                rec_result_x[i] = result.x[i*len(self.set_artnum_p):(i+1)*len(self.set_artnum_p)]

                rec_alloy[i] = np.sum(np.atleast_2d(np.squeeze(self.set_mean_final[p,:] * rec_amount[i][:, np.newaxis])), axis=0) / self.controller.cp_dict['weight_out'][i]
                


            self.rec_artnum = rec_artnum
            self.rec_amount = rec_amount    
            self.rec_['artnum'] = rec_artnum
            self.rec_['amount'] = rec_amount
            self.rec_['scrap_amount'] = rec_scrap_amount
            self.rec_['alloy'] = rec_alloy
            self.rec_['rec_scrap_result_x'] = rec_scrap_result_x
            self.rec_['rec_result_x'] = rec_result_x
            self.rec_['cost'] = self.set_cost
            self.rec_['set_description'] = self.set_description
            self.rec_['set_artnum_p'] = self.set_artnum_p
            self.rec_['rec_description'] = rec_description
            self.first_run = False

    def start_combined(self, _event=None):
        if not (self.controller.df1.empty or self.controller.df2.empty or self.controller.df1.dropna(how='all').empty or self.controller.df2.dropna(how='all').empty):
            if self.controller.checkbox_var.get() and self.mode == 'start':
                inhouse_artnum = ['345', '346', '347', '349', '632', '690', '691', '692', '693', '694']
                for item in inhouse_artnum:
                    if item + ' max 0' not in self.controller.text_list2.get(0, tk.END):
                        self.controller.text_list2.insert(tk.END, item + ' max 0')
                # for item in self.controller.set_styrplaner[0:40]:
                #     if item not in self.controller.text_list1.get(0, tk.END):
                #         self.controller.text_list1.insert(tk.END, item)   

            if self.mode == 'remake':
                self.controller.text_list2.delete(0, tk.END)
                if len(self.controller.text_list3.get(0, tk.END)) > 0:
                    for item in self.controller.text_list3.get(0, tk.END):
                        self.controller.text_list2.insert(tk.END, item)  

            if self.mode == 'start':
                self.controller.text_list3.delete(0, tk.END)
                if len(self.controller.text_list2.get(0, tk.END)) > 0:
                    for item in self.controller.text_list2.get(0, tk.END):
                        self.controller.text_list3.insert(tk.END, item)   

            if len(self.controller.text_list1.get(0, tk.END)) > 0:
                self.controller.show_page(self.controller.page2)

                #replicates textbox1 in Window2
                self.controller.box_select.delete(0, tk.END) 
                if len(self.controller.text_list1.get(0, tk.END)) > 0:
                    for item in self.controller.text_list1.get(0, tk.END):
                        self.controller.box_select.insert(tk.END, item)   

                if self.mode == 'start':
                    self.read_control_plan()

                self.read_testing()
                self.read_rules()
                self.read_inventory()
                self.compare()
                self.prepare()
                setattr(self.controller, self.rec_key, self.rec_)
   
class Window2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.controller.frame_box_select = ListBoxSelect(self, controller)
        self.controller.frame_box_select.grid(row=0, column=0, rowspan=3, sticky='nsew')

        frame_go_back = GoBack1(self, controller)
        frame_go_back.grid(row=0, column=0, sticky='nw')

        frame_export_button = ExportButton(self, controller)
        frame_export_button.grid(row=2, column=2, sticky='se')

        frame_start = Start(self, controller, rec_key='rec_', mode='remake')
        frame_start.grid(row=2, column=2, sticky='ne')

        frame_listbox3 = InputForm(self, controller, 'frame2')
        frame_listbox3.grid(row=0, column=2, sticky='nsew', rowspan=2)

        controller.text_list3 = frame_listbox3.text_list

class GoBack1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.go_back = tk.Button(self, text='<-', command=self.go_b)
        self.go_back.pack(anchor='nw', padx=5, pady=5)
    def go_b(self):
        self.controller.show_page(self.controller.page1)
        
        self.controller.text_list2.delete(0, tk.END)
        if len(self.controller.text_list3.get(0, tk.END)) > 0:
            for item in self.controller.text_list3.get(0, tk.END):
                self.controller.text_list2.insert(tk.END, item)            

class ListBoxSelect(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.box_select = tk.Listbox(self, font=tkFont.Font(size=12))
        self.controller.box_select.pack(padx=5, pady=(35, 5), anchor='sw', expand=True, fill='both')
        
        self.controller.box_select.bind("<Double-Button-1>", self.on_select)

    def on_select(self, _event=None):
        widget = self.controller.box_select
        selection = widget.curselection()   
        if selection:
            index = selection[0]
            self.controller.index = index
            self.update_page3()
    def update_page3(self):
        widget = self.controller.box_select
        self.controller.value = widget.get(self.controller.index)
        self.controller.show_page(self.controller.page3)
        self.controller.recipe_label.config(text=f'{self.controller.value} index: {self.controller.index}') #changes the recipe label to currently opened recipe
        
        rec_string = self.controller.rec_['artnum'][self.controller.index].astype('U100') + ' - ' + np.round(self.controller.rec_['scrap_amount'][self.controller.index], 0).astype('U100') + ', ' + self.controller.rec_['rec_description'][self.controller.index].astype('U100')
        self.controller.text_list4.delete(0, tk.END) #sätter lista för lokala bivillkor till matchande lista
        if self.controller.index in self.controller.lr_dict:
            for item in self.controller.lr_dict[self.controller.index]:
                self.controller.text_list4.insert(tk.END, item)  
        self.controller.recipe_box.delete(0, tk.END)
        if len(rec_string) > 0:
            for item in rec_string:
                self.controller.recipe_box.insert(tk.END, item)

        self.controller.frame_cost_label.cost_calculator()
        self.controller.frame_recomendation_box.recommend()
        self.controller.frame_tolerance_control.success_procent()
        self.controller.frame_tolerance_control.update_canvas()
        self.controller.frame_weight_in.update_value()
        self.controller.frame_weight_out.update_value()
class ExportButton(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.export_button = tk.Button(self, width=20, height=4, bg='green', text='Export', command=self.export, font=tkFont.Font(size=14))
        self.export_button.pack(anchor='se', padx=5, pady=5)

    def export(self):
        export_dict = {}
        n = len(self.controller.rec_['artnum'])
        if not self.controller.checkbox_var.get():
            for i in range(n):
                index_string = f'{self.controller.box_select.get(i)}, {i}'
                export_dict[index_string + ', artnum'] = pd.Series(list(self.controller.rec_['artnum'][i]))
                export_dict[index_string + ', amount'] = pd.Series(list(self.controller.rec_['scrap_amount'][i]))
            name = 'OptiX export'                

        else:
            set_scrap_amount = np.zeros(self.controller.rec_['rec_scrap_result_x'][0].shape)
            artnum = self.controller.rec_['set_artnum_p']
            for i in range(n):
                set_scrap_amount += self.controller.rec_['rec_scrap_result_x'][i]
            scrap_amount = set_scrap_amount[set_scrap_amount != 0]
            artnum = artnum[set_scrap_amount != 0]
            export_dict['artnum'] = pd.Series(list(artnum))
            export_dict['amonut'] = pd.Series(list(scrap_amount))
            name = 'OptiX simulation'
        
        df = pd.DataFrame(export_dict)
        now = datetime.now()
        formatted_datetime = now.strftime("%d-%m-%Y %H-%M")
        document_name = f'{formatted_datetime} {name}.xlsx'
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Save Excel File",
            initialfile=document_name
        )
        if file_path:
            df.to_excel(file_path, index=False)
        else:
            messagebox.showerror('Error', 'Export not possible')




class Window3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.columnconfigure(0, weight=5, uniform='group1')
        self.columnconfigure(1, weight=0, minsize=480)
        self.columnconfigure(2, weight=1, uniform='group1')
        self.columnconfigure(3, weight=4, uniform='group1')
        self.rowconfigure(0, weight=2, uniform='group2')
        self.rowconfigure(1, weight=0, minsize=550)
        self.rowconfigure(2, weight=1, uniform='group2')
        

        frame_recipe_box = RecipeListBox(self, controller)
        frame_recipe_box.grid(row=0, column=0, rowspan=3, sticky='nsew')

        frame_recipe_label = RecipeLabel(self, controller)
        frame_recipe_label.grid(row=0, column=0, sticky='n')

        frame_go_back = GoBack2(self, controller)
        frame_go_back.grid(row=0, column=0, sticky='nw')


        frame_percent_label = PercentLabel(self, controller)
        frame_percent_label.grid(row=2, column=1, sticky='ne')

        controller.frame_cost_label = CostLabel(self, controller)
        controller.frame_cost_label.grid(row=2, column=1, sticky='nw')

        controller.frame_recomendation_box = RecomendationBox(self, controller)
        controller.frame_recomendation_box.grid(row=0, column=1, sticky='nsew')

        frame_listbox4 = InputForm(self, controller, 'frame3')
        frame_listbox4.grid(row=0, column=2, rowspan=2, columnspan=2, sticky='nsew')

        controller.frame_tolerance_control = ToleranceControl(self, controller)
        controller.frame_tolerance_control.grid(row=1, column=1, sticky='ew')

        frame_next_btn = NextButton(self, controller)
        frame_next_btn.grid(row=0, column=0, sticky='ne')

        controller.frame_weight_out = WeightInOut(self, controller, 'weight_out')
        controller.frame_weight_out.grid(row=2, column=2, sticky='ne')
                              
        controller.frame_weight_in = WeightInOut(self, controller, 'weight_in')
        controller.frame_weight_in.grid(row=2, column=3, sticky='nw')

        controller.text_list4 = frame_listbox4.text_list
     
class GoBack2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.go_back = tk.Button(self, text='<-', command=self.go_b)
        self.go_back.pack(anchor='nw', padx=5, pady=5)
    def go_b(self):
        self.controller.show_page(self.controller.page2)

class RecipeLabel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.recipe_label = tk.Label(self, font=tkFont.Font(size=16), bd=5, relief='ridge', text='none')
        self.controller.recipe_label.pack(anchor='n')
             
class RecipeListBox(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.recipe_box = tk.Listbox(self, font=tkFont.Font(size=12))
        self.controller.recipe_box.pack(fill="both", padx=5, pady=(35, 5), expand=True)

class ToleranceControl(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.size = 0.25

        name = ['Al'] * 24
        lower_b = np.array([0] * 24)
        upper_b = np.array([1] * 24)
        complete_alloy = np.array([1/2] * 24)
        intervals = []
        for i in range(len(name)):
            interval = f'{name[i]} ({lower_b[i]}-{upper_b[i]}) {complete_alloy[i]:.2f}'
            intervals.append(interval)

        self.n = len(name)

        fig, self.ax = plt.subplots(figsize=(3, 5.6)) #adjust output size
        self.ax.set_xlim(0,1)
        self.ax.set_ylim(0.5, self.n + 0.5)
        self.ax.set_yticks(np.arange(1, self.n + 1))
        self.ax.set_yticklabels(intervals)

        self.move_upper_b = np.ones(24)
        self.pos_l_red_lines = np.zeros(24)
        # self.controller.prob = np.ones(24)

        self.red_lines = []
        self.l_red_lines = []
        self.blue_lines = []
        self.percents = []
        for i in range(self.n):
            val_norm = (complete_alloy[i] - lower_b[i]) / (upper_b[i] - lower_b[i])

            self.ax.add_patch(plt.Rectangle((0, i + 1 -self.size), 1 , 2*self.size, facecolor='lightgray', edgecolor='black'))
            red_line = self.ax.plot([self.move_upper_b[i], self.move_upper_b[i]], [i + 1 -self.size, i + 1 + self.size], color='red', linewidth=2)
            self.red_lines.append(red_line)
            l_red_line = self.ax.plot([self.pos_l_red_lines[i], self.pos_l_red_lines[i]], [i + 1 -self.size, i + 1 + self.size], color='red', linewidth=2)
            self.l_red_lines.append(l_red_line)
            blue_line = self.ax.plot([val_norm, val_norm], [i + 1 - self.size, i + 1 + self.size], color='blue', linewidth=2)
            self.blue_lines.append(blue_line)
            percent = self.ax.text(1.05, i + 1, f'100%', va='center')
            self.percents.append(percent) 

        # ax.set_title('Toleranskontroll')
        # ax.set_xlabel('Normaliserat intervall (0-100%)')
        # plt.tight_layout()
        # Embed the matplotlib figure in Tkinter
        fig.subplots_adjust(
            top=0.97,    # space at the top (1.0 = top edge of the figure)
            bottom=0.074,  # space at the bottom (0.0 = bottom edge of the figure)
            left=0.35,    # space on the left
            right=0.85    # space on the right
        )

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=0, column=0, padx=(0,26), sticky='ew')


        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, pady=(0,42), sticky='es')
        # Create buttons for each value
        for i in range(0, 24):
            frame = tk.Frame(button_frame)
            frame.grid(row=i, column=2)
            tk.Button(frame, text="+", font=('Arial', 7), command=lambda i=i: self.change_value(23-i, 0.1)).grid(row=0, column=1)
            tk.Button(frame, text="-", font=('Arial', 7), command=lambda i=i: self.change_value(23-i, -0.1)).grid(row=0, column=0)

    def update_canvas(self):
        def smart_format(value):
            # Om värdet är ett heltal, visa utan decimaler
            if abs(value) < 0.0005:
                return "0"
            if abs(value) > 50:
                return f"{value:.1f}"
            if value == int(value):
                return str(int(value))
            
            # Räkna antal decimaler
            decimal_str = f"{value:.10f}".rstrip("0")  # max 10 decimaler, ta bort överflödiga nollor
            decimals = decimal_str.split(".")[1] if "." in decimal_str else ""
            
            # Visa med så många decimaler som behövs (max 3)
            if len(decimals) == 1:
                return f"{value:.1f}"
            elif len(decimals) == 2:
                return f"{value:.2f}"
            elif len(decimals) >= 3:
                return f"{value:.3f}"
            else:
                return str(value)

        intervals = []
        for i in range(self.n):
            self.move_upper_b[i] = ((self.controller.cp_dict['tol_max'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i])/
                (self.controller.cp_dict['outer_max'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i]))
            self.red_lines[i][0].remove()
            red_line = self.ax.plot([self.move_upper_b[i], self.move_upper_b[i]], [i + 1 -self.size, i + 1 + self.size], color='red', linewidth=2)
            self.red_lines[i] = red_line
            
            self.pos_l_red_lines[i] = ((self.controller.cp_dict['tol_min'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i])/
                (self.controller.cp_dict['outer_max'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i]))
            self.l_red_lines[i][0].remove()
            l_red_line = self.ax.plot([self.pos_l_red_lines[i], self.pos_l_red_lines[i]], [i + 1 -self.size, i + 1 + self.size], color='red', linewidth=2)
            self.l_red_lines[i] = l_red_line
            
            val_norm = ((self.controller.rec_['alloy'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i])/
                (self.controller.cp_dict['outer_max'][self.controller.index][i]-self.controller.cp_dict['outer_min'][self.controller.index][i]))
            self.blue_lines[i][0].remove()
            blue_line = self.ax.plot([val_norm, val_norm], [i + 1 - self.size, i + 1 + self.size], color='blue', linewidth=2)
            self.blue_lines[i] = blue_line

            #interval = f"{self.controller.cp_dict['elem'][i]} ({self.controller.cp_dict['outer_min'][self.controller.index][i]:.1f}-{self.controller.cp_dict['outer_max'][self.controller.index][i]:.1f}) {self.controller.rec_['alloy'][self.controller.index][i]:.1f}"
            interval = (
            f"{self.controller.cp_dict['elem'][i]} "
            f"({smart_format(self.controller.cp_dict['outer_min'][self.controller.index][i])}-"
            f"{smart_format(self.controller.cp_dict['outer_max'][self.controller.index][i])}) "
            f"{smart_format(self.controller.rec_['alloy'][self.controller.index][i])}"
                )

            intervals.append(interval)
        self.ax.set_yticklabels(intervals)
        self.canvas.draw()
        
    # Function to change a value
    def change_value(self, index, delta):
      
        self.move_upper_b[index] += delta
        self.red_lines[index][0].remove()
        
        new_line = self.ax.plot([self.move_upper_b[index], self.move_upper_b[index]], [index + 1 -self.size, index + 1 + self.size], color='red', linewidth=2)
        self.red_lines[index] = new_line

        self.controller.cp_dict['tol_max'][self.controller.index][index] = self.move_upper_b[index]*(self.controller.cp_dict['outer_max'][self.controller.index][index] - self.controller.cp_dict['outer_min'][self.controller.index][index]) + self.controller.cp_dict['outer_min'][self.controller.index][index]
        self.canvas.draw()
    def success_procent(self):
        p = np.where(self.controller.rec_['rec_result_x'][self.controller.index] != 0)
        test_std = self.controller.all_test_std[p, :]
        rec_result = self.controller.rec_['rec_result_x'][self.controller.index][p]
        weighted_std = np.empty((0,24))
        sum_weighted_std = np.empty((0,24))

        for i in range(len(rec_result)):
            sum_weighted_std = np.vstack((sum_weighted_std, rec_result[i]*np.power(test_std[0][i,:], 2)/self.controller.cp_dict['weight_out'][self.controller.index]))
            weighted_std = np.vstack((weighted_std, rec_result[i]*test_std[0][i,:]/self.controller.cp_dict['weight_out'][self.controller.index]))

        sum_weighted_std = np.sqrt(np.sum(sum_weighted_std, axis=0))
        # sum_weighted_std = sum_weighted_std *100
        p = [] 
        for i in range(len(rec_result)):
            if np.all(test_std[0][i,:] == 0):
                p.append(i)
        alloy = self.controller.rec_['alloy'][self.controller.index].copy()
        amount = rec_result[p]/self.controller.cp_dict['weight_out'][self.controller.index]
        an = self.controller.rec_['artnum'][self.controller.index][p]

        for i in range(len(an)):
            p2 = np.where(an[i] == self.controller.testing_dict['set_artnum_p'])
            alloy[:] -= (np.squeeze(self.controller.testing_dict['set_mean_final'][p2,:]))*amount[i]
        prob = []
        for i in range(23):
            prob.append(norm.cdf(self.controller.cp_dict['outer_max'][self.controller.index][i], loc=alloy[i], scale=sum_weighted_std[i]))
        prob.append(np.float64(1.0)) #Hg
        if hasattr(self, 'percents'):
            for i in self.percents:
                i.remove()
        self.percents = []
        for i in range(24):
            percent = self.ax.text(1.05, i + 1, f'{int(round(prob[i]*100))}%', va='center')
            self.percents.append(percent)
        # self.ax.set_text(intervals)
        self.controller.percent_label.config(text=f'{int(round(np.prod(np.delete(np.array(prob), [4, 22]))*100))}%' )

        for i, value in enumerate(prob):
            if value < 0.97725 and (i != 4 and i !=22):
                p = np.where(np.max(weighted_std[:,i]) == weighted_std[:,i])[0]
                string = f"{self.controller.rec_['artnum'][self.controller.index][p][0]} has the highest deviation of {self.controller.cp_dict['elem'][i]}"
                self.controller.recomendation_box.insert(tk.END, string)
                
class PercentLabel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.percent_label = tk.Label(self, font=tkFont.Font(size=16), bd=5, relief='ridge', text='none')
        self.controller.percent_label.pack(anchor='ne')

class CostLabel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.cost_label = tk.Label(self, font=tkFont.Font(size=16), bd=5, relief='ridge', text='none')
        self.cost_label.pack(anchor='nw')
    def cost_calculator(self):
        p = np.where(self.controller.rec_['rec_result_x'][self.controller.index] != 0)[0]
        cost = np.sum(self.controller.rec_['cost'][p] * self.controller.rec_['rec_result_x'][self.controller.index][p])
        self.cost_label.config(text= f'{int(round(cost))} kr')
        cost_tot = 0
        for i in (range(len(list(self.controller.rec_['rec_result_x'])))):
            p = np.where(self.controller.rec_['rec_result_x'][i] != 0)[0]
            cost_tot += np.sum(self.controller.rec_['cost'][p] * self.controller.rec_['rec_result_x'][i][p])

class RecomendationBox(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.controller.recomendation_box = tk.Listbox(self, font=tkFont.Font(size=12))
        self.controller.recomendation_box.pack(fill="both", expand=True)
    def recommend(self):
        self.controller.recomendation_box.delete(0, tk.END)
        rec_artnum = self.controller.rec_['artnum'][self.controller.index]
        box_artnum = np.array(list(self.controller.boxes.keys()))
        box_recommend = np.intersect1d(rec_artnum, box_artnum)

        if len(box_recommend) > 0:
            for item in box_recommend:
                self.controller.recomendation_box.insert(tk.END, f"{item}: {', '.join(map(str, self.controller.boxes[item]))}. Rest: {self.controller.boxes[f'{item}rest'][0]}")

class NextButton(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.controller = controller
        self.next_btn = tk.Button(self, text='Next', font=tkFont.Font(size=12), command=self.go_next)
        self.next_btn.grid(row=0, column=1, pady=(5, 0), padx=(0, 5), sticky='ne')

        self.prev_btn = tk.Button(self, text='Prev', font=tkFont.Font(size=12), command=self.go_prev)
        self.prev_btn.grid(row=0, column=0, pady=(5, 0), padx=(0, 5), sticky='ne')

    def go_next(self, _event=None):
        self.change_page(btn_key= 'next')

    def go_prev(self, _event=None):
        self.change_page(btn_key= 'prev')

    def change_page(self, btn_key):
        n = len(self.controller.rec_['artnum'])

        if btn_key == 'next':
            self.controller.index = self.controller.index + 1 if self.controller.index + 1 < n else 0
        if btn_key == 'prev':
            self.controller.index = self.controller.index - 1 if self.controller.index - 1 >= 0 else n-1

        self.controller.frame_box_select.update_page3()

class WeightInOut(tk.Frame):
    def __init__(self, parent, controller, key):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.columnconfigure(0, weight=1)
        self.controller = controller
        self.key = key

        self.weight_label = tk.Label(self, text='None', font=tkFont.Font(size=12))
        self.weight_label.grid(row=1, column=0)

        add_btn = tk.Button(self, text='+100', font=tkFont.Font(size=12), command=self.add)
        add_btn.grid(row=0, column=0)

        sub_btn = tk.Button(self, text='-100', font=tkFont.Font(size=12), command=self.sub)
        sub_btn.grid(row=2, column=0)

    def update_value(self):
        self.weight_label.config(text=str(int(self.controller.cp_dict[self.key][self.controller.index])))
    def add(self):
        self.controller.cp_dict[self.key][self.controller.index] += 100
        self.weight_label.config(text=str(int(self.controller.cp_dict[self.key][self.controller.index])))
        
    def sub(self):
        self.controller.cp_dict[self.key][self.controller.index] -= 100
        self.weight_label.config(text=str(int(self.controller.cp_dict[self.key][self.controller.index])))






if __name__ == '__main__':
    main()