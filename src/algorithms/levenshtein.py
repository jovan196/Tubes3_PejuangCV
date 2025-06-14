from typing import List, Tuple

class LevenshteinDistance:
    def __init__(self):
        pass

    def distance(self, str1: str, str2: str) -> int:
        if not str1:
            return len(str2)
        if not str2:
            return len(str1)

        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # Inisialisasi baris dan kolom pertama
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        # DP untuk hitung edit distance
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],     
                        dp[i][j - 1],     
                        dp[i - 1][j - 1]   
                    )
        return dp[m][n]

    def similarity(self, str1: str, str2: str) -> float:
        if not str1 and not str2:
            return 1.0
        max_len = max(len(str1), len(str2), 1)
        return 1.0 - (self.distance(str1, str2) / max_len)

    def similarity_percentage(self, str1: str, str2: str) -> float:
        return self.similarity(str1, str2) * 100.0

    def is_similar(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        return self.similarity(str1, str2) >= threshold

    def find_closest_match(self, target: str, candidates: List[str]) -> Tuple[str, float]:
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
        # Ambil semua kandidat dengan similarity >= threshold
        result = []
        for candidate in candidates:
            sim = self.similarity(target, candidate)
            if sim >= threshold:
                result.append((candidate, sim))
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def distance_with_operations(self, str1: str, str2: str) -> Tuple[int, List[str]]:
        # Hitung jarak edit dan detail operasi 
        if not str1:
            return len(str2), [f"Insert '{c}'" for c in str2]
        if not str2:
            return len(str1), [f"Delete '{c}'" for c in str1]

        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i - 1] == str2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])

        operations = []
        i, j = m, n
        while i > 0 or j > 0:
            if i > 0 and j > 0 and str1[i - 1] == str2[j - 1]:
                i -= 1
                j -= 1
            elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
                operations.append(f"Substitute '{str1[i - 1]}' with '{str2[j - 1]}'")
                i -= 1
                j -= 1
            elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
                operations.append(f"Delete '{str1[i - 1]}'")
                i -= 1
            elif j > 0 and dp[i][j] == dp[i][j - 1] + 1:
                operations.append(f"Insert '{str2[j - 1]}'")
                j -= 1

        operations.reverse()
        return dp[m][n], operations

    def normalized_distance(self, str1: str, str2: str) -> float:
        max_len = max(len(str1), len(str2), 1)
        return self.distance(str1, str2) / max_len