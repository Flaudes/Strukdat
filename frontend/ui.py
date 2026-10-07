import sys
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Hubungkan path ke folder backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.m1_pesanan import muat_csv_pesanan, DynamicArray, LinkedList, Pesanan


class App2EZ4U:
    def __init__(self, root):
        self.root = root
        self.root.geometry("2560x1440")
        self.root.title("2EZ4U - APLIKASI ORDER MAKANAN")

        # Inisialisasi Data M1
        self.semua_data_raw = []
        self.arr = DynamicArray()
        self.ll = LinkedList()

        # Build Tampilan GUI
        self._setup_ui()

    def _setup_ui(self):
        # Frame Utama
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. PANEL ATAS (Judul Aplikasi)
        lbl_header = ttk.Label(
            main_frame, 
            text="2EZ4U - APLIKASI ORDER MAKANAN",
            font=("Helvetica", 18, "bold")
        )
        lbl_header.pack(side=tk.TOP, anchor=tk.W, pady=(0, 10))

        # Splitter Kiri & Kanan (PanedWindow)
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # 2. PANEL KIRI (Navigasi & Menu Operasi)
        left_frame = ttk.LabelFrame(paned, text=" Navigasi Menu ", width=300)
        paned.add(left_frame, weight=1)

        # Tombol Load Data CSV
        btn_load = ttk.Button(
            left_frame, 
            text="1. LOAD DATA CSV (200.000 Data)", 
            command=self.cmd_load_data
        )
        btn_load.pack(fill=tk.X, padx=10, pady=10)

        # Listbox Pilihan Menu M1
        lbl_list = ttk.Label(left_frame, text="Pilih Operasi Backend M1:", font=("Helvetica", 10, "bold"))
        lbl_list.pack(anchor=tk.W, padx=10, pady=(10, 2))

        self.menu_listbox = tk.Listbox(left_frame, font=("Helvetica", 11), selectmode=tk.SINGLE)
        menu_items = [
            "ARRAY - LIHAT PESANAN",
            "ARRAY - TAMBAH PESANAN REGULER",
            "ARRAY - TAMBAH PESANAN PRIORITAS",
            "ARRAY - TAMBAH PESANAN VIP",
            "ARRAY - HAPUS PESANAN",
            "LINKEDLIST - LIHAT PESANAN",
            "LINKEDLIST - TAMBAH PESANAN REGULER",
            "LINKEDLIST - TAMBAH PESANAN PRIORITAS",
            "LINKEDLIST - TAMBAH PESANAN VIP",
            "LINKEDLIST - HAPUS PESANAN",
        ]
        for item in menu_items:
            self.menu_listbox.insert(tk.END, item)
        self.menu_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.menu_listbox.bind("<<ListboxSelect>>", self.on_menu_selected)

        # 3. PANEL TENGAH (Form Parameter & Tampilan Output Data)
        right_frame = ttk.LabelFrame(paned, text=" Panel Eksekusi & Output ")
        paned.add(right_frame, weight=4)

        # Form Parameter (Indeks)
        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Masukkan Indeks Pesanan (ke-i):").pack(side=tk.LEFT, padx=5)
        self.ent_index = ttk.Entry(form_frame, width=15)
        self.ent_index.insert(0, "0")
        self.ent_index.pack(side=tk.LEFT, padx=5)

        self.btn_eksekusi = ttk.Button(form_frame, text="JALANKAN PERINTAH", command=self.cmd_eksekusi)
        self.btn_eksekusi.pack(side=tk.LEFT, padx=10)

        # Output Area Text
        self.txt_output = tk.Text(right_frame, font=("Consolas", 11), bg="#ffffff")
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 4. PANEL BAWAH (Log Perintah & Benchmarking Waktu)
        log_frame = ttk.LabelFrame(self.root, text=" Panel Performance & Command Log ")
        log_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))

        self.txt_log = tk.Text(log_frame, height=5, font=("Consolas", 10), bg="#1e1e1e", fg="#00ff00")
        self.txt_log.pack(fill=tk.X, expand=True, padx=5, pady=5)

    # ==========================================
    # LOGIKA & ACTION HANDLER
    # ==========================================
    def write_log(self, modul, aksi, elapsed_ms, keterangan=""):
        msg = f"[{modul}] {aksi:<35} | Waktu: {elapsed_ms:8.2f} ms | {keterangan}\n"
        self.txt_log.insert(tk.END, msg)
        self.txt_log.see(tk.END)

    def cmd_load_data(self):
        path_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'pesanan.csv')
        
        t0 = time.perf_counter()
        self.semua_data_raw = muat_csv_pesanan(path_csv)
        
        # Reset dan isi ulang struktur data
        self.arr = DynamicArray()
        self.ll = LinkedList()
        for p in self.semua_data_raw:
            self.arr.tambah_reguler(p)
            self.ll.tambah_reguler(p)
            
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000

        total_records = len(self.semua_data_raw)
        self.write_log("DATA", "Load CSV Pesanan", elapsed_ms, f"Total Data: {total_records} baris")
        
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"BERHASIL MEMUAT {total_records} DATA PESANAN DARI CSV.\n")
        self.txt_output.insert(tk.END, f"Data telah dimasukkan ke Dynamic Array dan Linked List secara simultan.\n")
        messagebox.showinfo("Sukses", f"Berhasil memuat {total_records} data pesanan!")

    def on_menu_selected(self, event):
        sel = self.menu_listbox.curselection()
        if not sel:
            return
        selected_text = self.menu_listbox.get(sel[0])
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"Menu Terpilih: {selected_text}\n")
        self.txt_output.insert(tk.END, "Tekan tombol 'JALANKAN PERINTAH' di atas untuk mengeksekusi.\n")

    def cmd_eksekusi(self):
        sel = self.menu_listbox.curselection()
        if not sel:
            messagebox.showwarning("Peringatan", "Pilih menu operasi di sebelah kiri dulu!")
            return

        if self.arr.size == 0 and self.ll.size == 0:
            messagebox.showwarning("Peringatan", "Muat data CSV terlebih dahulu!")
            return

        menu = self.menu_listbox.get(sel[0])
        idx_str = self.ent_index.get().strip()
        idx = int(idx_str) if idx_str.isdigit() else 0

        self.txt_output.delete("1.0", tk.END)

        # 1. ARRAY - LIHAT
        if menu == "ARRAY - LIHAT PESANAN":
            t0 = time.perf_counter()
            res = self.arr.get(idx)
            t1 = time.perf_counter()
            self.write_log("M1-Array", f"Get Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[ARRAY GET {idx}]\n{res}\n")

        # 2. ARRAY - TAMBAH REGULER
        elif menu == "ARRAY - TAMBAH REGULER":
            dummy = Pesanan("O-NEW-REG", "Pelanggan Baru", "Resto A", "Menu Reguler", 15000, 3, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_reguler(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah Reguler (Belakang)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menambah pesanan REGULER ke bagian belakang Array.\nTotal size: {self.arr.size}\n")

        # 3. ARRAY - TAMBAH PRIORITAS
        elif menu == "ARRAY - TAMBAH PRIORITAS":
            dummy = Pesanan("O-NEW-PRIO", "Pelanggan Prio", "Resto B", "Menu Prio", 25000, 2, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_prioritas(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah Prioritas (Tengah)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan PRIORITAS ke tengah Array (O(n) shift).\nTotal size: {self.arr.size}\n")

        # 4. ARRAY - TAMBAH VIP
        elif menu == "ARRAY - TAMBAH VIP":
            dummy = Pesanan("O-NEW-VIP", "Pelanggan VIP", "Resto C", "Menu VIP", 50000, 1, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_vip(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah VIP (Depan)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan VIP ke indeks 0 Array (O(n) shift all).\nTotal size: {self.arr.size}\n")

        # 5. ARRAY - HAPUS
        elif menu == "ARRAY - HAPUS PESANAN":
            t0 = time.perf_counter()
            res = self.arr.hapus(idx)
            t1 = time.perf_counter()
            self.write_log("M1-Array", f"Hapus Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[ARRAY HAPUS {idx}]\nData Terhapus: {res}\nSisa size: {self.arr.size}\n")

        # 6. LINKEDLIST - LIHAT
        elif menu == "LINKEDLIST - LIHAT PESANAN":
            t0 = time.perf_counter()
            res = self.ll.get(idx)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", f"Get Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[LINKED LIST GET {idx}]\n{res}\n")

        # 7. LINKEDLIST - TAMBAH REGULER
        elif menu == "LINKEDLIST - TAMBAH REGULER":
            dummy = Pesanan("O-NEW-REG", "Pelanggan Baru", "Resto A", "Menu Reguler", 15000, 3, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_reguler(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah Reguler (Tail)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menambah pesanan REGULER via pointer Tail (O(1)).\nTotal size: {self.ll.size}\n")

        # 8. LINKEDLIST - TAMBAH PRIORITAS
        elif menu == "LINKEDLIST - TAMBAH PRIORITAS":
            dummy = Pesanan("O-NEW-PRIO", "Pelanggan Prio", "Resto B", "Menu Prio", 25000, 2, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_prioritas(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah Prioritas (Tengah)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menelusuri ke tengah dan menyisipkan pesanan PRIORITAS.\nTotal size: {self.ll.size}\n")

        # 9. LINKEDLIST - TAMBAH VIP
        elif menu == "LINKEDLIST - TAMBAH VIP":
            dummy = Pesanan("O-NEW-VIP", "Pelanggan VIP", "Resto C", "Menu VIP", 50000, 1, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_vip(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah VIP (Head)", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyambungkan pesanan VIP langsung ke Head (O(1)).\nTotal size: {self.ll.size}\n")

        # 10. LINKEDLIST - HAPUS
        elif menu == "LINKEDLIST - HAPUS PESANAN":
            t0 = time.perf_counter()
            res = self.ll.hapus(idx)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", f"Hapus Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[LINKED LIST HAPUS {idx}]\nData Terhapus: {res}\nSisa size: {self.ll.size}\n")


if __name__ == "__main__":
    root = tk.Tk()
    app = App2EZ4U(root)
    root.mainloop()