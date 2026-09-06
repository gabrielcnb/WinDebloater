"""
Backup and restore system, the failsafe.
"""
import os
import sys
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import BloatwareItem
from utils.powershell import PowerShell


@dataclass
class BackupEntry:
    """Entrada de backup para um item."""
    item_id: str
    item_name: str
    timestamp: str
    registry_backup: Dict[str, Any]
    removal_technique: Optional[str]
    can_restore: bool


@dataclass
class RestorePoint:
    """A complete restore point."""
    id: str
    name: str
    timestamp: str
    entries: List[BackupEntry]
    system_restore_id: Optional[str]


class BackupManager:
    """Manages bloatware backups and restores."""

    def __init__(self, backup_dir: str = None):
        if backup_dir is None:
            # Usa pasta do projeto
            self.backup_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                "backups"
            )
        else:
            self.backup_dir = backup_dir

        os.makedirs(self.backup_dir, exist_ok=True)

        self.current_entries: List[BackupEntry] = []

    def _get_timestamp(self) -> str:
        """Retorna timestamp formatado."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _export_registry_key(self, key_path: str) -> Optional[Dict]:
        """Exporta uma chave de registro para dict."""
        # Converte formato de caminho
        key_path = key_path.replace("HKCU\\", "HKCU:\\").replace("HKLM\\", "HKLM:\\")

        command = f"""
        $props = Get-ItemProperty -Path '{key_path}' -ErrorAction SilentlyContinue
        if ($props) {{
            $props | Select-Object * -ExcludeProperty PS* | ConvertTo-Json
        }}
        """
        success, data = PowerShell.get_json(command)

        if success and data:
            return {'path': key_path, 'values': data}
        return None

    def _restore_registry_key(self, backup: Dict) -> bool:
        """Restaura uma chave de registro do backup."""
        if not backup or 'path' not in backup or 'values' not in backup:
            return False

        path = backup['path']
        values = backup['values']

        # Create the key when missing
        PowerShell.run(f"New-Item -Path '{path}' -Force -ErrorAction SilentlyContinue")

        # Restore each value
        for name, value in values.items():
            if isinstance(value, bool):
                value_type = "DWord"
                value = 1 if value else 0
            elif isinstance(value, int):
                value_type = "DWord"
            else:
                value_type = "String"

            command = f"Set-ItemProperty -Path '{path}' -Name '{name}' -Value {value} -Type {value_type} -Force"
            PowerShell.run(command)

        return True

    def backup_item(self, item: BloatwareItem) -> BackupEntry:
        """
        Back up an item before removal.

        Args:
            item: Item de bloatware a fazer backup.

        Returns:
            Entrada de backup criada.
        """
        registry_backup = {}

        # Back up the registry keys
        for key in item.registry_keys:
            exported = self._export_registry_key(key)
            if exported:
                registry_backup[key] = exported

        entry = BackupEntry(
            item_id=item.id,
            item_name=item.name,
            timestamp=self._get_timestamp(),
            registry_backup=registry_backup,
            removal_technique=None,
            can_restore=item.can_reinstall
        )

        self.current_entries.append(entry)
        return entry

    def create_restore_point(self, description: str = "WinDebloater Backup") -> Optional[RestorePoint]:
        """
        Create a complete restore point.

        Args:
            description: Description of the restore point.

        Returns:
            The restore point that was created.
        """
        timestamp = self._get_timestamp()
        point_id = f"restore_{timestamp}"

        # Try creating a Windows restore point
        system_restore_id = None
        command = f"""
        try {{
            Checkpoint-Computer -Description '{description}' -RestorePointType 'MODIFY_SETTINGS' -ErrorAction Stop
            $true
        }} catch {{
            $false
        }}
        """
        success, stdout, _ = PowerShell.run(command, timeout=120)

        if "True" in stdout:
            system_restore_id = timestamp

        # Create a local restore point
        restore_point = RestorePoint(
            id=point_id,
            name=description,
            timestamp=timestamp,
            entries=self.current_entries.copy(),
            system_restore_id=system_restore_id
        )

        # Write it to file
        self._save_restore_point(restore_point)

        # Limpa entradas atuais
        self.current_entries = []

        return restore_point

    def _save_restore_point(self, point: RestorePoint):
        """Write a restore point to a JSON file."""
        filename = f"{point.id}.json"
        filepath = os.path.join(self.backup_dir, filename)

        # Convert to a dict
        data = {
            'id': point.id,
            'name': point.name,
            'timestamp': point.timestamp,
            'entries': [asdict(e) for e in point.entries],
            'system_restore_id': point.system_restore_id
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def list_restore_points(self) -> List[RestorePoint]:
        """List every available restore point."""
        points = []

        for filename in os.listdir(self.backup_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.backup_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    entries = [
                        BackupEntry(**e) for e in data.get('entries', [])
                    ]

                    point = RestorePoint(
                        id=data['id'],
                        name=data['name'],
                        timestamp=data['timestamp'],
                        entries=entries,
                        system_restore_id=data.get('system_restore_id')
                    )
                    points.append(point)
                except Exception:
                    continue

        # Ordena por timestamp (mais recente primeiro)
        points.sort(key=lambda p: p.timestamp, reverse=True)
        return points

    def restore(self, point_id: str) -> Dict[str, Any]:
        """
        Roll back to a restore point.

        Args:
            point_id: ID of the restore point.

        Returns:
            Dict holding the restore results.
        """
        # Encontra o ponto
        points = self.list_restore_points()
        point = None
        for p in points:
            if p.id == point_id:
                point = p
                break

        if not point:
            return {'success': False, 'message': 'Restore point not found'}

        results = {
            'success': True,
            'restored': [],
            'failed': [],
            'message': ''
        }

        # Restore each entry
        for entry in point.entries:
            try:
                # Restore the registry
                for key, backup in entry.registry_backup.items():
                    self._restore_registry_key(backup)

                # Remove the IFEO entry when one was used
                if entry.removal_technique == 'IFEO':
                    ifeo_path = f"HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Image File Execution Options\\{entry.item_id}.exe"
                    PowerShell.run(f"Remove-Item -Path '{ifeo_path}' -Force -ErrorAction SilentlyContinue")

                # Try re-enabling the service where applicable
                command = f"Set-Service -Name '{entry.item_id}' -StartupType Automatic -ErrorAction SilentlyContinue"
                PowerShell.run(command)

                results['restored'].append(entry.item_name)

            except Exception as e:
                results['failed'].append(f"{entry.item_name}: {str(e)}")

        # Define mensagem final
        if results['failed']:
            results['success'] = False
            results['message'] = f"Restaurados: {len(results['restored'])}, Falharam: {len(results['failed'])}"
        else:
            results['message'] = f"Todos os {len(results['restored'])} itens foram restaurados"

        return results

    def delete_restore_point(self, point_id: str) -> bool:
        """Delete a restore point."""
        filename = f"{point_id}.json"
        filepath = os.path.join(self.backup_dir, filename)

        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception:
            pass

        return False

    def get_backup_size(self) -> int:
        """Retorna tamanho total dos backups em bytes."""
        total = 0
        for filename in os.listdir(self.backup_dir):
            filepath = os.path.join(self.backup_dir, filename)
            if os.path.isfile(filepath):
                total += os.path.getsize(filepath)
        return total

    def cleanup_old_backups(self, keep_count: int = 10):
        """Remove backups antigos, mantendo apenas os mais recentes."""
        points = self.list_restore_points()

        if len(points) > keep_count:
            for point in points[keep_count:]:
                self.delete_restore_point(point.id)
