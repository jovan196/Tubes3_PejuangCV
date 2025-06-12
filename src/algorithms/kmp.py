def kmp_search(text, pattern):
    # Buat array dari LPS (Longest Prefix Suffix)
    lps = [0]*len(pattern)
    j = 0
    for i in range(1, len(pattern)):
        while j and pattern[i] != pattern[j]:
            j = lps[j-1]
        if pattern[i] == pattern[j]:
            j += 1
            lps[i] = j
    # Proses pencarian KMP
    res = []
    i = j = 0
    while i < len(text): 
        if pattern[j] == text[i]:
            i += 1
            j += 1
        if j == len(pattern):
            res.append(i-j)
            j = lps[j-1]
        elif i < len(text) and pattern[j] != text[i]:
            if j != 0:
                j = lps[j-1]
            else:
                i += 1
    return res  # mengembalikan indeks pencocokan pattern