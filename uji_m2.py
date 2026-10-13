# uji_m2.py
import time
from backend.m2_antrean import ke_postfix, hitung, NaiveQueue, CircularQueue, UndoRedoManager

def test_kasir():
    print("=== PENGUJIAN STACK MESIN KASIR ===")
    ekspresi = "( 3 * 12000 ) + ( 2 * 8500 ) - 5000"
    postfix = ke_postfix(ekspresi)
    total = hitung(postfix)
    print(f"Infix   : {ekspresi}")
    print(f"Postfix : {' '.join(postfix)}")
    print(f"Total   : Rp {total:,}")
    assert total == 48000, "Perhitungan kasir keliru!"
    print("[OK] Kasir Postfix valid.\n")

def test_benchmark_queue():
    print("=== PENGUJIAN BENCHMARK NAIVE VS CIRCULAR QUEUE ===")
    n = 20000
    naive_q = NaiveQueue()
    circ_q = CircularQueue(capacity=50000)

    for i in range(n):
        pesanan = f"O-{i}"
        naive_q.enqueue(pesanan)
        circ_q.enqueue(pesanan)

    # Uji Dequeue 100 elemen
    t0 = time.perf_counter()
    for _ in range(100):
        naive_q.dequeue()
    t_naive = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for _ in range(100):
        circ_q.dequeue()
    t_circ = (time.perf_counter() - t0) * 1000

    print(f"Dequeue 100x Naive Queue   : {t_naive:.3f} ms (O(N))")
    print(f"Dequeue 100x Circular Queue: {t_circ:.3f} ms (O(1))")
    print("[OK] Benchmark queue selesai.\n")

def test_undo_redo():
    print("=== PENGUJIAN UNDO & REDO ===")
    cq = CircularQueue(capacity=10)
    ur = UndoRedoManager(cq)

    cq.enqueue("O-101")
    ur.catat_aksi("ENQUEUE", "O-101")
    print(f"Setelah enqueue, size: {cq.size()}")

    ur.undo_last()
    print(f"Setelah undo, size: {cq.size()}")
    assert cq.size() == 0

    ur.redo_last()
    print(f"Setelah redo, size: {cq.size()}")
    assert cq.size() == 1
    print("[OK] Undo-Redo valid.\n")

if __name__ == "__main__":
    test_kasir()
    test_benchmark_queue()
    test_undo_redo()