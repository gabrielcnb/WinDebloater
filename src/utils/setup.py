"""
Dependency auto-installation and environment checks.
"""
import subprocess
import sys
import os
from typing import List, Tuple


def check_python_version() -> Tuple[bool, str]:
    """Check that the Python version is compatible."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        return True, f"Python {version.major}.{version.minor}.{version.micro}"
    return False, f"Python {version.major}.{version.minor} (requer 3.8+)"


def check_pip() -> bool:
    """Check that pip is available."""
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            check=True
        )
        return True
    except Exception:
        return False


def get_installed_packages() -> List[str]:
    """Retorna lista de pacotes pip instalados."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True
        )
        packages = []
        for line in result.stdout.split('\n'):
            if '==' in line:
                packages.append(line.split('==')[0].lower())
        return packages
    except Exception:
        return []


def check_dependencies() -> List[Tuple[str, bool]]:
    """
    Check whether every dependency is installed.

    Returns:
        List of (package_name, is_installed) tuples
    """
    required = ['pyqt6', 'pywin32']
    installed = get_installed_packages()

    results = []
    for pkg in required:
        is_installed = pkg.lower() in installed
        results.append((pkg, is_installed))

    return results


def install_package(package_name: str) -> Tuple[bool, str]:
    """
    Instala um pacote via pip.

    Args:
        package_name: Nome do pacote a instalar.

    Returns:
        Tupla (sucesso, mensagem)
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos
        )

        if result.returncode == 0:
            return True, f"{package_name} instalado com sucesso"
        else:
            return False, result.stderr

    except subprocess.TimeoutExpired:
        return False, "Installation timed out"
    except Exception as e:
        return False, str(e)


def install_dependencies(packages: List[str] = None) -> List[Tuple[str, bool, str]]:
    """
    Install the required dependencies.

    Args:
        packages: Packages to install. When None, installs everything needed.

    Returns:
        Lista de tuplas (pacote, sucesso, mensagem)
    """
    if packages is None:
        # Work out which ones need installing
        deps = check_dependencies()
        packages = [name for name, installed in deps if not installed]

    results = []
    for pkg in packages:
        success, message = install_package(pkg)
        results.append((pkg, success, message))

    return results


def get_missing_dependencies() -> List[str]:
    """Return the list of missing dependencies."""
    deps = check_dependencies()
    return [name for name, installed in deps if not installed]


def setup_environment() -> Tuple[bool, List[str]]:
    """
    Configura o ambiente completo.

    Returns:
        Tupla (tudo_ok, lista_de_mensagens)
    """
    messages = []
    all_ok = True

    # Check Python
    py_ok, py_msg = check_python_version()
    messages.append(f"Python: {py_msg}")
    if not py_ok:
        all_ok = False

    # Check pip
    if not check_pip():
        messages.append("pip: not found")
        all_ok = False
    else:
        messages.append("pip: OK")

    # Check dependencies
    deps = check_dependencies()
    for name, installed in deps:
        status = "OK" if installed else "Not installed"
        messages.append(f"{name}: {status}")
        if not installed:
            all_ok = False

    return all_ok, messages
