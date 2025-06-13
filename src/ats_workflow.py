from algorithms.kmp import kmp_search
from algorithms.bm import bm_search
from algorithms.levenshtein import levenshtein
from utils.db_utils import fetch_applications, fetch_applicants
from utils.pdf_utils import extract_text_from_pdf
import os

def match_keywords(text, keywords, algorithm):
    # Normalisasi teks dan kata kunci
    text = text.lower()
    results = {}
    for kw in keywords:
        pattern = kw.strip().lower()
        if algorithm == "kmp":
            idxs = kmp_search(text, pattern)
        elif algorithm == "bm":
            idxs = bm_search(text, pattern)
        else:
            raise ValueError("Unsupported algorithm. Use 'kmp' or 'bm'.")
        results[pattern] = len(idxs)
    return results

def fuzzy_keywords(text, keywords, threshold=0.8):
    # Pencocokan fuzzy dengan jarak Levenshtein
    import re
    text_words = set(re.findall(r'\w+', text.lower()))
    result = {}
    for kw in keywords:
        best_score = 0
        for word in text_words:
            dist = levenshtein(word, kw.lower())
            sim = 1 - dist / max(len(word), len(kw))
            if sim > best_score:
                best_score = sim
        if best_score >= threshold:
            result[kw] = best_score
    return result

def main_workflow(user_keywords, top_n, algorithm):
    # Workflow utama untuk mengambil data lamaran, mencocokkan kata kunci, dan mengembalikan hasil
    apps = fetch_applications()
    results = []
    for app in apps:
        cv_path = app['cv_path']
        if not os.path.exists(cv_path):
            continue
        text = extract_text_from_pdf(cv_path)
        match = match_keywords(text, user_keywords, algorithm=algorithm)
        match_count = sum(1 for v in match.values() if v > 0)
        results.append({
            "detail_id": app['detail_id'],
            "applicant_id": app['applicant_id'],
            "cv_path": cv_path,
            "match_count": match_count,
            "matches": match
        })
    # Urutkan hasil berdasarkan jumlah kecocokan
    results.sort(key=lambda x: x['match_count'], reverse=True)
    # Jika tidak ada kecocokan, lakukan pencocokan fuzzy
    if results and results[0]["match_count"] == 0:
        for res in results:
            text = extract_text_from_pdf(res['cv_path'])
            fuzzy = fuzzy_keywords(text, user_keywords)
            res['fuzzy_matches'] = fuzzy
            res['fuzzy_score'] = sum(fuzzy.values())
        results.sort(key=lambda x: x.get('fuzzy_score', 0), reverse=True)
    # mengembalikan hanya top_n hasil
    return results[:top_n]