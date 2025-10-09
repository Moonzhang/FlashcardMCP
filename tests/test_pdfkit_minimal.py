import os
import pdfkit
import shutil
import pytest


def test_pdfkit_minimal_html_to_pdf(tmp_path):
    """
    Minimal smoke test: convert inline HTML to PDF using pdfkit.
    Runs entirely inside the uv-managed venv.
    """
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>PDFKit Minimal Test</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; }
          .wrap { padding: 24px; }
          h1 { font-size: 20px; margin: 0 0 12px; }
          p { font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="wrap">
          <h1>Hello PDF</h1>
          <p>This is a minimal HTML converted with wkhtmltopdf.</p>
        </div>
      </body>
    </html>
    """

    # Resolve wkhtmltopdf binary path with preference to env var
    wkhtmltopdf_path = (
        os.environ.get("WKHTMLTOPDF_BINARY")
        or shutil.which("wkhtmltopdf")
        or os.path.join(os.environ.get("VIRTUAL_ENV", ""), "bin", "wkhtmltopdf")
        or "/opt/homebrew/bin/wkhtmltopdf"
    )

    if not wkhtmltopdf_path or not os.path.exists(wkhtmltopdf_path):
        pytest.skip(
            "wkhtmltopdf 未找到。请在 uv venv 中安装或设置 WKHTMLTOPDF_BINARY 环境变量。"
        )

    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    out_file = tmp_path / "minimal.pdf"
    options = {
        "encoding": "UTF-8",
        "quiet": "",
        "print-media-type": True,
        "margin-top": "10mm",
        "margin-right": "10mm",
        "margin-bottom": "10mm",
        "margin-left": "10mm",
    }

    pdf_bytes = pdfkit.from_string(html, False, options=options, configuration=config)
    assert isinstance(pdf_bytes, (bytes, bytearray)) and len(pdf_bytes) > 1024

    out_file.write_bytes(pdf_bytes)
    assert out_file.exists() and out_file.stat().st_size > 1024