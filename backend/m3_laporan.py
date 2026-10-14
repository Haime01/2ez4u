# backend/m3_laporan.py

def _ambil_kunci(pesanan, kunci: str):
    """Mengambil nilai atribut dari objek Pesanan sesuai nama kunci."""
    if kunci == "oid":
        return str(getattr(pesanan, "oid", ""))
    elif kunci == "harga":
        return int(getattr(pesanan, "harga", 0))
    elif kunci in ("selesai", "t_selesai_detik"):
        val = getattr(pesanan, "t_selesai_detik", None)
        # Jika kosong/CANCEL/ANTRE, taruh di urutan paling akhir (nilai besar)
        if val is None or val == "" or val == "-":
            return 999999999
        return int(val)
    return str(getattr(pesanan, kunci, ""))


def insertion_sort(larik_input, kunci="harga"):
    """
    Insertion Sort yang stabil (O(n^2)).
    Mengembalikan: (hasil_list, jml_perbandingan, jml_pemindahan)
    Batas aman: maksimal 20.000 baris.
    """
    n = len(larik_input)
    if n > 20000:
        raise ValueError("DITOLAK: batasnya 20.000 baris, pakai merge sort untuk data penuh.")

    # Salin ke list kerja agar data asli M1 tidak rusak
    A = [larik_input[i] for i in range(n)]
    perbandingan = 0
    pemindahan = 0

    for i in range(1, n):
        item_sekarang = A[i]
        kunci_sekarang = _ambil_kunci(item_sekarang, kunci)
        j = i - 1

        while j >= 0:
            perbandingan += 1
            # Pakai '>' (bukan '>=') agar STABIL
            if _ambil_kunci(A[j], kunci) > kunci_sekarang:
                A[j + 1] = A[j]
                pemindahan += 1
                j -= 1
            else:
                break

        A[j + 1] = item_sekarang
        if j + 1 != i:
            pemindahan += 1

    return A, perbandingan, pemindahan


def merge_sort(larik_input, kunci="oid"):
    """
    Merge Sort yang stabil (O(n log n)).
    Mengembalikan: (hasil_list, jml_perbandingan, jml_pemindahan)
    """
    n = len(larik_input)
    A = [larik_input[i] for i in range(n)]
    statistik = [0, 0]  # [perbandingan, pemindahan]

    def _urutkan(arr):
        if len(arr) <= 1:
            return arr

        mid = len(arr) // 2
        kiri = _urutkan(arr[:mid])
        kanan = _urutkan(arr[mid:])
        return _gabung(kiri, kanan)

    def _gabung(kiri, kanan):
        hasil = []
        i = 0
        j = 0
        len_kiri = len(kiri)
        len_kanan = len(kanan)

        while i < len_kiri and j < len_kanan:
            statistik[0] += 1  # 1 perbandingan
            # Pakai '<=' agar elemen kiri didahulukan jika sama (STABIL)
            if _ambil_kunci(kiri[i], kunci) <= _ambil_kunci(kanan[j], kunci):
                hasil.append(kiri[i])
                i += 1
            else:
                hasil.append(kanan[j])
                j += 1
            statistik[1] += 1  # 1 pemindahan

        # Salin sisa elemen kiri (jika ada)
        while i < len_kiri:
            hasil.append(kiri[i])
            i += 1
            statistik[1] += 1

        # Salin sisa elemen kanan (jika ada)
        while j < len_kanan:
            hasil.append(kanan[j])
            j += 1
            statistik[1] += 1

        return hasil

    terurut = _urutkan(A)
    return terurut, statistik[0], statistik[1]


def linear_search(larik_input, target_oid: str):
    """
    Linear Search O(n): menelusuri satu per satu dari indeks 0.
    Mengembalikan: (indeks_ketemu, objek_pesanan, jml_perbandingan)
    """
    n = len(larik_input)
    perbandingan = 0

    for i in range(n):
        perbandingan += 1
        item = larik_input[i]
        if getattr(item, "oid", "") == target_oid:
            return i, item, perbandingan

    return -1, None, perbandingan


def binary_search(larik_terurut_oid, target_oid: str):
    """
    Binary Search O(log n): menuntut larik sudah terurut menurut oid.
    Mengembalikan: (indeks_ketemu, objek_pesanan, jml_perbandingan)
    """
    lo = 0
    hi = len(larik_terurut_oid) - 1
    perbandingan = 0

    while lo <= hi:
        mid = (lo + hi) // 2
        perbandingan += 1
        mid_oid = getattr(larik_terurut_oid[mid], "oid", "")

        if mid_oid == target_oid:
            return mid, larik_terurut_oid[mid], perbandingan
        elif mid_oid < target_oid:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, None, perbandingan