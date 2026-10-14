# backend/m2_antrean.py

class Stack:
    def __init__(self):
        self.data = []

    def push(self, nilai):
        self.data.append(nilai)

    def pop(self):
        if len(self.data) == 0:
            return None
        return self.data.pop()

    def peek(self):
        if len(self.data) == 0:
            return None
        return self.data[len(self.data) - 1]

    def kosong(self):
        return len(self.data) == 0

    def __len__(self):
        return len(self.data)


def tokenisasi(ekspresi):
    token = []
    angka = ""
    i = 0
    while i < len(ekspresi):
        c = ekspresi[i]
        if c.isdigit() or c == ".":
            angka += c
        else:
            if angka != "":
                token.append(angka)
                angka = ""
            if c in "+-*/()":
                token.append(c)
            elif not c.isspace():
                raise ValueError("Karakter tidak dikenal: " + c)
        i += 1
    if angka != "":
        token.append(angka)
    return token


def prioritas_operator(op):
    if op == "+" or op == "-":
        return 1
    if op == "*" or op == "/":
        return 2
    return 0


def ke_postfix(ekspresi):
    tokens = tokenisasi(ekspresi)
    operators = Stack()
    output = []

    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.replace(".", "", 1).isdigit():
            output.append(t)
        elif t == "(":
            operators.push(t)
        elif t == ")":
            while not operators.kosong() and operators.peek() != "(":
                output.append(operators.pop())
            if operators.kosong():
                raise ValueError("Kurung tutup tidak punya pasangan")
            operators.pop()
        else:
            while (
                not operators.kosong()
                and operators.peek() != "("
                and prioritas_operator(operators.peek()) >= prioritas_operator(t)
            ):
                output.append(operators.pop())
            operators.push(t)
        i += 1

    while not operators.kosong():
        op = operators.pop()
        if op == "(":
            raise ValueError("Kurung buka tidak punya pasangan")
        output.append(op)

    return output


def hitung_postfix(postfix):
    angka = Stack()
    i = 0
    while i < len(postfix):
        t = postfix[i]
        if isinstance(t, (int, float)):
            angka.push(t)
        elif t.replace(".", "", 1).isdigit():
            angka.push(float(t) if "." in t else int(t))
        else:
            b = angka.pop()
            a = angka.pop()
            if a is None or b is None:
                raise ValueError("Ekspresi postfix tidak valid")
            if t == "+":
                angka.push(a + b)
            elif t == "-":
                angka.push(a - b)
            elif t == "*":
                angka.push(a * b)
            elif t == "/":
                if b == 0:
                    raise ZeroDivisionError("Pembagian dengan nol")
                angka.push(a / b)
            else:
                raise ValueError("Operator tidak dikenal: " + t)
        i += 1

    hasil = angka.pop()
    if not angka.kosong():
        raise ValueError("Ekspresi postfix tidak valid")
    return hasil


class AntreanNaif:
    def __init__(self, data_awal=None):
        self.data = []
        self.total_geseran = 0
        if data_awal is not None:
            i = 0
            while i < len(data_awal):
                self.data.append(data_awal[i])
                i += 1

    def enqueue(self, x):
        self.data.append(x)

    def dequeue(self):
        if len(self.data) == 0:
            return None
        self.total_geseran += len(self.data) - 1
        return self.data.pop(0)

    def __len__(self):
        return len(self.data)


class AntreanMelingkar:
    def __init__(self, kapasitas=8):
        if kapasitas < 1:
            kapasitas = 1
        self.data = [None] * kapasitas
        self.front = 0
        self.rear = 0
        self.count = 0
        self.total_geseran = 0

    def __len__(self):
        return self.count

    def _grow(self):
        baru = [None] * (len(self.data) * 2)
        i = 0
        while i < self.count:
            baru[i] = self.data[(self.front + i) % len(self.data)]
            i += 1
        self.data = baru
        self.front = 0
        self.rear = self.count

    def enqueue(self, x):
        if self.count == len(self.data):
            self._grow()
        self.data[self.rear] = x
        self.rear = (self.rear + 1) % len(self.data)
        self.count += 1

    def dequeue(self):
        if self.count == 0:
            return None
        x = self.data[self.front]
        self.data[self.front] = None
        self.front = (self.front + 1) % len(self.data)
        self.count -= 1
        return x

    def prepend_many(self, items):
        i = len(items) - 1
        while i >= 0:
            self._prepend(items[i])
            i -= 1

    def _prepend(self, x):
        if self.count == len(self.data):
            self._grow()
        self.front = (self.front - 1) % len(self.data)
        self.data[self.front] = x
        self.count += 1

    def snapshot(self):
        hasil = []
        i = 0
        while i < self.count:
            hasil.append(self.data[(self.front + i) % len(self.data)])
            i += 1
        return hasil


class Aksi:
    def __init__(self, jenis, nilai):
        self.jenis = jenis
        self.nilai = nilai


class UndoRedoQueue:
    def __init__(self, antrean):
        self.antrean = antrean
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def _clear_redo(self):
        self.redo_stack = Stack()

    def enqueue(self, x):
        self.antrean.enqueue(x)
        self.undo_stack.push(Aksi("enqueue", x))
        self._clear_redo()

    def dequeue(self):
        x = self.antrean.dequeue()
        if x is not None:
            self.undo_stack.push(Aksi("dequeue", [x]))
            self._clear_redo()
        return x

    def dequeue_many(self, jumlah):
        items = []
        i = 0
        while i < jumlah:
            x = self.antrean.dequeue()
            if x is None:
                break
            items.append(x)
            i += 1
        if len(items) > 0:
            self.undo_stack.push(Aksi("dequeue", items))
            self._clear_redo()
        return items

    def undo_last(self):
        aksi = self.undo_stack.pop()
        if aksi is None:
            return False

        if aksi.jenis == "enqueue":
            current = self.antrean.snapshot()
            target = []
            i = 0
            while i < len(current):
                if i != len(current) - 1:
                    target.append(current[i])
                i += 1
            self._replace_queue(target)
        else:
            self.antrean.prepend_many(aksi.nilai)

        self.redo_stack.push(aksi)
        return True

    def redo_last(self):
        aksi = self.redo_stack.pop()
        if aksi is None:
            return False

        if aksi.jenis == "enqueue":
            self.antrean.enqueue(aksi.nilai)
        else:
            i = 0
            while i < len(aksi.nilai):
                self.antrean.dequeue()
                i += 1

        self.undo_stack.push(aksi)
        return True

    def _replace_queue(self, items):
        kapasitas = len(self.antrean.data)
        self.antrean = AntreanMelingkar(max(kapasitas, len(items) + 1))
        i = 0
        while i < len(items):
            self.antrean.enqueue(items[i])
            i += 1

    def history(self):
        return len(self.undo_stack), len(self.redo_stack)


def evaluasi_kasir(ekspresi):
    postfix = ke_postfix(ekspresi)
    total = hitung_postfix(postfix)
    return postfix, total