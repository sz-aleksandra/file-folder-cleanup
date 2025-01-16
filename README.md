# ASU Projekt - Porządkowanie plików
## Aleksandra Szymańska 16. 01. 2025

### Opis
Skrypt pythonowy do organizowania plików. Umożliwia:
 - przenoszenie (lub kopiowanie) plików z innych folderów do folderu głównego
 - usuwanie nowszych plików o identycznej zawartości
 - usuwanie pustych plików
 - usuwanie plików tymczasowych o wybranych w pliku konfiguracyjnym rozszerzeniach
 - usuwanie starszych plików o tej samej nazwie
 - zmianę uprawnień plików na wybrane w pliku konfiguracyjnego
 - zmianę ustalonych w pliku konfiguracyjnym, problematycznych znaków na znak wybrany w pliku konfiguracyjnym

UWAGA: przenoszenie lub kopiowanie plików nadpisuje te o tej samej nazwie!

### Użytkowanie
python3 [plik_konfiguracyjny] [główny_katalog] [pozostałe_katalogi] [--identical {do_nothing,ask,apply_to_all}] [--empty {do_nothing,ask,apply_to_all}] [--temporary {do_nothing,ask,apply_to_all}] [--samename {do_nothing,ask,apply_to_all}] [--unusual_attributes {do_nothing,ask,apply_to_all}] [--troublesome_characters {do_nothing,ask,apply_to_all}] [--move_or_copy {do_nothing,move,copy}]

Domyślną opcją jest nic nie rób.

#### Przykładowe wywołanie
python3 file_organizing.py .clean_files X Y1 Y2 --move_or_copy move --samename ask --empty apply_to_all
