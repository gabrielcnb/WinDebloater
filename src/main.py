"""
WinDebloater - Removedor de bloatware do Windows
Ponto de entrada principal do aplicativo.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_admin():
    """Check whether we are running as administrator."""
    from utils.admin import is_admin, run_as_admin

    if not is_admin():
        print("WinDebloater requires administrator privileges.")
        print("Requesting elevation...")

        if run_as_admin():
            sys.exit(0)
        else:
            print("Could not obtain administrator privileges.")
            print("Execute o programa como administrador.")
            input("Pressione Enter para sair...")
            sys.exit(1)


def check_dependencies():
    """Check and install the required dependencies."""
    try:
        from PyQt6.QtWidgets import QApplication
        return True
    except ImportError:
        print("PyQt6 not found. Installing...")
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "PyQt6", "pywin32"],
            capture_output=True
        )
        if result.returncode == 0:
            print("Dependencies installed.")
            return True
        else:
            print("Failed to install dependencies:")
            print(result.stderr.decode())
            return False


def show_setup_wizard(app):
    """Show the setup wizard when needed."""
    from utils.setup import get_missing_dependencies
    from utils.compat import check_compatibility

    missing = get_missing_dependencies()
    issues = check_compatibility()

    # Keep only the issues that are not "OK"
    real_issues = [(i, s, r) for i, s, r in issues if r != "OK"]

    if missing or real_issues:
        from ui.dialogs import SetupWizard
        wizard = SetupWizard(missing, real_issues)
        if wizard.exec() == 0:  # Cancelado
            return False

    return True


def main():
    """Entry point."""
    # Check admin
    check_admin()

    # Check dependencies
    if not check_dependencies():
        input("Pressione Enter para sair...")
        sys.exit(1)

    # Import Qt only after the dependency check
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon

    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("WinDebloater")
    app.setOrganizationName("WinDebloater")

    # Icon, when present
    icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Show the wizard when needed
    if not show_setup_wizard(app):
        sys.exit(0)

    # Import and show the main window
    from ui.main_window import MainWindow

    window = MainWindow()
    window.show()

    # Run the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
