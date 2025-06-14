# algorithms/aho_corasick.py
from typing import List, Dict, Set
from collections import deque, defaultdict

class TrieNode:
    """Node untuk Trie yang digunakan dalam algoritma Aho-Corasick"""
    
    def __init__(self):
        self.children = {}  # Dictionary untuk child nodes
        self.failure = None  # Failure link
        self.output = []  # Pattern yang berakhir di node ini
        self.is_end = False  # Apakah node ini akhir dari sebuah pattern

class AhoCorasickSearch:
    """
    Implementasi algoritma Aho-Corasick untuk multi-pattern string matching.
    Algoritma ini dapat mencari multiple patterns secara bersamaan dalam satu pass.
    Kompleksitas waktu: O(n + m + z) dimana n = panjang text, m = total panjang patterns, z = jumlah matches
    """
    
    def __init__(self):
        self.root = TrieNode()
        self.patterns = []
    
    def add_pattern(self, pattern: str) -> None:
        """
        Menambahkan pattern ke dalam Trie.
        
        Args:
            pattern (str): Pattern yang akan ditambahkan
        """
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
        """
        Membangun failure links untuk semua node dalam Trie.
        Failure links digunakan untuk menentukan state berikutnya ketika terjadi mismatch.
        """
        # BFS untuk membangun failure links
        queue = deque()
        
        # Set failure links untuk children dari root
        for child in self.root.children.values():
            child.failure = self.root
            queue.append(child)
        
        # BFS untuk node lainnya
        while queue:
            current = queue.popleft()
            
            for char, child in current.children.items():
                queue.append(child)
                
                # Cari failure link untuk child
                failure = current.failure
                while failure is not None and char not in failure.children:
                    failure = failure.failure
                
                if failure is not None:
                    child.failure = failure.children[char]
                else:
                    child.failure = self.root
                
                # Tambahkan output dari failure node ke child
                child.output.extend(child.failure.output)
    
    def search_multiple(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """
        Mencari multiple patterns dalam text menggunakan algoritma Aho-Corasick.
        
        Args:
            text (str): Teks yang akan dicari
            patterns (List[str]): List berisi patterns yang dicari
            
        Returns:
            Dict[str, List[int]]: Dictionary dengan pattern sebagai key dan list posisi sebagai value
        """
        # Reset dan build automaton
        self.root = TrieNode()
        self.patterns = []
        
        # Tambahkan semua patterns ke Trie
        for pattern in patterns:
            if pattern.strip():  # Hanya tambahkan pattern yang tidak kosong
                self.add_pattern(pattern.strip())
        
        if not self.patterns:
            return {}
        
        # Build failure links
        self.build_failure_links()
        
        # Cari patterns dalam text
        results = defaultdict(list)
        current = self.root
        
        for i, char in enumerate(text):
            # Traverse failure links sampai menemukan karakter yang cocok atau kembali ke root
            while current is not None and char not in current.children:
                current = current.failure
            
            if current is None:
                current = self.root
                continue
            
            current = current.children[char]
            
            # Check untuk matches
            for pattern in current.output:
                # Posisi akhir pattern ditemukan di index i
                # Posisi awal pattern adalah i - len(pattern) + 1
                start_pos = i - len(pattern) + 1
                results[pattern].append(start_pos)
        
        return dict(results)
    
    def search_single(self, text: str, pattern: str) -> List[int]:
        """
        Mencari single pattern dalam text.
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            List[int]: List berisi semua index kemunculan pattern dalam text
        """
        results = self.search_multiple(text, [pattern])
        return results.get(pattern, [])
    
    def count_occurrences(self, text: str, pattern: str) -> int:
        """
        Menghitung jumlah kemunculan pattern dalam text.
        
        Args:
            text (str): Teks yang akan dicari
            pattern (str): Pattern yang dicari
            
        Returns:
            int: Jumlah kemunculan pattern dalam text
        """
        return len(self.search_single(text, pattern))
    
    def search_case_insensitive(self, text: str, patterns: List[str]) -> Dict[str, List[int]]:
        """
        Mencari patterns dalam text tanpa memperhatikan case (case-insensitive).
        
        Args:
            text (str): Teks yang akan dicari
            patterns (List[str]): List berisi patterns yang dicari
            
        Returns:
            Dict[str, List[int]]: Dictionary dengan pattern sebagai key dan list posisi sebagai value
        """
        # Convert ke lowercase untuk pencarian
        lower_text = text.lower()
        lower_patterns = [p.lower() for p in patterns]
        
        # Lakukan pencarian
        lower_results = self.search_multiple(lower_text, lower_patterns)
        
        # Map kembali ke pattern asli
        results = {}
        for i, original_pattern in enumerate(patterns):
            lower_pattern = lower_patterns[i]
            if lower_pattern in lower_results:
                results[original_pattern] = lower_results[lower_pattern]
        
        return results
    
    def find_all_matches(self, text: str, patterns: List[str]) -> List[Dict]:
        """
        Mencari semua matches dan mengembalikan informasi detail.
        
        Args:
            text (str): Teks yang akan dicari
            patterns (List[str]): List berisi patterns yang dicari
            
        Returns:
            List[Dict]: List berisi informasi detail setiap match
        """
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
        
        # Sort berdasarkan posisi
        matches.sort(key=lambda x: x['position'])
        return matches