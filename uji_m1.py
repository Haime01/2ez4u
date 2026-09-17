# uji_m1.py
import time
from backend.m1_pesanan import Array, LinkList, Pesanan, baca_csv_pesanan

print("Membaca 50.000 sampel data awal...")
data_sampel = baca_csv_pesanan("data/pesanan.csv", batas=50000)
print(f"Selesai membaca {len(data_sampel)} data.")

arr = Array()
ll = LinkList()

for p in data_sampel:
    arr.append(p)
    ll.append(p)

pesanan_vip = Pesanan("VIP-01", "Pelanggan Sultan", "resto-a", "steak", 150000, 1, 1000, None, "ANTRE")
pesanan_prio = Pesanan("PRIO-01", "Pelanggan Cepat", "resto-b", "kopi", 25000, 2, 1001, None, "ANTRE")

# 1. Adu Tambah VIP (Paling Depan)
t0 = time.perf_counter()
arr.insert(0, pesanan_vip)
t_arr_vip = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
ll.insert(0, pesanan_vip)
t_ll_vip = (time.perf_counter() - t0) * 1000

# 2. Adu Tambah PRIORITAS (Tengah)
t0 = time.perf_counter()
arr.insert(len(arr) // 2, pesanan_prio)
t_arr_prio = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
ll.insert(len(ll) // 2, pesanan_prio)
t_ll_prio = (time.perf_counter() - t0) * 1000

# 3. Adu Akses Indeks Tengah
idx_tengah = len(arr) // 2
t0 = time.perf_counter()
_ = arr.get(idx_tengah)
t_arr_get = (time.perf_counter() - t0) * 1000

t0 = time.perf_counter()
_ = ll.get(idx_tengah)
t_ll_get = (time.perf_counter() - t0) * 1000

print("\n--- HASIL BENCHMARK M1 ---")
print(f"VIP (Depan)      -> Array: {t_arr_vip:.4f} ms | LinkedList: {t_ll_vip:.4f} ms")
print(f"PRIORITAS (Mid)  -> Array: {t_arr_prio:.4f} ms | LinkedList: {t_ll_prio:.4f} ms")
print(f"Akses get({idx_tengah}) -> Array: {t_arr_get:.4f} ms | LinkedList: {t_ll_get:.4f} ms")