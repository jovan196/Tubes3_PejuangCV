import flet as ft
import time
import traceback
import os

def handle_search_cv(app, e):
    if not app.keyword_input.value:
        app.show_snackbar("⚠️ Mohon masukkan kata kunci untuk pencarian!", ft.Colors.ORANGE_600)
        return

    app.loading_indicator.visible = True
    app.search_button.content.content = ft.Row([
        ft.Icon(ft.Icons.HOURGLASS_EMPTY, color=ft.Colors.WHITE, size=24),
        ft.Text("Sedang mencari...", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
    ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
    app.search_button.content.disabled = True
    app.page.update()

    try:
        keywords = [k.strip() for k in app.keyword_input.value.split(",") if k.strip()]
        algorithm = app.algorithm_radio.value
        top_matches_filter = app.top_matches_dropdown.value

        start_time = time.time()
        exact_search_time = 0
        fuzzy_search_time = 0
        extracted_cvs = app.db.get_all_extracted_cvs()
        db_cvs = app.load_cvs_from_db()

        db_lookup = {}
        extracted_cv_ids = set()

        for cv in db_cvs:
            cv_id_path = cv.get('cv_path', '')
            cv_id = app.db.get_cv_id_from_path(cv_id_path) if cv_id_path else None
            if cv_id:
                db_lookup[cv_id] = cv
        
        if extracted_cvs:
            for extracted_cv in extracted_cvs:
                extracted_cv_ids.add(extracted_cv['cv_id'])

        if not extracted_cvs and not db_cvs:
            app.show_snackbar("⚠️ Tidak ada data CV yang tersedia. Periksa database atau jalankan extract_cv_to_csv.py.", ft.Colors.ORANGE_600)
            app.loading_indicator.visible = False
            app.search_button.content.disabled = False
            app.search_button.content.content = ft.Row([
                ft.Text("🔍 Mulai Pencarian CV", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
            app.page.update()
            return

        all_results = []
        # Process extracted CVs first
        if extracted_cvs:
            for extracted_cv in extracted_cvs:
                cv_id = extracted_cv['cv_id']
                resume_text = extracted_cv['resume_str']
                resume_html = extracted_cv['resume_html']
                category = extracted_cv['category']
                parsed_info = app.regex_extractor.extract_cv_info(resume_text) if resume_text else {}
                db_record = db_lookup.get(cv_id, {})

                searchable_text = resume_text or ""
                if db_record:
                    db_fields = [
                        db_record.get('first_name', ''), db_record.get('last_name', ''),
                        db_record.get('address', ''), db_record.get('phone_number', ''),
                        db_record.get('application_role', ''), db_record.get('date_of_birth', ''),
                        str(db_record.get('applicant_id', '')), str(db_record.get('detail_id', ''))
                    ]
                    db_text = ' '.join([str(field) for field in db_fields if field])
                    searchable_text += ' ' + db_text
                if category:
                    searchable_text += ' ' + category
                
                matches, total_matches, keywords_found_count, current_exact_time = perform_exact_search(app, searchable_text, keywords, algorithm)
                exact_search_time += current_exact_time

                match_type = 'no_match'
                similarity = 0.0
                current_fuzzy_time = 0

                if total_matches > 0:
                    match_type = 'exact'
                    keyword_coverage = keywords_found_count / len(keywords) if keywords else 0
                    avg_frequency = total_matches / keywords_found_count if keywords_found_count > 0 else 0
                    similarity = keyword_coverage * 0.7 + min(1.0, avg_frequency / 5) * 0.3
                else: # Fallback to fuzzy search
                    fuzzy_matches_dict, fuzzy_total, fuzzy_keywords_found, current_fuzzy_time = perform_fuzzy_search(app, searchable_text, keywords)
                    fuzzy_search_time += current_fuzzy_time
                    if fuzzy_total > 0:
                        match_type = 'fuzzy'
                        matches = fuzzy_matches_dict # Use fuzzy matches
                        total_matches = fuzzy_total
                        keywords_found_count = fuzzy_keywords_found
                        keyword_coverage = fuzzy_keywords_found / len(keywords) if keywords else 0
                        avg_frequency = fuzzy_total / fuzzy_keywords_found if fuzzy_keywords_found > 0 else 0
                        similarity = keyword_coverage * 0.6 + min(1.0, avg_frequency / 3) * 0.4
                
                name = f"CV {cv_id}"
                if db_record:
                    first_name = db_record.get('first_name', '')
                    last_name = db_record.get('last_name', '')
                    if first_name or last_name:
                        name = f"{first_name} {last_name}".strip()

                all_results.append({
                    'cv_data': {
                        'cv_id': cv_id, 'name': name,
                        'first_name': db_record.get('first_name', ''), 'last_name': db_record.get('last_name', ''),
                        'address': db_record.get('address', ''), 'phone': db_record.get('phone_number', ''),
                        'application_role': db_record.get('application_role', category),
                        'cv_path': db_record.get('cv_path', f"data/cv/{category}/{cv_id}.pdf"),
                        'category': category, 'resume_text': resume_text, 'resume_html': resume_html,
                        'parsed_info': parsed_info,
                        'emails': parsed_info.get('emails', []),
                        'phones': parsed_info.get('phones', []),
                        'skills': parsed_info.get('skills', []),
                        'education': parsed_info.get('education', []),
                        'experience': parsed_info.get('experience', []),
                        'summary': parsed_info.get('summary', []),
                        'names': parsed_info.get('names', [])
                    },
                    'matches': matches, 'match_count': total_matches, 'match_type': match_type,
                    'similarity_score': similarity, 'keywords_found': keywords_found_count,
                    'total_keywords': len(keywords),
                    'keyword_coverage': (keywords_found_count / len(keywords) if keywords else 0)
                })

        # Process database-only records (those not in extracted_cvs but in db_cvs)
        # This logic might be redundant if all db_cvs are expected to have corresponding extracted_cvs.
        # For now, keeping it as per original structure.
        processed_db_cv_ids = set(res['cv_data']['cv_id'] for res in all_results)

        for cv_db_record in db_cvs:
            cv_id = cv_db_record.get('cv_id') # Assuming cv_id is directly in db_cvs items
            if not cv_id or cv_id in processed_db_cv_ids or cv_id in extracted_cv_ids:
                continue # Skip if already processed or has an extracted version

            # This block is for CVs in the database but NOT in the extracted_cvs.csv
            # They likely won't have resume_text, resume_html, or category from extraction.
            parsed_info = {}
            searchable_text = ""
            db_fields = [
                cv_db_record.get('first_name', ''), cv_db_record.get('last_name', ''),
                cv_db_record.get('address', ''), cv_db_record.get('phone_number', ''),
                cv_db_record.get('application_role', ''), cv_db_record.get('date_of_birth', ''),
                str(cv_db_record.get('applicant_id', '')), str(cv_db_record.get('detail_id', ''))
            ]
            db_text = ' '.join([str(field) for field in db_fields if field])
            searchable_text += ' ' + db_text
            # Category might be missing here if not in extracted_cvs
            category_from_db = cv_db_record.get('category', '') # Or derive from cv_path if possible
            if category_from_db:
                 searchable_text += ' ' + category_from_db

            matches, total_matches, keywords_found_count, current_exact_time = perform_exact_search(app, searchable_text, keywords, algorithm)
            exact_search_time += current_exact_time

            match_type = 'no_match'
            similarity = 0.0
            current_fuzzy_time = 0

            if total_matches > 0:
                match_type = 'exact'
                keyword_coverage = keywords_found_count / len(keywords) if keywords else 0
                avg_frequency = total_matches / keywords_found_count if keywords_found_count > 0 else 0
                similarity = keyword_coverage * 0.7 + min(1.0, avg_frequency / 5) * 0.3
            else: # Fallback to fuzzy search
                fuzzy_matches_dict, fuzzy_total, fuzzy_keywords_found, current_fuzzy_time = perform_fuzzy_search(app, searchable_text, keywords)
                fuzzy_search_time += current_fuzzy_time
                if fuzzy_total > 0:
                    match_type = 'fuzzy'
                    matches = fuzzy_matches_dict
                    total_matches = fuzzy_total
                    keywords_found_count = fuzzy_keywords_found
                    keyword_coverage = fuzzy_keywords_found / len(keywords) if keywords else 0
                    avg_frequency = fuzzy_total / fuzzy_keywords_found if fuzzy_keywords_found > 0 else 0
                    similarity = keyword_coverage * 0.6 + min(1.0, avg_frequency / 3) * 0.4
            
            name = f"CV {cv_id}"
            first_name = cv_db_record.get('first_name', '')
            last_name = cv_db_record.get('last_name', '')
            if first_name or last_name:
                name = f"{first_name} {last_name}".strip()

            all_results.append({
                'cv_data': {
                    'cv_id': cv_id, 'name': name,
                    'first_name': first_name, 'last_name': last_name,
                    'address': cv_db_record.get('address', ''), 'phone': cv_db_record.get('phone_number', ''),
                    'application_role': cv_db_record.get('application_role', category_from_db),
                    'cv_path': cv_db_record.get('cv_path', f"data/cv/{category_from_db}/{cv_id}.pdf" if category_from_db else f"data/cv/UNKNOWN/{cv_id}.pdf"),
                    'category': category_from_db,
                    'resume_text': "", 'resume_html': "", # No extracted text for these
                    'parsed_info': parsed_info, # Empty for these
                    'emails': [], 'phones': [], 'skills': [], 'education': [], 'experience': [], 'summary': [], 'names': []
                },
                'matches': matches, 'match_count': total_matches, 'match_type': match_type,
                'similarity_score': similarity, 'keywords_found': keywords_found_count,
                'total_keywords': len(keywords),
                'keyword_coverage': (keywords_found_count / len(keywords) if keywords else 0)
            })

        def sort_key(result):
            coverage = result['keyword_coverage']
            match_type_val = result['match_type']
            match_count = result['match_count']
            similarity_val = result['similarity_score']
            match_type_score = 3 if match_type_val == 'exact' else 2 if match_type_val == 'fuzzy' else 0
            return (coverage, match_type_score, match_count, similarity_val)

        all_results.sort(key=sort_key, reverse=True)

        if top_matches_filter == "all":
            app.search_results = all_results
        else:
            app.search_results = all_results[:int(top_matches_filter)]

        matching_count = len([r for r in app.search_results if r['match_count'] > 0])
        app.current_pagination_page = 1
        total_cvs_processed = len(all_results)

        app.update_summary_result_section(total_cvs_processed, exact_search_time, fuzzy_search_time, algorithm)
        app.update_results_display()
        app.show_snackbar(f"✅ Pencarian selesai! Ditemukan {matching_count} CV relevan dari {total_cvs_processed} total CV", ft.Colors.GREEN_600)

    except Exception as ex:
        app.show_snackbar(f"❌ Error dalam pencarian: {str(ex)}", ft.Colors.RED_600)
        print(f"Search error: {ex}")
        print(f"Traceback: {traceback.format_exc()}")
    finally:
        app.loading_indicator.visible = False
        app.search_button.content.disabled = False
        app.search_button.content.content = ft.Row([
            ft.Text("🔍 Mulai Pencarian CV", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        if hasattr(app, 'page') and app.page: # Ensure page exists
            app.page.update()

def perform_exact_search(app, text, keywords, algorithm):
    matches = {}
    total_matches = 0
    keywords_found_count = 0
    text_lower = text.lower()
    keywords_lower = [k.lower() for k in keywords]
    start_time = time.time()

    if algorithm == "AC" and len(keywords_lower) > 1:
        all_found_matches = app.ac_search.search_multiple(text_lower, keywords_lower)
        for kw in keywords_lower:
            count = len(all_found_matches.get(kw, []))
            if count > 0:
                matches[kw] = count
                total_matches += count
                keywords_found_count += 1
    else:
        for kw in keywords_lower:
            count = 0
            if algorithm == "KMP":
                positions = app.kmp_search.search_all(text_lower, kw)
                count = len(positions)
            elif algorithm == "BM":
                positions = app.bm_search.search_all(text_lower, kw)
                count = len(positions)
            elif algorithm == "AC": # Single keyword AC
                positions = app.ac_search.search_single(text_lower, kw)
                count = len(positions)
            else: # Default to string count if algorithm not specified or unknown
                count = text_lower.count(kw)
            
            if count > 0:
                matches[kw] = count
                total_matches += count
                keywords_found_count += 1
                
    elapsed_time_ms = (time.time() - start_time) * 1000
    return matches, total_matches, keywords_found_count, elapsed_time_ms

def perform_fuzzy_search(app, text, keywords):
    fuzzy_matches_dict = {}
    fuzzy_total = 0
    fuzzy_keywords_found = 0
    text_lower = text.lower()
    keywords_lower = [k.lower() for k in keywords]
    start_time = time.time()

    for kw in keywords_lower:
        keyword_fuzzy_count = 0
        # Split text into unique words for Levenshtein to avoid overcounting on repeated words in text
        unique_words_in_text = set(text_lower.split())
        for word in unique_words_in_text:
            if len(word) > 2: # Avoid matching very short words
                sim = app.levenshtein.similarity(kw, word)
                if sim >= 0.7: # Similarity threshold
                    keyword_fuzzy_count += 1 # Count how many words in text are similar to this keyword
        
        if keyword_fuzzy_count > 0:
            fuzzy_matches_dict[kw] = keyword_fuzzy_count
            fuzzy_total += keyword_fuzzy_count # Sum of all similar word counts for this keyword
            fuzzy_keywords_found += 1
            
    elapsed_time_ms = (time.time() - start_time) * 1000
    return fuzzy_matches_dict, fuzzy_total, fuzzy_keywords_found, elapsed_time_ms

def handle_button_hover(app, e):
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

def handle_go_to_home(app, e=None):
    app.current_page = "home"
    app.home_view.visible = True
    app.summary_view.visible = False 
    app.header_back_button.visible = False
    if hasattr(app, 'page') and app.page: # Ensure page exists
        app.page.update()

def handle_show_snackbar(app, message: str, color: str = ft.Colors.INDIGO_600):
    # Display a SnackBar using the Page.snack_bar property
    if hasattr(app, 'page') and app.page:
        snackbar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            bgcolor=color,
            duration=3000,
            action="OK",
            action_color=ft.Colors.WHITE
        )
        # Assign to the page's snack_bar and open it
        app.page.snack_bar = snackbar
        snackbar.open = True
        app.page.update()

def handle_prev_page(app, e):
    if app.current_pagination_page > 1:
        app.current_pagination_page -= 1
        app.update_results_display()

def handle_next_page(app, e):
    # paginated_results, total_results = app.get_paginated_results()
    # total_pages = math.ceil(total_results / app.results_per_page)
    # The above lines are not needed if get_paginated_results correctly returns total_results
    # that reflects the *filtered* list that pagination is based on.
    # We need to ensure total_pages is calculated based on the *actual* number of items being paginated.
    
    # Get the total number of results that are being paginated
    # This should be the count of results that have match_count > 0, or all results if "all" is selected.
    filtered_results_for_pagination = [r for r in app.search_results if r['match_count'] > 0]
    if app.top_matches_dropdown.value == "all":
         filtered_results_for_pagination = app.search_results
    total_paginatable_results = len(filtered_results_for_pagination)
    
    import math # Make sure math is imported
    total_pages = math.ceil(total_paginatable_results / app.results_per_page)

    if app.current_pagination_page < total_pages:
        app.current_pagination_page += 1
        app.update_results_display()

def handle_go_to_page(app, page_num):
    app.current_pagination_page = page_num
    app.update_results_display()

def handle_show_summary(app, cv_data):
    from .components import create_summary_page_component
    # Prepare parsed info
    parsed_info = cv_data.get('parsed_info', {})
    if not parsed_info and cv_data.get('resume_text'):
        parsed_info = app.regex_extractor.extract_cv_info(cv_data['resume_text'])
    # Build full summary page container
    summary_container = create_summary_page_component(app, cv_data, parsed_info)
    # Show summary view, hide home view
    app.home_view.visible = False
    app.summary_view = summary_container
    app.summary_view.visible = True
    app.header_back_button.visible = True
    # Replace main content panel
    app.main_container.content.controls[2] = app.summary_view
    app.page.update()

def handle_view_cv(app, cv_data):
    import subprocess
    import platform
    import os
    # Original path
    cv_path = cv_data.get('cv_path', '')
    # Debug logs
    print(f"🔍 Debug - Attempting to open CV: {cv_path}")
    # Make absolute if needed
    if cv_path and not os.path.isabs(cv_path):
        cv_path = os.path.abspath(cv_path)
        print(f"   Absolute cv_path: {cv_path}")
    # Try opening the file directly
    if cv_path and os.path.exists(cv_path):
        try:
            print(f"   ✅ File exists, attempting to open: {cv_path}")
            if platform.system() == 'Windows':
                os.startfile(cv_path)
            elif platform.system() == 'Darwin':
                subprocess.call(['open', cv_path])
            else:
                subprocess.call(['xdg-open', cv_path])
            app.show_snackbar(f"📄 Membuka file CV: {os.path.basename(cv_path)}", ft.Colors.INDIGO_600)
        except Exception as e:
            print(f"   ❌ Error opening file: {e}")
            app.show_snackbar(f"❌ Gagal membuka file CV: {e}", ft.Colors.RED_600)
        return
    # Try alternative paths by category and CV ID
    cv_id = cv_data.get('cv_id', '')
    category = cv_data.get('category', '')
    if cv_id and category:
        possible_paths = [
            f"data/cv/{category}/{cv_id}.pdf",
            f"data/cv/{category.upper()}/{cv_id}.pdf",
            f"data/cv/{category.lower()}/{cv_id}.pdf"
        ]
        print(f"   🔄 Trying alternative paths for CV ID {cv_id}:")
        for p in possible_paths:
            abs_path = os.path.abspath(p)
            print(f"      Checking: {abs_path}")
            if os.path.exists(abs_path):
                try:
                    print(f"      ✅ Found file, attempting to open: {abs_path}")
                    if platform.system() == 'Windows':
                        os.startfile(abs_path)
                    elif platform.system() == 'Darwin':
                        subprocess.call(['open', abs_path])
                    else:
                        subprocess.call(['xdg-open', abs_path])
                    app.show_snackbar(f"📄 Membuka file CV: {os.path.basename(abs_path)}", ft.Colors.INDIGO_600)
                    return
                except Exception as e:
                    print(f"      ❌ Error opening alternative path: {e}")
                    continue
            else:
                print(f"      ❌ Not found: {abs_path}")
    # If all fails
    app.show_snackbar(f"❌ File CV tidak ditemukan: {cv_path or 'Path tidak tersedia'}", ft.Colors.RED_600)

def handle_close_dialog(app, e):
    """Close any open dialog on the page"""
    if hasattr(app, 'page') and app.page and hasattr(app.page, 'dialog') and app.page.dialog:
        app.page.dialog.open = False
        app.page.update()
