import sys
import os
import flet as ft
import time
import math
import random
from typing import List, Dict

# Pastikan src ada di sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from algorithms.kmp import KMPSearch
from algorithms.bm import BoyerMooreSearch
from algorithms.aho_corasick import AhoCorasickSearch
from algorithms.levenshtein import LevenshteinDistance
from algorithms.encryption import DataEncryption
from database.db_manager import DatabaseManager
from utils.pdf_extractor import PDFExtractor
from utils.regex_extractor import RegexExtractor

class ATSFrontend:
    def __init__(self):
        self.current_page = "home"
        self.search_results = []
        self.selected_cv = None
        self.current_pagination_page = 1
        self.results_per_page = 5

        # Backend
        self.db_manager = DatabaseManager()
        self.kmp_search = KMPSearch()
        self.bm_search = BoyerMooreSearch()
        self.ac_search = AhoCorasickSearch()
        self.levenshtein = LevenshteinDistance()
        self.pdf_extractor = PDFExtractor()
        self.regex_extractor = RegexExtractor()

    def main(self, page: ft.Page):
        page.title = "ATS - Applicant Tracking System"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.window_width = 1400
        page.window_height = 900
        page.window_resizable = True
        page.padding = 0
        page.scroll = ft.ScrollMode.AUTO

        page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.INDIGO,
            visual_density=ft.VisualDensity.COMFORTABLE,
        )

        self.page = page
        self.init_components()

        # Main container
        self.main_container = ft.Container(
            content=ft.Column([
                self.create_header(),
                self.home_view,
                self.summary_view
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
            expand=True
        )

        page.add(self.main_container)
        page.update()

    def init_components(self):
        self.keyword_input = ft.TextField(
            label="Masukkan kata kunci pencarian",
            hint_text="Contoh: React, Express, HTML",
            width=500,
            multiline=False,
            prefix_icon=ft.Icons.SEARCH,
            border_radius=10,
            border_color=ft.Colors.INDIGO_400,
            focused_border_color=ft.Colors.INDIGO_600,
        )

        self.algorithm_radio = ft.RadioGroup(
            content=ft.Row([
                ft.Container(
                    content=ft.Radio(value="KMP", label="KMP (Knuth-Morris-Pratt)"),
                    width=190
                ),
                ft.Container(
                    content=ft.Radio(value="BM", label="BM (Boyer-Moore)"),
                    width=150
                ),
                ft.Container(
                    content=ft.Radio(value="AC", label="AC (Aho-Corasick)"),
                    width=150
                ),
            ], spacing=10),
            value="KMP"
        )
        self.top_matches_dropdown = ft.Dropdown(
            width=250,
            options=[
                ft.dropdown.Option("5", "Top 5 CV"),
                ft.dropdown.Option("10", "Top 10 CV"),
                ft.dropdown.Option("15", "Top 15 CV"),
                ft.dropdown.Option("20", "Top 20 CV"),
                ft.dropdown.Option("25", "Top 25 CV"),
                ft.dropdown.Option("all", "Tampilkan Semua CV"),
            ],
            value="10",
            border_radius=10,
            border_color=ft.Colors.INDIGO_400,
            focused_border_color=ft.Colors.INDIGO_600,
        )

        self.search_button = ft.Container(
            content=ft.ElevatedButton(
                content=ft.Row([
                    ft.Text("🔍 Mulai Pencarian CV", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10),
                on_click=self.search_cv,
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.TRANSPARENT,
                    color=ft.Colors.WHITE,
                    padding=ft.padding.all(20),
                    animation_duration=300,
                    elevation={"": 8, "hovered": 12},
                    shape=ft.RoundedRectangleBorder(radius=15),
                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                    side=ft.BorderSide(2, ft.Colors.with_opacity(0.3, ft.Colors.WHITE)),
                    shadow_color=ft.Colors.with_opacity(0.4, ft.Colors.BLUE_GREY_900),
                ),
                width=250,
                height=70
            ),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[
                    ft.Colors.BLUE_900,
                    ft.Colors.INDIGO_900,
                    ft.Colors.BLUE_900,
                    ft.Colors.INDIGO_900,
                ]
            ),
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLUE_GREY_900),
                offset=ft.Offset(0, 6)
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
            on_hover=self.on_button_hover,
        )

        self.loading_indicator = ft.ProgressRing(
            width=30,
            height=30,
            stroke_width=3,
            color=ft.Colors.INDIGO_400,
            visible=False
        )

        self.summary_result_section = ft.Container(
            content=ft.Column([
                ft.Text("📊 Summary Result Section", size=18, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Belum ada pencarian yang dilakukan", size=14, color=ft.Colors.GREY_600)
            ]),
            padding=20,
            border=ft.border.all(2, ft.Colors.INDIGO_200),
            border_radius=15,
            bgcolor=ft.Colors.INDIGO_50,
            visible=False,
            width=600,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_900),
                offset=ft.Offset(0, 4)
            )
        )

        self.results_container = ft.Column(
            spacing=15,
            scroll=ft.ScrollMode.AUTO
        )

        self.pagination_container = ft.Container(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            padding=20,
            visible=False
        )

        self.header_back_button = ft.IconButton(
            icon=ft.Icons.HOME,
            tooltip="Kembali ke Beranda",
            on_click=self.go_to_home,
            visible=False,
            icon_size=30,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100,
                color=ft.Colors.INDIGO_600,
                shape=ft.CircleBorder(),
            )
        )

        self.home_view = self.create_home_view()
        self.summary_view = ft.Container(visible=False)

    def on_button_hover(self, e):
        if e.data == "true":
            e.control.shadow = ft.BoxShadow(
                spread_radius=3,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.6, ft.Colors.BLUE_GREY_900),
                offset=ft.Offset(0, 8)
            )
            e.control.scale = 1.02
        else:
            e.control.shadow = ft.BoxShadow(
                spread_radius=2,
                blur_radius=15,
                color=ft.Colors.with_opacity(0.4, ft.Colors.BLUE_GREY_900),
                offset=ft.Offset(0, 6)
            )
            e.control.scale = 1.0
        e.control.update()

    def create_header(self):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(ft.Icons.WORK_OUTLINE, size=60, color=ft.Colors.WHITE),
                        width=80,
                        height=80,
                        bgcolor=ft.Colors.INDIGO_600,
                        border_radius=40,
                        alignment=ft.alignment.center,
                        shadow=ft.BoxShadow(
                            spread_radius=1,
                            blur_radius=10,
                            color=ft.Colors.with_opacity(0.3, ft.Colors.INDIGO_900),
                            offset=ft.Offset(0, 4)
                        )
                    ),
                    ft.Column([
                        ft.Text(
                            "Applicant Tracking System (ATS)",
                            size=36,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.INDIGO_600
                        ),
                        ft.Text(
                            "Pemanfaatan Pattern Matching untuk Membangun Sistem ATS Berbasis CV Digital",
                            size=16,
                            color=ft.Colors.GREY_600
                        )
                    ], spacing=5, expand=True),
                    self.header_back_button
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ]),
            padding=ft.padding.only(bottom=30),
            margin=ft.margin.only(bottom=20),
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.Colors.INDIGO_50, ft.Colors.WHITE]
            ),
            border=ft.border.only(bottom=ft.BorderSide(3, ft.Colors.INDIGO_200))
        )

    def create_home_view(self):
        return ft.Container(
            content=ft.Column([
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📃 Pencarian CV", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600)
                        ]),
                        ft.Divider(thickness=2, color=ft.Colors.INDIGO_200),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Kata Kunci Pencarian:", size=16, weight=ft.FontWeight.W_500),
                                self.keyword_input,
                                ft.Text("Untuk multiple keywords pisahkan dengan tanda koma (contoh: React, HTML, Javascript)",
                                       size=12, color=ft.Colors.GREY_600, italic=True)
                            ], spacing=8),
                            margin=ft.margin.only(bottom=25)
                        ),
                        ft.Row([
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Pilih Algoritma Pencarian:", size=16, weight=ft.FontWeight.W_500),
                                    ft.Container(
                                        content=self.algorithm_radio,
                                        padding=15,
                                        border=ft.border.all(2, ft.Colors.INDIGO_300),
                                        border_radius=10,
                                        bgcolor=ft.Colors.INDIGO_50
                                    )
                                ], spacing=8),
                                expand=1
                            ),
                            ft.VerticalDivider(width=30, color=ft.Colors.INDIGO_100),
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("Jumlah CV yang Ditampilkan:", size=16, weight=ft.FontWeight.W_500),
                                    self.top_matches_dropdown
                                ], spacing=8),
                                expand=1
                            )
                        ], spacing=20),
                        ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    self.search_button,
                                    self.loading_indicator
                                ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                                ft.Text("Klik tombol di atas untuk memulai proses pencarian",
                                       size=12, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER)
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                            margin=ft.margin.only(top=30)
                        )
                    ], spacing=15),
                    padding=30,
                    border=ft.border.all(2, ft.Colors.INDIGO_200),
                    border_radius=20,
                    bgcolor=ft.Colors.with_opacity(0.7, ft.Colors.INDIGO_50),
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_900),
                        offset=ft.Offset(0, 5)
                    )
                ),
                ft.Container(
                    content=ft.Row([
                        self.summary_result_section
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    margin=ft.margin.only(top=30)
                ),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("📋 Hasil Pencarian CV", size=22, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Text("Kartu CV akan menampilkan nama kandidat, jumlah kecocokan, dan frekuensi keyword",
                               size=14, color=ft.Colors.GREY_600),
                        ft.Divider(thickness=2, color=ft.Colors.INDIGO_200),
                        self.results_container,
                        self.pagination_container
                    ], spacing=15),
                    padding=25,
                    border=ft.border.all(2, ft.Colors.INDIGO_100),
                    border_radius=15,
                    bgcolor=ft.Colors.WHITE,
                    margin=ft.margin.only(top=30),
                    shadow=ft.BoxShadow(
                        spread_radius=0,
                        blur_radius=10,
                        color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                        offset=ft.Offset(0, 4)
                    )
                )
            ], spacing=20, scroll=ft.ScrollMode.AUTO),
            visible=True
        )

    def search_cv(self, e):
        if not self.keyword_input.value:
            self.show_snackbar("⚠️ Mohon masukkan kata kunci untuk pencarian!", ft.Colors.ORANGE_600)
            return

        self.loading_indicator.visible = True
        self.search_button.content.content = ft.Row([
            ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=ft.Colors.WHITE, size=24),
            ft.Text("Sedang mencari...", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        self.search_button.content.disabled = True
        self.page.update()

        try:
            keywords = [k.strip() for k in self.keyword_input.value.split(",") if k.strip()]
            algorithm = self.algorithm_radio.value
            top_matches = self.top_matches_dropdown.value

            # Ambil semua data CV dari database
            cv_data = self.db_manager.get_all_cvs()
            if not cv_data:
                self.show_snackbar("⚠️ Tidak ada CV dalam database. Silakan upload CV terlebih dahulu.", ft.Colors.ORANGE_600)
                return

            start_time = time.time()
            all_results = []
            for cv in cv_data:
                cv_path = os.path.join("data", cv["cv_path"])
                cv_text = self.pdf_extractor.extract_text(cv_path)
                matches = {}
                total_matches = 0

                if not cv_text:
                    all_results.append({
                        'cv_data': {
                            'name': f"{cv['first_name']} {cv['last_name']}",
                            'position': cv['application_role'],
                            'company': "Unknown",
                            'skills': []
                        },
                        'matches': {},
                        'match_count': 0,
                        'match_type': 'no_match',
                        'similarity_score': 0.0
                    })
                    continue

                cv_text_lower = cv_text.lower()
                keywords_lower = [k.lower() for k in keywords]

                # --- Exact match ---
                if algorithm == "AC":
                    ac_result = self.ac_search.search_multiple(cv_text_lower, keywords_lower)
                    for kw in keywords_lower:
                        count = len(ac_result.get(kw, []))
                        if count > 0:
                            matches[kw] = count
                            total_matches += count
                else:
                    for keyword_lower in keywords_lower:
                        if algorithm == "KMP":
                            match_positions = self.kmp_search.search_all(cv_text_lower, keyword_lower)
                        elif algorithm == "BM":
                            match_positions = self.bm_search.search_all(cv_text_lower, keyword_lower)
                        else:
                            match_positions = self.kmp_search.search_all(cv_text_lower, keyword_lower)
                        if match_positions:
                            matches[keyword_lower] = len(match_positions)
                            total_matches += len(match_positions)

                # --- Fuzzy match (Levenshtein) jika tidak ada exact match ---
                fuzzy_matches = {}
                fuzzy_total = 0
                if total_matches == 0:
                    # Split seluruh teks CV menjadi kata-kata unik
                    words = set(cv_text_lower.split())
                    for keyword_lower in keywords_lower:
                        for word in words:
                            if len(word) >= 3:
                                similarity = self.levenshtein.similarity(keyword_lower, word)
                                if similarity >= 0.7:
                                    fuzzy_matches[keyword_lower] = fuzzy_matches.get(keyword_lower, 0) + 1
                                    fuzzy_total += 1

                # Gabungkan hasil
                if total_matches > 0:
                    match_type = 'exact'
                    similarity_score = min(1.0, total_matches / len(keywords))
                elif fuzzy_total > 0:
                    match_type = 'fuzzy'
                    similarity_score = min(1.0, fuzzy_total / len(keywords))
                    matches = fuzzy_matches
                    total_matches = fuzzy_total
                else:
                    match_type = 'no_match'
                    similarity_score = 0.0

                all_results.append({
                    'cv_data': {
                        'name': f"{cv['first_name']} {cv['last_name']}",
                        'position': cv['application_role'],
                        'company': "Unknown",
                        'skills': self.regex_extractor.extract_skills(cv_text)
                    },
                    'matches': matches,
                    'match_count': total_matches,
                    'match_type': match_type,
                    'similarity_score': similarity_score
                })

            exact_time = (time.time() - start_time) * 1000

            # Sort dan filter hasil
            all_results.sort(key=lambda x: x['match_count'], reverse=True)
            if top_matches == "all":
                self.search_results = all_results
            else:
                self.search_results = all_results[:int(top_matches)]

            matching_count = len([r for r in self.search_results if r['match_count'] > 0])
            self.current_pagination_page = 1
            total_cvs = len(all_results)
            fuzzy_time = 0

            self.update_summary_result_section(total_cvs, exact_time, fuzzy_time, algorithm)
            self.update_results_display()
            self.show_snackbar(f"✅ Pencarian selesai! Ditemukan {matching_count} CV relevan dari {total_cvs} total CV", ft.Colors.GREEN_600)

        except Exception as ex:
            self.show_snackbar(f"❌ Error dalam pencarian: {str(ex)}", ft.Colors.RED_600)
        finally:
            self.loading_indicator.visible = False
            self.search_button.content.disabled = False
            self.search_button.content.content = ft.Row([
                ft.Text("🔍 Mulai Pencarian CV", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            self.page.update()

    def update_summary_result_section(self, total_cvs: int, exact_time: float, fuzzy_time: float, algorithm: str):
        exact_match_text = f"Exact Match: {total_cvs} CVs scanned in {exact_time:.0f}ms"
        fuzzy_match_text = f"Fuzzy Match: {total_cvs} CVs scanned in {fuzzy_time:.0f}ms"

        self.summary_result_section.content = ft.Column([
            ft.Text("📊 Summary Result Section", size=18, weight=ft.FontWeight.BOLD),
            ft.Divider(color=ft.Colors.INDIGO_200),
            ft.Column([
                ft.Text(exact_match_text, size=14, weight=ft.FontWeight.W_500),
                ft.Text(fuzzy_match_text, size=14, weight=ft.FontWeight.W_500),
                ft.Divider(color=ft.Colors.INDIGO_100),
                ft.Text(f"Algoritma yang digunakan: {algorithm}", size=14, weight=ft.FontWeight.BOLD),
                ft.Text(f"Total CV relevan: {len([r for r in self.search_results if r['match_count'] > 0])}", size=14)
            ], spacing=8)
        ])
        self.summary_result_section.visible = True

    def get_paginated_results(self):
        filtered_results = [r for r in self.search_results if r['match_count'] > 0]
        if self.top_matches_dropdown.value == "all":
            filtered_results = self.search_results
        start_idx = (self.current_pagination_page - 1) * self.results_per_page
        end_idx = start_idx + self.results_per_page
        return filtered_results[start_idx:end_idx], len(filtered_results)

    def update_pagination(self, total_results: int):
        total_pages = math.ceil(total_results / self.results_per_page)
        if total_pages <= 1:
            self.pagination_container.visible = False
            return

        pagination_controls = []
        prev_button = ft.ElevatedButton(
            text="← Sebelumnya",
            on_click=self.prev_page,
            disabled=self.current_pagination_page <= 1,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100 if self.current_pagination_page > 1 else ft.Colors.GREY_200,
                color=ft.Colors.INDIGO_600 if self.current_pagination_page > 1 else ft.Colors.GREY_500,
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        pagination_controls.append(prev_button)

        start_page = max(1, self.current_pagination_page - 2)
        end_page = min(total_pages, start_page + 4)

        if start_page > 1:
            pagination_controls.append(ft.Text("...", color=ft.Colors.GREY_500))

        for page_num in range(start_page, end_page + 1):
            page_button = ft.ElevatedButton(
                text=str(page_num),
                on_click=lambda e, page=page_num: self.go_to_page(page),
                style=ft.ButtonStyle(
                    bgcolor=ft.Colors.INDIGO_600 if page_num == self.current_pagination_page else ft.Colors.INDIGO_100,
                    color=ft.Colors.WHITE if page_num == self.current_pagination_page else ft.Colors.INDIGO_600,
                    padding=ft.padding.all(12),
                    shape=ft.RoundedRectangleBorder(radius=8),
                ),
                width=50
            )
            pagination_controls.append(page_button)

        if end_page < total_pages:
            pagination_controls.append(ft.Text("...", color=ft.Colors.GREY_500))

        next_button = ft.ElevatedButton(
            text="Selanjutnya →",
            on_click=self.next_page,
            disabled=self.current_pagination_page >= total_pages,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100 if self.current_pagination_page < total_pages else ft.Colors.GREY_200,
                color=ft.Colors.INDIGO_600 if self.current_pagination_page < total_pages else ft.Colors.GREY_500,
                padding=ft.padding.symmetric(horizontal=15, vertical=10),
                shape=ft.RoundedRectangleBorder(radius=8),
            )
        )
        pagination_controls.append(next_button)

        page_info = ft.Text(
            f"Halaman {self.current_pagination_page} dari {total_pages} ({total_results} CV)",
            size=14,
            color=ft.Colors.GREY_600
        )

        self.pagination_container.content = ft.Column([
            ft.Row(pagination_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            ft.Container(page_info, padding=ft.padding.only(top=10))
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.pagination_container.visible = True

    def prev_page(self, e):
        if self.current_pagination_page > 1:
            self.current_pagination_page -= 1
            self.update_results_display()

    def next_page(self, e):
        paginated_results, total_results = self.get_paginated_results()
        total_pages = math.ceil(total_results / self.results_per_page)
        if self.current_pagination_page < total_pages:
            self.current_pagination_page += 1
            self.update_results_display()

    def go_to_page(self, page_num):
        self.current_pagination_page = page_num
        self.update_results_display()

    def update_results_display(self):
        self.results_container.controls.clear()
        if not self.search_results:
            self.results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.SEARCH_OFF, size=80, color=ft.Colors.GREY_400),
                        ft.Text("Tidak ada CV yang ditemukan",
                               size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                        ft.Text("Coba gunakan kata kunci yang berbeda",
                               size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center
                )
            )
            self.pagination_container.visible = False
        else:
            paginated_results, total_results = self.get_paginated_results()
            if not paginated_results:
                self.results_container.controls.append(
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.SEARCH_OFF, size=80, color=ft.Colors.GREY_400),
                            ft.Text("Tidak ada CV yang cocok dengan kata kunci",
                                   size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                            ft.Text("Coba kata kunci lain seperti: Python, React, JavaScript, HTML, CSS",
                                   size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                        padding=50,
                        alignment=ft.alignment.center
                    )
                )
                self.pagination_container.visible = False
            else:
                start_rank = (self.current_pagination_page - 1) * self.results_per_page + 1
                for i, result in enumerate(paginated_results):
                    card = self.create_cv_card(result, start_rank + i)
                    self.results_container.controls.append(card)
                self.update_pagination(total_results)
        try:
            self.results_container.update()
            self.pagination_container.update()
            self.page.update()
        except Exception:
            self.page.update()

    def create_cv_card(self, result: Dict, rank: int):
        cv_data = result['cv_data']
        matches = result['matches']
        match_count = result['match_count']
        match_type = result['match_type']
        similarity = result.get('similarity_score', 0.0)

        match_chips = []
        if matches:
            for keyword, count in matches.items():
                chip_color = ft.Colors.INDIGO_100 if match_type == 'exact' else ft.Colors.ORANGE_100
                text_color = ft.Colors.INDIGO_800 if match_type == 'exact' else ft.Colors.ORANGE_800
                match_chips.append(
                    ft.Container(
                        content=ft.Text(f"{keyword}: {count}x",
                                       size=12, weight=ft.FontWeight.W_500, color=text_color),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                        bgcolor=chip_color,
                        border_radius=15,
                        border=ft.border.all(1, text_color)
                    )
                )
        else:
            match_chips.append(
                ft.Container(
                    content=ft.Text("Tidak ada keyword yang cocok",
                                   size=12, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=15,
                    border=ft.border.all(1, ft.Colors.GREY_400)
                )
            )

        if match_count == 0:
            rank_color = ft.Colors.GREY_500
        elif rank <= 3:
            rank_color = ft.Colors.AMBER
        else:
            rank_color = ft.Colors.INDIGO_600

        if match_count > 5:
            card_gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(0.05, ft.Colors.INDIGO_400), ft.Colors.WHITE]
            )
        elif match_count > 0:
            card_gradient = ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.Colors.with_opacity(0.03, ft.Colors.INDIGO_200), ft.Colors.WHITE]
            )
        else:
            card_gradient = None

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Container(
                            content=ft.Text(f"#{rank}", color=ft.Colors.WHITE,
                                           size=16, weight=ft.FontWeight.BOLD),
                            width=50,
                            height=50,
                            bgcolor=rank_color,
                            border_radius=25,
                            alignment=ft.alignment.center,
                            shadow=ft.BoxShadow(
                                spread_radius=0,
                                blur_radius=5,
                                color=ft.Colors.with_opacity(0.3, ft.Colors.BLACK),
                                offset=ft.Offset(0, 2)
                            )
                        ),
                        ft.Column([
                            ft.Text(cv_data['name'], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"📍 {cv_data['position']} di {cv_data.get('company', '-')}",
                                   size=14, color=ft.Colors.GREY_600),
                            ft.Row([
                                ft.Icon(ft.Icons.TRENDING_UP, size=16,
                                       color=ft.Colors.GREEN_600 if match_count > 0 else ft.Colors.GREY_500),
                                ft.Text(f"Jumlah Kecocokan: {match_count}",
                                       size=14, weight=ft.FontWeight.W_500),
                                ft.Text(f"• {match_type.replace('_', ' ').title()}",
                                       size=12, color=ft.Colors.INDIGO_600 if match_type == 'exact'
                                       else ft.Colors.ORANGE_600 if match_type == 'fuzzy' else ft.Colors.GREY_500),
                                ft.Text(f"• Similarity: {similarity:.1%}",
                                       size=12, color=ft.Colors.GREY_600) if match_count > 0 else ft.Text("")
                            ])
                        ], expand=True, spacing=5),
                        ft.Row([
                            ft.ElevatedButton(
                                text="📄 Summary",
                                on_click=lambda e, cv=cv_data: self.show_summary(cv),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor={"": ft.Colors.GREEN_600, "hovered": ft.Colors.GREEN_700},
                                    padding=ft.padding.symmetric(horizontal=25, vertical=12),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=140
                            ),
                            ft.ElevatedButton(
                                text="👁️ View CV",
                                on_click=lambda e, cv=cv_data: self.view_cv(cv),
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    bgcolor={"": ft.Colors.INDIGO_600, "hovered": ft.Colors.INDIGO_700},
                                    padding=ft.padding.symmetric(horizontal=25, vertical=12),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                width=140
                            )
                        ], spacing=15)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Divider(color=ft.Colors.INDIGO_100),
                    ft.Column([
                        ft.Text("Kata Kunci yang Sesuai dan Frekuensinya:", size=14, weight=ft.FontWeight.W_500),
                        ft.Row(match_chips, wrap=True, spacing=8)
                    ], spacing=8)
                ], spacing=15),
                padding=20,
                gradient=card_gradient
            ),
            elevation=3,
            shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_900) if match_count > 0 else ft.Colors.with_opacity(0.1, ft.Colors.GREY_800),
            surface_tint_color=ft.Colors.INDIGO_50 if match_count > 0 else ft.Colors.GREY_50
        )

    def show_summary(self, cv_data: Dict):
        # Untuk demo, gunakan data dummy. Untuk produksi, ekstrak info dari PDF.
        mock_info = {
            'summary': f"Profesional berpengalaman di bidang {cv_data['position']} dengan keahlian yang solid dan track record yang baik di {cv_data.get('company', '-')}. Memiliki kemampuan analitis yang kuat dan dapat bekerja dalam tim maupun individu.",
            'skills': cv_data.get('skills', ['Python', 'JavaScript', 'React', 'SQL', 'Git', 'Docker', 'AWS']),
            'experience': [
                f"Senior {cv_data['position']} di {cv_data.get('company', '-')}",
                "Software Developer di StartupXYZ (2019-2021)",
                "Junior Developer di Tech Solutions (2018-2019)"
            ],
            'education': [
                "S1 Teknik Informatika, Institut Teknologi Bandung (2014-2018)",
                "SMA Negeri 1 Jakarta (2011-2014)"
            ],
            'contact': {
                'email': f"{cv_data['name'].lower().replace(' ', '.')}@email.com",
                'phone': f"+628{random.randint(10000000, 99999999)}",
                'location': random.choice(['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta'])
            }
        }

        summary_content = ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Kembali ke Hasil Pencarian",
                    on_click=self.go_to_home,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_100,
                        color=ft.Colors.INDIGO_600,
                        shape=ft.CircleBorder(),
                    )
                ),
                ft.Text("📄 Informasi CV", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600),
                ft.Container(expand=True),
                ft.Chip(
                    label=ft.Text("CV Aktif", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_600
                )
            ]),
            ft.Divider(thickness=2, color=ft.Colors.INDIGO_200),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.PERSON, size=30, color=ft.Colors.INDIGO_600),
                            ft.Text("Informasi Pribadi", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600)
                        ]),
                        ft.Divider(color=ft.Colors.INDIGO_100),
                        ft.Row([
                            ft.Column([
                                ft.Text(f"👤 Nama: {cv_data['name']}", size=16, weight=ft.FontWeight.W_500),
                                ft.Text(f"💼 Posisi: {cv_data['position']}", size=14),
                                ft.Text(f"🏢 Perusahaan: {cv_data.get('company', '-')}", size=14),
                            ], expand=1),
                            ft.Column([
                                ft.Text(f"📧 Email: {mock_info['contact']['email']}", size=14),
                                ft.Text(f"📱 Telepon: {mock_info['contact']['phone']}", size=14),
                                ft.Text(f"📍 Lokasi: {mock_info['contact']['location']}", size=14),
                            ], expand=1)
                        ])
                    ], spacing=10),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.with_opacity(0.05, ft.Colors.INDIGO_400), ft.Colors.WHITE]
                    ),
                ),
                elevation=2,
                shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_900)
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SUMMARIZE, size=30, color=ft.Colors.GREEN_600),
                            ft.Text("Ringkasan Profesional", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)
                        ]),
                        ft.Divider(color=ft.Colors.GREEN_100),
                        ft.Text(mock_info['summary'], size=14, color=ft.Colors.GREY_800)
                    ], spacing=10),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.with_opacity(0.05, ft.Colors.GREEN_400), ft.Colors.WHITE]
                    ),
                ),
                elevation=2,
                shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_900)
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.STAR, size=30, color=ft.Colors.ORANGE_600),
                            ft.Text("Keahlian & Teknologi", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600)
                        ]),
                        ft.Divider(color=ft.Colors.ORANGE_100),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(skill, size=12, color=ft.Colors.ORANGE_800, weight=ft.FontWeight.W_500),
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                bgcolor=ft.Colors.ORANGE_100,
                                border_radius=15,
                                border=ft.border.all(1, ft.Colors.ORANGE_300)
                            ) for skill in mock_info['skills']
                        ], wrap=True, spacing=8)
                    ], spacing=10),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.with_opacity(0.05, ft.Colors.ORANGE_400), ft.Colors.WHITE]
                    ),
                ),
                elevation=2,
                shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_900)
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.WORK_HISTORY, size=30, color=ft.Colors.PURPLE_600),
                            ft.Text("Pengalaman Kerja", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_600)
                        ]),
                        ft.Divider(color=ft.Colors.PURPLE_100),
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.PURPLE_600),
                                ft.Text(exp, size=14)
                            ]) for exp in mock_info['experience']
                        ], spacing=8)
                    ], spacing=10),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.with_opacity(0.05, ft.Colors.PURPLE_400), ft.Colors.WHITE]
                    ),
                ),
                elevation=2,
                shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_900)
            ),
            ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.SCHOOL, size=30, color=ft.Colors.RED_600),
                            ft.Text("Riwayat Pendidikan", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600)
                        ]),
                        ft.Divider(color=ft.Colors.RED_100),
                        ft.Column([
                            ft.Row([
                                ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.RED_600),
                                ft.Text(edu, size=14)
                            ]) for edu in mock_info['education']
                        ], spacing=8)
                    ], spacing=10),
                    padding=20,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.top_left,
                        end=ft.alignment.bottom_right,
                        colors=[ft.Colors.with_opacity(0.05, ft.Colors.RED_400), ft.Colors.WHITE]
                    ),
                ),
                elevation=2,
                shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.RED_900)
            ),
        ], scroll=ft.ScrollMode.AUTO, spacing=20)

        self.home_view.visible = False
        self.summary_view = ft.Container(
            content=summary_content,
            padding=20,
            visible=True
        )
        self.header_back_button.visible = True
        self.main_container.content.controls[2] = self.summary_view
        self.page.update()

    def view_cv(self, cv_data: Dict):
        self.show_snackbar(f"🔍 Membuka file CV asli: {cv_data['name']}.pdf", ft.Colors.INDIGO_600)

    def go_to_home(self, e=None):
        self.home_view.visible = True
        self.summary_view.visible = False
        self.header_back_button.visible = False
        self.main_container.content.controls[1] = self.home_view
        self.main_container.content.controls[2] = ft.Container(visible=False)
        self.page.update()

    def show_snackbar(self, message: str, color: str = ft.Colors.INDIGO_600):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color,
            action="OK",
            action_color=ft.Colors.WHITE,
            duration=3000
        )
        self.page.snack_bar.open = True
        self.page.update()

def main(page: ft.Page):
    app = ATSFrontend()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main)