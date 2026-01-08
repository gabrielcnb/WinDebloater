"""
WinDebloater - Removedor de bloatware do Windows
Ponto de entrada principal do aplicativo.
"""
import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_admin():
    """Verifica se está rodando como administrador."""
    from utils.admin import is_admin, run_as_admin

    if not is_admin():
        print("WinDebloater requer privilégios de administrador.")
        print("Solicitando elevação...")

        if run_as_admin():
            sys.exit(0)
        else:
            print("Não foi possível obter privilégios de administrador.")
            print("Execute o programa como administrador.")
            input("Pressione Enter para sair...")
            sys.exit(1)


def check_dependencies():
    """Verifica e instala dependências necessárias."""
    try:
        from PyQt6.QtWidgets import QApplication
        return True
    except ImportError:
        print("PyQt6 não encontrado. Instalando...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "PyQt6", "pywin32"],
            capture_output=True
        )
        if result.returncode == 0:
            print("Dependências instaladas com sucesso!")
            return True
        else:
            print("Erro ao instalar dependências:")
            print(result.stderr.decode())
            return False


def show_setup_wizard(app):
    """Mostra o wizard de configuração se necessário."""
    from utils.setup import get_missing_dependencies
    from utils.compat import check_compatibility

    missing = get_missing_dependencies()
    issues = check_compatibility()

    # Filtra apenas issues que não são "OK"
    real_issues = [(i, s, r) for i, s, r in issues if r != "OK"]

    if missing or real_issues:
        from ui.dialogs import SetupWizard
        wizard = SetupWizard(missing, real_issues)
        if wizard.exec() == 0:  # Cancelado
            return False

    return True


def main():
    """Função principal."""
    # Verifica admin
    check_admin()

    # Verifica dependências
    if not check_dependencies():
        input("Pressione Enter para sair...")
        sys.exit(1)

    # Importa Qt depois de verificar dependências
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon

    # Cria aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("WinDebloater")
    app.setOrganizationName("WinDebloater")

    # Ícone (se existir)
    icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Mostra wizard se necessário
    if not show_setup_wizard(app):
        sys.exit(0)

    # Importa e mostra janela principal
    from ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    # Executa loop de eventos
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
