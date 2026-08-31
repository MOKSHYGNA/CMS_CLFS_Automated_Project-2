from pypdf import PdfReader
from zipfile import ZipFile
from pathlib import Path


zip_files = [
    Path.home() / "Documents" / "pfrev26c" / "PFREV26C_QP.zip",
    Path.home() / "Documents" / "pfrev26c" / "PFREV26C_nonQP.zip"
]

for zip_file in zip_files:

    print("\n" + "=" * 70)
    print(f"ZIP FILE: {zip_file.name}")
    print("=" * 70)

    with ZipFile(zip_file, "r") as zip_ref:

        pdf_files = [
            name for name in zip_ref.namelist()
            if name.lower().endswith(".pdf")
        ]

        for pdf_file in pdf_files:

            print(f"\nPDF FILE: {pdf_file}")
            print("-" * 70)

            # Extract PDF temporarily
            extracted_path = Path("temp_" + Path(pdf_file).name)

            with zip_ref.open(pdf_file) as source:
                with open(extracted_path, "wb") as target:
                    target.write(source.read())

            reader = PdfReader(extracted_path)

            for page_number, page in enumerate(reader.pages[:5], start=1):

                text = page.extract_text()

                print(f"\n--- PAGE {page_number} ---")
                print(text[:5000])

            extracted_path.unlink()