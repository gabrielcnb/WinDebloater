"""
Utilitários para verificação e elevação de privilégios de administrador.
"""
import ctypes
import sys
import os


def is_admin() -> bool:
    """Verifica se o programa está rodando como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def run_as_admin(script_path: str = None) -> bool:
    """
    Reinicia o programa com privilégios de administrador.

    Args:
        script_path: Caminho do script a executar. Se None, usa o script atual.

    Returns:
        True se conseguiu iniciar como admin, False caso contrário.
    """
    if is_admin():
        return True

    if script_path is None:
        script_path = sys.argv[0]

    try:
        # Usa ShellExecute para pedir elevação UAC
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
        print(f"Erro ao solicitar privilégios de administrador: {e}")
        return False


def require_admin():
    """
    Decorator/função que garante que o código rode como admin.
    Se não for admin, reinicia o programa pedindo elevação.
    """
    if not is_admin():
        print("Este programa requer privilégios de administrador.")
        print("Solicitando elevação...")
        if run_as_admin():
            sys.exit(0)  # Sai do processo atual, o novo processo admin vai rodar
        else:
            print("Não foi possível obter privilégios de administrador.")
            sys.exit(1)
