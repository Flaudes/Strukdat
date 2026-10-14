import sys
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox

# Hubungkan path ke folder backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.m1_pesanan import muat_csv_pesanan, DynamicArray, LinkedList, Pesanan
from backend.m2_antrean import AntreanNaif, AntreanMelingkar, UndoRedoQueue, evaluasi_kasir
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search

class App2EZ4U:
    def __init__(self, root):
        self.root = root
        self.root.geometry("800x650")
        self.root.title("2EZ4U - APLIKASI ORDER MAKANAN")

        # Data M1
        self.semua_data_raw = []
        self.arr = DynamicArray()
        self.ll = LinkedList()
        
        # Data M2
        self.q_naif = AntreanNaif()
        self.q_circular = AntreanMelingkar()
        self.undo_naif = UndoRedoQueue(self.q_naif)
        self.undo_circular = UndoRedoQueue(self.q_circular)
        
        # Data M3
        self.sorted_by_oid_cache = []
        
        self.selected_menu_text = ""
        self.all_listboxes = []

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

        # 2. PANEL KIRI (Navigasi & Menu Operasi Berkelompok dengan Scrollbar)
        left_container = ttk.Frame(paned, width=280)
        paned.add(left_container, weight=1)

        canvas = tk.Canvas(left_container, borderwidth=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Daftar Kategori & Operasi Menu Sesuai Spesifikasi PDF
        menu_groups = [
            ("DATA", [
                "Load"
            ]),
            ("M1 - DATA PESANAN", [
                "ARRAY - LIHAT PESANAN",
                "ARRAY - TAMBAH PESANAN REGULER",
                "ARRAY - TAMBAH PESANAN PRIORITAS",
                "ARRAY - TAMBAH PESANAN VIP",
                "ARRAY - HAPUS PESANAN",
                "LINKEDLIST - LIHAT PESANAN",
                "LINKEDLIST - TAMBAH PESANAN REGULER",
                "LINKEDLIST - TAMBAH PESANAN PRIORITAS",
                "LINKEDLIST - TAMBAH PESANAN VIP",
                "LINKEDLIST - HAPUS PESANAN"
            ]),
            ("M2 - STACK DAN QUEUE", [
                "STACK - POSTFIX (MESIN KASIR)",
                "STACK - UNDO",
                "STACK - REDO",
                "QUEUE - ENQUEUE",
                "QUEUE - DEQUEUE NAIF",
                "QUEUE - DEQUEUE CIRCULAR"
            ]),
            ("M3 - SORT DAN SEARCH", [
                "SORT - INSERTION SORT",
                "SORT - MERGE SORT",
                "SEARCH - LINEAR SEARCH",
                "SEARCH - BINARY SEARCH"
            ])
        ]

        # Generate LabelFrame + Listbox untuk tiap kelompok
        for group_title, items in menu_groups:
            grp_frame = ttk.LabelFrame(scrollable_frame, text=f" {group_title} ")
            grp_frame.pack(fill=tk.X, expand=True, padx=5, pady=3)

            lb = tk.Listbox(
                grp_frame, 
                height=len(items), 
                font=("Helvetica", 9), 
                selectmode=tk.SINGLE,
                exportselection=False
            )
            for item in items:
                lb.insert(tk.END, item)
            lb.pack(fill=tk.X, expand=True, padx=5, pady=2)
            lb.bind("<<ListboxSelect>>", lambda event, current_lb=lb: self.on_menu_selected(current_lb))
            self.all_listboxes.append(lb)

        # 3. PANEL TENGAH (Form Parameter & Tampilan Output Data)
        right_frame = ttk.LabelFrame(paned, text=" Panel Eksekusi & Output ")
        paned.add(right_frame, weight=4)

        form_frame = ttk.Frame(right_frame)
        form_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Label(form_frame, text="Parameter (Indeks / OID / Ekspresi):").pack(side=tk.LEFT, padx=5)
        self.ent_index = ttk.Entry(form_frame, width=25)
        self.ent_index.insert(0, "0")
        self.ent_index.pack(side=tk.LEFT, padx=5)

        self.btn_eksekusi = ttk.Button(form_frame, text="JALANKAN PERINTAH", command=self.cmd_eksekusi)
        self.btn_eksekusi.pack(side=tk.LEFT, padx=10)

        self.txt_output = tk.Text(right_frame, font=("Consolas", 10), bg="#ffffff")
        self.txt_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 4. PANEL BAWAH (Log Perintah & Benchmarking Waktu)
        log_frame = ttk.LabelFrame(self.root, text=" Panel Performance & Command Log ")
        log_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(5, 10))

        self.txt_log = tk.Text(log_frame, height=5, font=("Consolas", 9), bg="#1e1e1e", fg="#00ff00")
        self.txt_log.pack(fill=tk.X, expand=True, padx=5, pady=5)

    # ==========================================
    # LOGIKA & ACTION HANDLER
    # ==========================================
    def write_log(self, modul, aksi, elapsed_ms, keterangan=""):
        msg = f"[{modul}] {aksi:<32} | Waktu: {elapsed_ms:8.2f} ms | {keterangan}\n"
        self.txt_log.insert(tk.END, msg)
        self.txt_log.see(tk.END)

    def cmd_load_data(self):
        path_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'pesanan.csv')
        
        t0 = time.perf_counter()
        self.semua_data_raw = muat_csv_pesanan(path_csv)
        
        # Reset dan isi ulang seluruh struktur data
        self.arr = DynamicArray()
        self.ll = LinkedList()
        self.q_naif = AntreanNaif()
        self.q_circular = AntreanMelingkar(kapasitas=32768)
        self.undo_naif = UndoRedoQueue(self.q_naif)
        self.undo_circular = UndoRedoQueue(self.q_circular)
        self.sorted_by_oid_cache = []
        
        for p in self.semua_data_raw:
            self.arr.tambah_reguler(p)
            self.ll.tambah_reguler(p)
            self.undo_naif.enqueue(p)
            self.undo_circular.enqueue(p)
        
        t1 = time.perf_counter()
        elapsed_ms = (t1 - t0) * 1000

        total_records = len(self.semua_data_raw)
        self.write_log("DATA", "Load CSV Pesanan", elapsed_ms, f"Total Data: {total_records} baris")
        
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"BERHASIL MEMUAT {total_records} DATA PESANAN DARI CSV.\n")
        self.txt_output.insert(tk.END, f"Data telah dimasukkan ke Dynamic Array, Linked List, serta Antrean M2.\n")
        messagebox.showinfo("Sukses", f"Berhasil memuat {total_records} data pesanan!")

    def on_menu_selected(self, active_lb):
        for lb in self.all_listboxes:
            if lb != active_lb:
                lb.selection_clear(0, tk.END)

        sel = active_lb.curselection()
        if not sel:
            return
        self.selected_menu_text = active_lb.get(sel[0])
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, f"Menu Terpilih: {self.selected_menu_text}\n")
        self.txt_output.insert(tk.END, "Tekan tombol 'JALANKAN PERINTAH' di atas untuk mengeksekusi.\n")

    def cmd_eksekusi(self):
        menu = self.selected_menu_text
        if not menu:
            messagebox.showwarning("Peringatan", "Pilih menu operasi di sebelah kiri dulu!")
            return

        if menu == "Load":
            self.cmd_load_data()
            return

        if self.arr.size == 0 and self.ll.size == 0:
            messagebox.showwarning("Peringatan", "Muat data CSV terlebih dahulu!")
            return

        input_val = self.ent_index.get().strip()
        idx = int(input_val) if input_val.isdigit() else 0

        self.txt_output.delete("1.0", tk.END)

        # ==========================================
        # M1 OPERASI (Array vs Linked List)
        # ==========================================
        if menu == "ARRAY - LIHAT PESANAN":
            t0 = time.perf_counter()
            res = self.arr.get(idx)
            t1 = time.perf_counter()
            self.write_log("M1-Array", f"Get Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[ARRAY GET {idx}]\n{res}\n")

        elif menu == "ARRAY - TAMBAH PESANAN REGULER":
            dummy = Pesanan("O-NEW-REG", "Pelanggan Baru", "Resto A", "Menu Reguler", 15000, 3, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_reguler(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah Reguler", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menambah pesanan REGULER.\nTotal size: {self.arr.size}\n")

        elif menu == "ARRAY - TAMBAH PESANAN PRIORITAS":
            dummy = Pesanan("O-NEW-PRIO", "Pelanggan Prio", "Resto B", "Menu Prio", 25000, 2, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_prioritas(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah Prioritas", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan PRIORITAS.\nTotal size: {self.arr.size}\n")

        elif menu == "ARRAY - TAMBAH PESANAN VIP":
            dummy = Pesanan("O-NEW-VIP", "Pelanggan VIP", "Resto C", "Menu VIP", 50000, 1, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.arr.tambah_vip(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-Array", "Tambah VIP", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan VIP.\nTotal size: {self.arr.size}\n")

        elif menu == "ARRAY - HAPUS PESANAN":
            t0 = time.perf_counter()
            res = self.arr.hapus(idx)
            t1 = time.perf_counter()
            self.write_log("M1-Array", f"Hapus Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[ARRAY HAPUS {idx}]\nData Terhapus: {res}\nSisa size: {self.arr.size}\n")

        elif menu == "LINKEDLIST - LIHAT PESANAN":
            t0 = time.perf_counter()
            res = self.ll.get(idx)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", f"Get Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[LINKED LIST GET {idx}]\n{res}\n")

        elif menu == "LINKEDLIST - TAMBAH PESANAN REGULER":
            dummy = Pesanan("O-NEW-REG", "Pelanggan Baru", "Resto A", "Menu Reguler", 15000, 3, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_reguler(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah Reguler", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menambah pesanan REGULER.\nTotal size: {self.ll.size}\n")

        elif menu == "LINKEDLIST - TAMBAH PESANAN PRIORITAS":
            dummy = Pesanan("O-NEW-PRIO", "Pelanggan Prio", "Resto B", "Menu Prio", 25000, 2, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_prioritas(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah Prioritas", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan PRIORITAS.\nTotal size: {self.ll.size}\n")

        elif menu == "LINKEDLIST - TAMBAH PESANAN VIP":
            dummy = Pesanan("O-NEW-VIP", "Pelanggan VIP", "Resto C", "Menu VIP", 50000, 1, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.ll.tambah_vip(dummy)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", "Tambah VIP", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Berhasil menyisipkan pesanan VIP.\nTotal size: {self.ll.size}\n")

        elif menu == "LINKEDLIST - HAPUS PESANAN":
            t0 = time.perf_counter()
            res = self.ll.hapus(idx)
            t1 = time.perf_counter()
            self.write_log("M1-LinkedList", f"Hapus Indeks {idx}", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"[LINKED LIST HAPUS {idx}]\nData Terhapus: {res}\nSisa size: {self.ll.size}\n")

        # ==========================================
        # M2 OPERASI (Stack, Postfix, Undo/Redo, Queue)
        # ==========================================
        elif menu == "STACK - POSTFIX (MESIN KASIR)":
            struk_infix = input_val if ("+" in input_val or "*" in input_val) else "(3*12000)+(2*8500)-5000"
            t0 = time.perf_counter()
            try:
                postfix, total = evaluasi_kasir(struk_infix)
                t1 = time.perf_counter()
                self.write_log("M2-Stack", "Kasir Postfix", (t1 - t0) * 1000)
                self.txt_output.insert(tk.END, f"Struk belanja (infix) : {struk_infix}\n")
                self.txt_output.insert(tk.END, f"Hasil Postfix         : {' '.join(postfix)}\n")
                self.txt_output.insert(tk.END, f"TOTAL HARGA           : Rp {total:,.0f}\n")
            except Exception as e:
                self.txt_output.insert(tk.END, f"[ERROR KASIR] {e}\n")

        elif menu == "QUEUE - ENQUEUE":
            dummy = Pesanan("O-NEW-Q", "Pelanggan Antrean", "Resto Q", "Menu Q", 15000, 3, 0, 0, "ANTRE")
            t0 = time.perf_counter()
            self.undo_naif.enqueue(dummy)
            self.undo_circular.enqueue(dummy)
            t1 = time.perf_counter()
            self.write_log("M2-Queue", "Enqueue", (t1 - t0) * 1000)
            self.txt_output.insert(tk.END, f"Pesanan {dummy.oid} masuk ke barisan belakang KEDUA antrean.\n")
            self.txt_output.insert(tk.END, f"Panjang antrean saat ini: Naif = {len(self.q_naif)}, Circular = {len(self.q_circular)}.\n")

        elif menu == "QUEUE - DEQUEUE NAIF":
            t0 = time.perf_counter()
            p = self.undo_naif.dequeue()
            t1 = time.perf_counter()
            if p:
                self.write_log("M2-Queue", "Dequeue Naif", (t1 - t0) * 1000, f"Geseran: {self.q_naif.total_geseran}")
                self.txt_output.insert(tk.END, f"[DEQUEUE NAIF]\n1 pesanan keluar dari depan antrean naif.\n")
                self.txt_output.insert(tk.END, f"Total elemen digeser: {self.q_naif.total_geseran}\n")
                self.txt_output.insert(tk.END, f"Sisa antrean naif: {len(self.q_naif)} pesanan.\n")
            else:
                self.txt_output.insert(tk.END, "Antrean Naif Kosong.\n")

        elif menu == "QUEUE - DEQUEUE CIRCULAR":
            t0 = time.perf_counter()
            p = self.undo_circular.dequeue()
            t1 = time.perf_counter()
            if p:
                self.write_log("M2-Queue", "Dequeue Circular", (t1 - t0) * 1000)
                self.txt_output.insert(tk.END, f"[DEQUEUE CIRCULAR]\n1 pesanan keluar dari depan antrean circular.\n")
                self.txt_output.insert(tk.END, f"Tidak ada elemen yang digeser (Front = {self.q_circular.front}, Rear = {self.q_circular.rear}).\n")
                self.txt_output.insert(tk.END, f"Sisa antrean circular: {len(self.q_circular)} pesanan.\n")
            else:
                self.txt_output.insert(tk.END, "Antrean Circular Kosong.\n")
                
        elif menu == "STACK - UNDO":
            t0 = time.perf_counter()
            res_naif = self.undo_naif.undo_last()
            res_circ = self.undo_circular.undo_last()
            t1 = time.perf_counter()
            if res_naif and res_circ:
                self.write_log("M2-Stack", "Undo Last", (t1 - t0) * 1000)
                u_cnt, r_cnt = self.undo_circular.history()
                self.txt_output.insert(tk.END, f"[STACK UNDO]\nAksi terakhir berhasil dibatalkan.\n")
                self.txt_output.insert(tk.END, f"Riwayat -> Undo Depth: {u_cnt}, Redo Depth: {r_cnt}\n")
                self.txt_output.insert(tk.END, f"Panjang Antrean saat ini: Naif = {len(self.q_naif)}, Circular = {len(self.q_circular)}.\n")
            else:
                self.txt_output.insert(tk.END, "Tumpukan Undo kosong.\n")

        elif menu == "STACK - REDO":
            t0 = time.perf_counter()
            res_naif = self.undo_naif.redo_last()
            res_circ = self.undo_circular.redo_last()
            t1 = time.perf_counter()
            if res_naif and res_circ:
                self.write_log("M2-Stack", "Redo Last", (t1 - t0) * 1000)
                u_cnt, r_cnt = self.undo_circular.history()
                self.txt_output.insert(tk.END, f"[STACK REDO]\nAksi yang dibatalkan dikerjakan ulang.\n")
                self.txt_output.insert(tk.END, f"Riwayat -> Undo Depth: {u_cnt}, Redo Depth: {r_cnt}\n")
                self.txt_output.insert(tk.END, f"Panjang Antrean saat ini: Naif = {len(self.q_naif)}, Circular = {len(self.q_circular)}.\n")
            else:
                self.txt_output.insert(tk.END, "Tumpukan Redo kosong.\n")

        # ==========================================
        # M3 OPERASI (Sort & Search)
        # ==========================================
        elif menu == "SORT - INSERTION SORT":
            jumlah = (
                int(input_val)
                if (input_val.isdigit() and int(input_val) > 0)
                else self.arr.size
            )

            self.txt_output.insert(
                tk.END,
                f"> insertion_sort   jumlah={jumlah}   kunci=harga\n",
            )

            if jumlah > 20000:
                self.txt_output.insert(
                    tk.END,
                    "DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh\n\n",
                )
            else:
                data_sample = [self.arr.get(i) for i in range(jumlah)]
                t0 = time.perf_counter()
                sorted_res, banding, pindah = insertion_sort(
                    data_sample, kunci="harga"
                )
                t1 = time.perf_counter()
                ms = (t1 - t0) * 1000

                self.txt_output.insert(
                    tk.END,
                    f"{fmt_ribuan(jumlah)} pesanan terurut | {fmt_ribuan(banding)} perbandingan   [M3 - insertion sort] {fmt_waktu(ms)}\n\n",
                )
                self.write_log("M3-Sort", f"Insertion Sort ({jumlah})", ms)

        elif menu == "SORT - MERGE SORT":
            jumlah = (
                int(input_val)
                if (input_val.isdigit() and int(input_val) > 0)
                else self.arr.size
            )

            self.txt_output.insert(
                tk.END, f"> merge_sort   jumlah={jumlah}   kunci=harga\n"
            )

            data_sample = [self.arr.get(i) for i in range(jumlah)]
            t0 = time.perf_counter()
            sorted_res, banding, pindah = merge_sort(data_sample, kunci="harga")
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            self.txt_output.insert(
                tk.END,
                f"{fmt_ribuan(jumlah)} pesanan terurut | {fmt_ribuan(banding)} perbandingan   [M3 - merge sort] {fmt_waktu(ms)}\n\n",
            )
            self.write_log("M3-Sort", f"Merge Sort ({jumlah})", ms)

        elif menu == "SEARCH - LINEAR SEARCH":
            data_all = [self.arr.get(i) for i in range(self.arr.size)]

            if input_val.isdigit() and int(input_val) < len(data_all):
                target_oid = data_all[int(input_val)].oid
            else:
                target_oid = input_val if input_val else data_all[-1].oid

            self.txt_output.insert(tk.END, f"> linear_search   {target_oid}\n")

            t0 = time.perf_counter()
            idx_found, banding = linear_search(
                data_all, target_oid, kunci="oid"
            )
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            if idx_found != -1:
                self.txt_output.insert(
                    tk.END,
                    f"ditemukan di indeks {fmt_ribuan(idx_found)} | {fmt_ribuan(banding)} perbandingan   [M3 - linear] {fmt_waktu(ms)}\n\n",
                )
            else:
                self.txt_output.insert(
                    tk.END,
                    f"tidak ditemukan | {fmt_ribuan(banding)} perbandingan   [M3 - linear] {fmt_waktu(ms)}\n\n",
                )

            self.write_log("M3-Search", "Linear Search", ms)

        elif menu == "SEARCH - BINARY SEARCH":
            data_all = [self.arr.get(i) for i in range(self.arr.size)]

            if input_val.isdigit() and int(input_val) < len(data_all):
                target_oid = data_all[int(input_val)].oid
            else:
                target_oid = input_val if input_val else data_all[-1].oid

            self.txt_output.insert(tk.END, f"> binary_search   {target_oid}\n")

            if not self.sorted_by_oid_cache or len(
                self.sorted_by_oid_cache
            ) != len(data_all):
                t_c0 = time.perf_counter()
                self.sorted_by_oid_cache, _, _ = merge_sort(
                    data_all, kunci="oid"
                )
                t_c1 = time.perf_counter()
                ms_cache = (t_c1 - t_c0) * 1000
                self.txt_output.insert(
                    tk.END,
                    f"daftar terurut oid dibangun sekali (merge sort)   {fmt_waktu(ms_cache)}\n",
                )

            t0 = time.perf_counter()
            idx_found, banding = binary_search(
                self.sorted_by_oid_cache, target_oid, kunci="oid"
            )
            t1 = time.perf_counter()
            ms = (t1 - t0) * 1000

            if idx_found != -1:
                self.txt_output.insert(
                    tk.END,
                    f"ditemukan di baris {fmt_ribuan(idx_found)} | {fmt_ribuan(banding)} perbandingan   [M3 - binary] {fmt_waktu(ms)}\n\n",
                )
            else:
                self.txt_output.insert(
                    tk.END,
                    f"tidak ditemukan | {fmt_ribuan(banding)} perbandingan   [M3 - binary] {fmt_waktu(ms)}\n\n",
                )

            self.write_log("M3-Search", "Binary Search", ms)

if __name__ == "__main__":
    root = tk.Tk()
    app = App2EZ4U(root)
    root.mainloop()