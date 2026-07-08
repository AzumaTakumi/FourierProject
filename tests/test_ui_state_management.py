import numpy as np
import pytest
from PyQt6.QtWidgets import QWidget

from src.controller.file_controller import FileLoader
from src.model.fourier_model_context import FourierModelContext
from src.view.edit_dialog_1d_view import EditDialogView1d
from src.view.edit_dialog_view_2d import EditDialogView2d
from src.view.main_window_view import MainWindowView


class _SpectrumWidgetStub(QWidget):
    def __init__(self):
        super().__init__()
        self._displayImage = None
        self._powerSpectrum = None
        self._displayValueRange = None

    def setMinimumSize(self, *args, **kwargs):
        pass

    def setSizePolicy(self, *args, **kwargs):
        pass

    def setScaledContents(self, *args, **kwargs):
        pass

    def addMousePressEventListener(self, *args, **kwargs):
        pass

    def addMouseMoveEventListener(self, *args, **kwargs):
        pass

    def addMouseReleaseEventListener(self, *args, **kwargs):
        pass

    def renderAll(self, *args, **kwargs):
        pass

    def renderDirtyRegion(self, *args, **kwargs):
        pass


def test_undo_then_new_edit_clears_redo_stack():
    """Undoした後に別の編集を行うと、Redo履歴が破棄されることを確認する"""
    context = FourierModelContext(lambda _change: None)
    context.set1dSourceData(np.array([0.0, 1.0, 0.0, -1.0], dtype=float))

    context.editSpectrumValueAtIndex(1, 2.0, 0.0)
    assert context.getUndoCount() == 1

    assert context.undo() is True
    assert context.getRedoCount() == 1

    context.editSpectrumValueAtIndex(2, -3.0, 0.0)
    assert context.getRedoCount() == 0

    with pytest.raises(IndexError):
        context.redo()


def test_1d_and_2d_windows_share_the_same_model_context(qtbot):
    """1D/2D編集ウィンドウが同じModelContextを共有し、同じモデル状態を参照することを確認する"""
    context = FourierModelContext(lambda _change: None)
    context.set1dSourceData(np.array([0.1, 0.2, 0.3, 0.4], dtype=float))

    dialog_1d = EditDialogView1d(modelContext=context, spectrum_component=_SpectrumWidgetStub())
    dialog_2d = EditDialogView2d(modelContext=context, spectrumComponent=_SpectrumWidgetStub())
    qtbot.addWidget(dialog_1d)
    qtbot.addWidget(dialog_2d)

    assert dialog_1d.modelContext is context
    assert dialog_2d.modelContext is context
    assert dialog_1d.modelContext.currentModel is dialog_2d.modelContext.currentModel

    context.editSpectrumValueAtIndex(0, 0.5, 0.0)
    assert dialog_1d.modelContext.currentModel.interactiveRealPart[0] == 0.5
    assert dialog_2d.modelContext.currentModel.interactiveRealPart[0] == 0.5


def test_main_window_and_edit_dialog_share_model_state(qtbot):
    """メインウィンドウと編集ダイアログが同じモデル状態を参照して更新できることを確認する"""
    context = FourierModelContext(lambda _change: None)
    context.set2dSourceData(np.arange(9, dtype=float).reshape(3, 3))

    window = MainWindowView()
    qtbot.addWidget(window)
    window.display(context.currentModel)

    dialog = EditDialogView2d(modelContext=context, spectrumComponent=_SpectrumWidgetStub())
    qtbot.addWidget(dialog)

    context.beginSpectrumEdit()
    context.paintRgbSpectrumAtPositions([(0, 0)], radius=0, rgbColor=[0.4, 0.2, 0.1])
    context.endSpectrumEdit()

    assert dialog.modelContext.currentModel is context.currentModel
    assert window._restoredDataImage is not None
    assert dialog.modelContext.currentModel.interactiveRealPart.shape == (3, 3, 3)


def test_loading_file_while_editing_replaces_current_model(tmp_path):
    """編集中でもファイル読み込みを行うと、現在のモデルが置換されることを確認する"""
    path = tmp_path / "signal.txt"
    np.savetxt(path, np.array([1.0, 2.0, 3.0], dtype=float))

    loader = FileLoader(aView=None)
    loader.model.set1dSourceData(np.array([9.0, 9.0], dtype=float))

    loader.loadSignalData(str(path))

    assert loader.model.is1dModel()
    assert loader.model.currentModel.sourceData.shape == (3,)
    assert np.allclose(loader.model.currentModel.sourceData, np.array([1.0, 2.0, 3.0]))


def test_closing_dirty_dialog_still_closes(qtbot):
    """未保存状態のダイアログでも、閉じる操作で通常どおり閉じることを確認する"""
    dialog = EditDialogView2d(modelContext=None, spectrumComponent=_SpectrumWidgetStub())
    qtbot.addWidget(dialog)

    dialog.isDirty = True
    dialog.close()

    assert not dialog.isVisible()
