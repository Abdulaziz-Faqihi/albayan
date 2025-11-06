import shutil
import sys
import os
from cx_Freeze import setup, Executable

if os.path.exists("main.py"):
    os.rename("main.py", "Albayan.py")

include_files = [
    ("database", "database"),
    ("documentation", "documentation"),
    ("Audio", "Audio"),
    ("bass.dll", "bass.dll"),
    ("Albayan.ico", "Albayan.ico")
]


build_exe_options = {
    "build_exe": "albayan_build",
    "optimize": 1,
    "include_files": include_files,
    "packages": ["core_functions", "theme", "ui", "utils"],
    "includes": ["packaging", "requests", "UniversalSpeech", "sqlalchemy", "sqlalchemy.dialects.sqlite", "apscheduler", "wx"],
    "excludes": ["tkinter", "test", "setuptools", "pip", "numpy", "unittest"],
    "include_msvcr": True
}

setup(
    name="Albayan",
    version="3.0.1",
    description="Albayan",
    long_description="البيان - Albayan, كل ما يخص الإسلام",
    author="TecWindow",
    author_email="support@tecwindow.net",
    url="https://tecwindow.net",
    download_url="https://github.com/tecwindow/albayan",
    keywords=["islamic", "islam", "quran", "desktop", "alquran", "tecwindow", "القرآن", "إسلام"],
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "Albayan.py",
            base="Win32GUI" if sys.platform == "win32" else None,
            target_name="Albayan.exe",
            icon="Albayan.ico",
            copyright="2025 tecwindow"
        )
    ]
)

if os.path.exists("Albayan.py"):
    os.rename("Albayan.py", "main.py")
