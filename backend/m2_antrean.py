# backend/m2_antrean.py

class Stack:
    """Implementasi Stack mandiri (LIFO) menggunakan list primitif."""
    def __init__(self):
        self._data = []

    def push(self, item):
        self._data.append(item)

    def pop(self):
        if self.is_empty():
            return None
        return self._data.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._data[-1]

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)

    def clear(self):
        self._data = []


# ==========================================
# BAGIAN A (1): STACK POSTFIX (KASIR)
# ==========================================

def ke_postfix(ekspresi: str):
    """
    Mengubah infix ke postfix.
    Contoh: '( 3 * 12000 ) + ( 2 * 8500 ) - 5000'
    Token dipisahkan spasi.
    """
    prioritas = {'+': 1, '-': 1, '*': 2, '/': 2}
    stack_op = Stack()
    output = []
    
    # Tokenisasi sederhana berdasarkan spasi
    tokens = ekspresi.strip().split()

    for token in tokens:
        if token.isdigit():
            output.append(token)
        elif token == '(':
            stack_op.push(token)
        elif token == ')':
            while not stack_op.is_empty() and stack_op.peek() != '(':
                output.append(stack_op.pop())
            stack_op.pop()  # Buang '('
        elif token in prioritas:
            while (not stack_op.is_empty() and stack_op.peek() in prioritas and
                   prioritas[stack_op.peek()] >= prioritas[token]):
                output.append(stack_op.pop())
            stack_op.push(token)

    while not stack_op.is_empty():
        output.append(stack_op.pop())

    return output


def hitung(postfix_tokens: list):
    """
    Mengevaluasi postfix menggunakan Stack operand.
    """
    stack_val = Stack()

    for token in postfix_tokens:
        if token.isdigit():
            stack_val.push(float(token))
        else:
            # Perhatikan urutan operand
            b = stack_val.pop()
            a = stack_val.pop()
            if token == '+':
                stack_val.push(a + b)
            elif token == '-':
                stack_val.push(a - b)
            elif token == '*':
                stack_val.push(a * b)
            elif token == '/':
                stack_val.push(a / b if b != 0 else 0)

    hasil = stack_val.pop()
    return int(hasil) if hasil is not None and hasil.is_integer() else hasil


# ==========================================
# BAGIAN B: QUEUE NAIF VS CIRCULAR QUEUE
# ==========================================

class NaiveQueue:
    """Antrean menggunakan list biasa: Dequeue O(n) akibat pop(0)."""
    def __init__(self):
        self._data = []

    def enqueue(self, item):
        self._data.append(item)

    def dequeue(self):
        if self.is_empty():
            return None
        return self._data.pop(0)

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)


class CircularQueue:
    """Antrean melingkar berkapasitas tetap: Enqueue O(1), Dequeue O(1)."""
    def __init__(self, capacity=250000):
        self.capacity = capacity
        self._data = [None] * capacity
        self.front = 0
        self.rear = 0
        self.count = 0

    def enqueue(self, item):
        if self.count == self.capacity:
            raise OverflowError("Circular Queue penuh")
        self._data[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        item = self._data[self.front]
        self._data[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.count -= 1
        return item

    def push_front(self, item):
        """Khusus untuk undo dequeue: mengembalikan pesanan ke baris paling depan."""
        if self.count == self.capacity:
            raise OverflowError("Circular Queue penuh")
        self.front = (self.front - 1 + self.capacity) % self.capacity
        self._data[self.front] = item
        self.count += 1

    def pop_rear(self):
        """Khusus untuk undo enqueue: mengeluarkan kembali pesanan dari belakang."""
        if self.count == 0:
            return None
        self.rear = (self.rear - 1 + self.capacity) % self.capacity
        item = self._data[self.rear]
        self._data[self.rear] = None
        self.count -= 1
        return item

    def is_empty(self):
        return self.count == 0

    def size(self):
        return self.count


# ==========================================
# BAGIAN A (2): UNDO & REDO MANAGER
# ==========================================

class UndoRedoManager:
    def __init__(self, circular_queue: CircularQueue):
        self.cq = circular_queue
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def catat_aksi(self, tipe: str, data):
        """
        tipe: 'ENQUEUE' atau 'DEQUEUE'
        data: item pesanan atau list of items
        """
        self.undo_stack.push({'tipe': tipe, 'data': data})
        self.redo_stack.clear()  # Cabang baru -> bersihkan redo

    def undo_last(self):
        if self.undo_stack.is_empty():
            return False, "Tidak ada aksi untuk di-undo."
        
        aksi = self.undo_stack.pop()
        tipe, data = aksi['tipe'], aksi['data']

        if tipe == 'ENQUEUE':
            # Kebalikan enqueue: keluarkan item dari belakang antrean
            self.cq.pop_rear()
        elif tipe == 'DEQUEUE':
            # Kebalikan dequeue: masukkan kembali ke depan antrean (FIFO)
            # data berupa list item yang di-dequeue
            for item in reversed(data):
                self.cq.push_front(item)

        self.redo_stack.push(aksi)
        return True, f"Undo {tipe} berhasil."

    def redo_last(self):
        if self.redo_stack.is_empty():
            return False, "Tidak ada aksi untuk di-redo."

        aksi = self.redo_stack.pop()
        tipe, data = aksi['tipe'], aksi['data']

        if tipe == 'ENQUEUE':
            self.cq.enqueue(data)
        elif tipe == 'DEQUEUE':
            for _ in data:
                self.cq.dequeue()

        self.undo_stack.push(aksi)
        return True, f"Redo {tipe} berhasil."