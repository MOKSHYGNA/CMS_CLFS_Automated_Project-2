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

    if not zip_file.exists():
        print(f"File not found: {zip_file}")
        continue

    with ZipFile(zip_file, "r") as zip_ref:

        txt_files = [
            name for name in zip_ref.namelist()
            if name.lower().endswith(".txt")
        ]

        for txt_file in txt_files:

            print(f"\nTEXT FILE: {txt_file}")
            print("-" * 70)

            with zip_ref.open(txt_file) as file:

                for i, line in enumerate(file):

                    print(line.decode("utf-8", errors="replace").rstrip())

                    if i >= 19:
                        break