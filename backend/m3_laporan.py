def _get_val(obj, kunci):
    """Mendapatkan nilai atribut baik dari objek Class maupun Dictionary."""
    if isinstance(obj, dict):
        return obj[kunci]
    return getattr(obj, kunci)

def insertion_sort(larik, kunci='harga'):
    n = len(larik)
    # Aturan PDF: Wajib menolak jika data > 20.000 baris
    if n > 20000:
        return None, 0, 0
        
    perbandingan = 0
    pemindahan = 0
    arr = list(larik) # Salin larik agar tidak mengubah data asli
    
    for i in range(1, n):
        elemen = arr[i]
        j = i - 1
        
        while j >= 0:
            perbandingan += 1
            # Stabil: Menggunakan > bukan >=
            if _get_val(arr[j], kunci) > _get_val(elemen, kunci):
                arr[j + 1] = arr[j]
                pemindahan += 1
                j -= 1
            else:
                break
        arr[j + 1] = elemen
        pemindahan += 1
        
    return arr, perbandingan, pemindahan

def merge_sort(larik, kunci='harga'):
    perbandingan = [0]
    pemindahan = [0]
    
    def _merge_sort(arr):
        if len(arr) <= 1:
            return arr
            
        mid = len(arr) // 2
        kiri = _merge_sort(arr[:mid])
        kanan = _merge_sort(arr[mid:])
        
        hasil = []
        i = j = 0
        
        while i < len(kiri) and j < len(kanan):
            perbandingan[0] += 1
            # Stabil: Menggunakan <= agar elemen dari bagian kiri didahulukan saat kunci sama
            if _get_val(kiri[i], kunci) <= _get_val(kanan[j], kunci):
                hasil.append(kiri[i])
                pemindahan[0] += 1
                i += 1
            else:
                hasil.append(kanan[j])
                pemindahan[0] += 1
                j += 1
                
        while i < len(kiri):
            hasil.append(kiri[i])
            pemindahan[0] += 1
            i += 1
            
        while j < len(kanan):
            hasil.append(kanan[j])
            pemindahan[0] += 1
            j += 1
            
        return hasil

    larik_terurut = _merge_sort(list(larik))
    return larik_terurut, perbandingan[0], pemindahan[0]

def linear_search(larik, target, kunci='oid'):
    perbandingan = 0
    for i in range(len(larik)):
        perbandingan += 1
        if _get_val(larik[i], kunci) == target:
            return i, perbandingan
    return -1, perbandingan

def binary_search(larik_terurut, target, kunci='oid'):
    lo = 0
    hi = len(larik_terurut) - 1
    perbandingan = 0
    
    # Syarat PDF: Menggunakan <= untuk memeriksa elemen tersisa
    while lo <= hi:
        perbandingan += 1
        mid = (lo + hi) // 2
        val = _get_val(larik_terurut[mid], kunci)
        
        if val == target:
            return mid, perbandingan
        elif val < target:
            lo = mid + 1
        else:
            hi = mid - 1
            
    return -1, perbandingan