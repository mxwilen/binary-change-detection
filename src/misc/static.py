# ANSI Color Codes for success prints
CLI_GREEN  = "\033[0;32m"
CLI_RED    = "\033[0;31m"
CLI_YELLOW = "\033[0;33m"
CLI_PINK   = "\033[0;35m"
CLI_NC     = "\033[0m"  # No color

# HTML tags for colored text
GREEN  = '<span style="color:green;">'
RED    = '<span style="color:red;">'
YELLOW = '<span style="color:yellow;">'
ORANGE = '<span style="color:orange;">'
PINK   = '<span style="color:pink;">'
BLUE   = '<span style="color:cyan;">'
BROWN  = '<span style="color:brown;">'
PURPLE = '<span style="color:purple;">'
NC     = "</span>"  # No color (closing tag)

# HTML tags for using drop down info
DETAILS_1 = "<details><summary>"
DETAILS_2 = "</summary>"
DETAILS_3 = "</details>"

# HTML line break
HTML_BREAK = "<hr>"

# Python CLI line break
PYTHON_LINE_BREAK = "-" * 100

# CSS STYLING
STYLE_CSS = """
<style>
    :root {
        --page-font-family: monospace;
        --page-font-size: 15px;
    }
    body {
        font-family: var(--page-font-family);
        font-size: var(--page-font-size);
    }
    pre {
        white-space: pre-wrap;
    }
    .container {
        display: flex; 
        gap: 10px;
        padding:25px;
    }
    iframe {
        border: none;
    }
</style>
"""

# CSS for dark mode
DARK_MODE_CSS = """
<style>
  .dark-mode {
      background-color: #121212;
      color: #e0e0e0;
  }

  .dark-mode table.dataTable {
      background-color: #1e1e1e;
      color: #e0e0e0;
  }

  .dark-mode .dataTables_wrapper .dataTables_filter input,
  .dark-mode .dataTables_wrapper .dataTables_length select {
      background-color: #333;
      color: #e0e0e0;
      border: 1px solid #555;
  }

  #darkModeBtn {
      position: fixed;
      top: 10px;
      right: 10px;
      padding: 8px 12px;
      cursor: pointer;
      z-index: 1000;
  }
</style>
"""


FILTER_BUTTONS_STYLE = """
<style>
    .filter-btn {
        padding: 6px 10px;
        background-color: #f0f0f0;
        border: 1px solid #ccc;
        cursor: pointer;
        border-radius: 4px;
    }

    .filter-btn:hover {
        background-color: #e0e0e0;
    }

    .active-filter {
        background-color: #007bff;
        color: white;
        border-color: #007bff;
    }

    body.dark-mode .filter-btn {
        background-color: #333;
        color: #ddd;
        border-color: #666;
    }

    body.dark-mode .filter-btn.active-filter {
        background-color: #0d6efd;
        color: white;
    }
</style>
"""

DATATABLE_STYLING = """
<style>
    /* Make footer row sticky */
    #dataTable tfoot {
        display: table-header-group; /* This places footer like a header row */
    }
</style>
"""

EXPANDABLE_DATA_STYLING = """
<style>
    .shown td.details-control::before {
      content: "▼";
    }

    td.details-control::before {
        content: "▶";
        cursor: pointer;
        padding-right: 10px;
    }

    .clean-details {
        font-family: 'Segoe UI', sans-serif;
        padding: 10px 20px;
        background: #fafafa;
        border-left: 4px solid #007bff;
        margin: 10px 0;
        border-radius: 6px;
        font-size: 0.95em;
    }

    .clean-details h4.section-title {
        margin-top: 1em;
        font-size: 1em;
        font-weight: bold;
        color: #333;
        border-bottom: 1px solid #ddd;
        padding-bottom: 2px;
    }

    .clean-details dl {
        display: grid;
        grid-template-columns: max-content 1fr;
        row-gap: 7px;
        column-gap: 10px;
        margin: 0.5em 0;
    }

    .clean-details dt {
        font-weight: 600;
        color: #444;
    }

    .clean-details dd {
        margin: 0;
        color: #222;
    }

    .clean-details dt.red { color: #c0392b; }
    .clean-details dt.orange { color: #e67e22; }
    .clean-details dt.blue { color: #2980b9; }

    mark {
        background-color: #fffd60;
        padding: 0 2px;
        border-radius: 3px;
    }

    .clean-details pre {
        background: #f6f6f6;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 0.9em;
        white-space: pre-wrap;
        word-break: break-word;

        margin-top: -7px;
    }
</style>
"""