import zipfile
import os

# ZIP 파일에서 Flask 앱 파일 찾기
zip_path = "project-template-enterprise.zip"

if os.path.exists(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        # src/app.py 찾기
        app_files = [f for f in z.namelist() if "app.py" in f]
        print(f"Found app.py files: {app_files}")

        # 첫 번째 app.py 내용 확인
        for app_file in app_files:
            if "src" in app_file or "app.py" in app_file:
                print(f"\n=== Content of {app_file} ===")
                content = z.read(app_file).decode("utf-8")
                # 처음 50줄만 출력
                lines = content.split("\n")[:50]
                for i, line in enumerate(lines, 1):
                    print(f"{i:3}: {line}")
                break
else:
    print(f"ZIP file not found: {zip_path}")
