"""
Bloatware remover: persistent, with several techniques.
"""
import time
import sys
import os
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Callable, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import BloatwareItem
from core.scanner import BloatwareScanner, DetectedBloatware
from core.restore import BackupManager
from utils.powershell import PowerShell


class RemovalTechnique(Enum):
    """Removal techniques, ordered by aggressiveness."""
    APPX_USER = "Remove-AppxPackage (current user)"
    APPX_ALL_USERS = "Remove-AppxPackage -AllUsers"
    APPX_PROVISIONED = "Remove-AppxProvisionedPackage"
    STOP_SERVICE = "Stop-Service + Disable"
    STOP_PROCESS = "Stop-Process + Startup"
    SCHEDULED_TASKS = "Disable-ScheduledTask"
    IFEO = "Image File Execution Options"
    RENAME = "Rename the executable"


@dataclass
class RemovalResult:
    """Result of one removal attempt."""
    item: BloatwareItem
    success: bool
    technique_used: Optional[RemovalTechnique]
    message: str
    attempts: int


class BloatwareRemover:
    """Removes bloatware persistently, using several techniques."""

    def __init__(self, backup_manager: Optional[BackupManager] = None):
        self.scanner = BloatwareScanner()
        self.backup = backup_manager or BackupManager()
        self._progress_callback: Optional[Callable] = None
        self._log_callback: Optional[Callable] = None

    def set_progress_callback(self, callback: Callable[[int, int, str], None]):
        """Define callback para progresso (current, total, message)."""
        self._progress_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]):
        """Define callback para log de mensagens."""
        self._log_callback = callback

    def _log(self, message: str):
        """Loga uma mensagem."""
        if self._log_callback:
            self._log_callback(message)

    def _progress(self, current: int, total: int, message: str):
        """Reporta progresso."""
        if self._progress_callback:
            self._progress_callback(current, total, message)

    def _is_still_present(self, item: BloatwareItem) -> bool:
        """Check whether the item is still present on the system."""
        # Check the process
        if item.process_name:
            success, stdout, _ = PowerShell.run(
                f"Get-Process -Name '{item.process_name}' -ErrorAction SilentlyContinue"
            )
            if stdout.strip():
                return True

        # Check the AppX package
        if item.package_name:
            success, stdout, _ = PowerShell.run(
                f"Get-AppxPackage -Name '{item.package_name}' -ErrorAction SilentlyContinue"
            )
            if stdout.strip():
                return True

        # Check the service
        if item.service_name:
            success, stdout, _ = PowerShell.run(
                f"Get-Service -Name '{item.service_name}' -ErrorAction SilentlyContinue | Where-Object {{$_.Status -eq 'Running'}}"
            )
            if stdout.strip():
                return True

        return False

    def _try_appx_user(self, item: BloatwareItem) -> bool:
        """Try removing the AppX package for the current user."""
        if not item.package_name:
            return False

        self._log(f"  Trying Remove-AppxPackage (current user)...")
        success, _ = PowerShell.remove_appx_package(item.package_name, all_users=False)
        time.sleep(0.5)
        return success and not self._is_still_present(item)

    def _try_appx_all_users(self, item: BloatwareItem) -> bool:
        """Try removing the AppX package for all users."""
        if not item.package_name:
            return False

        self._log(f"  Tentando Remove-AppxPackage -AllUsers...")
        success, _ = PowerShell.remove_appx_package(item.package_name, all_users=True)
        time.sleep(0.5)
        return success and not self._is_still_present(item)

    def _try_appx_provisioned(self, item: BloatwareItem) -> bool:
        """Tenta remover pacote provisionado."""
        if not item.package_name:
            return False

        self._log(f"  Tentando Remove-AppxProvisionedPackage...")
        command = f"""
        Get-AppxProvisionedPackage -Online |
        Where-Object {{$_.DisplayName -like '*{item.package_name}*'}} |
        Remove-AppxProvisionedPackage -Online
        """
        success, _, _ = PowerShell.run(command)
        time.sleep(0.5)
        return success

    def _try_stop_service(self, item: BloatwareItem) -> bool:
        """Try stopping and disabling the service."""
        if not item.service_name:
            return False

        self._log(f"  Tentando Stop-Service + Disable...")
        PowerShell.stop_service(item.service_name)
        success, _ = PowerShell.set_service_startup(item.service_name, "Disabled")
        time.sleep(0.5)
        return success and not self._is_still_present(item)

    def _try_stop_process(self, item: BloatwareItem) -> bool:
        """Tenta encerrar processo e remover do startup."""
        if not item.process_name:
            return False

        self._log(f"  Tentando Stop-Process + remover startup...")

        # Encerra processo
        PowerShell.stop_process(item.process_name)

        # Drop it from startup
        for key in item.registry_keys:
            if "Run" in key:
                PowerShell.run(f"Remove-ItemProperty -Path '{key}' -Name '*{item.process_name}*' -ErrorAction SilentlyContinue")

        time.sleep(0.5)
        return not self._is_still_present(item)

    def _try_scheduled_tasks(self, item: BloatwareItem) -> bool:
        """Tenta desativar tarefas agendadas relacionadas."""
        self._log(f"  Tentando desativar tarefas agendadas...")

        search_terms = [item.name, item.process_name, item.package_name]
        search_terms = [t for t in search_terms if t]

        for term in search_terms:
            command = f"""
            Get-ScheduledTask -TaskName '*{term}*' -ErrorAction SilentlyContinue |
            Disable-ScheduledTask -ErrorAction SilentlyContinue
            """
            PowerShell.run(command)

        time.sleep(0.5)
        return not self._is_still_present(item)

    def _try_ifeo(self, item: BloatwareItem) -> bool:
        """Tenta bloquear via IFEO (Image File Execution Options)."""
        if not item.process_name:
            return False

        self._log(f"  Trying IFEO (block the executable)...")

        exe_name = f"{item.process_name}.exe"
        command = f"""
        $path = 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{exe_name}'
        New-Item -Path $path -Force | Out-Null
        Set-ItemProperty -Path $path -Name 'Debugger' -Value 'systray.exe' -Type String -Force
        """
        success, _, _ = PowerShell.run(command)

        # Tenta encerrar o processo novamente
        if success:
            PowerShell.stop_process(item.process_name)
            time.sleep(1)

        return success and not self._is_still_present(item)

    def _try_rename(self, item: BloatwareItem) -> bool:
        """Last resort: rename the executable."""
        if not item.process_name:
            return False

        self._log(f"  Trying to rename the executable (last resort)...")

        # Try to locate and rename the executable
        command = f"""
        $exes = Get-ChildItem -Path "$env:ProgramFiles", "$env:ProgramFiles(x86)", "$env:SystemRoot" -Recurse -Filter "{item.process_name}.exe" -ErrorAction SilentlyContinue | Select-Object -First 3
        foreach ($exe in $exes) {{
            try {{
                Stop-Process -Name '{item.process_name}' -Force -ErrorAction SilentlyContinue
                Rename-Item -Path $exe.FullName -NewName "$($exe.Name).disabled" -Force -ErrorAction SilentlyContinue
            }} catch {{}}
        }}
        """
        success, _, _ = PowerShell.run(command, timeout=30)

        time.sleep(0.5)
        return not self._is_still_present(item)

    def remove_single(self, item: BloatwareItem, create_backup: bool = True) -> RemovalResult:
        """
        Remove a single bloatware item, cascading through the techniques.

        Args:
            item: Item a remover.
            create_backup: Se deve criar backup antes.

        Returns:
            The removal result.
        """
        self._log(f"\n{'='*50}")
        self._log(f"Removendo: {item.name}")
        self._log(f"{'='*50}")

        # Take a backup when asked
        if create_backup:
            self._log("Criando backup...")
            self.backup.backup_item(item)

        # Techniques to try, in order
        techniques = [
            (RemovalTechnique.APPX_USER, self._try_appx_user),
            (RemovalTechnique.APPX_ALL_USERS, self._try_appx_all_users),
            (RemovalTechnique.APPX_PROVISIONED, self._try_appx_provisioned),
            (RemovalTechnique.STOP_SERVICE, self._try_stop_service),
            (RemovalTechnique.STOP_PROCESS, self._try_stop_process),
            (RemovalTechnique.SCHEDULED_TASKS, self._try_scheduled_tasks),
            (RemovalTechnique.IFEO, self._try_ifeo),
            (RemovalTechnique.RENAME, self._try_rename),
        ]

        attempts = 0
        for technique, method in techniques:
            attempts += 1

            try:
                if method(item):
                    self._log(f"✓ Sucesso com: {technique.value}")
                    return RemovalResult(
                        item=item,
                        success=True,
                        technique_used=technique,
                        message=f"Removido com {technique.value}",
                        attempts=attempts
                    )
            except Exception as e:
                self._log(f"  Erro: {str(e)}")

        # Nothing worked
        self._log(f"✗ Failed: every technique failed")
        return RemovalResult(
            item=item,
            success=False,
            technique_used=None,
            message="Every technique failed",
            attempts=attempts
        )

    def remove_multiple(self, items: List[BloatwareItem], create_backup: bool = True) -> List[RemovalResult]:
        """
        Remove several bloatware items.

        Args:
            items: Lista de itens a remover.
            create_backup: Se deve criar backup antes.

        Returns:
            Lista de resultados.
        """
        results = []
        total = len(items)

        # Take an overall backup
        if create_backup:
            self._log("Creating an overall backup before removal...")
            self.backup.create_restore_point(f"WinDebloater - Removendo {total} itens")

        for i, item in enumerate(items, 1):
            self._progress(i, total, f"Removendo {item.name}...")
            result = self.remove_single(item, create_backup=False)  # the overall backup is already done
            results.append(result)

        # Resumo
        successful = sum(1 for r in results if r.success)
        failed = total - successful

        self._log(f"\n{'='*50}")
        self._log(f"RESUMO")
        self._log(f"{'='*50}")
        self._log(f"Removidos com sucesso: {successful}/{total}")
        if failed > 0:
            self._log(f"Falharam: {failed}/{total}")

        return results

    def remove_detected(self, detected: List[DetectedBloatware], create_backup: bool = True) -> List[RemovalResult]:
        """Remove itens detectados pelo scanner."""
        items = [d.item for d in detected]
        return self.remove_multiple(items, create_backup)
