import flet as ft
import os

def create_header_component(app):
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
                app.header_back_button
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

def create_home_view_component(app):
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
                            app.keyword_input,
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
                                    content=app.algorithm_radio,
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
                                app.top_matches_dropdown
                            ], spacing=8),
                            expand=1
                        )
                    ], spacing=20),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                app.search_button,
                                app.loading_indicator
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
                    app.summary_result_section
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
                    app.results_container,
                    app.pagination_container
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

def create_summary_view_component(app):
    # This view is initially empty and populated by search results or CV details
    return ft.Container(visible=False) 

def init_ui_components(app):
    app.keyword_input = ft.TextField(
        label="Masukkan kata kunci pencarian",
        hint_text="Contoh: React, Express, HTML",
        width=500,
        multiline=False,
        prefix_icon=ft.Icons.SEARCH,
        border_radius=10,
        border_color=ft.Colors.INDIGO_400,
        focused_border_color=ft.Colors.INDIGO_600,
    )

    app.algorithm_radio = ft.RadioGroup(
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
    app.top_matches_dropdown = ft.Dropdown(
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

    app.search_button = ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row([
                ft.Text("🔍 Mulai Pencarian CV", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10),
            on_click=app.search_cv,
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
        on_hover=app.on_button_hover,
    )

    app.loading_indicator = ft.ProgressRing(
        width=30,
        height=30,
        stroke_width=3,
        color=ft.Colors.INDIGO_400,
        visible=False
    )

    app.summary_result_section = ft.Container(
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

    app.results_container = ft.Column(
        spacing=15,
        scroll=ft.ScrollMode.AUTO
    )

    app.pagination_container = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        padding=20,
        visible=False
    )

    app.header_back_button = ft.IconButton(
        icon=ft.Icons.HOME,
        tooltip="Kembali ke Beranda",
        on_click=app.go_to_home,
        visible=False,
        icon_size=30,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.INDIGO_100,
            color=ft.Colors.INDIGO_600,
            shape=ft.CircleBorder(),
        )
    )
    app.home_view = create_home_view_component(app) # Create home view after other components are initialized
    app.summary_view = create_summary_view_component(app) # Create summary view

def create_cv_card_component(app, result, rank):
    cv_data = result['cv_data']
    matches = result['matches']
    match_count = result['match_count']
    match_type = result['match_type']
    similarity = result.get('similarity_score', 0.0)

    match_chips = []
    if matches:
        for keyword, freq in matches.items():
            chip_color = ft.Colors.INDIGO_100 if match_type == 'exact' else ft.Colors.ORANGE_100
            text_color = ft.Colors.INDIGO_800 if match_type == 'exact' else ft.Colors.ORANGE_800
            match_chips.append(
                ft.Container(
                    content=ft.Text(f"{keyword}: {freq}x", size=12, weight=ft.FontWeight.W_500, color=text_color),
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    bgcolor=chip_color,
                    border_radius=15,
                    border=ft.border.all(1, text_color)
                )
            )
    else:
        match_chips.append(
            ft.Container(
                content=ft.Text("Tidak ada kata kunci yang cocok", size=12, weight=ft.FontWeight.W_500, color=ft.Colors.GREY_600),
                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                bgcolor=ft.Colors.GREY_100,
                border_radius=15,
                border=ft.border.all(1, ft.Colors.GREY_400)
            )
        )

    if match_count == 0:
        rank_color = ft.Colors.GREY_400
    elif rank <= 3:
        rank_color = ft.Colors.AMBER_600
    else:
        rank_color = ft.Colors.INDIGO_400

    if match_count > 5:
        card_gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.Colors.INDIGO_50, ft.Colors.BLUE_50]
        )
    elif match_count > 0:
        card_gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.Colors.TEAL_50, ft.Colors.LIGHT_GREEN_50]
        )
    else:
        card_gradient = ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.Colors.GREY_100, ft.Colors.BLUE_GREY_50]
        )

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
                        ft.Text(f"📍 {cv_data.get('application_role', cv_data.get('category', 'Unknown'))} • {cv_data.get('category', 'Unknown')}",
                               size=14, color=ft.Colors.GREY_600),
                        ft.Row([
                            ft.Icon(ft.Icons.TRENDING_UP, size=16,
                                   color=ft.Colors.GREEN_600 if match_count > 0 else ft.Colors.GREY_500),
                            ft.Text(f"Kecocokan: {match_count}",
                                   size=14, weight=ft.FontWeight.W_500),
                            ft.Text(f"• {result.get('keywords_found', 0)}/{result.get('total_keywords', 1)} keywords",
                                   size=12, color=ft.Colors.BLUE_600),
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
                            on_click=lambda e, cv=cv_data: app.show_summary(cv),
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
                            on_click=lambda e, cv=cv_data: app.view_cv(cv),
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

def create_summary_dialog_component(app, cv_data, parsed_info):
    # Get names - try from parsed info first, then from database fields
    names = parsed_info.get('names', [])
    if not names:
        # Try to get from cv_data if available
        first_name = cv_data.get('first_name', '')
        last_name = cv_data.get('last_name', '')
        if first_name or last_name:
            names = [f"{first_name} {last_name}".strip()]
    
    if not names:
        # Fallback if no name found anywhere
        names = [cv_data.get('name', "Unknown Applicant")]
        
    # Format and organize the extracted information
    emails = parsed_info.get('emails', [])
    phones = parsed_info.get('phones', [])
    skills = parsed_info.get('skills', [])
    education = parsed_info.get('education', [])
    experience = parsed_info.get('experience', [])
    summary_text = parsed_info.get('summary', []) # Renamed to avoid conflict
    
    # Combine phone info from both sources
    if cv_data.get('phone'):
        phones.append(cv_data.get('phone'))
    phones = list(set(phones))  # Remove duplicates

    def create_section(title, items):
        if not items:
            return ft.Container() # Return empty container if no items
        return ft.Column([
            ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_700),
            ft.Column([ft.Text(f"• {item}", size=14) for item in items], spacing=5),
            ft.Divider(height=10, color=ft.Colors.INDIGO_100)
        ], spacing=8)

    dialog_content = ft.Column([
        ft.Text("📝 CV Summary", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_800),
        ft.Divider(height=15, thickness=2, color=ft.Colors.INDIGO_200),
        create_section("👤 Name(s)", names),
        create_section("📧 Email(s)", emails),
        create_section("📞 Phone(s)", phones),
        create_section("🛠️ Skills", skills),
        # Show raw education entries, truncated if too long
        create_section("🎓 Education", [edu[:150] + "..." if len(edu) > 150 else edu for edu in education] if education else []),
        # Show raw experience entries, truncated if too long
        create_section("💼 Experience", [exp[:200] + "..." if len(exp) > 200 else exp for exp in experience] if experience else []),
        create_section("📄 Summary Points", summary_text),
    ], scroll=ft.ScrollMode.AUTO, spacing=15, width=700, height=500)

    return ft.AlertDialog(
        modal=True,
        title=ft.Text(f"Summary for {names[0] if names else 'CV'}", weight=ft.FontWeight.BOLD),
        content=dialog_content,
        actions=[
            ft.TextButton("Close", on_click=lambda e: app.close_dialog(e)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        shape=ft.RoundedRectangleBorder(radius=15),
        bgcolor=ft.Colors.INDIGO_50,
        surface_tint_color=ft.Colors.INDIGO_100
    )

def create_pdf_view_component(app, cv_data):
    cv_path = cv_data.get('cv_path', '')
    if not cv_path or not os.path.exists(cv_path):
        app.show_snackbar(f"❌ File PDF tidak ditemukan di: {cv_path}", ft.Colors.RED_600)
        return None # Return None if PDF not found

    # For local PDF files, we need to serve them or use an external viewer.
    # Flet's WebView might not directly support local file paths due to security restrictions.
    # A simple approach for local files is to open them with the default system PDF viewer.
    try:
        if os.name == 'nt': # Windows
            os.startfile(cv_path)
        elif os.name == 'posix': # macOS, Linux
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, cv_path])
        app.show_snackbar(f"📄 Membuka CV: {os.path.basename(cv_path)}", ft.Colors.GREEN_600)
        return None # No Flet component to return, as it's opened externally
    except Exception as e:
        app.show_snackbar(f"❌ Gagal membuka PDF: {e}", ft.Colors.RED_600)
        # Fallback: Display a message if opening externally fails
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED_400),
                ft.Text(f"Tidak dapat membuka file PDF: {os.path.basename(cv_path)}", size=16, weight=ft.FontWeight.BOLD),
                ft.Text("Pastikan Anda memiliki penampil PDF yang terinstal dan file tersebut ada.", size=14, color=ft.Colors.GREY_600),
                ft.Text(f"Lokasi file: {cv_path}", size=12, italic=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=30,
            alignment=ft.alignment.center,
            expand=True
        )

def create_summary_page_component(app, cv_data, parsed_info):
    # Mirror old monolithic show_summary implementation to build a full summary page
    names = parsed_info.get('names', [])
    if not names:
        first_name = cv_data.get('first_name', '')
        last_name = cv_data.get('last_name', '')
        if first_name or last_name:
            names = [f"{first_name} {last_name}".strip()]
    if not names:
        names = [f"CV {cv_data.get('cv_id', 'Unknown')}" ]

    emails = parsed_info.get('emails', [])
    phones = parsed_info.get('phones', [])
    skills = parsed_info.get('skills', [])
    education = parsed_info.get('education', [])
    experience = parsed_info.get('experience', [])
    summary_list = parsed_info.get('summary', [])

    if cv_data.get('phone'):
        phones.append(cv_data.get('phone'))
    phones = list(set(phones))

    # Header row
    header_row = ft.Row([
        ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            tooltip="Kembali ke Hasil Pencarian",
            on_click=lambda e: app.go_to_home(e),
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.INDIGO_100,
                color=ft.Colors.INDIGO_600,
                shape=ft.CircleBorder(),
            )
        ),
        ft.Text("📄 Informasi CV", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600),
        ft.Container(expand=True),
        ft.Chip(label=ft.Text("CV Aktif", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN_600)
    ])
    divider = ft.Divider(thickness=2, color=ft.Colors.INDIGO_200)

    # Personal Info card
    personal_info = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.PERSON, size=30, color=ft.Colors.INDIGO_600),
                        ft.Text("Informasi Pribadi", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.INDIGO_600)]),
                ft.Divider(color=ft.Colors.INDIGO_100),
                ft.Column([
                    ft.Text(f"👤 Nama: {', '.join(names)}", size=16, weight=ft.FontWeight.W_500),
                    ft.Text(f"📧 Email: {', '.join(emails) if emails else 'Tidak tersedia'}", size=14),
                    ft.Text(f"📱 Telepon: {', '.join(phones) if phones else 'Tidak tersedia'}", size=14),
                    ft.Text(f"📍 Alamat: {cv_data.get('address', 'Tidak tersedia')}", size=14),
                    ft.Text(f"💼 Role: {cv_data.get('application_role', cv_data.get('category', 'Unknown'))}", size=14),
                    ft.Text(f"📂 Kategori: {cv_data.get('category', 'Unknown')}", size=14)
                ], spacing=5)
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.INDIGO_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.INDIGO_900)
    )

    # Professional summary card
    summary_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.SUMMARIZE, size=30, color=ft.Colors.GREEN_600),
                        ft.Text("Ringkasan Profesional", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_600)]),
                ft.Divider(color=ft.Colors.GREEN_100),
                ft.Column([
                    ft.Text(text, size=14, color=ft.Colors.GREY_800)
                    for text in (summary_list[:3] if len(summary_list) > 3 else summary_list)
                ], spacing=10) if summary_list else ft.Text("Tidak ada ringkasan profesional yang tersedia.", size=14, color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.GREEN_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.GREEN_900)
    )

    # Skills card
    skills_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.STAR, size=30, color=ft.Colors.ORANGE_600),
                        ft.Text("Keahlian & Teknologi", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_600)]),
                ft.Divider(color=ft.Colors.ORANGE_100),
                ft.Row([
                    ft.Container(content=ft.Text(skill, size=12, color=ft.Colors.ORANGE_800,
                                                  weight=ft.FontWeight.W_500),
                                padding=ft.padding.symmetric(horizontal=12, vertical=6),
                                bgcolor=ft.Colors.ORANGE_100,
                                border_radius=15,
                                border=ft.border.all(1, ft.Colors.ORANGE_300))
                    for skill in skills[:20]
                ], wrap=True, spacing=8) if skills else ft.Text("Tidak ada informasi keahlian yang tersedia.", size=14, color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.ORANGE_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.ORANGE_900)
    )

    # Experience card
    experience_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.WORK_HISTORY, size=30, color=ft.Colors.PURPLE_600),
                        ft.Text("Pengalaman Kerja", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_600)]),
                ft.Divider(color=ft.Colors.PURPLE_100),
                ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.PURPLE_600),
                            ft.Container(content=ft.Text(exp[:200] + "..." if len(exp) > 200 else exp, size=14), expand=True)
                    ]) for exp in experience[:10]
                ], spacing=8) if experience else ft.Text("Tidak ada informasi pengalaman kerja yang tersedia.", size=14, color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.PURPLE_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.PURPLE_900)
    )

    # Education card
    education_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.SCHOOL, size=30, color=ft.Colors.RED_600),
                        ft.Text("Riwayat Pendidikan", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600)]),
                ft.Divider(color=ft.Colors.RED_100),
                ft.Column([
                    ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=ft.Colors.RED_600),
                            ft.Container(content=ft.Text(edu[:150] + "..." if len(edu) > 150 else edu, size=14), expand=True)
                    ]) for edu in education[:10]
                ], spacing=8) if education else ft.Text("Tidak ada informasi pendidikan yang tersedia.", size=14, color=ft.Colors.GREY_600)
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.RED_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.RED_900)
    )

    # Stats card
    stats_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.ANALYTICS, size=30, color=ft.Colors.BLUE_600),
                        ft.Text("Statistik CV", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_600)]),
                ft.Divider(color=ft.Colors.BLUE_100),
                ft.Row([
                    ft.Column([
                        ft.Text(f"📝 Total Kata: {len(cv_data.get('resume_text', '').split()) if cv_data.get('resume_text') else 0}", size=14),
                        ft.Text(f"📊 Skills Ditemukan: {len(skills)}", size=14),
                        ft.Text(f"🎓 Info Pendidikan: {len(education)}", size=14),
                    ], expand=1),
                    ft.Column([
                        ft.Text(f"💼 Pengalaman Kerja: {len(experience)}", size=14),
                        ft.Text(f"📄 Ringkasan: {len(summary_list)}", size=14),
                        ft.Text(f"🆔 CV ID: {cv_data.get('cv_id', 'Unknown')}", size=14),
                    ], expand=1),
                ])
            ], spacing=10),
            padding=20,
            gradient=ft.LinearGradient(begin=ft.alignment.top_left, end=ft.alignment.bottom_right,
                                       colors=[ft.Colors.with_opacity(0.05, ft.Colors.BLUE_400), ft.Colors.WHITE])
        ), elevation=2, shadow_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_900)
    )

    summary_content = ft.Column([
        header_row,
        divider,
        personal_info,
        summary_card,
        skills_card,
        experience_card,
        education_card,
        stats_card
    ], scroll=ft.ScrollMode.AUTO, spacing=20)

    return ft.Container(content=summary_content, padding=20, visible=True)
