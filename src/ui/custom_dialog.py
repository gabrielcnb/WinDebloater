"""
Diálogo para adicionar processos customizados.
"""
import sys
import os
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.custom_bloat import SystemProcessValidator


class AddCustomProcessDialog(QDialog):
    """Diálogo para adicionar processo customizado."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.process_name = ""
        self.description = ""
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Adicionar Processo Customizado")
        self.setMinimumSize(600, 450)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Título
        title = QLabel("🎯 Adicionar Processo Persistente")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        # Descrição
        desc = QLabel(
            "Use esta função para adicionar processos que continuam voltando mesmo após remoção.\n"
            "O WinDebloater aplicará todas as técnicas de remoção persistente."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #8888aa;")
        layout.addWidget(desc)

        # Aviso de segurança
        warning = QLabel(
            "⚠️ ATENÇÃO: Processos críticos do Windows são bloqueados automaticamente "
            "para sua segurança."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(
            "background-color: #3a2f00; color: #ffa500; padding: 10px; "
            "border-radius: 5px; font-weight: bold;"
        )
        layout.addWidget(warning)

        # Nome do processo
        process_label = QLabel("Nome do Processo:")
        process_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(process_label)

        self.process_input = QLineEdit()
        self.process_input.setPlaceholderText("Ex: msedgewebview2 (sem .exe)")
        self.process_input.textChanged.connect(self._on_process_changed)
        layout.addWidget(self.process_input)

        # Status de validação
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        layout.addWidget(self.validation_label)

        # Descrição opcional
        desc_label = QLabel("Descrição (opcional):")
        desc_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText(
            "Ex: Componente do Edge que fica reiniciando"
        )
        self.desc_input.setMaximumHeight(80)
        layout.addWidget(self.desc_input)

        # Info sobre técnicas
        info = QLabel(
            "Técnicas que serão aplicadas:\n"
            "  • Encerrar processo\n"
            "  • Remover do startup\n"
            "  • IFEO (Image File Execution Options)\n"
            "  • Bloquear reinício automático"
        )
        info.setStyleSheet("color: #6a9fb5; padding: 10px; background: #1a2a3a; border-radius: 5px;")
        layout.addWidget(info)

        layout.addStretch()

        # Botões
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        btn_layout.addStretch()

        self.add_btn = QPushButton("Adicionar Processo")
        self.add_btn.setObjectName("removeButton")
        self.add_btn.setEnabled(False)
        self.add_btn.clicked.connect(self._on_add)
        btn_layout.addWidget(self.add_btn)

        layout.addLayout(btn_layout)

    def _on_process_changed(self, text: str):
        """Valida o processo em tempo real."""
        if not text:
            self.validation_label.setText("")
            self.add_btn.setEnabled(False)
            return

        # Remove .exe se usuário digitou
        text = text.replace('.exe', '')

        # Valida nome
        valid, error = SystemProcessValidator.validate_process_name(text)
        if not valid:
            self.validation_label.setText(f"❌ {error}")
            self.validation_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.add_btn.setEnabled(False)
            return

        # Verifica se é seguro
        safe, msg = SystemProcessValidator.is_safe_to_remove(text)
        if not safe:
            self.validation_label.setText(msg)
            self.validation_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            self.add_btn.setEnabled(False)
            return

        # Tudo OK
        self.validation_label.setText(msg)
        if "ATENÇÃO" in msg:
            self.validation_label.setStyleSheet("color: #ffa500; font-weight: bold;")
        else:
            self.validation_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.add_btn.setEnabled(True)

    def _on_add(self):
        """Adiciona o processo."""
        process = self.process_input.text().strip().replace('.exe', '')
        desc = self.desc_input.toPlainText().strip()

        if not process:
            return

        # Confirmação final
        reply = QMessageBox.question(
            self,
            "Confirmar Adição",
            f"Adicionar o processo '{process}' à lista de remoção?\n\n"
            "O WinDebloater tentará remover este processo usando todas as "
            "técnicas de persistência disponíveis.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.process_name = process
            self.description = desc or f"Processo customizado: {process}"
            self.accept()
