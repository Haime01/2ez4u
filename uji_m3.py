# uji_m3.py
from backend.m1_pesanan import Pesanan
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search

def buat_dummy():
    return [
        Pesanan("O-000005", "Budi", "resto-a", "nasi", 20000, 1, 100, 200, "DONE"),
        Pesanan("O-000002", "Siti", "resto-b", "mie", 11000, 3, 110, 250, "DONE"),
        Pesanan("O-000009", "Andi", "resto-c", "kopi", 11000, 3, 120, 300, "DONE"),
        Pesanan("O-000001", "Rina", "resto-a", "roti", 12000, 2, 130, "", "CANCEL"),
    ]

def test_sort_stabil():
    data = buat_dummy()
    hasil_ins, komp_i, _ = insertion_sort(data, "harga")
    hasil_mrg, komp_m, _ = merge_sort(data, "harga")

    # Cek urutan oid harus sama persis (stabil: O-000002 sebelum O-000009 karena harga sama 11000)
    oid_ins = [p.oid for p in hasil_ins]
    oid_mrg = [p.oid for p in hasil_mrg]
    assert oid_ins == oid_mrg == ["O-000002", "O-000009", "O-000001", "O-000005"]
    print(f"[OK] Kedua sort stabil & identik! (Insertion: {komp_i} komp, Merge: {komp_m} komp)")

def test_search():
    data = buat_dummy()
    terurut_oid, _, _ = merge_sort(data, "oid")

    # 1. Kasus kiri, tengah, kanan, tidak ada, dan larik kosong
    for target in ["O-000001", "O-000005", "O-000009", "O-999999"]:
        idx_l, _, _ = linear_search(terurut_oid, target)
        idx_b, _, _ = binary_search(terurut_oid, target)
        assert idx_l == idx_b, f"Mismatch pada {target}"

    idx_kosong, _, _ = binary_search([], "O-000001")
    assert idx_kosong == -1
    print("[OK] Linear & Binary Search lolos semua kasus uji!")

if __name__ == "__main__":
    test_sort_stabil()
    test_search()