"""
Management of user-defined bloatware entries.
"""
from dataclasses import dataclass
from typing import List, Optional
from .database import BloatwareItem, RiskLevel, Category


@dataclass
class CustomBloatware:
    """A bloatware entry added by the user."""
    process_name: str
    description: str

    def to_bloatware_item(self) -> BloatwareItem:
        """Converte para BloatwareItem."""
        return BloatwareItem(
            id=f"custom_{self.process_name.lower()}",
            name=f"Customizado: {self.process_name}",
            description=self.description,
            category=Category.PROCESSES,
            risk_level=RiskLevel.RISKY,
            package_name=None,
            process_name=self.process_name,
            service_name=None,
            registry_keys=[
                f"HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{self.process_name}.exe"
            ],
            removal_commands=[
                f"Stop-Process -Name '{self.process_name}' -Force",
                f"New-Item -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{self.process_name}.exe' -Force",
                f"Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{self.process_name}.exe' -Name 'Debugger' -Value 'systray.exe'"
            ],
            can_reinstall=True
        )


class SystemProcessValidator:
    """Validate that a process is safe to remove."""

    # Critical Windows processes that must NEVER be removed
    CRITICAL_PROCESSES = {
        # Kernel e sistema
        'system', 'smss', 'csrss', 'wininit', 'services', 'lsass', 'winlogon',
        'svchost', 'dllhost', 'conhost', 'dwm', 'explorer',

        # Security
        'msmpeng', 'nissrv', 'securityhealthservice', 'sgrmbroker',

        # Drivers e hardware
        'registry', 'fontdrvhost', 'audiodg',

        # Networking and communication
        'spoolsv', 'taskhostw', 'runtimebroker',

        # Sistema de arquivos
        'ntoskrnl', 'idle',

        # Critical updates
        'tiworker', 'trustedinstaller',

        # Shell e UI
        'sihost', 'shellexperiencehost', 'startmenuexperiencehost',
        'textinputhost', 'applicationframehost',

        # Python (do not remove while it is running)
        'python', 'pythonw',
    }

    # Suspicious processes that still need care
    WARNING_PROCESSES = {
        'chrome', 'firefox', 'edge', 'msedge',
        'discord', 'spotify', 'steam',
        'notepad', 'code', 'devenv',
    }

    @staticmethod
    def is_safe_to_remove(process_name: str) -> tuple[bool, str]:
        """
        Verifica se um processo pode ser removido.

        Args:
            process_name: Nome do processo (sem .exe)

        Returns:
            Tupla (pode_remover, mensagem)
        """
        process_lower = process_name.lower().replace('.exe', '')

        # Check the critical processes
        if process_lower in SystemProcessValidator.CRITICAL_PROCESSES:
            return False, f"❌ BLOCKED: '{process_name}' is a critical Windows process and cannot be removed."

        # Check the processes that need care
        if process_lower in SystemProcessValidator.WARNING_PROCESSES:
            return True, f"⚠️ CAREFUL: '{process_name}' is a common application. Are you sure you want to remove it?"

        # Unknown processes need confirmation too
        return True, f"✓ Processo pode ser removido (mas use com cautela)"

    @staticmethod
    def validate_process_name(process_name: str) -> tuple[bool, str]:
        """
        Valida o nome do processo.

        Returns:
            Tuple (is_valid, error_message)
        """
        if not process_name:
            return False, "The process name cannot be empty"

        # Strip .exe when the user typed it
        process_name = process_name.replace('.exe', '')

        # Check for valid characters
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', process_name):
            return False, "The process name contains invalid characters"

        # Check that it is not too short
        if len(process_name) < 2:
            return False, "Nome do processo muito curto"

        return True, ""


class CustomBloatwareManager:
    """Gerencia bloatwares customizados."""

    def __init__(self):
        self.custom_items: List[CustomBloatware] = []

    def add_custom(self, process_name: str, description: str) -> tuple[bool, str]:
        """
        Adiciona um bloatware customizado.

        Returns:
            Tupla (sucesso, mensagem)
        """
        # Strip .exe when present
        process_name = process_name.replace('.exe', '')

        # Valida nome
        valid, error = SystemProcessValidator.validate_process_name(process_name)
        if not valid:
            return False, error

        # Check that it is safe
        safe, msg = SystemProcessValidator.is_safe_to_remove(process_name)
        if not safe:
            return False, msg

        # Check whether it already exists
        if any(item.process_name.lower() == process_name.lower() for item in self.custom_items):
            return False, f"Process '{process_name}' has already been added"

        # Adiciona
        custom = CustomBloatware(
            process_name=process_name,
            description=description or f"Processo customizado: {process_name}"
        )
        self.custom_items.append(custom)

        return True, f"✓ Processo '{process_name}' adicionado com sucesso!"

    def remove_custom(self, process_name: str) -> bool:
        """Remove um bloatware customizado."""
        process_name = process_name.replace('.exe', '')
        self.custom_items = [
            item for item in self.custom_items
            if item.process_name.lower() != process_name.lower()
        ]
        return True

    def get_all(self) -> List[BloatwareItem]:
        """Retorna todos os bloatwares customizados como BloatwareItems."""
        return [item.to_bloatware_item() for item in self.custom_items]

    def clear(self):
        """Remove todos os customizados."""
        self.custom_items.clear()
