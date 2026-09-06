"""
Janela principal do WinDebloater.
"""
import os
import sys
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QTextEdit,
    QProgressBar, QSplitter, QFrame, QMessageBox, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import BloatwareDatabase, Category, RiskLevel
from core.scanner import BloatwareScanner, DetectedBloatware
from core.remover import BloatwareRemover
from core.restore import BackupManager
from core.custom_bloat import CustomBloatwareManager
from ui.dialogs import ConfirmDialog, RestoreDialog
from ui.custom_dialog import AddCustomProcessDialog


class ScanThread(QThread):
    """Thread para executar scan em background."""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, scanner: BloatwareScanner):
        super().__init__()
        self.scanner = scanner

    def run(self):
        try:
            results = self.scanner.scan()
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class RemoveThread(QThread):
    """Thread that runs the removal in the background."""
    progress = pyqtSignal(int, int, str)
    log = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, remover: BloatwareRemover, items: list):
        super().__init__()
        self.remover = remover
        self.items = items

    def run(self):
        try:
            self.remover.set_progress_callback(lambda c, t, m: self.progress.emit(c, t, m))
            self.remover.set_log_callback(lambda m: self.log.emit(m))
            results = self.remover.remove_detected(self.items)
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Janela principal do aplicativo."""

    def __init__(self):
        super().__init__()

        self.scanner = BloatwareScanner()
        self.remover = BloatwareRemover()
        self.backup_manager = BackupManager()
        self.custom_manager = CustomBloatwareManager()

        self.detected_items: list[DetectedBloatware] = []
        self.selected_items: list[DetectedBloatware] = []

        self._setup_ui()
        self._load_styles()

        # Auto-scan ao iniciar
        QTimer.singleShot(500, self._on_scan)

    def _setup_ui(self):
        self.setWindowTitle("WinDebloater")
        self.setMinimumSize(1000, 700)

        # Widget central
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Header
        header = self._create_header()
        main_layout.addWidget(header)

        # Splitter principal (lista + log)
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Bloatware list
        list_container = self._create_list_section()
        splitter.addWidget(list_container)

        # Log (collapsible)
        log_container = self._create_log_section()
        splitter.addWidget(log_container)

        splitter.setSizes([500, 200])
        main_layout.addWidget(splitter)

        # Footer with progress
        footer = self._create_footer()
        main_layout.addWidget(footer)

    def _create_header(self) -> QWidget:
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)

        # Title and subtitle
        title_layout = QVBoxLayout()

        title = QLabel("WinDebloater")
        title.setObjectName("titleLabel")
        title_layout.addWidget(title)

        subtitle = QLabel("Safely remove Windows bloatware")
        subtitle.setObjectName("subtitleLabel")
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)
        layout.addStretch()

        # RAM economizada
        ram_layout = QVBoxLayout()
        ram_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        ram_title = QLabel("RAM a economizar:")
        ram_title.setStyleSheet("color: #8888aa;")
        ram_layout.addWidget(ram_title)

        self.ram_label = QLabel("0 MB")
        self.ram_label.setObjectName("ramLabel")
        ram_layout.addWidget(self.ram_label)

        layout.addLayout(ram_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.scan_btn = QPushButton("🔍 Scan")
        self.scan_btn.setObjectName("scanButton")
        self.scan_btn.clicked.connect(self._on_scan)
        btn_layout.addWidget(self.scan_btn)

        self.remove_btn = QPushButton("🗑️ Remover")
        self.remove_btn.setObjectName("removeButton")
        self.remove_btn.setEnabled(False)
        self.remove_btn.clicked.connect(self._on_remove)
        btn_layout.addWidget(self.remove_btn)

        self.restore_btn = QPushButton("↩️ Restaurar")
        self.restore_btn.setObjectName("restoreButton")
        self.restore_btn.clicked.connect(self._on_restore)
        btn_layout.addWidget(self.restore_btn)

        self.custom_btn = QPushButton("🎯 Adicionar Processo")
        self.custom_btn.setObjectName("customButton")
        self.custom_btn.setToolTip("Adicionar processo customizado persistente")
        self.custom_btn.clicked.connect(self._on_add_custom)
        btn_layout.addWidget(self.custom_btn)

        layout.addLayout(btn_layout)

        return header

    def _create_list_section(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Quick filters
        filter_layout = QHBoxLayout()

        select_safe_btn = QPushButton("Selecionar Seguros (🟢)")
        select_safe_btn.clicked.connect(self._select_safe)
        filter_layout.addWidget(select_safe_btn)

        select_all_btn = QPushButton("Selecionar Todos")
        select_all_btn.clicked.connect(self._select_all)
        filter_layout.addWidget(select_all_btn)

        deselect_btn = QPushButton("Desmarcar Todos")
        deselect_btn.clicked.connect(self._deselect_all)
        filter_layout.addWidget(deselect_btn)

        filter_layout.addStretch()

        self.count_label = QLabel("0 itens detectados")
        filter_layout.addWidget(self.count_label)

        layout.addLayout(filter_layout)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["", "Name", "Description", "RAM", "Risk"])
        self.tree.setColumnWidth(0, 40)   # Checkbox
        self.tree.setColumnWidth(1, 200)  # Nome
        self.tree.setColumnWidth(2, 350)  # Description
        self.tree.setColumnWidth(3, 80)   # RAM
        self.tree.setColumnWidth(4, 80)   # Risco
        self.tree.itemChanged.connect(self._on_item_changed)
        layout.addWidget(self.tree)

        return container

    def _create_log_section(self) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        log_header = QLabel("📋 Log de Atividades")
        log_header.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        layout.addWidget(log_header)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        layout.addWidget(self.log_text)

        return container

    def _create_footer(self) -> QWidget:
        footer = QWidget()
        layout = QVBoxLayout(footer)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Pronto")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        return footer

    def _load_styles(self):
        """Carrega estilos CSS."""
        style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def _log(self, message: str):
        """Adiciona mensagem ao log."""
        self.log_text.append(message)
        # Auto-scroll
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def _update_status(self, message: str):
        """Atualiza status bar."""
        self.status_label.setText(message)

    def _get_risk_icon(self, risk: RiskLevel) -> str:
        if risk == RiskLevel.SAFE:
            return "🟢"
        elif risk == RiskLevel.CAUTION:
            return "🟡"
        else:
            return "🔴"

    def _populate_tree(self, detected: list[DetectedBloatware]):
        """Fill the tree with the detected items."""
        self.tree.clear()
        self.detected_items = detected

        # Agrupa por categoria
        categories = {}
        for d in detected:
            cat = d.item.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(d)

        # Build the tree items
        for category, items in categories.items():
            # Item pai (categoria)
            cat_item = QTreeWidgetItem(self.tree)
            cat_item.setText(1, f"{category.value} ({len(items)})")
            cat_item.setFont(1, QFont("Segoe UI", 11, QFont.Weight.Bold))
            cat_item.setExpanded(True)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)

            # Itens filhos
            for d in items:
                child = QTreeWidgetItem(cat_item)
                child.setFlags(child.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                child.setCheckState(0, Qt.CheckState.Unchecked)
                child.setText(1, d.item.name)
                child.setText(2, d.item.description[:60] + "..." if len(d.item.description) > 60 else d.item.description)
                child.setText(3, f"{d.ram_usage_mb:.1f} MB" if d.ram_usage_mb > 0 else "-")
                child.setText(4, self._get_risk_icon(d.item.risk_level))
                child.setToolTip(2, d.item.description)
                child.setData(0, Qt.ItemDataRole.UserRole, d)

        self.count_label.setText(f"{len(detected)} itens detectados")

    def _update_selected_ram(self):
        """Atualiza RAM total dos itens selecionados."""
        total_ram = sum(d.ram_usage_mb for d in self.selected_items)
        self.ram_label.setText(f"{total_ram:.1f} MB")
        self.remove_btn.setEnabled(len(self.selected_items) > 0)

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Called when an item is ticked or unticked."""
        if column != 0:
            return

        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data is None:
            return

        if item.checkState(0) == Qt.CheckState.Checked:
            if data not in self.selected_items:
                self.selected_items.append(data)
        else:
            if data in self.selected_items:
                self.selected_items.remove(data)

        self._update_selected_ram()

    def _select_safe(self):
        """Seleciona apenas itens seguros."""
        self._deselect_all()

        def select_recursive(item: QTreeWidgetItem):
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data and data.item.risk_level == RiskLevel.SAFE:
                item.setCheckState(0, Qt.CheckState.Checked)

            for i in range(item.childCount()):
                select_recursive(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            select_recursive(self.tree.topLevelItem(i))

    def _select_all(self):
        """Seleciona todos os itens."""
        def select_recursive(item: QTreeWidgetItem):
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(0, Qt.CheckState.Checked)

            for i in range(item.childCount()):
                select_recursive(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            select_recursive(self.tree.topLevelItem(i))

    def _deselect_all(self):
        """Desmarca todos os itens."""
        self.selected_items.clear()

        def deselect_recursive(item: QTreeWidgetItem):
            if item.flags() & Qt.ItemFlag.ItemIsUserCheckable:
                item.setCheckState(0, Qt.CheckState.Unchecked)

            for i in range(item.childCount()):
                deselect_recursive(item.child(i))

        for i in range(self.tree.topLevelItemCount()):
            deselect_recursive(self.tree.topLevelItem(i))

        self._update_selected_ram()

    def _on_scan(self):
        """Inicia scan de bloatwares."""
        self._log("Iniciando scan...")
        self._update_status("Escaneando...")
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        self.scan_thread = ScanThread(self.scanner)
        self.scan_thread.finished.connect(self._on_scan_finished)
        self.scan_thread.error.connect(self._on_scan_error)
        self.scan_thread.start()

    def _on_scan_finished(self, results: list[DetectedBloatware]):
        """Chamado quando scan termina."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)

        self._populate_tree(results)

        # Auto-seleciona itens seguros
        self._select_safe()

        total_ram = sum(d.ram_usage_mb for d in results)
        self._log(f"✅ Scan completo: {len(results)} bloatwares detectados ({total_ram:.1f} MB)")
        self._update_status(f"Scan completo: {len(results)} itens encontrados")

    def _on_scan_error(self, error: str):
        """Chamado quando scan falha."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)

        self._log(f"❌ Erro no scan: {error}")
        self._update_status("Erro no scan")

        QMessageBox.critical(self, "Erro", f"Erro durante o scan:\n{error}")

    def _on_remove(self):
        """Start removing the selected items."""
        if not self.selected_items:
            return

        # Confirmation dialog
        items_to_remove = [d.item for d in self.selected_items]
        dialog = ConfirmDialog(items_to_remove, self)

        if dialog.exec() and dialog.confirmed:
            self._start_removal()

    def _start_removal(self):
        """Start the removal thread."""
        self._log("\n" + "="*50)
        self._log("Starting removal...")
        self._update_status("Removendo bloatwares...")

        self.scan_btn.setEnabled(False)
        self.remove_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.selected_items))
        self.progress_bar.setValue(0)

        self.remove_thread = RemoveThread(self.remover, self.selected_items)
        self.remove_thread.progress.connect(self._on_remove_progress)
        self.remove_thread.log.connect(self._log)
        self.remove_thread.finished.connect(self._on_remove_finished)
        self.remove_thread.error.connect(self._on_remove_error)
        self.remove_thread.start()

    def _on_remove_progress(self, current: int, total: int, message: str):
        """Update the removal progress."""
        self.progress_bar.setValue(current)
        self._update_status(message)

    def _on_remove_finished(self, results: list):
        """Called when the removal finishes."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)

        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful

        self._log(f"\n✅ Removal complete: {successful} removed, {failed} failed")
        self._update_status(f"Removidos: {successful} | Falharam: {failed}")

        # Show the summary
        if failed > 0:
            QMessageBox.warning(
                self,
                "Removal Complete",
                f"Removidos: {successful}\nFalharam: {failed}\n\n"
                "Verifique o log para detalhes."
            )
        else:
            QMessageBox.information(
                self,
                "Sucesso!",
                f"Todos os {successful} itens foram removidos com sucesso!"
            )

        # Refresh
        self.selected_items.clear()
        self._on_scan()

    def _on_remove_error(self, error: str):
        """Called when the removal fails."""
        self.progress_bar.setVisible(False)
        self.scan_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)

        self._log(f"❌ Removal error: {error}")
        self._update_status("Removal error")

        QMessageBox.critical(self, "Error", f"Error during removal:\n{error}")

    def _on_add_custom(self):
        """Open the dialog for adding a custom process."""
        dialog = AddCustomProcessDialog(self)

        if dialog.exec():
            # The user confirmed
            process = dialog.process_name
            description = dialog.description

            # Add it to the manager
            success, msg = self.custom_manager.add_custom(process, description)

            if success:
                self._log(f"✓ Processo customizado adicionado: {process}")
                QMessageBox.information(self, "Sucesso", msg)

                # Rescan so the process is detected
                self._on_scan()
            else:
                self._log(f"✗ Falha ao adicionar: {msg}")
                QMessageBox.warning(self, "Erro", msg)

    def _on_restore(self):
        """Open the restore dialog."""
        points = self.backup_manager.list_restore_points()

        dialog = RestoreDialog(points, self)
        if dialog.exec() and dialog.selected_point:
            self._log(f"\nRestaurando backup: {dialog.selected_point.name}")
            self._update_status("Restaurando...")

            result = self.backup_manager.restore(dialog.selected_point.id)

            if result['success']:
                self._log(f"✅ {result['message']}")
                QMessageBox.information(self, "Sucesso", result['message'])
            else:
                self._log(f"⚠️ {result['message']}")
                QMessageBox.warning(self, "Aviso", result['message'])

            # Refresh
            self._on_scan()
