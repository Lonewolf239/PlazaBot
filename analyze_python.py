import time
from pathlib import Path
from collections import defaultdict
# noinspection PyPackageRequirements
from tabulate import tabulate


def analyze_python_files(verbose=False):
    total_chars = 0
    total_lines = 0
    total_size = 0
    file_count = 0
    file_stats = []
    extension_stats = defaultdict(lambda: {'files': 0, 'lines': 0, 'size': 0})
    ignore_dirs = {'.git', '.idea', '.venv', '__pycache__', '.vscode', 'node_modules', '.pytest_cache'}
    root_dir = Path(__file__).parent
    start_time = time.time()
    for py_file in root_dir.rglob("*.py"):
        if any(ignore_dir in py_file.parts for ignore_dir in ignore_dirs):
            continue
        try:
            file_size = py_file.stat().st_size
            total_size += file_size
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            chars = len(content)
            lines = len(content.splitlines())
            total_chars += chars
            total_lines += lines
            file_count += 1
            file_stats.append({
                'path': str(py_file.relative_to(root_dir)),
                'lines': lines,
                'size': file_size,
                'chars': chars
            })
            extension_stats['py']['files'] += 1
            extension_stats['py']['lines'] += lines
            extension_stats['py']['size'] += file_size
        except Exception as e:
            print(f"Ошибка при обработке {py_file}: {e}")
    elapsed = time.time() - start_time
    _print_stats(file_count, total_lines, total_chars, total_size, elapsed, file_stats, verbose)
    return {
        'files': file_count,
        'lines': total_lines,
        'chars': total_chars,
        'size_bytes': total_size,
        'time': elapsed
    }


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} Б"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} КБ"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} МБ"


def _print_stats(file_count, total_lines, total_chars, total_size, elapsed, file_stats, verbose):
    print("=" * 80)
    print("АНАЛИЗ PYTHON ПРОЕКТА".center(80))
    print("=" * 80 + "\n")
    avg_lines = total_lines // file_count if file_count > 0 else 0
    avg_chars = total_chars // file_count if file_count > 0 else 0
    summary_data = [
        ["Файлы", f"{file_count} шт."],
        ["Строк кода (всего)", f"{total_lines:,}"],
        ["Строк кода (среднее)", f"{avg_lines} строк/файл"],
        ["Символов (всего)", f"{total_chars:,}"],
        ["Символов (среднее)", f"{avg_chars:,} символов/файл"],
        ["Размер", _format_size(total_size)],
        ["Время анализа", f"{elapsed:.3f} сек"],
    ]
    print(tabulate(summary_data, headers=["Метрика", "Значение"], tablefmt="fancy_grid"))
    print()
    if file_stats:
        print("ТОП-5 САМЫХ БОЛЬШИХ ФАЙЛОВ")
        sorted_files = sorted(file_stats, key=lambda x: x['lines'], reverse=True)[:5]
        top_files_data = []
        for i, file_info in enumerate(sorted_files, 1):
            top_files_data.append([
                i,
                file_info['path'],
                f"{file_info['lines']:,}",
                _format_size(file_info['size']),
            ])
        print(tabulate(
            top_files_data,
            headers=["№", "Файл", "Строк", "Размер"],
            tablefmt="fancy_grid",
            stralign="left"
        ))
        print()
    if verbose and file_stats:
        print("ВСЕ ФАЙЛЫ")
        sorted_files = sorted(file_stats, key=lambda x: x['lines'], reverse=True)
        all_files_data = []
        for i, file_info in enumerate(sorted_files, 1):
            all_files_data.append([
                i,
                file_info['path'],
                f"{file_info['lines']:,}",
                _format_size(file_info['size']),
                f"{file_info['chars']:,}",
            ])
        print(tabulate(
            all_files_data,
            headers=["№", "Файл", "Строк", "Размер", "Символов"],
            tablefmt="fancy_grid",
            stralign="left",
            maxcolwidths=[3, 50, 10, 10, 12]
        ))
        print()
    print("=" * 80 + "\n")


if __name__ == "__main__":
    analyze_python_files(verbose=False)
    input("Нажмите Enter для выхода...")
