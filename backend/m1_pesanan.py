# backend/m1_pesanan.py
import csv


class Pesanan:
    """Wadah data pesanan per baris (pengganti dict)."""
    __slots__ = (
        'oid', 'pelanggan', 'resto', 'menu', 'harga',
        'prioritas', 't_masuk_detik', 't_selesai_detik', 'status'
    )

    def __init__(self, oid, pelanggan, resto, menu, harga, prioritas, t_masuk, t_selesai, status):
        self.oid = oid
        self.pelanggan = pelanggan
        self.resto = resto
        self.menu = menu
        self.harga = int(harga) if harga else 0
        self.prioritas = int(prioritas) if prioritas else 3
        self.t_masuk_detik = int(t_masuk) if t_masuk else 0
        self.t_selesai_detik = int(t_selesai) if (t_selesai and t_selesai != "") else None
        self.status = status

    def __repr__(self):
        return f"[{self.oid}] {self.pelanggan} - {self.menu} (P{self.prioritas}) - {self.status}"


class Array:
    """
    Array dinamis berbasis contiguous memory dengan doubling capacity:
    - append (Reguler): O(1) amortized
    - insert tengah (Prioritas): O(n) geser elemen
    - insert depan (VIP): O(n) geser seluruh elemen
    - get: O(1)
    - delete: O(n)
    """
    def __init__(self, kapasitas_awal=4):
        self.kapasitas = kapasitas_awal
        self.size = 0
        self.data = [None] * self.kapasitas

    def _resize(self, kapasitas_baru):
        petak_baru = [None] * kapasitas_baru
        for i in range(self.size):
            petak_baru[i] = self.data[i]
        self.data = petak_baru
        self.kapasitas = kapasitas_baru

    def append(self, val):
        """Pesanan REGULER: masuk barisan paling belakang."""
        if self.size == self.kapasitas:
            self._resize(self.kapasitas * 2)
        self.data[self.size] = val
        self.size += 1

    def insert(self, idx, val):
        """
        Sisip pesanan:
        - VIP: idx = 0
        - PRIORITAS: idx = self.size // 2
        """
        if idx < 0 or idx > self.size:
            raise IndexError("Indeks di luar jangkauan")

        if self.size == self.kapasitas:
            self._resize(self.kapasitas * 2)

        for i in range(self.size, idx, -1):
            self.data[i] = self.data[i - 1]

        self.data[idx] = val
        self.size += 1

    def get(self, idx):
        if idx < 0 or idx >= self.size:
            raise IndexError("Indeks di luar jangkauan")
        return self.data[idx]

    def delete(self, idx):
        if idx < 0 or idx >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        item_terhapus = self.data[idx]
        for i in range(idx, self.size - 1):
            self.data[i] = self.data[i + 1]

        self.data[self.size - 1] = None
        self.size -= 1
        return item_terhapus

    def __len__(self):
        return self.size


class Node:
    __slots__ = ('data', 'next')
    def __init__(self, data=None):
        self.data = data
        self.next = None


class LinkList:
    """
    Singly Linked List dengan pointer head dan tail:
    - append (Reguler): O(1) via tail
    - insert tengah (Prioritas): O(n) telusur simpul
    - insert depan (VIP): O(1) ubah pointer head
    - get: O(n) telusur simpul
    - delete: O(n)
    """
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, val):
        """Pesanan REGULER: tempel di tail."""
        node_baru = Node(val)
        if self.head is None:
            self.head = node_baru
            self.tail = node_baru
        else:
            self.tail.next = node_baru
            self.tail = node_baru
        self.size += 1

    def insert(self, idx, val):
        """
        Sisip pesanan:
        - VIP: idx = 0 (O(1))
        - PRIORITAS: idx = self.size // 2 (O(n) telusur)
        """
        if idx < 0 or idx > self.size:
            raise IndexError("Indeks di luar jangkauan")

        node_baru = Node(val)

        # Kasus VIP: masuk paling depan
        if idx == 0:
            node_baru.next = self.head
            self.head = node_baru
            if self.size == 0:
                self.tail = node_baru
            self.size += 1
            return

        # Kasus REGULER lewat insert
        if idx == self.size:
            self.append(val)
            return

        # Kasus PRIORITAS: cari simpul tepat sebelum posisi target
        bantu = self.head
        for _ in range(idx - 1):
            bantu = bantu.next

        node_baru.next = bantu.next
        bantu.next = node_baru
        self.size += 1

    def get(self, idx):
        if idx < 0 or idx >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        bantu = self.head
        for _ in range(idx):
            bantu = bantu.next
        return bantu.data

    def delete(self, idx):
        if idx < 0 or idx >= self.size:
            raise IndexError("Indeks di luar jangkauan")

        if idx == 0:
            item_terhapus = self.head.data
            self.head = self.head.next
            if self.size == 1:
                self.tail = None
            self.size -= 1
            return item_terhapus

        bantu = self.head
        for _ in range(idx - 1):
            bantu = bantu.next

        item_terhapus = bantu.next.data
        if bantu.next == self.tail:
            self.tail = bantu
        bantu.next = bantu.next.next
        self.size -= 1
        return item_terhapus

    def __len__(self):
        return self.size


def baca_csv_pesanan(path_file, batas=None):
    """Fungsi pembantu membaca baris data/pesanan.csv ke list objek Pesanan."""
    daftar = []
    with open(path_file, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        _ = next(reader)  # skip header
        hitung = 0
        for baris in reader:
            if not baris:
                continue
            p = Pesanan(
                oid=baris[0],
                pelanggan=baris[1],
                resto=baris[2],
                menu=baris[3],
                harga=baris[4],
                prioritas=baris[5],
                t_masuk=baris[6],
                t_selesai=baris[7],
                status=baris[8]
            )
            daftar.append(p)
            hitung += 1
            if batas and hitung >= batas:
                break
    return daftar