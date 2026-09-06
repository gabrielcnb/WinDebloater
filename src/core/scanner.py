"""
Scanner para detectar bloatware instalado no sistema.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import sys
import os

# Adjust the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import BloatwareDatabase, BloatwareItem, Category
from utils.powershell import PowerShell


@dataclass
class DetectedBloatware:
    """Representa um bloatware detectado no sistema."""
    item: BloatwareItem           # Item do database
    is_installed: bool            # Whether it is installed
    ram_usage_mb: float           # Uso de RAM em MB (se processo ativo)
    process_id: Optional[int]     # PID se estiver rodando
    status: str                   # "installed", "running", "service_active"


class BloatwareScanner:
    """Scanner para detectar bloatwares no sistema."""

    def __init__(self):
        self.database = BloatwareDatabase()
        self._installed_packages: List[Dict] = []
        self._running_processes: List[Dict] = []
        self._services: List[Dict] = []
        self._startup_items: List[Dict] = []

    def refresh_system_data(self) -> None:
        """Refresh system data (packages, processes, services)."""
        self._installed_packages = PowerShell.get_appx_packages()
        self._running_processes = PowerShell.get_processes()
        self._services = PowerShell.get_services()
        self._startup_items = PowerShell.get_startup_items()

    def _is_package_installed(self, package_name: str) -> bool:
        """Check whether an AppX package is installed."""
        if not package_name:
            return False

        for pkg in self._installed_packages:
            if package_name.lower() in pkg.get('Name', '').lower():
                return True
        return False

    def _get_process_info(self, process_name: str) -> Optional[Dict]:
        """Return information about a running process."""
        if not process_name:
            return None

        for proc in self._running_processes:
            if proc.get('Name', '').lower() == process_name.lower():
                return proc
        return None

    def _is_service_active(self, service_name: str) -> bool:
        """Check whether a service is active."""
        if not service_name:
            return False

        for svc in self._services:
            if svc.get('Name', '').lower() == service_name.lower():
                status = svc.get('Status', '')
                # Status pode ser int (4=Running) ou string
                if isinstance(status, int):
                    return status == 4
                return status.lower() == 'running'
        return False

    def _get_service_startup_type(self, service_name: str) -> Optional[str]:
        """Return a service's startup type."""
        if not service_name:
            return None

        for svc in self._services:
            if svc.get('Name', '').lower() == service_name.lower():
                return svc.get('StartType', '')
        return None

    def scan(self, refresh: bool = True) -> List[DetectedBloatware]:
        """
        Escaneia o sistema em busca de bloatwares.

        Args:
            refresh: Se deve atualizar dados do sistema antes de escanear.

        Returns:
            Lista de bloatwares detectados.
        """
        if refresh:
            self.refresh_system_data()

        detected = []

        for item in self.database.get_all():
            is_installed = False
            ram_usage = 0.0
            process_id = None
            status = "not_found"

            # Check the AppX package
            if item.package_name:
                if self._is_package_installed(item.package_name):
                    is_installed = True
                    status = "installed"

            # Check for a running process
            if item.process_name:
                proc_info = self._get_process_info(item.process_name)
                if proc_info:
                    is_installed = True
                    ram_usage = proc_info.get('RAM_MB', 0)
                    process_id = proc_info.get('Id')
                    status = "running"

            # Check the service
            if item.service_name:
                if self._is_service_active(item.service_name):
                    is_installed = True
                    status = "service_active"
                else:
                    # A disabled service does not count as "installed",
                    # since it has already been handled
                    startup_type = self._get_service_startup_type(item.service_name)
                    if startup_type:
                        startup_str = str(startup_type).lower()
                        if startup_str not in ['disabled', '4']:
                            is_installed = True
                            if status == "not_found":
                                status = "service_stopped"

            # Only add it when installed/active
            if is_installed:
                detected.append(DetectedBloatware(
                    item=item,
                    is_installed=is_installed,
                    ram_usage_mb=ram_usage,
                    process_id=process_id,
                    status=status
                ))

        return detected

    def scan_by_category(self, category: Category) -> List[DetectedBloatware]:
        """Scan a single category."""
        all_detected = self.scan(refresh=True)
        return [d for d in all_detected if d.item.category == category]

    def get_total_ram_usage(self, detected: List[DetectedBloatware]) -> float:
        """Calcula uso total de RAM dos bloatwares detectados."""
        return sum(d.ram_usage_mb for d in detected)

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do scan."""
        detected = self.scan(refresh=True)

        summary = {
            'total_detected': len(detected),
            'total_ram_mb': self.get_total_ram_usage(detected),
            'by_category': {},
            'by_risk': {
                'safe': 0,
                'caution': 0,
                'risky': 0
            },
            'running_processes': 0,
            'active_services': 0
        }

        for d in detected:
            # Por categoria
            cat_name = d.item.category.value
            if cat_name not in summary['by_category']:
                summary['by_category'][cat_name] = 0
            summary['by_category'][cat_name] += 1

            # Por risco
            risk = d.item.risk_level.value
            summary['by_risk'][risk] += 1

            # Contadores
            if d.status == 'running':
                summary['running_processes'] += 1
            elif d.status == 'service_active':
                summary['active_services'] += 1

        return summary

    def quick_scan(self) -> List[DetectedBloatware]:
        """Quick scan: running processes only."""
        self._running_processes = PowerShell.get_processes()

        detected = []
        for item in self.database.get_all():
            if item.process_name:
                proc_info = self._get_process_info(item.process_name)
                if proc_info:
                    detected.append(DetectedBloatware(
                        item=item,
                        is_installed=True,
                        ram_usage_mb=proc_info.get('RAM_MB', 0),
                        process_id=proc_info.get('Id'),
                        status="running"
                    ))

        return detected
