import os
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv(".env")
PIPELINE_JSON_PATH = os.getenv("PIPELINE_JSON_PATH")
PIPELINE_MAIN_HTML_REPORT = os.getenv("PIPELINE_MAIN_HTML_REPORT")
OVERVIEW_OUTPUT = os.getenv("OVERVIEW_OUTPUT")
CRITICAL_CATEGORIES_OUTPUT = os.getenv("CRITICAL_CATEGORIES_OUTPUT")
NON_CRITICAL_CATEGORIES_OUTPUT = os.getenv("NON_CRITICAL_CATEGORIES_OUTPUT")

from dotenv import load_dotenv
load_dotenv(".env")
APK_LOC_V1 = os.getenv("APK_LOC_V1")
APK_LOC_V2 = os.getenv("APK_LOC_V2")

import re
v1 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V1).group(1)
v2 = re.search(r'Signal_Android_(\d+\.\d+\.\d+)\.apk$', APK_LOC_V2).group(1)
VERSION_ID = f"{v1}-{v2}"

COLUMNS_TO_DISPLAY = [
    ("func_status", "Status"),
    ("func_name", "Function"),
    ("func_eval", "Rating"),
    ("flag_classification_type", "Classification"),
    ("flag_strings_in_diff", "Strings in diff"),
    ("flag_library_func", "External"),
    ("flag_is_synthetic", "Synthetic"),
    ("flag_control_flow_in_diff", "CF Change"),
]


def load_json_data():
    with open(f"result/{VERSION_ID}/{PIPELINE_JSON_PATH}", "r") as f:
        raw_data = json.load(f)
    f.close

    rows = []
    for id, entry in raw_data.items():
        filtered_entry = {key: entry.get(key, "") for key, _ in COLUMNS_TO_DISPLAY}
        filtered_entry["id"] = id  # explicitly add the ID

        # Add expandable data that should be searchable (but not shown)
        filtered_entry["classifications_critical"] = ", ".join(
            entry.get("classifications_critical", [])
        )
        rows.append(filtered_entry)

    columns_js = [
            {
                "data": None,
                "title": "",
                "className": "details-control",
                "orderable": False,
                "defaultContent": "",
            }
        ] + [{"data": key, "title": title} for key, title in COLUMNS_TO_DISPLAY]

    # Add hidden column definition for filtering on classifications_critical
    columns_js.append(
        {
            "data": "classifications_critical",
            "title": "Critical Classifications",
            "visible": False,     # Don't show it
            "searchable": True    # But allow filtering
        }
    )

    return raw_data, rows, json.dumps(columns_js)


def generate_html_report():
    
    from src.misc.static import (
        STYLE_CSS, 
        DARK_MODE_CSS, 
        FILTER_BUTTONS_STYLE, 
        DATATABLE_STYLING,
        EXPANDABLE_DATA_STYLING
        )
    from src.misc.static import NC, PINK, RED, ORANGE, BLUE
    from src.misc.static import DETAILS_1, DETAILS_2, DETAILS_3

    raw_data, rows, columns_js = load_json_data()

    raw_data_js = json.dumps(raw_data)
    json_data = json.dumps(rows)

    current_time = datetime.now()

    js_content = f"""
        const data = {json_data};
        const rawDataMap = {raw_data_js};
        const columns = {columns_js};
        
        // The set of active classifications to base filter on
        let activeFilters = new Set();

        $(document).ready(function() {{
            // Dynamically insert headers
            $('#dataTable thead tr').html(columns.map(col => `<th>${{col.title}}</th>`).join(''));

            const uniqueTags = getUniqueCriticals(data);
            renderFilterButtons(uniqueTags);

            const table = $('#dataTable').DataTable({{
                data: data,
                columns: columns,
                pageLength: 100,
                dom: 'Bfrtip',
                buttons: ['copy', 'csv', 'excel', 'pdf', 'print'],
                initComplete: function () {{
                    setupColumnFilters(this.api());
                }}
            }});

            // Now that table is initialized, we can safely use it
            const CRITICAL_COLUMN_INDEX = columns.findIndex(col => col.data === 'classifications_critical');

            $(document).on('click', '.filter-btn', function () {{
                const tag = $(this).data('tag');

                // Toggle the tag
                if (activeFilters.has(tag)) {{
                    activeFilters.delete(tag);
                    $(this).removeClass('active-filter');
                }} else {{
                    activeFilters.add(tag);
                    $(this).addClass('active-filter');
                }}

                /* 
                Build regex search string for handling multiple classifications 
                at once. On button press, the category is added to the regex grammar,
                then checks are made to that grammar instead of each item in a list
                */
                if (activeFilters.size === 0) {{
                    table.column(CRITICAL_COLUMN_INDEX).search('').draw();
                }} else {{
                    const pattern = Array.from(activeFilters)
                        .map(tag => tag.trim().replace(/[.*+?^$\\{{\\}}()|[\\]\\\\]/g, "\\\\$&"))
                        .join("|");

                    table.column(CRITICAL_COLUMN_INDEX).search(pattern, true, false).draw();
                }}
            }});

            // Column filters
            function setupColumnFilters(api) {{
                $('#dataTable tfoot').html('<tr>' + columns.map(() => '<th></th>').join('') + '</tr>');

                api.columns().every(function () {{
                    var column = this;
                    $("<input type='text' placeholder='Search' style='width: 100%; font-size: 0.8em;'>")
                        .appendTo($(column.footer()).empty())
                        .on('keyup change', function () {{
                            column.search($(this).val()).draw();
                        }});
                }});
            }}


            // Expandable row data formatting
            function formatRowDetails(rowData) {{
                const big_data = rawDataMap[rowData.id];

                return `
                    <div class='row-details'>
                        <div class="clean-details">
                            <h4 class="section-title">Function Details</h4>
                            <dl>
                                <dt>Func</dt><dd><pre>${{big_data.fullname}}</pre></dd>
                                <dt>Signature</dt><dd><pre>${{big_data.signature}}</pre></dd>
                                <dt>Source File</dt><dd><pre>${{big_data.source_file}}</pre></dd>
                                <dt>Source Class</dt><dd><pre>${{big_data.source_class}}</pre></dd>
                                <dt>Source Superclass</dt><dd><pre>${{big_data.source_superclass}}</pre></dd>
                            </dl>

                            <h4 class="section-title">Categories</h4>
                            <dl>
                                <dt>General</dt><dd>${{big_data.classifications_general}}</dd>
                                <dt class="red">Critical</dt><dd>${{big_data.classifications_critical}}</dd>
                                <dt>Matched Keywords</dt><dd><pre>${{big_data.classifications_matched_keywords}}</pre></dd>
                            </dl>

                            <h4 class="section-title">Code Changes</h4>
                            <dl>
                                <dt>Diff</dt><dd><pre>${{big_data.code_diff_changes}}</pre></dd>
                                <dt class="red">Critical Changes</dt><dd><pre>${{big_data.code_critical_code_changes}}</pre></dd>
                                <dt class="orange">Strings</dt><dd><pre>${{big_data.code_strings}}</pre></dd>
                                <dt class="blue">Changed Ifs</dt><dd><pre>${{big_data.control_flow_changes_changed_ifs}}</pre></dd>
                                <dt class="blue">Added Else</dt><dd>${{big_data.control_flow_changes_added_else}}</dd>
                                <dt class="blue">Deleted Else</dt><dd>${{big_data.control_flow_changes_deleted_else}}</dd>
                            </dl>

                            <h4 class="section-title">Inheritance</h4>
                            <dl>
                                <dt>Parents</dt><dd><pre>${{big_data.inheritance_parents}}</pre></dd>
                                <dt>Children</dt><dd><pre>${{big_data.inheritance_children}}</pre></dd>
                            </dl>

                        {DETAILS_1}{PINK}Code diff: {NC}{DETAILS_2}
                        ${{big_data.html_diff}}{DETAILS_3}
                        {DETAILS_3}
                    </div>
                `;
            }}

            // Toggle row details
            $('#dataTable tbody').on('click', 'td.details-control', function () {{
                var tr = $(this).closest('tr');
                var row = table.row(tr);

                if (row.child.isShown()) {{
                    row.child.hide();
                    tr.removeClass('shown');
                }} else {{
                    row.child(formatRowDetails(row.data())).show();
                    tr.addClass('shown');
                }}
            }});

            // Dark Mode Toggle Button functionality
            $('#darkModeBtn').on('click', function() {{
                $('body').toggleClass('dark-mode');
            }});

            // Extract unique critical categories
            function getUniqueCriticals(data) {{
                const all = new Set();
                data.forEach(row => {{
                    const crits = (row.classifications_critical || '').split(',').map(s => s.trim()).filter(Boolean);
                    crits.forEach(c => all.add(c));
                }});
                return Array.from(all).sort();
            }}

            // Render filter buttons above the table
            function renderFilterButtons(uniqueTags) {{
                const $container = $("<div id='classificationFilters' style='margin: 10px 0;'></div>");
                
                uniqueTags.forEach(tag => {{
                    const $btn = $(`<button class='filter-btn' data-tag='${{tag}}' style='margin: 0 5px 5px 0;'>${{tag}}</button>`);
                    $container.append($btn);
                }});

                $('#dataTable').before($container);
            }}
        }});
    """


    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Critical Functions Report</title>

            <!-- DataTables core -->
            <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>

            <!-- Buttons extension -->
            <link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.1/css/buttons.dataTables.min.css" />

            <!-- Scripts -->
            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.1/js/dataTables.buttons.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.html5.min.js"></script>
            <script src="https://cdn.datatables.net/buttons/2.4.1/js/buttons.print.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/pdfmake.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.2.7/vfs_fonts.js"></script>
            {STYLE_CSS}
            {DARK_MODE_CSS}
            {FILTER_BUTTONS_STYLE}
            {DATATABLE_STYLING}
            {EXPANDABLE_DATA_STYLING}
        </head>
        <body>
            <!-- Toggle Dark Mode Button -->
            <button id="darkModeBtn">Toggle Dark Mode</button>

            <div>
                <small>Version: {VERSION_ID}</small></br>
                <small>Executed at: {current_time}</small>
            </div>

            <div class="container">
                <iframe src="{OVERVIEW_OUTPUT}" width="100%" height="400"></iframe>
                <iframe src="{CRITICAL_CATEGORIES_OUTPUT}" width="100%" height="400"></iframe>
                <iframe src="{NON_CRITICAL_CATEGORIES_OUTPUT}" width="100%" height="400"></iframe>
            </div>

            <div style="overflow-x:auto;">
                <table id="dataTable" class="display nowrap" style="width:100%">
                    <thead><tr></tr></thead>
                    <tfoot><tr></tr></tfoot>
                </table>
            </div>

            <script>
                {js_content}
            </script>
        </body>
        </html>
    """

    # Write to HTML file
    with open(f"result/{VERSION_ID}/{PIPELINE_MAIN_HTML_REPORT}", "w", encoding="utf-8") as out_file:
        out_file.write(html_content)
    out_file.close()