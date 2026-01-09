"""
Gerenciamento de bloatwares customizados pelo usuário.
"""
from dataclasses import dataclass
from typing import List, Optional
from .database import BloatwareItem, RiskLevel, Category


@dataclass
class CustomBloatware:
    """Bloatware customizado adicionado pelo usuário."""
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
    """Valida se um processo pode ser removido com segurança."""

    # Processos críticos do Windows que NUNCA devem ser removidos
    CRITICAL_PROCESSES = {
        # Kernel e sistema
        'system', 'smss', 'csrss', 'wininit', 'services', 'lsass', 'winlogon',
        'svchost', 'dllhost', 'conhost', 'dwm', 'explorer',

        # Segurança
        'msmpeng', 'nissrv', 'securityhealthservice', 'sgrmbroker',

        # Drivers e hardware
        'registry', 'fontdrvhost', 'audiodg',

        # Rede e comunicação
        'spoolsv', 'taskhostw', 'runtimebroker',

        # Sistema de arquivos
        'ntoskrnl', 'idle',

        # Atualizações críticas
        'tiworker', 'trustedinstaller',

        # Shell e UI
        'sihost', 'shellexperiencehost', 'startmenuexperiencehost',
        'textinputhost', 'applicationframehost',

        # Python (não remover durante execução)
        'python', 'pythonw',
    }

    # Processos suspeitos mas que requerem atenção
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

        # Verifica processos críticos
        if process_lower in SystemProcessValidator.CRITICAL_PROCESSES:
            return False, f"❌ BLOQUEADO: '{process_name}' é um processo crítico do Windows e não pode ser removido!"

        # Verifica processos que requerem atenção
        if process_lower in SystemProcessValidator.WARNING_PROCESSES:
            return True, f"⚠️ ATENÇÃO: '{process_name}' é um aplicativo comum. Tem certeza que deseja remover?"

        # Processos desconhecidos também requerem confirmação
        return True, f"✓ Processo pode ser removido (mas use com cautela)"

    @staticmethod
    def validate_process_name(process_name: str) -> tuple[bool, str]:
        """
        Valida o nome do processo.

        Returns:
            Tupla (válido, mensagem_erro)
        """
        if not process_name:
            return False, "Nome do processo não pode estar vazio"

        # Remove .exe se usuário digitou
        process_name = process_name.replace('.exe', '')

        # Verifica caracteres válidos
        import re
        if not re.match(r'^[a-zA-Z0-9_\-\.]+$', process_name):
            return False, "Nome do processo contém caracteres inválidos"

        # Verifica se não é muito curto
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
        # Remove .exe se existir
        process_name = process_name.replace('.exe', '')

        # Valida nome
        valid, error = SystemProcessValidator.validate_process_name(process_name)
        if not valid:
            return False, error

        # Verifica se é seguro
        safe, msg = SystemProcessValidator.is_safe_to_remove(process_name)
        if not safe:
            return False, msg

        # Verifica se já existe
        if any(item.process_name.lower() == process_name.lower() for item in self.custom_items):
            return False, f"Processo '{process_name}' já foi adicionado"

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
