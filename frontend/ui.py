# frontend/ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
from backend.m1_pesanan import Array, LinkList, Pesanan, baca_csv_pesanan
from backend.m2_antrean import ke_postfix, hitung, NaiveQueue, CircularQueue, UndoRedoManager
from backend.m3_laporan import insertion_sort, merge_sort, linear_search, binary_search

class App2EZ4U:
    def __init__(self, root):
        self.root = root
        self.root.title("2EZ4U Food Delivery")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        # Backend storage untuk M1
        self.arr_pesanan = Array()
        self.ll_pesanan = LinkList()
        self.data_termuat = False

        # Backend storage untuk M2
        self.naive_q = NaiveQueue()
        self.circ_q = CircularQueue(capacity=100000)
        self.undo_manager = UndoRedoManager(self.circ_q)
        # Backend storage untuk M3
        self.cache_terurut_oid = None
        self.waktu_bangun_oid_ms = 0.0

        self._buat_layout()
        self._set_mode_default()
        # Otomatis load data CSV0.1 detik setelah jendela tampil
        # Otomatis load data CSV 0.1 detik setelah jendela tampil
        self.root.after(100, lambda: self._menu_load_data(auto_run=True))

    def _buat_layout(self):
        # 1. Header Banner
        header = tk.Frame(self.root, bg="#1d3557", height=45)
        header.pack(fill=tk.X, side=tk.TOP)
        lbl_title = tk.Label(
            header, text="2EZ4U Food Delivery",
            fg="white", bg="#1d3557", font=("Segoe UI", 14, "bold")
        )
        lbl_title.pack(side=tk.LEFT, padx=15, pady=8)

        # Container Utama (Kiri + Kanan)
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        # 2. Sidebar Kiri (Daftar Menu Navigasi)
        sidebar_frame = tk.Frame(main_container, width=280, bg="#f1f5f9", bd=1, relief=tk.SOLID)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar_frame.pack_propagate(False)

        canvas = tk.Canvas(sidebar_frame, bg="#f1f5f9", highlightthickness=0)
        scrollbar = ttk.Scrollbar(sidebar_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scroll_sidebar = tk.Frame(canvas, bg="#f1f5f9")

        self.scroll_sidebar.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scroll_sidebar, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._isi_menu_sidebar()

        # 3. Area Kanan (Form Parameter + Tampilan Hasil)
        kanan_container = tk.Frame(main_container, bg="white")
        kanan_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Form
        self.lbl_form_title = tk.Label(
            kanan_container, text="Pilih menu di sisi kiri",
            font=("Segoe UI", 12, "bold"), bg="white", anchor="w"
        )
        self.lbl_form_title.pack(fill=tk.X, pady=(0, 5))

        self.lbl_form_desc = tk.Label(
            kanan_container, text="-",
            font=("Segoe UI", 9), fg="#64748b", bg="white", anchor="w"
        )
        self.lbl_form_desc.pack(fill=tk.X, pady=(0, 10))

        # Panel Input Form
        self.frame_input = tk.Frame(kanan_container, bg="white")
        self.frame_input.pack(fill=tk.X, pady=(0, 10))

        # Output Teks / Hasil
        lbl_hasil = tk.Label(kanan_container, text="Hasil Tampilan:", font=("Segoe UI", 10, "bold"), bg="white", anchor="w")
        lbl_hasil.pack(fill=tk.X)

        frame_output = tk.Frame(kanan_container)
        frame_output.pack(fill=tk.BOTH, expand=True)

        self.txt_output = tk.Text(frame_output, wrap=tk.NONE, font=("Consolas", 10))
        scroll_y = ttk.Scrollbar(frame_output, orient=tk.VERTICAL, command=self.txt_output.yview)
        scroll_x = ttk.Scrollbar(frame_output, orient=tk.HORIZONTAL, command=self.txt_output.xview)
        self.txt_output.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        self.txt_output.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        frame_output.grid_rowconfigure(0, weight=1)
        frame_output.grid_columnconfigure(0, weight=1)

        # 4. Panel Command Log di Bawah
        frame_bottom = tk.Frame(self.root, height=130, bg="#f8fafc", bd=1, relief=tk.SOLID)
        frame_bottom.pack(fill=tk.X, side=tk.BOTTOM)
        frame_bottom.pack_propagate(False)

        lbl_cmd = tk.Label(frame_bottom, text="COMMAND / LOG AKTIVITAS:", font=("Segoe UI", 9, "bold"), bg="#f8fafc")
        lbl_cmd.pack(anchor="w", padx=10, pady=(5, 0))

        self.txt_cmd = tk.Text(frame_bottom, height=4, bg="#0f172a", fg="#38bdf8", font=("Consolas", 9))
        self.txt_cmd.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def _tombol_sidebar(self, teks, perintah, bg="#e2e8f0"):
        btn = tk.Button(
            self.scroll_sidebar, text=teks, command=perintah,
            anchor="w", bg=bg, fg="#0f172a", font=("Segoe UI", 8, "bold"),
            relief=tk.FLAT, padx=8, pady=1, cursor="hand2"
        )
        btn.pack(fill=tk.X, padx=6, pady=1)
        return btn

    def _isi_menu_sidebar(self):
        lbl_data = tk.Label(self.scroll_sidebar, text="DATA", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f1f5f9")
        lbl_data.pack(anchor="w", padx=8, pady=(8, 2))
        self._tombol_sidebar("LOAD DATA (CSV)", self._menu_load_data, bg="#cbd5e1")

        # Milestone 1: Array
        lbl_m1_arr = tk.Label(self.scroll_sidebar, text="M1 - DATA PESANAN (ARRAY)", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f1f5f9")
        lbl_m1_arr.pack(anchor="w", padx=8, pady=(12, 2))
        self._tombol_sidebar("ARRAY - LIHAT PESANAN", lambda: self._tampilkan_form_lihat("ARRAY"))
        self._tombol_sidebar("ARRAY - TAMBAH PESANAN REGULER", lambda: self._tampilkan_form_tambah("ARRAY", 3))
        self._tombol_sidebar("ARRAY - TAMBAH PESANAN PRIORITAS", lambda: self._tampilkan_form_tambah("ARRAY", 2))
        self._tombol_sidebar("ARRAY - TAMBAH PESANAN VIP", lambda: self._tampilkan_form_tambah("ARRAY", 1))
        self._tombol_sidebar("ARRAY - HAPUS PESANAN", lambda: self._tampilkan_form_hapus("ARRAY"))

        # Milestone 1: LinkedList
        lbl_m1_ll = tk.Label(self.scroll_sidebar, text="M1 - DATA PESANAN (LINKEDLIST)", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f1f5f9")
        lbl_m1_ll.pack(anchor="w", padx=8, pady=(12, 2))
        self._tombol_sidebar("LINKEDLIST - LIHAT PESANAN", lambda: self._tampilkan_form_lihat("LINKEDLIST"))
        self._tombol_sidebar("LINKEDLIST - TAMBAH PESANAN REGULER", lambda: self._tampilkan_form_tambah("LINKEDLIST", 3))
        self._tombol_sidebar("LINKEDLIST - TAMBAH PESANAN PRIORITAS", lambda: self._tampilkan_form_tambah("LINKEDLIST", 2))
        self._tombol_sidebar("LINKEDLIST - TAMBAH PESANAN VIP", lambda: self._tampilkan_form_tambah("LINKEDLIST", 1))
        self._tombol_sidebar("LINKEDLIST - HAPUS PESANAN", lambda: self._tampilkan_form_hapus("LINKEDLIST"))
        # Milestone 2: Antrean & Stack
        lbl_m2 = tk.Label(self.scroll_sidebar, text="M2 - ANTREAN & STACK", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f1f5f9")
        lbl_m2.pack(anchor="w", padx=8, pady=(12, 2))
        self._tombol_sidebar("MESIN KASIR (POSTFIX)", self._tampilkan_form_kasir)
        self._tombol_sidebar("BENCHMARK ANTREAN (QUEUE)", self._tampilkan_form_benchmark_queue)
        self._tombol_sidebar("ANTREAN DAPUR (UNDO/REDO)", self._tampilkan_form_antrean_dapur)
        # Milestone 3: Sort & Search
        lbl_m3 = tk.Label(self.scroll_sidebar, text="M3 - SORT DAN SEARCH", font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#f1f5f9")
        lbl_m3.pack(anchor="w", padx=8, pady=(12, 2))
        self._tombol_sidebar("SORT - INSERTION SORT", lambda: self._tampilkan_form_sort("INSERTION"))
        self._tombol_sidebar("SORT - MERGE SORT", lambda: self._tampilkan_form_sort("MERGE"))
        self._tombol_sidebar("SEARCH - LINEAR SEARCH", self._tampilkan_form_linear_search)
        self._tombol_sidebar("SEARCH - BINARY SEARCH", self._tampilkan_form_binary_search)

    def _catat_log(self, modul, aksi, durasi_ms):
        pesan = f"[{modul}] {aksi:<30} -> Waktu eksekusi: {durasi_ms:.4f} ms\n"
        self.txt_cmd.insert(tk.END, pesan)
        self.txt_cmd.see(tk.END)

    def _set_mode_default(self):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "Silakan muat data pesanan terlebih dahulu lewat menu 'LOAD DATA (CSV)'.\n")

    # ==================== OPERASI DATA ====================
    def _menu_load_data(self, auto_run=False):
        for widget in self.frame_input.winfo_children():
            widget.destroy()

        self.lbl_form_title.config(text="Muat Data CSV")
        self.lbl_form_desc.config(text="Membaca data/pesanan.csv ke dalam Array dan LinkedList secara paralel.")

        tk.Label(self.frame_input, text="Batas Baris Data (contoh: 20000 atau kosongkan untuk semua):", bg="white").pack(anchor="w")
        ent_limit = ttk.Entry(self.frame_input, width=25)
        ent_limit.insert(0, "")
        ent_limit.pack(anchor="w", pady=4)

        def proses_muat():
            teks_limit = ent_limit.get().strip()
            batas = int(teks_limit) if teks_limit.isdigit() else None

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Memuat data (Batas: {batas if batas else '200.000'})...\n")
            self.root.update()
            self.cache_terurut_oid = None
            t0 = time.perf_counter()
            data = baca_csv_pesanan("data/pesanan.csv", batas=batas)
            durasi_baca = (time.perf_counter() - t0) * 1000

            # Inisialisasi ulang
            self.arr_pesanan = Array(kapasitas_awal=max(4, len(data)))
            self.ll_pesanan = LinkList()

            t0_arr = time.perf_counter()
            for p in data:
                self.arr_pesanan.append(p)
            d_arr = (time.perf_counter() - t0_arr) * 1000

            t0_ll = time.perf_counter()
            for p in data:
                self.ll_pesanan.append(p)
            d_ll = (time.perf_counter() - t0_ll) * 1000

            self.data_termuat = True
            self.txt_output.insert(tk.END, f"Berhasil memuat {len(data)} pesanan!\n")
            self.txt_output.insert(tk.END, f"- Baca CSV : {durasi_baca:.2f} ms\n")
            self.txt_output.insert(tk.END, f"- Isi Array: {d_arr:.2f} ms\n")
            self.txt_output.insert(tk.END, f"- Isi LL   : {d_ll:.2f} ms\n")

            self._catat_log("DATA", f"Load {len(data)} baris CSV", durasi_baca)
            self._catat_log("M1:ARRAY", f"Append {len(data)} elemen", d_arr)
            self._catat_log("M1:LINKEDLIST", f"Append {len(data)} elemen", d_ll)

        ttk.Button(self.frame_input, text="MUAT SEKARANG", command=proses_muat).pack(anchor="w", pady=6)
        if auto_run:
            proses_muat()
    def _tampilkan_form_lihat(self, struktur):
        for widget in self.frame_input.winfo_children():
            widget.destroy()

        self.lbl_form_title.config(text=f"{struktur}: Lihat Pesanan")
        self.lbl_form_desc.config(text=f"Akses elemen ke-i. Kompleksitas: {'O(1)' if struktur == 'ARRAY' else 'O(n)'}")

        tk.Label(self.frame_input, text="Indeks Pesanan (0 s/d N-1):", bg="white").pack(anchor="w")
        ent_idx = ttk.Entry(self.frame_input, width=15)
        ent_idx.insert(0, "0")
        ent_idx.pack(anchor="w", pady=4)

        def aksi_lihat():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Muat data terlebih dahulu!")
                return
            idx = int(ent_idx.get().strip())
            total = len(self.arr_pesanan) if struktur == "ARRAY" else len(self.ll_pesanan)
            if idx < 0 or idx >= total:
                messagebox.showerror("Error", f"Indeks di luar rentang (0 - {total - 1})")
                return

            t0 = time.perf_counter()
            item = self.arr_pesanan.get(idx) if struktur == "ARRAY" else self.ll_pesanan.get(idx)
            durasi = (time.perf_counter() - t0) * 1000

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"=== DETAIL PESANAN (INDEKS {idx}) ===\n")
            self.txt_output.insert(tk.END, f"OID          : {item.oid}\n")
            self.txt_output.insert(tk.END, f"Pelanggan    : {item.pelanggan}\n")
            self.txt_output.insert(tk.END, f"Resto        : {item.resto}\n")
            self.txt_output.insert(tk.END, f"Menu         : {item.menu}\n")
            self.txt_output.insert(tk.END, f"Harga        : Rp{item.harga:,}\n")
            self.txt_output.insert(tk.END, f"Prioritas    : {item.prioritas}\n")
            self.txt_output.insert(tk.END, f"Status       : {item.status}\n")

            self._catat_log(f"M1:{struktur}", f"Lihat indeks {idx}", durasi)

        ttk.Button(self.frame_input, text="LIHAT", command=aksi_lihat).pack(anchor="w", pady=4)

    def _tampilkan_form_tambah(self, struktur, prioritas):
        for widget in self.frame_input.winfo_children():
            widget.destroy()

        label_prio = {1: "VIP (Paling Depan)", 2: "PRIORITAS (Tengah)", 3: "REGULER (Paling Belakang)"}[prioritas]
        self.lbl_form_title.config(text=f"{struktur}: Tambah Pesanan {label_prio}")
        
        desc = {
            1: "Menyisipkan di barisan paling depan (indeks 0).",
            2: "Menyisipkan di barisan tengah (indeks size // 2).",
            3: "Menambahkan di barisan paling belakang."
        }[prioritas]
        self.lbl_form_desc.config(text=desc)

        # Form Field
        tk.Label(self.frame_input, text="Nama Pelanggan:", bg="white").grid(row=0, column=0, sticky="w", pady=2)
        ent_nama = ttk.Entry(self.frame_input, width=30)
        ent_nama.insert(0, "Pelanggan Baru")
        ent_nama.grid(row=0, column=1, sticky="w", pady=2, padx=5)

        tk.Label(self.frame_input, text="Restoran:", bg="white").grid(row=1, column=0, sticky="w", pady=2)
        ent_resto = ttk.Entry(self.frame_input, width=30)
        ent_resto.insert(0, "kafe-teknik")
        ent_resto.grid(row=1, column=1, sticky="w", pady=2, padx=5)

        tk.Label(self.frame_input, text="Menu Makanan:", bg="white").grid(row=2, column=0, sticky="w", pady=2)
        ent_menu = ttk.Entry(self.frame_input, width=30)
        ent_menu.insert(0, "nasi-goreng")
        ent_menu.grid(row=2, column=1, sticky="w", pady=2, padx=5)

        tk.Label(self.frame_input, text="Harga (Rp):", bg="white").grid(row=3, column=0, sticky="w", pady=2)
        ent_harga = ttk.Entry(self.frame_input, width=30)
        ent_harga.insert(0, "20000")
        ent_harga.grid(row=3, column=1, sticky="w", pady=2, padx=5)

        def aksi_tambah():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Muat data terlebih dahulu!")
                return

            wadah = self.arr_pesanan if struktur == "ARRAY" else self.ll_pesanan
            p_baru = Pesanan(
                oid=f"O-NEW{len(wadah)+1}",
                pelanggan=ent_nama.get().strip(),
                resto=ent_resto.get().strip(),
                menu=ent_menu.get().strip(),
                harga=ent_harga.get().strip(),
                prioritas=prioritas,
                t_masuk=int(time.time()) % 86400,
                t_selesai=None,
                status="ANTRE"
            )

            t0 = time.perf_counter()
            posisi = ""
            if prioritas == 1:
                wadah.insert(0, p_baru)
                posisi = "Depan (idx 0)"
            elif prioritas == 2:
                idx_tengah = len(wadah) // 2
                wadah.insert(idx_tengah, p_baru)
                posisi = f"Tengah (idx {idx_tengah})"
            else:
                wadah.append(p_baru)
                posisi = f"Belakang (idx {len(wadah)-1})"
            durasi = (time.perf_counter() - t0) * 1000

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Pesanan berhasil ditambahkan ke {struktur}!\n")
            self.txt_output.insert(tk.END, f"- Posisi Sisip : {posisi}\n")
            self.txt_output.insert(tk.END, f"- Data         : {p_baru}\n")
            self.txt_output.insert(tk.END, f"- Total Data   : {len(wadah)}\n")

            self._catat_log(f"M1:{struktur}", f"Tambah P{prioritas} ({posisi})", durasi)

        btn_tambah = ttk.Button(self.frame_input, text="TAMBAH SEKARANG", command=aksi_tambah)
        btn_tambah.grid(row=4, column=0, columnspan=2, sticky="w", pady=8)

    def _tampilkan_form_hapus(self, struktur):
        for widget in self.frame_input.winfo_children():
            widget.destroy()

        self.lbl_form_title.config(text=f"{struktur}: Hapus Pesanan")
        self.lbl_form_desc.config(text="Menghapus pesanan pada indeks ke-i (O(n)).")

        tk.Label(self.frame_input, text="Indeks yang akan dihapus:", bg="white").pack(anchor="w")
        ent_idx = ttk.Entry(self.frame_input, width=15)
        ent_idx.insert(0, "0")
        ent_idx.pack(anchor="w", pady=4)

        def aksi_hapus():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Muat data terlebih dahulu!")
                return
            idx = int(ent_idx.get().strip())
            wadah = self.arr_pesanan if struktur == "ARRAY" else self.ll_pesanan
            if idx < 0 or idx >= len(wadah):
                messagebox.showerror("Error", f"Indeks di luar rentang (0 - {len(wadah)-1})")
                return

            t0 = time.perf_counter()
            terhapus = wadah.delete(idx)
            durasi = (time.perf_counter() - t0) * 1000

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Pesanan berhasil dihapus dari {struktur} pada indeks {idx}!\n")
            self.txt_output.insert(tk.END, f"- Data Dihapus : {terhapus}\n")
            self.txt_output.insert(tk.END, f"- Sisa Data    : {len(wadah)}\n")

            self._catat_log(f"M1:{struktur}", f"Hapus idx {idx}", durasi)

        ttk.Button(self.frame_input, text="HAPUS", command=aksi_hapus).pack(anchor="w", pady=4)

    def _bersihkan_form(self):
        """Membersihkan frame input dan output sebelum membuka form baru."""
        for widget in self.frame_input.winfo_children():
            widget.destroy()
        self.txt_output.delete("1.0", tk.END)

    def _tampilkan_form_kasir(self):
        self._bersihkan_form()

        lbl_jdl = tk.Label(self.frame_input, text="MESIN KASIR: Evaluasi Struk Belanja (Stack Postfix)", font=("Segoe UI", 9, "bold"))
        lbl_jdl.pack(anchor="w", pady=(0, 2))

        lbl_sub = tk.Label(self.frame_input, text="Konversi ekspresi infix ke postfix lalu evaluasi nilainya.", font=("Segoe UI", 8), fg="#666")
        lbl_sub.pack(anchor="w", pady=(0, 6))

        tk.Label(self.frame_input, text="Ekspresi Struk (pisahkan dengan spasi):").pack(anchor="w")
        ent_ekspresi = ttk.Entry(self.frame_input, width=45)
        ent_ekspresi.insert(0, "( 3 * 12000 ) + ( 2 * 8500 ) - 5000")
        ent_ekspresi.pack(anchor="w", pady=3)

        def aksi_hitung():
            ekspresi = ent_ekspresi.get().strip()
            t0 = time.perf_counter()
            try:
                postfix = ke_postfix(ekspresi)
                total = hitung(postfix)
                durasi = (time.perf_counter() - t0) * 1000

                self.txt_output.delete("1.0", tk.END)
                self.txt_output.insert(tk.END, "=== HASIL EVALUASI STACK POSTFIX ===\n")
                self.txt_output.insert(tk.END, f"Infix   : {ekspresi}\n")
                self.txt_output.insert(tk.END, f"Postfix : {' '.join(postfix)}\n")
                self.txt_output.insert(tk.END, "-" * 40 + "\n")
                self.txt_output.insert(tk.END, f"Total Pembayaran : Rp {total:,}\n")

                self._catat_log("M2:STACK", "Hitung Postfix", durasi)
            except Exception as e:
                messagebox.showerror("Error", f"Perhitungan gagal: {e}")

        ttk.Button(self.frame_input, text="HITUNG", command=aksi_hitung).pack(anchor="w", pady=6)

    def _tampilkan_form_benchmark_queue(self):
        self._bersihkan_form()

        lbl_jdl = tk.Label(self.frame_input, text="BENCHMARK: Naive Queue vs Circular Queue", font=("Segoe UI", 9, "bold"))
        lbl_jdl.pack(anchor="w", pady=(0, 2))

        lbl_sub = tk.Label(self.frame_input, text="Membandingkan kompleksitas Dequeue O(N) vs Circular Queue O(1).", font=("Segoe UI", 8), fg="#666")
        lbl_sub.pack(anchor="w", pady=(0, 6))

        def aksi_benchmark():
            n = 20000
            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Menyiapkan {n:,} antrean dummy...\n")
            self.root.update()

            self.naive_q = NaiveQueue()
            self.circ_q = CircularQueue(capacity=50000)
            for i in range(n):
                self.naive_q.enqueue(f"ORD-{i+1}")
                self.circ_q.enqueue(f"ORD-{i+1}")

            self.txt_output.insert(tk.END, "Menguji Dequeue 100 elemen...\n\n")
            self.root.update()

            # Benchmark Naive Queue
            t0 = time.perf_counter()
            for _ in range(100):
                self.naive_q.dequeue()
            t_naive = (time.perf_counter() - t0) * 1000

            # Benchmark Circular Queue
            t0 = time.perf_counter()
            for _ in range(100):
                self.circ_q.dequeue()
            t_circ = (time.perf_counter() - t0) * 1000

            self.txt_output.insert(tk.END, f"Naive Queue    (pop(0) - O(N)) : {t_naive:.4f} ms\n")
            self.txt_output.insert(tk.END, f"Circular Queue (Pointer - O(1)): {t_circ:.4f} ms\n")
            self.txt_output.insert(tk.END, "-" * 40 + "\n")
            rasio = t_naive / max(t_circ, 1e-6)
            self.txt_output.insert(tk.END, f"Circular Queue lebih cepat {rasio:.2f}x lipat!\n")

            self._catat_log("M2:QUEUE", "Benchmark Dequeue 100x", t_circ)

        ttk.Button(self.frame_input, text="MULAI BENCHMARK", command=aksi_benchmark).pack(anchor="w", pady=6)

    def _tampilkan_form_antrean_dapur(self):
        self._bersihkan_form()

        lbl_jdl = tk.Label(self.frame_input, text="ANTREAN DAPUR: Undo & Redo", font=("Segoe UI", 9, "bold"))
        lbl_jdl.pack(anchor="w", pady=(0, 2))

        lbl_status = tk.Label(self.frame_input, text="", font=("Segoe UI", 8, "bold"))
        lbl_status.pack(anchor="w", pady=(2, 6))

        def perbarui_view(pesan=""):
            lbl_status.config(text=f"Antrean: {self.circ_q.size()} | Undo: {self.undo_manager.undo_stack.size()} | Redo: {self.undo_manager.redo_stack.size()}")
            self.txt_output.delete("1.0", tk.END)
            if pesan:
                self.txt_output.insert(tk.END, f"[LOG] {pesan}\n" + "-" * 40 + "\n")
            self.txt_output.insert(tk.END, f"Pesanan aktif di dapur: {self.circ_q.size()}\n")

        counter = [self.circ_q.size() + 1]

        def on_enqueue():
            item = f"ORD-{counter[0]:03d}"
            counter[0] += 1
            self.circ_q.enqueue(item)
            self.undo_manager.catat_aksi("ENQUEUE", item)
            self._catat_log("M2:QUEUE", f"Enqueue {item}", 0.01)
            perbarui_view(f"Pesanan {item} masuk ke antrean.")

        def on_dequeue():
            if self.circ_q.is_empty():
                messagebox.showwarning("Peringatan", "Antrean dapur kosong!")
                return
            item = self.circ_q.dequeue()
            self.undo_manager.catat_aksi("DEQUEUE", [item])
            self._catat_log("M2:QUEUE", f"Dequeue {item}", 0.01)
            perbarui_view(f"Pesanan {item} disajikan (Dequeued).")

        def on_undo():
            sukses, msg = self.undo_manager.undo_last()
            self._catat_log("M2:STACK", "Undo", 0.01)
            perbarui_view(msg)

        def on_redo():
            sukses, msg = self.undo_manager.redo_last()
            self._catat_log("M2:STACK", "Redo", 0.01)
            perbarui_view(msg)

        f_tombol = tk.Frame(self.frame_input)
        f_tombol.pack(anchor="w", pady=4)

        ttk.Button(f_tombol, text="+ Enqueue", command=on_enqueue).pack(side="left", padx=2)
        ttk.Button(f_tombol, text="Dequeue", command=on_dequeue).pack(side="left", padx=2)
        ttk.Button(f_tombol, text="Undo", command=on_undo).pack(side="left", padx=2)
        ttk.Button(f_tombol, text="Redo", command=on_redo).pack(side="left", padx=2)

        perbarui_view()

    # ==========================================
    # MILESTONE 3: SORT & SEARCH
    # ==========================================

    def _ambil_potongan_data(self, batas=None):
        """Mengambil list pesanan dari Array M1."""
        total = len(self.arr_pesanan)
        n = total if batas is None else min(batas, total)
        return [self.arr_pesanan.get(i) for i in range(n)]

    def _tampilkan_form_sort(self, jenis_sort):
        self._bersihkan_form()
        nama_alg = "insertion sort, O(n²)" if jenis_sort == "INSERTION" else "merge sort, O(n log n)"

        tk.Label(self.frame_input, text=f"Sort: {nama_alg}", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        f_param = tk.Frame(self.frame_input)
        f_param.pack(anchor="w", pady=4)

        tk.Label(f_param, text="Jumlah baris diurutkan:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        ent_jumlah = ttk.Entry(f_param, width=12)
        ent_jumlah.insert(0, "1000" if jenis_sort == "INSERTION" else "4000")
        ent_jumlah.grid(row=1, column=0, sticky="w", padx=(0, 8), pady=2)

        tk.Label(f_param, text="Diurutkan menurut:").grid(row=0, column=1, sticky="w", padx=8)
        cmb_kunci = ttk.Combobox(f_param, values=["oid", "harga", "selesai"], state="readonly", width=12)
        cmb_kunci.set("harga")
        cmb_kunci.grid(row=1, column=1, sticky="w", padx=8, pady=2)

        def aksi_urutkan():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Silakan muat data CSV terlebih dahulu!")
                return
            try:
                jml = int(ent_jumlah.get().strip())
                kunci = cmb_kunci.get()
                potongan = self._ambil_potongan_data(jml)

                t0 = time.perf_counter()
                if jenis_sort == "INSERTION":
                    hasil, komp, pindah = insertion_sort(potongan, kunci)
                    tag_log = "M3:insertion_sort"
                else:
                    hasil, komp, pindah = merge_sort(potongan, kunci)
                    tag_log = "M3:merge_sort"
                durasi = (time.perf_counter() - t0) * 1000

                self.txt_output.delete("1.0", tk.END)
                self.txt_output.insert(tk.END, f"{len(hasil):,} pesanan diurutkan menurut {kunci}.\n")
                self.txt_output.insert(tk.END, f"{komp:,} perbandingan, {pindah:,} pemindahan.\n")
                self.txt_output.insert(tk.END, "-" * 70 + "\n")
                self.txt_output.insert(tk.END, f"{'#':<5} {'oid':<10} {'harga':<10} {'selesai':<10} {'resto':<18} {'menu'}\n")
                self.txt_output.insert(tk.END, "-" * 70 + "\n")

                for idx, p in enumerate(hasil[:20], start=1):
                    selesai = getattr(p, "t_selesai_detik", "-") or "-"
                    self.txt_output.insert(tk.END, f"{idx:<5} {p.oid:<10} {p.harga:<10,} {str(selesai):<10} {p.resto:<18} {p.menu}\n")

                self._catat_log(tag_log, f"n={len(hasil)} ({kunci})", durasi)
            except ValueError as ve:
                messagebox.showerror("Ditolak", str(ve))
            except Exception as e:
                messagebox.showerror("Error", f"Gagal mengurutkan: {e}")

        ttk.Button(f_param, text="URUTKAN", command=aksi_urutkan).grid(row=1, column=2, padx=10)

    def _tampilkan_form_linear_search(self):
        self._bersihkan_form()
        tk.Label(self.frame_input, text="Search: linear search, O(n)", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        tk.Label(self.frame_input, text="Nomor pesanan (oid):").pack(anchor="w")
        ent_oid = ttk.Entry(self.frame_input, width=25)
        ent_oid.insert(0, "O-000010")
        ent_oid.pack(anchor="w", pady=3)

        def aksi_cari():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Silakan muat data CSV terlebih dahulu!")
                return
            target = ent_oid.get().strip()
            semua_data = self._ambil_potongan_data()

            t0 = time.perf_counter()
            idx, ketemu, komp = linear_search(semua_data, target)
            durasi = (time.perf_counter() - t0) * 1000

            self.txt_output.delete("1.0", tk.END)
            if ketemu:
                self.txt_output.insert(tk.END, f"Ditemukan pada indeks {idx:,}.\n")
                self.txt_output.insert(tk.END, f"{komp:,} perbandingan.\n")
                self.txt_output.insert(tk.END, "-" * 50 + "\n")
                self.txt_output.insert(tk.END, f"oid       : {ketemu.oid}\n")
                self.txt_output.insert(tk.END, f"pelanggan : {ketemu.pelanggan}\n")
                self.txt_output.insert(tk.END, f"resto     : {ketemu.resto}\n")
                self.txt_output.insert(tk.END, f"menu      : {ketemu.menu}\n")
                self.txt_output.insert(tk.END, f"harga     : Rp {ketemu.harga:,}\n")
                self.txt_output.insert(tk.END, f"status    : {ketemu.status}\n")
            else:
                self.txt_output.insert(tk.END, f"Pesanan '{target}' TIDAK DITEMUKAN.\n")
                self.txt_output.insert(tk.END, f"{komp:,} perbandingan telah dilakukan.\n")

            self._catat_log("M3:linear_search", f"Cari {target}", durasi)

        ttk.Button(self.frame_input, text="CARI", command=aksi_cari).pack(anchor="w", pady=5)

    def _tampilkan_form_binary_search(self):
        self._bersihkan_form()
        tk.Label(self.frame_input, text="Search: binary search, O(log n)", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        tk.Label(self.frame_input, text="Nomor pesanan (oid):").pack(anchor="w")
        ent_oid = ttk.Entry(self.frame_input, width=25)
        ent_oid.insert(0, "O-000010")
        ent_oid.pack(anchor="w", pady=3)

        def aksi_cari_bin():
            if not self.data_termuat:
                messagebox.showwarning("Peringatan", "Silakan muat data CSV terlebih dahulu!")
                return
            target = ent_oid.get().strip()

            if self.cache_terurut_oid is None or len(self.cache_terurut_oid) != len(self.arr_pesanan):
                semua_data = self._ambil_potongan_data()
                t_sort = time.perf_counter()
                self.cache_terurut_oid, _, _ = merge_sort(semua_data, "oid")
                self.waktu_bangun_oid_ms = (time.perf_counter() - t_sort) * 1000

            t0 = time.perf_counter()
            idx, ketemu, komp = binary_search(self.cache_terurut_oid, target)
            durasi = (time.perf_counter() - t0) * 1000

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Daftar terurut oid dibangun sekali dengan merge sort, {self.waktu_bangun_oid_ms:.2f} ms.\n")
            if ketemu:
                self.txt_output.insert(tk.END, f"Ditemukan pada baris ke-{idx+1:,} dari {len(self.cache_terurut_oid):,} baris.\n")
                self.txt_output.insert(tk.END, f"{komp:,} perbandingan, bandingkan dengan linear search.\n")
                self.txt_output.insert(tk.END, "-" * 50 + "\n")
                self.txt_output.insert(tk.END, f"oid       : {ketemu.oid}\n")
                self.txt_output.insert(tk.END, f"pelanggan : {ketemu.pelanggan}\n")
                self.txt_output.insert(tk.END, f"resto     : {ketemu.resto}\n")
                self.txt_output.insert(tk.END, f"menu      : {ketemu.menu}\n")
                self.txt_output.insert(tk.END, f"harga     : Rp {ketemu.harga:,}\n")
                self.txt_output.insert(tk.END, f"status    : {ketemu.status}\n")
            else:
                self.txt_output.insert(tk.END, f"Pesanan '{target}' TIDAK DITEMUKAN ({komp} perbandingan).\n")

            self._catat_log("M3:binary_search", f"Cari {target}", durasi)

        ttk.Button(self.frame_input, text="CARI", command=aksi_cari_bin).pack(anchor="w", pady=5)