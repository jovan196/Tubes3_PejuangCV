from typing import List, Dict

class BoyerMooreSearch:
    def __init__(self):
        pass
    
    def bad_char_heuristic(self, pattern: str) -> Dict[str, int]:
        # Buat tabel posisi terakhir tiap karakter dalam pattern
        bad_char = {}
        m = len(pattern)
        for i in range(256):
            bad_char[chr(i)] = -1
        for i in range(m):
            bad_char[pattern[i]] = i
        return bad_char
    
    def good_suffix_heuristic(self, pattern: str) -> List[int]:
        # Tabel pergeseran berdasarkan suffix yang cocok
        m = len(pattern)
        shift = [0] * (m + 1)
        border = [0] * (m + 1)
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
        j = border[0]
        for i in range(m + 1):
            if shift[i] == 0:
                shift[i] = j
            if i == j:
                j = border[j]
        return shift
    
    def search(self, text: str, pattern: str) -> int:
        # Cari kemunculan pertama dari pattern 
        if not pattern or not text:
            return -1
        n = len(text)
        m = len(pattern)
        bad_char = self.bad_char_heuristic(pattern)
        good_suffix = self.good_suffix_heuristic(pattern)
        s = 0
        while s <= n - m:
            j = m - 1
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
            if j < 0:
                return s
            else:
                bad_char_shift = j - bad_char.get(text[s + j], -1)
                good_suffix_shift = good_suffix[j + 1]
                s += max(bad_char_shift, good_suffix_shift)
        return -1
    
    def search_all(self, text: str, pattern: str) -> List[int]:
        # Cari semua kemunculan pattern 
        if not pattern or not text:
            return []
        positions = []
        n = len(text)
        m = len(pattern)
        bad_char = self.bad_char_heuristic(pattern)
        good_suffix = self.good_suffix_heuristic(pattern)
        s = 0
        while s <= n - m:
            j = m - 1
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
            if j < 0:
                positions.append(s)
                s += good_suffix[0]
            else:
                bad_char_shift = j - bad_char.get(text[s + j], -1)
                good_suffix_shift = good_suffix[j + 1]
                s += max(bad_char_shift, good_suffix_shift)
        return positions
    
    def count_occurrences(self, text: str, pattern: str) -> int:
        # Hitung jumlah kemunculan pattern
        return len(self.search_all(text, pattern))
    
    def search_case_insensitive(self, text: str, pattern: str) -> List[int]:
        return self.search_all(text.lower(), pattern.lower())
