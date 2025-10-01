from flask import Flask, request, jsonify
import pdfplumber
import ftfy

app = Flask(__name__)

@app.route("/extract-table", methods=["POST"])
def extract_table():
    try:
        if "file" not in request.files:
            return jsonify({"error": "Thiếu file PDF"}), 400

        file = request.files["file"]
        all_rows = []

        with pdfplumber.open(file.stream) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                row_start =0
                if page_num == 1:
                    row_start = 1
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        # Bỏ qua header -> chỉ lấy các dòng từ index 1 trở đi
                        for row in table[row_start:]:
                            # Fix Unicode cho từng ô
                            fixed_row = [ftfy.fix_text(cell) if cell else "" for cell in row]
                            all_rows.append(fixed_row)

        if not all_rows:
            return jsonify({"error": "Không tìm thấy bảng nào"}), 400

        return jsonify(all_rows)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
