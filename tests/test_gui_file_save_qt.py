import os
from PIL import Image
import pytest
from PyQt6.QtWidgets import QWidget

from src.controller.file_saver import FileSaver


def test_export_restored_image_with_qt(monkeypatch, tmp_path, qtbot):
    """`FileSaver.exportRestoredImage` が QFileDialog と連携して画像を保存することを確認する（pytest-qt 使用）"""
    img = Image.new("RGB", (2, 2), color=(10, 20, 30))

    view = QWidget()
    # MainWindowView の期待する属性を最低限揃える
    view._restoredDataImage = img

    saved = tmp_path / "saved.png"

    # QFileDialog.getSaveFileName をモックして確定パスを返す
    monkeypatch.setattr(
        "src.controller.file_saver.QFileDialog.getSaveFileName",
        lambda *args, **kwargs: (str(saved), "PNG Files (*.png)"),
    )

    # QMessageBox の表示を抑制
    monkeypatch.setattr("src.controller.file_saver.QMessageBox.information", lambda *a, **k: None)
    monkeypatch.setattr("src.controller.file_saver.QMessageBox.critical", lambda *a, **k: None)
    monkeypatch.setattr("src.controller.file_saver.QMessageBox.warning", lambda *a, **k: None)

    saver = FileSaver(aView=None)
    saver.exportRestoredImage(view)

    assert saved.exists()
