import subprocess
import sys
from pathlib import Path
from typing import List, Set
import shutil
import tarfile
import io

SSH_SERVER = "root@185.11.134.213"
REMOTE_PATH = "~/PlazaBot"
LOCAL_DIR = Path(__file__).parent.resolve()
EXCLUDE_PATTERNS = [
    ".venv",
    "venv",
    ".env",
    ".git",
    ".gitignore",
    ".github",
    ".gitlab-ci.yml",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.egg-info",
    "dist",
    "build",
    "node_modules",
    ".DS_Store",
    "Thumbs.db",
    "casino.db",
    "*.log",
    "web_app",
    "update_server.py",
    "analyze_python.py"
]
USE_RSYNC = True
VERBOSE = True


def log(message: str, level: str = "INFO"):
    prefixes = {"INFO": "ℹ️ ", "SUCCESS": "✅ ", "ERROR": "❌ ", "WARNING": "⚠️ "}
    prefix = prefixes.get(level, "")
    print(f"{prefix}{message}")


def should_exclude(filepath: Path, patterns: List[str]) -> bool:
    filepath_str = str(filepath)
    path_parts = filepath.parts
    for pattern in patterns:
        if pattern.startswith("*."):
            ext = pattern.replace("*", "")
            if filepath_str.endswith(ext):
                return True
        else:
            if pattern in path_parts:
                return True
    return False


def collect_files(root_dir: Path, patterns: List[str]) -> Set[Path]:
    files = set()
    try:
        for item in root_dir.rglob("*"):
            if not should_exclude(item, patterns):
                files.add(item)
    except PermissionError as e:
        log(f"Ошибка доступа при сканировании: {e}", "WARNING")
    return files


def sync_with_rsync(local_dir: Path, remote: str, patterns: List[str]) -> bool:
    exclude_params = []
    for pattern in patterns:
        exclude_params.append(f"--exclude={pattern}")
    command = ["rsync", "-avz", "--delete", "--progress", "--filter=:- .gitignore", *exclude_params, f"{local_dir}/",
               remote]
    if VERBOSE:
        log(f"Команда: {' '.join(command)}", "INFO")
    try:
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        log(f"Ошибка rsync: {e}", "ERROR")
        return False
    except FileNotFoundError:
        log("rsync не найден в системе", "WARNING")
        return False


def sync_with_tar_ssh(local_dir: Path, remote: str, patterns: List[str]) -> bool:
    try:
        files_to_sync = collect_files(local_dir, patterns)
        if not files_to_sync:
            log("Нет файлов для синхронизации", "WARNING")
            return False
        total_files = len(files_to_sync)
        log(f"Найдено файлов для загрузки: {total_files}", "INFO")
        log("Создание архива...", "INFO")
        tar_buffer = io.BytesIO()
        with tarfile.open(fileobj=tar_buffer, mode="w:gz") as tar:
            for idx, filepath in enumerate(sorted(files_to_sync), 1):
                try:
                    arcname = filepath.relative_to(local_dir)
                    tar.add(filepath, arcname=arcname)
                    progress = int((idx / total_files) * 100)
                    print(f"\r[{'=' * int(progress / 2):<50}] {progress}% ({idx}/{total_files})",
                          end='', flush=True)
                except Exception as e:
                    log(f"Не удалось добавить {filepath}: {e}", "WARNING")
            print('\033[2K\r', end='')
        tar_buffer.seek(0)
        archive_size = len(tar_buffer.getvalue())
        log(f"Архив создан ({archive_size / 1024 / 1024:.2f} MB)", "INFO")
        log("Отправка на сервер...", "INFO")
        ssh_host = remote.split(":")[0] if ":" in remote else remote
        remote_path = remote.split(":")[1] if ":" in remote else "~"
        ssh_command = ["ssh", ssh_host, f"mkdir -p {remote_path} && cd {remote_path} && tar -xzf -"]
        if VERBOSE:
            log(f"SSH команда: {' '.join(ssh_command)}", "INFO")
        subprocess.run(ssh_command, input=tar_buffer.getvalue(), check=True, capture_output=True)
        log("Обновление успешно завершено!", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        log(f"Ошибка при отправке на сервер: {e.stderr.decode() if e.stderr else e}", "ERROR")
        return False
    except Exception as e:
        log(f"Неожиданная ошибка: {e}", "ERROR")
        return False


def check_ssh_available() -> bool:
    return shutil.which("ssh") is not None


# TODO: fix
def run_pm2_commands(ssh_host: str, process_name: str = "Plaza") -> bool:
    try:
        log(f"Запуск update_pm2.py для процесса '{process_name}'...", "INFO")
        ssh_command = ["ssh", ssh_host,
                       f"cd ~/ && source ~/.bashrc && python3 update_pm2.py {process_name}"]
        if VERBOSE:
            log(f"SSH команда: {' '.join(ssh_command)}", "INFO")
        result = subprocess.run(ssh_command, check=False, timeout=30)
        if result.returncode == 0:
            log("PM2 обновление выполнено успешно!", "SUCCESS")
            return True
        else:
            log(f"PM2 обновление завершилось с кодом ошибки: {result.returncode}", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log("Timeout при выполнении обновления PM2", "ERROR")
        return False
    except Exception as e:
        log(f"Неожиданная ошибка при выполнении PM2: {e}", "ERROR")
        return False


def main():
    log(f"Локальная директория: {LOCAL_DIR}", "INFO")
    log(f"Удалённый сервер: {SSH_SERVER}:{REMOTE_PATH}", "INFO")
    log(f"Операционная система: {sys.platform}", "INFO")
    if not check_ssh_available():
        log("SSH не найден! Убедитесь, что SSH установлен и доступен в PATH", "ERROR")
        return False
    if not LOCAL_DIR.exists():
        log(f"Локальная директория не существует: {LOCAL_DIR}", "ERROR")
        return False
    remote_full = f"{SSH_SERVER}:{REMOTE_PATH}"
    success = False
    if USE_RSYNC and shutil.which("rsync") is not None:
        log("Попытка использовать rsync...", "INFO")
        success = sync_with_rsync(LOCAL_DIR, remote_full, EXCLUDE_PATTERNS)
    if not success:
        log("Использование метода tar+ssh...", "INFO")
        success = sync_with_tar_ssh(LOCAL_DIR, remote_full, EXCLUDE_PATTERNS)
    # if success:
    #     run_pm2_commands(SSH_SERVER)
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        log("\nПроцесс прерван пользователем", "WARNING")
        sys.exit(130)
    except Exception as e:
        log(f"Критическая ошибка: {e}", "ERROR")
        sys.exit(1)
