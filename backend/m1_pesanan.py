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
    return daftar                                                   # Buat baca data di csv

class DynamicArray:                                     # Metode Array 
    def __init__(self, capacity=4):
        self.capacity = capacity
        self.size = 0
        self.data = [None] * capacity

    def _resize(self, new_capacity):
        new_data = [None] * new_capacity
        for i in range(self.size):
            new_data[i] = self.data[i]
        self.data = new_data
        self.capacity = new_capacity

    def get(self, index):  # O(1)
        if 0 <= index < self.size:
            return self.data[index]
        return None

    def tambah_reguler(self, item):  # O(1) - Masuk paling belakang
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        self.data[self.size] = item
        self.size += 1

    def tambah_vip(self, item):  # O(n) - Masuk paling depan (menggeser semua elemen ke kanan)
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        for i in range(self.size, 0, -1):
            self.data[i] = self.data[i-1]
        self.data[0] = item
        self.size += 1

    def tambah_prioritas(self, item):  # O(n) - Masuk ke tengah barisan
        if self.size == self.capacity:
            self._resize(self.capacity * 2)
        mid = self.size // 2
        for i in range(self.size, mid, -1):
            self.data[i] = self.data[i-1]
        self.data[mid] = item
        self.size += 1

    def hapus(self, index):  # O(n) - Hapus dan geser elemen tersisa ke kiri
        if not (0 <= index < self.size):
            return None
        val = self.data[index]
        for i in range(index, self.size - 1):
            self.data[i] = self.data[i+1]
        self.data[self.size - 1] = None
        self.size -= 1
        return val

class Node:                             # Metode LinkedList
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def get(self, index):  # O(n) - Penelusuran simpul
        if not (0 <= index < self.size):
            return None
        curr = self.head
        for _ in range(index):
            curr = curr.next
        return curr.data

    def tambah_reguler(self, item):  # O(1) via pointer tail
        new_node = Node(item)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.size += 1

    def tambah_vip(self, item):  # O(1) via pointer head
        new_node = Node(item)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            new_node.next = self.head
            self.head = new_node
        self.size += 1

    def tambah_prioritas(self, item):  # O(n) - Penelusuran ke pertengahan
        if self.size == 0 or self.size == 1:
            self.tambah_vip(item)
            return
        mid = self.size // 2
        new_node = Node(item)
        curr = self.head
        for _ in range(mid - 1):
            curr = curr.next
        new_node.next = curr.next
        curr.next = new_node
        self.size += 1

    def hapus(self, index):  # O(n) - Menelusuri dan memutus rantai
        if not (0 <= index < self.size):
            return None
            
        if index == 0:
            val = self.head.data
            self.head = self.head.next
            if not self.head:
                self.tail = None
            self.size -= 1
            return val

        curr = self.head
        for _ in range(index - 1):
            curr = curr.next
            
        val = curr.next.data
        if curr.next == self.tail:
            self.tail = curr
            
        curr.next = curr.next.next
        self.size -= 1
        return val




