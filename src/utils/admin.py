"""
Helpers for checking and elevating administrator privileges.
"""
import ctypes
import sys
import os


def is_admin() -> bool:
    """Check whether the program is running as administrator."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin(script_path: str = None) -> bool:
    """
    Restart the program with administrator privileges.

    Args:
        script_path: Caminho do script a executar. Se None, usa o script atual.

    Returns:
        True when it managed to start as admin, False otherwise.
    """
    if is_admin():
        return True

    if script_path is None:
        script_path = sys.argv[0]

    try:
        # Use ShellExecute to trigger the UAC prompt
        params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])

        ctypes.windll.shell32.ShellExecuteW(
            None,                   # hwnd
            "runas",                # lpOperation (pedir admin)
            sys.executable,         # lpFile (python.exe)
            f'"{script_path}" {params}',  # lpParameters
            None,                   # lpDirectory
            1                       # nShowCmd (SW_SHOWNORMAL)
        )
        return True
    except Exception as e:
        print(f"Failed to request administrator privileges: {e}")
        return False


def require_admin():
    """
    Ensures the code runs as admin.
    When it is not admin, restarts the program asking for elevation.
    """
    if not is_admin():
        print("This program requires administrator privileges.")
        print("Requesting elevation...")
        if run_as_admin():
            sys.exit(0)  # Sai do processo atual, o novo processo admin vai rodar
        else:
            print("Could not obtain administrator privileges.")
            sys.exit(1)
