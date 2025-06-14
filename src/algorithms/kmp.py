# algorithms/kmp.py
from typing import List

class KMPSearch:
    """
    Implementasi algoritma Knuth-Morris-Pratt (KMP) untuk pencarian pattern matching.
    Algoritma ini memiliki kompleksitas waktu O(n + m) dimana n adalah panjang teks dan m adalah panjang pattern.
    """
    
    def __init__(self):
        pass
    
    def compute_lps_array(self, pattern: str) -> List[int]:
        """
        Menghitung Longest Proper Prefix which is also Suffix (LPS) array.
        LPS array digunakan untuk menghindari pencocokan karakter yang tidak perlu.
        
        Args:
            pattern (str): Pattern yang akan dicari
            
        Returns:
            List[int]: Array LPS untuk pattern
        """
        m = len(pattern)
        lps = [0] * m
        length = 0  # panjang longest proper prefix yang juga suffix
        i = 1
        
        # Loop untuk menghitung lps[i] untuk i = 1 to m-1
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    # Ini adalah bagian terpenting dari algoritma KMP
                    # Gunakan nilai lps yang sudah dihitung sebelumnya
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        return lps
    
    def search(self, text: str, pattern: str) -> int:
        """
        Mencari kemunculan pertama dari pattern dalam text menggunakan algoritma KMP.
        
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
        
        # Hitung LPS array untuk pattern
        lps = self.compute_lps_array(pattern)
        
        i = 0  # index untuk text
        j = 0  # index untuk pattern
        
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            
            if j == m:
                # Pattern ditemukan
                return i - j
            elif i < n and pattern[j] != text[i]:
                # Karakter tidak cocok setelah j matches
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        return -1  # Pattern tidak ditemukan
    
    def search_all(self, text: str, pattern: str) -> List[int]:
        """
        Mencari semua kemunculan pattern dalam text menggunakan algoritma KMP.
        
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
        
        # Hitung LPS array untuk pattern
        lps = self.compute_lps_array(pattern)
        
        i = 0  # index untuk text
        j = 0  # index untuk pattern
        
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            
            if j == m:
                # Pattern ditemukan
                positions.append(i - j)
                j = lps[j - 1]  # Cari kemunculan berikutnya
            elif i < n and pattern[j] != text[i]:
                # Karakter tidak cocok setelah j matches
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
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