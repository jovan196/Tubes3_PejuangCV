import os
import flet as ft
import math

def load_seed_data_util(app):
    try:
        existing_applicants = app.db.get_all_applicants()
        if not existing_applicants:
            seed_file = "data/tubes3_seeding.sql"
            if os.path.exists(seed_file):
                print("🔄 Loading seed data from data/tubes3_seeding.sql...")
                app.db.import_sql_file(seed_file)
                print(f"✅ Loaded {len(app.db.get_all_applicants())} applicants from seed data")
            else:
                print("⚠️ No seed data file found at data/tubes3_seeding.sql")
        else:
            print(f"📊 Using existing data: {len(existing_applicants)} applicants already in database")
    except Exception as e:
        print(f"❌ Error loading seed data: {e}")

def load_extracted_cv_data_util(app):
    print("🔧 Creating ExtractedCV table (if not exists)...")
    app.db.create_extracted_cv_table()

    csv_path = "data/extracted_cvs.csv"
    if os.path.exists(csv_path):
        existing_cvs = app.db.get_all_extracted_cvs()
        print(f"📊 Current extracted CVs in database: {len(existing_cvs)}")

        if not existing_cvs:
            print("🔄 Loading extracted CV data...")
            try:
                app.db.import_extracted_cv_data(csv_path)
                loaded_cvs = app.db.get_all_extracted_cvs()
                print(f"✅ Loaded {len(loaded_cvs)} extracted CVs")
                if len(loaded_cvs) == 0:
                    print("⚠️ Warning: No CVs were loaded from CSV file")
            except Exception as e:
                print(f"❌ Error loading extracted CV data: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"📊 Using existing extracted CV data: {len(existing_cvs)} CVs already in database")
    else:
        print("⚠️ No extracted CV data found at data/extracted_cvs.csv. Run cv2csv.py or other extraction scripts first.")

def load_cvs_from_db_util(app):
    return app.db.get_all_applications() # This likely fetches from ApplicantProfile & ApplicationDetail

def update_summary_result_section_util(app, total_cvs: int, exact_time: float, fuzzy_time: float, algorithm: str):
    total_time = exact_time + fuzzy_time
    exact_matches = len([r for r in app.search_results if r.get('match_type') == 'exact'])
    fuzzy_matches = len([r for r in app.search_results if r.get('match_type') == 'fuzzy'])

    exact_match_text = f"Exact Match: {exact_matches} CVs found, {exact_time:.1f}ms processing time"
    fuzzy_match_text = f"Fuzzy Match: {fuzzy_matches} CVs found, {fuzzy_time:.1f}ms processing time"
    total_time_text = f"Total Processing Time: {total_time:.1f}ms for {total_cvs} CVs"

    app.summary_result_section.content = ft.Column([
        ft.Text("📊 Summary Result Section", size=18, weight=ft.FontWeight.BOLD),
        ft.Divider(color=ft.Colors.INDIGO_200),
        ft.Column([
            ft.Text(exact_match_text, size=14, weight=ft.FontWeight.W_500),
            ft.Text(fuzzy_match_text, size=14, weight=ft.FontWeight.W_500),
            ft.Text(total_time_text, size=14, weight=ft.FontWeight.W_500, color=ft.Colors.INDIGO_600),
            ft.Divider(color=ft.Colors.INDIGO_100),
            ft.Text(f"Algoritma yang digunakan: {algorithm}", size=14, weight=ft.FontWeight.BOLD),
            ft.Text(f"Total CV relevan: {exact_matches + fuzzy_matches}", size=14, weight=ft.FontWeight.BOLD)
        ], spacing=8)
    ])
    app.summary_result_section.visible = True
    if hasattr(app, 'page') and app.page: app.page.update() # Ensure UI update

def get_paginated_results_util(app):
    # Filter results based on match_count > 0, unless "all" is selected in dropdown
    if app.top_matches_dropdown.value == "all":
        # If "all" is selected, pagination should still apply to all search_results
        # The number of items shown per page is still app.results_per_page
        # The filtering for top_matches (e.g., top 5, 10) is done during the search_cv logic itself.
        # Here, we are just paginating the app.search_results list.
        results_to_paginate = app.search_results
    else:
        # If a specific number (e.g., Top 10) was selected, app.search_results already contains those.
        # However, the original code also had a filter here for match_count > 0.
        # Let's clarify: if top_X is selected, does it mean top_X *matching* CVs, or just top_X from sorted list?
        # Assuming app.search_results is already the list to be paginated (potentially pre-filtered by top_X)
        # And we only show those with actual matches in the paginated view.
        results_to_paginate = [r for r in app.search_results if r['match_count'] > 0]

    start_idx = (app.current_pagination_page - 1) * app.results_per_page
    end_idx = start_idx + app.results_per_page
    return results_to_paginate[start_idx:end_idx], len(results_to_paginate)

def update_pagination_util(app, total_results: int):
    if total_results == 0: # if no results to paginate (e.g. no matches)
        app.pagination_container.visible = False
        if hasattr(app, 'page') and app.page: app.page.update()
        return
        
    total_pages = math.ceil(total_results / app.results_per_page)
    if total_pages <= 1 and app.top_matches_dropdown.value != "all": # Hide if only one page and not showing all
        app.pagination_container.visible = False
        if hasattr(app, 'page') and app.page: app.page.update()
        return

    pagination_controls = []
    prev_button = ft.ElevatedButton(
        text="← Sebelumnya",
        on_click=app.prev_page, # Assumes app has a prev_page method
        disabled=app.current_pagination_page <= 1,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.INDIGO_100 if app.current_pagination_page > 1 else ft.Colors.GREY_200,
            color=ft.Colors.INDIGO_600 if app.current_pagination_page > 1 else ft.Colors.GREY_500,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )
    pagination_controls.append(prev_button)

    # Page number buttons (e.g., 1 ... 5 6 7 ... 10)
    start_page = max(1, app.current_pagination_page - 2)
    end_page = min(total_pages, start_page + 4)
    if total_pages > 5 and end_page - start_page < 4 : # Adjust if near the end
        if app.current_pagination_page > total_pages - 2:
             start_page = max(1, total_pages - 4)
        else:
            end_page = min(total_pages, start_page + 4)

    if start_page > 1:
        pagination_controls.append(ft.TextButton("1", on_click=lambda _, p=1: app.go_to_page(p)))
        if start_page > 2:
            pagination_controls.append(ft.Text("...", color=ft.Colors.GREY_500))

    for page_num in range(start_page, end_page + 1):
        page_button = ft.ElevatedButton(
            text=str(page_num),
            on_click=lambda _, p=page_num: app.go_to_page(p), # Assumes app has go_to_page
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_600 if page_num == app.current_pagination_page else ft.Colors.INDIGO_100,
                color=ft.Colors.WHITE if page_num == app.current_pagination_page else ft.Colors.INDIGO_600,
                padding=ft.padding.all(12),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            width=50
        )
        pagination_controls.append(page_button)

    if end_page < total_pages:
        if end_page < total_pages -1:
            pagination_controls.append(ft.Text("...", color=ft.Colors.GREY_500))
        pagination_controls.append(ft.TextButton(str(total_pages),on_click=lambda _, p=total_pages: app.go_to_page(p)))

    next_button = ft.ElevatedButton(
        text="Selanjutnya →",
        on_click=app.next_page, # Assumes app has a next_page method
        disabled=app.current_pagination_page >= total_pages,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.INDIGO_100 if app.current_pagination_page < total_pages else ft.Colors.GREY_200,
            color=ft.Colors.INDIGO_600 if app.current_pagination_page < total_pages else ft.Colors.GREY_500,
            padding=ft.padding.symmetric(horizontal=15, vertical=10),
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )
    pagination_controls.append(next_button)

    page_info = ft.Text(
        f"Halaman {app.current_pagination_page} dari {total_pages} ({total_results} CV)",
        size=14,
        color=ft.Colors.GREY_600
    )

    app.pagination_container.content = ft.Column([
        ft.Row(pagination_controls, alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ft.Container(page_info, padding=ft.padding.only(top=10))
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    app.pagination_container.visible = True
    if hasattr(app, 'page') and app.page: app.page.update()

def update_results_display_util(app):
    app.results_container.controls.clear()
    if not app.search_results: # This means the initial search yielded no results at all
        app.results_container.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.SEARCH_OFF, size=80, color=ft.Colors.GREY_400),
                    ft.Text("Tidak ada CV yang ditemukan untuk kriteria ini",
                           size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                    ft.Text("Coba gunakan kata kunci yang berbeda atau ubah filter.",
                           size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                padding=50,
                alignment=ft.alignment.center
            )
        )
        app.pagination_container.visible = False
    else:
        paginated_results, total_paginatable_results = app.get_paginated_results()
        if not paginated_results: # No results for the current page (might happen if all results were on previous pages)
            app.results_container.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.INFO_OUTLINE, size=80, color=ft.Colors.GREY_400),
                        ft.Text("Tidak ada CV yang cocok di halaman ini.",
                               size=18, color=ft.Colors.GREY_600, text_align=ft.TextAlign.CENTER),
                        ft.Text("Mungkin semua CV yang cocok ada di halaman lain, atau tidak ada CV yang cocok sama sekali.",
                               size=14, color=ft.Colors.GREY_500, text_align=ft.TextAlign.CENTER)
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=50,
                    alignment=ft.alignment.center
                )
            )
            # Still show pagination if there are total results, even if current page is empty
            if total_paginatable_results > 0:
                app.update_pagination(total_paginatable_results)
            else:
                app.pagination_container.visible = False
        else:
            rank_offset = (app.current_pagination_page - 1) * app.results_per_page
            for i, result in enumerate(paginated_results):
                # Pass the app instance to create_cv_card_component
                card = app.create_cv_card(result, rank=rank_offset + i + 1)
                app.results_container.controls.append(card)
            app.update_pagination(total_paginatable_results)
            
    if hasattr(app, 'page') and app.page: app.page.update()
