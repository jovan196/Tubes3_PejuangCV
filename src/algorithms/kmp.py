from typing import List

class KMPSearch:
    def __init__(self):
        pass

    def compute_lps_array(self, pattern: str) -> List[int]:
        # LPS array
        m = len(pattern)
        lps = [0] * m
        length = 0
        i = 1
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    def search(self, text: str, pattern: str) -> int:
        # Cari kemunculan pertama pattern dalam teks
        if not pattern or not text:
            return -1
        n = len(text)
        m = len(pattern)
        lps = self.compute_lps_array(pattern)
        i = j = 0
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            if j == m:
                return i - j
            elif i < n and pattern[j] != text[i]:
                j = lps[j - 1] if j != 0 else 0
                if j == 0:
                    i += 1
        return -1

    def search_all(self, text: str, pattern: str) -> List[int]:
        # Cari semua kemunculan pattern
        if not pattern or not text:
            return []
        positions = []
        n = len(text)
        m = len(pattern)
        lps = self.compute_lps_array(pattern)
        i = j = 0
        while i < n:
            if pattern[j] == text[i]:
                i += 1
                j += 1
            if j == m:
                positions.append(i - j)
                j = lps[j - 1]
            elif i < n and pattern[j] != text[i]:
                j = lps[j - 1] if j != 0 else 0
                if j == 0:
                    i += 1
        return positions

    def count_occurrences(self, text: str, pattern: str) -> int:
        # Menghitung jumlah kemunculan pattern
        return len(self.search_all(text, pattern))

    def search_case_insensitive(self, text: str, pattern: str) -> List[int]:
        return self.search_all(text.lower(), pattern.lower())