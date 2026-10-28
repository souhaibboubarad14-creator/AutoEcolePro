import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

# تهيئة قاعدة البيانات المحلية
def init_db():
    conn = sqlite3.connect("auto_ecole.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cin TEXT UNIQUE NOT NULL,
            nom_complet TEXT NOT NULL,
            telephone TEXT,
            permis TEXT DEFAULT 'B',
            prix_total REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_id INTEGER,
            montant REAL NOT NULL,
            date_payment DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (candidate_id) REFERENCES candidates (id)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class AutoEcoleDesktopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام تسيير مدرسة تعليم السياقة")
        self.root.geometry("850x600")
        self.root.config(bg="#f3f4f6")
        
        # العنوان العلوي
        header = tk.Frame(root, bg="#1d4ed8", pady=12)
        header.pack(fill=tk.X)
        tk.Label(header, text="🚗 تسيير مدرسة تعليم السياقة", fg="white", bg="#1d4ed8", font=("Arial", 16, "bold")).pack()

        # إطار الإدخال
        form_frame = tk.LabelFrame(root, text=" تسجيل مرشح جديد ", font=("Arial", 11, "bold"), bg="white", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=15, pady=10)

        # الحقول
        tk.Label(form_frame, text="رقم البطاقة (CIN):", bg="white", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.cin_e = tk.Entry(form_frame, font=("Arial", 10), width=18)
        self.cin_e.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="الاسم الكامل:", bg="white", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.nom_e = tk.Entry(form_frame, font=("Arial", 10), width=22)
        self.nom_e.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="الهاتف:", bg="white", font=("Arial", 10)).grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.tel_e = tk.Entry(form_frame, font=("Arial", 10), width=18)
        self.tel_e.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="صنف الرخصة:", bg="white", font=("Arial", 10)).grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.permis_cb = ttk.Combobox(form_frame, values=["B", "A", "C", "D"], width=20, state="readonly")
        self.permis_cb.set("B")
        self.permis_cb.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(form_frame, text="المبلغ الإجمالي (DH):", bg="white", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.prix_e = tk.Entry(form_frame, font=("Arial", 10), width=18)
        self.prix_e.grid(row=2, column=1, padx=5, pady=5)

        btn_add = tk.Button(form_frame, text="حفظ وتسجيل المرشح", bg="#16a34a", fg="white", font=("Arial", 10, "bold"), command=self.add_candidate, padx=15, pady=3)
        btn_add.grid(row=2, column=3, sticky="e", padx=5, pady=5)

        # جدول العرض
        table_frame = tk.Frame(root, bg="white", padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self.tree = ttk.Treeview(table_frame, columns=("CIN", "Nom", "Permis", "Total", "Paye", "Reste"), show="headings", height=10)
        self.tree.heading("CIN", text="CIN")
        self.tree.heading("Nom", text="الاسم الكامل")
        self.tree.heading("Permis", text="الصنف")
        self.tree.heading("Total", text="الإجمالي")
        self.tree.heading("Paye", text="المؤدى")
        self.tree.heading("Reste", text="الباقي")
        
        self.tree.column("CIN", width=100)
        self.tree.column("Nom", width=200)
        self.tree.column("Permis", width=70)
        self.tree.column("Total", width=90)
        self.tree.column("Paye", width=90)
        self.tree.column("Reste", width=90)
        
        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_data()

    def add_candidate(self):
        cin = self.cin_e.get().strip()
        nom = self.nom_e.get().strip()
        tel = self.tel_e.get().strip()
        permis = self.permis_cb.get()
        prix = self.prix_e.get().strip()

        if not cin or not nom or not prix:
            messagebox.showerror("تنبيه", "المرجو ملء جميع الحقول الضرورية!")
            return

        try:
            prix_val = float(prix)
        except ValueError:
            messagebox.showerror("خطأ", "المبلغ يجب أن يكون رقماً صحيحاً!")
            return

        conn = sqlite3.connect("auto_ecole.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO candidates (cin, nom_complet, telephone, permis, prix_total) VALUES (?, ?, ?, ?, ?)",
                           (cin, nom, tel, permis, prix_val))
            conn.commit()
            messagebox.showinfo("نجاح", "تم تسجيل المرشح بنجاح في النظام!")
            self.cin_e.delete(0, tk.END)
            self.nom_e.delete(0, tk.END)
            self.tel_e.delete(0, tk.END)
            self.prix_e.delete(0, tk.END)
            self.load_data()
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ", "رقم البطاقة الوطنية (CIN) مسجل مسبقاً!")
        finally:
            conn.close()

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = sqlite3.connect("auto_ecole.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.cin, c.nom_complet, c.permis, c.prix_total, 
                   COALESCE(SUM(p.montant), 0) as paye
            FROM candidates c
            LEFT JOIN payments p ON c.id = p.candidate_id
            GROUP BY c.id
        ''')
        for r in cursor.fetchall():
            cin, nom, permis, total, paye = r
            reste = total - paye
            self.tree.insert("", tk.END, values=(cin, nom, permis, f"{total} DH", f"{paye} DH", f"{reste} DH"))
        conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoEcoleDesktopApp(root)
    root.mainloop()