"""Teste rápido do scanner (sem GUI)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'src')

from core.scanner import BloatwareScanner
from core.database import RiskLevel

print("="*60)
print("WinDebloater - Teste do Scanner")
print("="*60)

scanner = BloatwareScanner()
print("\nEscaneando sistema...")

detected = scanner.scan()

print(f"\n{len(detected)} bloatwares detectados:\n")

for d in detected:
    risk = "[SAFE]" if d.item.risk_level == RiskLevel.SAFE else "[WARN]" if d.item.risk_level == RiskLevel.CAUTION else "[RISK]"
    ram = f"{d.ram_usage_mb:.1f} MB" if d.ram_usage_mb > 0 else "-"
    print(f"  {risk} {d.item.name:<30} | RAM: {ram:<10} | Status: {d.status}")

summary = scanner.get_summary()
print(f"\n{'='*60}")
print(f"RESUMO:")
print(f"  Total detectados: {summary['total_detected']}")
print(f"  RAM total: {summary['total_ram_mb']:.1f} MB")
print(f"  Seguros: {summary['by_risk']['safe']}")
print(f"  Com cautela: {summary['by_risk']['caution']}")
print(f"  Arriscados: {summary['by_risk']['risky']}")
print("="*60)
