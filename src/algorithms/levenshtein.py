# algorithms/levenshtein.py
from typing import List, Tuple

class LevenshteinDistance:
    """
    Implementasi algoritma Levenshtein Distance untuk mengukur similarity/jarak edit antar string.
    Algoritma ini menghitung jumlah minimum operasi edit (insert, delete, substitute) 
    yang diperlukan untuk mengubah satu string menjadi string lain.
    Kompleksitas waktu: O(m*n) dimana m dan n adalah panjang kedua string.
    """
    
    def __init__(self):
        pass
    
    def distance(self, str1: str, str2: str) -> int:
        """
        Menghitung Levenshtein distance antara dua string.
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            
        Returns:
            int: Jarak Levenshtein antara kedua string
        """
        if not str1:
            return len(str2)
        if not str2:
            return len(str1)
        
        # Buat matrix untuk dynamic programming
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Inisialisasi base cases
        for i in range(m + 1):
            dp[i][0] = i  # Jarak dari string kosong
        for j in range(n + 1):
            dp[0][j] = j  # Jarak ke string kosong
        
        # Fill matrix menggunakan dynamic programming
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    # Karakter sama, tidak perlu operasi edit
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    # Ambil minimum dari tiga operasi
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Deletion
                        dp[i][j - 1],      # Insertion
                        dp[i - 1][j - 1]   # Substitution
                    )
        
        return dp[m][n]
    
    def similarity(self, str1: str, str2: str) -> float:
        """
        Menghitung similarity ratio antara dua string berdasarkan Levenshtein distance.
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            
        Returns:
            float: Similarity ratio antara 0.0 dan 1.0 (1.0 = identik)
        """
        if not str1 and not str2:
            return 1.0
        
        max_len = max(len(str1), len(str2))
        if max_len == 0:
            return 1.0
        
        distance = self.distance(str1, str2)
        return 1.0 - (distance / max_len)
    
    def similarity_percentage(self, str1: str, str2: str) -> float:
        """
        Menghitung similarity percentage antara dua string.
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            
        Returns:
            float: Similarity percentage antara 0.0 dan 100.0
        """
        return self.similarity(str1, str2) * 100.0
    
    def is_similar(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """
        Menentukan apakah dua string similar berdasarkan threshold.
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            threshold (float): Threshold similarity (default: 0.8)
            
        Returns:
            bool: True jika similarity >= threshold
        """
        return self.similarity(str1, str2) >= threshold
    
    def find_closest_match(self, target: str, candidates: List[str]) -> Tuple[str, float]:
        """
        Mencari string yang paling mirip dengan target dari list candidates.
        
        Args:
            target (str): String target
            candidates (List[str]): List string kandidat
            
        Returns:
            Tuple[str, float]: Tuple berisi string terbaik dan similarity score
        """
        if not candidates:
            return "", 0.0
        
        best_match = ""
        best_similarity = 0.0
        
        for candidate in candidates:
            sim = self.similarity(target, candidate)
            if sim > best_similarity:
                best_similarity = sim
                best_match = candidate
        
        return best_match, best_similarity
    
    def find_all_similar(self, target: str, candidates: List[str], threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Mencari semua string yang mirip dengan target di atas threshold tertentu.
        
        Args:
            target (str): String target
            candidates (List[str]): List string kandidat
            threshold (float): Threshold minimum similarity
            
        Returns:
            List[Tuple[str, float]]: List tuple berisi string dan similarity score
        """
        similar_strings = []
        
        for candidate in candidates:
            sim = self.similarity(target, candidate)
            if sim >= threshold:
                similar_strings.append((candidate, sim))
        
        # Sort berdasarkan similarity score (descending)
        similar_strings.sort(key=lambda x: x[1], reverse=True)
        return similar_strings
    
    def distance_with_operations(self, str1: str, str2: str) -> Tuple[int, List[str]]:
        """
        Menghitung Levenshtein distance beserta operasi yang diperlukan.
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            
        Returns:
            Tuple[int, List[str]]: Distance dan list operasi yang diperlukan
        """
        if not str1:
            return len(str2), [f"Insert '{c}'" for c in str2]
        if not str2:
            return len(str1), [f"Delete '{c}'" for c in str1]
        
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Inisialisasi base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # Deletion
                        dp[i][j - 1],      # Insertion
                        dp[i - 1][j - 1]   # Substitution
                    )
        
        # Backtrack untuk mendapatkan operasi
        operations = []
        i, j = m, n
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and str1[i - 1] == str2[j - 1]:
                # Karakter sama, tidak perlu operasi
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                # Substitution
                operations.append(f"Substitute '{str1[i - 1]}' with '{str2[j - 1]}'")
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                # Deletion
                operations.append(f"Delete '{str1[i - 1]}'")
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                # Insertion
                operations.append(f"Insert '{str2[j - 1]}'")
                j -= 1
        
        operations.reverse()
        return dp[m][n], operations
    
    def normalized_distance(self, str1: str, str2: str) -> float:
        """
        Menghitung normalized Levenshtein distance (0.0 - 1.0).
        
        Args:
            str1 (str): String pertama
            str2 (str): String kedua
            
        Returns:
            float: Normalized distance antara 0.0 dan 1.0
        """
        max_len = max(len(str1), len(str2), 1)  # Hindari division by zero
        return self.distance(str1, str2) / max_len