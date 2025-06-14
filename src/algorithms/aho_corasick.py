from typing import List, Dict, Set
from collections import deque, defaultdict

class TrieNode:
    def __init__(self):
        self.children = {}
        self.failure = None
        self.output = []
        self.is_end = False

class AhoCorasickSearch:
    def __init__(self):
        self.root = TrieNode()
        self.patterns = []
    
    def add_pattern(self, pattern: str) -> None:
        # Tambahkan satu pattern ke trie
        if pattern not in self.patterns:
            self.patterns.append(pattern)
        node = self.root
        for char in pattern:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.output.append(pattern)
    
    def build_failure_links(self) -> None:
        # Bangun failure link 
        queue = deque()
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)
        while queue:
            current = queue.popleft()
            for char, child in current.children.items():
                queue.append(child)
                failure = current.failure
                while failure is not None and char not in failure.children:
                    failure = failure.failure
                child.failure = failure.children[char] if failure and char in failure.children else self.root
                child.output.extend(child.failure.output)
    
    def search_multiple(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        # Cari semua pola, lalu kembalikan posisi kemunculannya
        self.root = TrieNode()
        self.patterns = []
        for pattern in patterns:
            if pattern.strip():
                self.add_pattern(pattern.strip())
        if not self.patterns:
            return {}
        self.build_failure_links()
        results = defaultdict(list)
        current = self.root
        for i, char in enumerate(text):
            while current is not None and char not in current.children:
                current = current.failure
            if current is None:
                current = self.root
                continue
            current = current.children[char]
            for pattern in current.output:
                start_pos = i - len(pattern) + 1
                results[pattern].append(start_pos)
        return dict(results)
    
    def search_single(self, text: str, pattern: str) -> List[int]:
        # Cari satu pola, lalu kembalikan semua posisi munculnya
        results = self.search_multiple(text, [pattern])
        return results.get(pattern, [])
    
    def count_occurrences(self, text: str, pattern: str) -> int:
        # Hitung jumlah kemunculan satu pola
        return len(self.search_single(text, pattern))
    
    def search_case_insensitive(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        # Tidak case sensitive
        lower_text = text.lower()
        lower_patterns = [p.lower() for p in patterns]
        lower_results = self.search_multiple(lower_text, lower_patterns)
        results = {}
        for i, original_pattern in enumerate(patterns):
            lower_pattern = lower_patterns[i]
            if lower_pattern in lower_results:
                results[original_pattern] = lower_results[lower_pattern]
        return results
    
    def find_all_matches(self, text: str, patterns: List[str]) -> List[Dict]:
        # Kebalikan detail match
        results = self.search_multiple(text, patterns)
        matches = []
        for pattern, positions in results.items():
            for pos in positions:
                matches.append({
                    'pattern': pattern,
                    'position': pos,
                    'end_position': pos + len(pattern) - 1,
                    'matched_text': text[pos:pos + len(pattern)]
                })
        matches.sort(key=lambda x: x['position'])
        return matches
