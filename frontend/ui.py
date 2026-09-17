# frontend/ui.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
from backend.m1_pesanan import Array, LinkList, Pesanan, baca_csv_pesanan


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

        self._buat_layout()
        self._set_mode_default()

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
            relief=tk.FLAT, padx=8, pady=4, cursor="hand2"
        )
        btn.pack(fill=tk.X, padx=6, pady=2)
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

    def _catat_log(self, modul, aksi, durasi_ms):
        pesan = f"[{modul}] {aksi:<30} -> Waktu eksekusi: {durasi_ms:.4f} ms\n"
        self.txt_cmd.insert(tk.END, pesan)
        self.txt_cmd.see(tk.END)

    def _set_mode_default(self):
        self.txt_output.delete("1.0", tk.END)
        self.txt_output.insert(tk.END, "Silakan muat data pesanan terlebih dahulu lewat menu 'LOAD DATA (CSV)'.\n")

    # ==================== OPERASI DATA ====================
    def _menu_load_data(self):
        for widget in self.frame_input.winfo_children():
            widget.destroy()

        self.lbl_form_title.config(text="Muat Data CSV")
        self.lbl_form_desc.config(text="Membaca data/pesanan.csv ke dalam Array dan LinkedList secara paralel.")

        tk.Label(self.frame_input, text="Batas Baris Data (contoh: 20000 atau kosongkan untuk semua):", bg="white").pack(anchor="w")
        ent_limit = ttk.Entry(self.frame_input, width=25)
        ent_limit.insert(0, "20000")
        ent_limit.pack(anchor="w", pady=4)

        def proses_muat():
            teks_limit = ent_limit.get().strip()
            batas = int(teks_limit) if teks_limit.isdigit() else None

            self.txt_output.delete("1.0", tk.END)
            self.txt_output.insert(tk.END, f"Memuat data (Batas: {batas if batas else '200.000'})...\n")
            self.root.update()

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