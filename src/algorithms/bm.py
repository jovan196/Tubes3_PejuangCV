# algorithms/boyer_moore.py
from typing import List, Dict

class BoyerMooreSearch:
    """
    Implementasi algoritma Boyer-Moore untuk pencarian pattern matching.
    Algoritma ini menggunakan dua heuristik: Bad Character dan Good Suffix.
    Kompleksitas waktu rata-rata: O(n/m), worst case: O(nm)
    """
    
    def __init__(self):
        pass
    
    def bad_char_heuristic(self, pattern: str) -> Dict[str, int]:
        """
        Membuat bad character table untuk algoritma Boyer-Moore.
        Bad character heuristic menentukan seberapa jauh pattern harus digeser
        ketika terjadi mismatch.
        
        Args:
            pattern (str): Pattern yang akan dicari
            
        Returns:
            Dict[str, int]: Dictionary berisi posisi terakhir setiap karakter dalam pattern
        """
        bad_char = {}
        m = len(pattern)
        
        # Isi array dengan -1 untuk semua karakter ASCII
        for i in range(256):
            bad_char[chr(i)] = -1
        
        # Isi posisi aktual dari karakter dalam pattern
        for i in range(m):
            bad_char[pattern[i]] = i
            
        return bad_char
    
    def good_suffix_heuristic(self, pattern: str) -> List[int]:
        """
        Membuat good suffix table untuk algoritma Boyer-Moore.
        Good suffix heuristic menentukan pergeseran berdasarkan suffix yang cocok.
        
        Args:
            pattern (str): Pattern yang akan dicari
            
        Returns:
            List[int]: Array berisi nilai pergeseran untuk setiap posisi
        """
        m = len(pattern)
        shift = [0] * (m + 1)
        border = [0] * (m + 1)
        
        # Preprocessing
        i = m
        j = m + 1
        border[i] = j
        
        while i > 0:
            while j <= m and pattern[i - 1] != pattern[j - 1]:
                if shift[j] == 0:
                    shift[j] = j - i
                j = border[j]
            
            i -= 1
            j -= 1
            border[i] = j
        
        # Menghitung shift untuk case 2
        j = border[0]
        for i in range(m + 1):
            if shift[i] == 0:
                shift[i] = j
            if i == j:
                j = border[j]
        
        return shift
    
    def search(self, text: str, pattern: str) -> int:
        """
        Mencari kemunculan pertama dari pattern dalam text menggunakan algoritma Boyer-Moore.
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            int: Index kemunculan pertama pattern dalam text, -1 jika tidak ditemukan
        """
        if not pattern or not text:
            return -1
            
        n = len(text)
        m = len(pattern)
        
        # Preprocessing
        bad_char = self.bad_char_heuristic(pattern)
        good_suffix = self.good_suffix_heuristic(pattern)
        
        s = 0  # shift dari pattern terhadap text
        
        while s <= n - m:
            j = m - 1
            
            # Cocokkan pattern dari kanan ke kiri
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
            
            # Jika pattern ditemukan
            if j < 0:
                return s
            else:
                # Hitung pergeseran menggunakan kedua heuristik
                bad_char_shift = j - bad_char.get(text[s + j], -1)
                good_suffix_shift = good_suffix[j + 1]
                
                # Ambil pergeseran maksimum
                s += max(bad_char_shift, good_suffix_shift)
        
        return -1
    
    def search_all(self, text: str, pattern: str) -> List[int]:
        """
        Mencari semua kemunculan pattern dalam text menggunakan algoritma Boyer-Moore.
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            List[int]: List berisi semua index kemunculan pattern dalam text
        """
        if not pattern or not text:
            return []
            
        positions = []
        n = len(text)
        m = len(pattern)
        
        # Preprocessing
        bad_char = self.bad_char_heuristic(pattern)
        good_suffix = self.good_suffix_heuristic(pattern)
        
        s = 0  # shift dari pattern terhadap text
        
        while s <= n - m:
            j = m - 1
            
            # Cocokkan pattern dari kanan ke kiri
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
            
            # Jika pattern ditemukan
            if j < 0:
                positions.append(s)
                s += good_suffix[0]  # Shift untuk mencari kemunculan berikutnya
            else:
                # Hitung pergeseran menggunakan kedua heuristik
                bad_char_shift = j - bad_char.get(text[s + j], -1)
                good_suffix_shift = good_suffix[j + 1]
                
                # Ambil pergeseran maksimum
                s += max(bad_char_shift, good_suffix_shift)
        
        return positions
    
    def count_occurrences(self, text: str, pattern: str) -> int:
        """
        Menghitung jumlah kemunculan pattern dalam text.
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            int: Jumlah kemunculan pattern dalam text
        """
        return len(self.search_all(text, pattern))
    
    def search_case_insensitive(self, text: str, pattern: str) -> List[int]:
        """
        Mencari pattern dalam text tanpa memperhatikan case (case-insensitive).
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            List[int]: List berisi semua index kemunculan pattern dalam text
        """
        return self.search_all(text.lower(), pattern.lower())