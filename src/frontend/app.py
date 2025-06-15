import os
import sys
import csv
import time
import math
import random
import traceback
import flet as ft
from typing import List, Dict

# Adjust sys.path untuk allow import dari folder src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.algorithms.kmp import KMPSearch
from src.algorithms.bm import BoyerMooreSearch
from src.algorithms.aho_corasick import AhoCorasickSearch
from src.algorithms.levenshtein import LevenshteinDistance
from src.utils.pdf_extractor import PDFExtractor
from src.utils.regex_extractor import RegexExtractor
from src.database.db_manager import DatabaseManager
from src.frontend.components import (
    create_header_component,
    create_home_view_component,
    create_summary_view_component,
    init_ui_components,
    create_cv_card_component,
    create_summary_dialog_component,
    create_pdf_view_component,
)
from src.frontend.event_handlers import (
    handle_search_cv,
    handle_button_hover,
    handle_go_to_home,
    handle_show_snackbar,
    handle_prev_page,
    handle_next_page,
    handle_go_to_page,
    handle_show_summary,
    handle_view_cv,
    handle_close_dialog,
)
from src.frontend.utils import (
    load_seed_data_util,
    load_extracted_cv_data_util,
    load_cvs_from_db_util,
    update_summary_result_section_util,
    get_paginated_results_util,
    update_pagination_util,
    update_results_display_util,
)


class ATSFrontend:
    def __init__(self):
        print("🔗 Connecting to MySQL/MariaDB database...")

        try:
            # Koneksi ke database
            self.db = DatabaseManager()
            print("✅ Successfully connected to MySQL/MariaDB database!")
        except Exception as e:
            print(f"❌ Failed to connect to MySQL/MariaDB: {e}")
            print("Please ensure:")
            print("  1. MariaDB/MySQL server is running")
            print("  2. Connection settings are correct in src/database/db_manager.py")
            print("  3. Database server is accessible on localhost:3306")
            raise e

        self.db.create_tables()

        # Load data profil dan CV dari file SQL (tubes3_seeding.sql)
        self.load_seed_data()

        # Load data CV yang sudah diekstrak dari file CSV
        self.load_extracted_cv_data()

        self.current_page = "home"
        self.search_results = []
        self.selected_cv = None
        self.current_pagination_page = 1
        self.results_per_page = 5

        # Menginisialisasi algoritma
        self.kmp_search = KMPSearch()
        self.bm_search = BoyerMooreSearch()
        self.ac_search = AhoCorasickSearch()
        self.levenshtein = LevenshteinDistance()
        self.pdf_extractor = PDFExtractor()
        self.regex_extractor = RegexExtractor()

    # Delegated methods
    def load_seed_data(self):
        load_seed_data_util(self)

    def load_extracted_cv_data(self):
        load_extracted_cv_data_util(self)

    def load_cvs_from_db(self):
        return load_cvs_from_db_util(self)

    def init_components(self):
        init_ui_components(self)

    def on_button_hover(self, e):
        handle_button_hover(self, e)

    def create_header(self):
        return create_header_component(self)

    def create_home_view(self):
        return create_home_view_component(self)

    def search_cv(self, e):
        handle_search_cv(self, e)

    def update_summary_result_section(self, total_cvs: int, exact_time: float, fuzzy_time: float, algorithm: str):
        update_summary_result_section_util(self, total_cvs, exact_time, fuzzy_time, algorithm)

    def get_paginated_results(self):
        return get_paginated_results_util(self)

    def update_pagination(self, total_results: int):
        update_pagination_util(self, total_results)

    def prev_page(self, e):
        handle_prev_page(self, e)

    def next_page(self, e):
        handle_next_page(self, e)

    def go_to_page(self, page_num):
        handle_go_to_page(self, page_num)

    def update_results_display(self):
        update_results_display_util(self)

    def create_cv_card(self, result: Dict, rank: int):
        return create_cv_card_component(self, result, rank)

    def show_summary(self, cv_data: Dict):
        handle_show_summary(self, cv_data)
        
    def view_cv(self, cv_data: Dict):
        handle_view_cv(self, cv_data)

    def go_to_home(self, e=None):
        handle_go_to_home(self, e)

    def show_snackbar(self, message: str, color: str = ft.Colors.INDIGO_600):
        handle_show_snackbar(self, message, color)
        
    def close_dialog(self, e):
        handle_close_dialog(self, e)
    
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

        if not self.db.get_all_applications():
            csv_path = "data/cv_data.csv"
            if os.path.exists(csv_path):

                try:
                    self.db.import_csv_to_db(csv_path)
                except AttributeError:
                    print(f"⚠️ Warning: self.db.import_csv_to_db method not found. Skipping import of {csv_path}")


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

def main_app(page: ft.Page):
    app = ATSFrontend()
    app.main(page)

if __name__ == "__main__":
    ft.app(target=main_app)
