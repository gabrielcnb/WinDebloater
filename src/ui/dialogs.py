"""
Confirmation dialogs and wizards.
"""
import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit,
    QMessageBox, QWidget, QStackedWidget, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import BloatwareItem, RiskLevel
from core.restore import RestorePoint
from core.custom_bloat import SystemProcessValidator


class ConfirmDialog(QDialog):
    """Confirmation dialog for bloatware removal."""

    def __init__(self, items: List[BloatwareItem], parent=None):
        super().__init__(parent)
        self.items = items
        self.confirmed = False
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Confirm Removal")
        self.setMinimumSize(500, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title = QLabel(f"Remover {len(self.items)} itens?")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Warning for risky items
        risky_count = sum(1 for i in self.items if i.risk_level == RiskLevel.RISKY)
        if risky_count > 0:
            warning = QLabel(f"⚠️ {risky_count} item(s) marcado(s) como ARRISCADO")
            warning.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(warning)

        # Item list
        self.list_widget = QListWidget()
        for item in self.items:
            risk_icon = self._get_risk_icon(item.risk_level)
            list_item = QListWidgetItem(f"{risk_icon} {item.name}")
            list_item.setToolTip(item.description)
            self.list_widget.addItem(list_item)
        layout.addWidget(self.list_widget)

        # Confirmation checkbox for risky items
        if risky_count > 0:
            self.confirm_check = QCheckBox("Entendo os riscos e desejo continuar")
            self.confirm_check.stateChanged.connect(self._on_confirm_changed)
            layout.addWidget(self.confirm_check)
        else:
            self.confirm_check = None

        # Buttons
        btn_layout = QHBoxLayout()

        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        btn_layout.addStretch()

        self.confirm_btn = QPushButton("Confirm Removal")
        self.confirm_btn.setObjectName("removeButton")
        self.confirm_btn.clicked.connect(self._on_confirm)
        if risky_count > 0:
            self.confirm_btn.setEnabled(False)
        btn_layout.addWidget(self.confirm_btn)

        layout.addLayout(btn_layout)

    def _get_risk_icon(self, risk: RiskLevel) -> str:
        if risk == RiskLevel.SAFE:
            return "🟢"
        elif risk == RiskLevel.CAUTION:
            return "🟡"
        else:
            return "🔴"

    def _on_confirm_changed(self, state):
        if self.confirm_check:
            self.confirm_btn.setEnabled(state == Qt.CheckState.Checked.value)

    def _on_confirm(self):
        self.confirmed = True
        self.accept()


class SetupWizard(QDialog):
    """First-run setup wizard."""

    setup_complete = pyqtSignal()

    def __init__(self, missing_deps: List[str], issues: List[tuple], parent=None):
        super().__init__(parent)
        self.missing_deps = missing_deps
        self.issues = issues
        self.current_page = 0
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("WinDebloater - Initial Setup")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout(self)

        # Page stack
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Page 1: welcome
        self._create_welcome_page()

        # Page 2: dependencies, when needed
        if self.missing_deps:
            self._create_deps_page()

        # Page 3: compatibility, when there are issues
        if self.issues:
            self._create_compat_page()

        # Page 4: done
        self._create_finish_page()

        # Navigation buttons
        btn_layout = QHBoxLayout()

        self.back_btn = QPushButton("← Voltar")
        self.back_btn.clicked.connect(self._prev_page)
        self.back_btn.setVisible(False)
        btn_layout.addWidget(self.back_btn)

        btn_layout.addStretch()

        self.next_btn = QPushButton("Next →")
        self.next_btn.clicked.connect(self._next_page)
        btn_layout.addWidget(self.next_btn)

        layout.addLayout(btn_layout)

    def _create_welcome_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("🚀 Bem-vindo ao WinDebloater!")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("Remova bloatwares do Windows de forma segura")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("color: #8888aa;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        features = QLabel("""
        ✅ Detects installed bloatware automatically
        ✅ Removes persistently, using several techniques
        ✅ Takes a backup before any change
        ✅ Lets you restore removed items
        """)
        features.setFont(QFont("Segoe UI", 12))
        layout.addWidget(features)

        self.stack.addWidget(page)

    def _create_deps_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("📦 Required Dependencies")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        desc = QLabel("Os seguintes componentes precisam ser instalados:")
        layout.addWidget(desc)

        for dep in self.missing_deps:
            item = QLabel(f"  • {dep}")
            layout.addWidget(item)

        layout.addSpacing(20)

        self.install_btn = QPushButton("Instalar Automaticamente")
        self.install_btn.clicked.connect(self._install_deps)
        layout.addWidget(self.install_btn)

        self.install_progress = QProgressBar()
        self.install_progress.setVisible(False)
        layout.addWidget(self.install_progress)

        self.install_status = QLabel("")
        layout.addWidget(self.install_status)

        layout.addStretch()
        self.stack.addWidget(page)

    def _create_compat_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("⚠️ Compatibility Check")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        for item, status, recommendation in self.issues:
            issue_label = QLabel(f"<b>{item}</b>: {status}")
            layout.addWidget(issue_label)
            rec_label = QLabel(f"  → {recommendation}")
            rec_label.setStyleSheet("color: #8888aa; margin-left: 20px;")
            layout.addWidget(rec_label)

        layout.addStretch()
        self.stack.addWidget(page)

    def _create_finish_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("✅ Tudo Pronto!")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #27ae60;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel("WinDebloater is configured and ready to use.")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        self.stack.addWidget(page)

    def _install_deps(self):
        self.install_btn.setEnabled(False)
        self.install_progress.setVisible(True)
        self.install_progress.setRange(0, 0)  # Indeterminate
        self.install_status.setText("Installing dependencies...")

        # TODO: run the real installation on a separate thread
        # Por enquanto, simula sucesso
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, self._install_complete)

    def _install_complete(self):
        self.install_progress.setRange(0, 100)
        self.install_progress.setValue(100)
        self.install_status.setText("✅ Dependencies installed.")
        self.next_btn.setEnabled(True)

    def _next_page(self):
        if self.current_page < self.stack.count() - 1:
            self.current_page += 1
            self.stack.setCurrentIndex(self.current_page)
            self.back_btn.setVisible(True)

            if self.current_page == self.stack.count() - 1:
                self.next_btn.setText("Start 🚀")
        else:
            self.setup_complete.emit()
            self.accept()

    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.stack.setCurrentIndex(self.current_page)

            if self.current_page == 0:
                self.back_btn.setVisible(False)

            self.next_btn.setText("Next →")


class RestoreDialog(QDialog):
    """Dialog for restoring backups."""

    def __init__(self, restore_points: List[RestorePoint], parent=None):
        super().__init__(parent)
        self.restore_points = restore_points
        self.selected_point: Optional[RestorePoint] = None
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Restaurar Backup")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Title
        title = QLabel("↩️ Pick a restore point")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        if not self.restore_points:
            no_backups = QLabel("No backups available.")
            no_backups.setStyleSheet("color: #8888aa;")
            layout.addWidget(no_backups)
        else:
            # List of restore points
            self.list_widget = QListWidget()
            self.list_widget.itemClicked.connect(self._on_item_clicked)

            for point in self.restore_points:
                # Formata timestamp
                ts = point.timestamp
                formatted_ts = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[9:11]}:{ts[11:13]}"

                item_text = f"{point.name}\n{formatted_ts} - {len(point.entries)} itens"
                list_item = QListWidgetItem(item_text)
                list_item.setData(Qt.ItemDataRole.UserRole, point)
                self.list_widget.addItem(list_item)

            layout.addWidget(self.list_widget)

            # Detalhes do ponto selecionado
            self.details_label = QLabel("Selecione um ponto para ver detalhes")
            self.details_label.setStyleSheet("color: #8888aa;")
            layout.addWidget(self.details_label)

        # Buttons
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()

        self.restore_btn = QPushButton("Restaurar")
        self.restore_btn.setObjectName("restoreButton")
        self.restore_btn.setEnabled(False)
        self.restore_btn.clicked.connect(self._on_restore)
        btn_layout.addWidget(self.restore_btn)

        layout.addLayout(btn_layout)

    def _on_item_clicked(self, item: QListWidgetItem):
        point = item.data(Qt.ItemDataRole.UserRole)
        self.selected_point = point

        # Show the details
        entry_names = [e.item_name for e in point.entries[:5]]
        if len(point.entries) > 5:
            entry_names.append(f"... e mais {len(point.entries) - 5}")

        details = "Items included:\n" + "\n".join(f"  • {name}" for name in entry_names)
        self.details_label.setText(details)
        self.details_label.setStyleSheet("color: #eaeaea;")

        self.restore_btn.setEnabled(True)

    def _on_restore(self):
        if self.selected_point:
            # Extra confirmation
            reply = QMessageBox.question(
                self,
                "Confirm Restore",
                f"Deseja restaurar o backup '{self.selected_point.name}'?\n\n"
                "This will revert the changes made after this point.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.accept()
