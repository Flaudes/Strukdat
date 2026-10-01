import csv
import os

path_csv = os.path.join(os.path.dirname(__file__), '..', 'data', 'pesanan.csv')

class Pesanan:
    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = int(harga)
        self.prioritas = int(prioritas)  # 1: VIP, 2: Prioritas, 3: Reguler
        self.t_masuk_detik = int(t_masuk) if t_masuk else 0
        self.t_selesai_detik = int(t_selesai) if t_selesai else 0
        self.status = status

    def __repr__(self):
        return f"[{self.oid}] {self.pelanggan} - {self.menu} (Prio: {self.prioritas})"
    
def muat_csv_pesanan(path_csv):
    daftar = []
    if not os.path.exists(path_csv):
        print(f"File '{path_csv}' tidak ditemukan!")
        return daftar

    with open(path_csv, 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        next(reader, None)
        for cols in reader:
            if not cols or len(cols) < 9:
                continue
                
            p = Pesanan(
                oid=cols[0].strip(),
                pelanggan=cols[1].strip(),
                resto=cols[2].strip(),
                menu=cols[3].strip(),
                harga=cols[4].strip(),
                prioritas=cols[5].strip(),
                t_masuk=cols[6].strip(),
                t_selesai=cols[7].strip(),
                status=cols[8].strip()
            )
            daftar.append(p)
    return daftar

print({path_csv})
semua_data = muat_csv_pesanan(path_csv)
print(f"Total data CSV terbaca: {len(semua_data)} baris.")