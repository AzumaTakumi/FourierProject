from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image
from PyQt6.QtCore import Qt

from src.model.pane_type import PaneType
from src.model.spectrum_1_d_change import Spectrum1dChange
from src.model.spectrum_2_d_change import Spectrum2dChange
from src.view.edit_dialog_1d_view import EditDialogView1d
from src.view.edit_dialog_view_2d import EditDialogView2d
from src.view.interactive_spectrum_component import (
    Interactive1dSpectrumComponent,
    Interactive2dSpectrumComponent,
)
from src.view.main_window_view import MainWindowView


class FakePosition:
    def __init__(self, x, y):
        self._x = x
        self._y = y

    def x(self):
        return self._x

    def y(self):
        return self._y


class FakeMouseEvent:
    def __init__(self, x, y, button, buttons=None):
        self._position = FakePosition(x, y)
        self._button = button
        self._buttons = button if buttons is None else buttons

    def position(self):
        return self._position

    def button(self):
        return self._button

    def buttons(self):
        return self._buttons


def testInteractive1dRenderAllStoresCopyAndDisplaysImage(qtbot):
    """1D全体描画が入力をコピーし、表示画像とPixmapを作ることを確認する。"""
    component = Interactive1dSpectrumComponent()
    qtbot.addWidget(component)
    spectrum = np.array([1.0, 2.0, 3.0, 4.0])

    component.renderAll(spectrum)
    spectrum[0] = 999.0

    assert np.array_equal(component._powerSpectrum, [1.0, 2.0, 3.0, 4.0])
    assert component._displayImage is not None
    assert component.pixmap() is not None
    assert not component.pixmap().isNull()


def testInteractive1dRenderDirtyRegionUpdatesOnlyTargetRange(qtbot):
    """1D部分描画が指定インデックスの範囲だけを更新することを確認する。"""
    component = Interactive1dSpectrumComponent()
    qtbot.addWidget(component)
    component.renderAll(np.zeros(5))
    change = Spectrum1dChange(
        index=1,
        changedPowerSpectrum=np.array([7.0, 8.0]),
    )

    component.renderDirtyRegion(change)

    assert np.array_equal(component._powerSpectrum, [0.0, 7.0, 8.0, 0.0, 0.0])
    assert component._displayImage is not None


def testInteractive2dRenderAllCopiesDataAndSetsDisplayRange(qtbot):
    """2D全体描画が表示レンジを計算し、画像を生成することを確認する。"""
    component = Interactive2dSpectrumComponent()
    qtbot.addWidget(component)
    spectrum = np.arange(16, dtype=float).reshape(4, 4)

    component.renderAll(spectrum)
    spectrum[0, 0] = 999.0

    assert component._powerSpectrum[0, 0] == 0.0
    assert component._displayValueRange is not None
    assert component._displayRangeShape == (4, 4)
    assert component._displayImage.size == (4, 4)


def testInteractive2dRenderDirtyRegionUpdatesOnlyRectangle(qtbot):
    """2D部分描画が指定矩形だけを更新し、表示レンジを維持することを確認する。"""
    component = Interactive2dSpectrumComponent()
    qtbot.addWidget(component)
    component.renderAll(np.zeros((4, 4), dtype=float))
    initialRange = component._displayValueRange
    change = Spectrum2dChange(
        x=1,
        y=1,
        width=2,
        height=2,
        changedPowerSpectrum=np.full((2, 2), 9.0),
    )

    component.renderDirtyRegion(change)

    expected = np.zeros((4, 4), dtype=float)
    expected[1:3, 1:3] = 9.0
    assert np.array_equal(component._powerSpectrum, expected)
    assert component._displayValueRange == initialRange
    assert component.pixmap() is not None


@pytest.mark.parametrize(
    ("componentClass", "addMethod", "eventMethod"),
    [
        (Interactive1dSpectrumComponent, "addMouseMoveEventListener", "mouseMoveEvent"),
        (Interactive1dSpectrumComponent, "addMousePressEventListener", "mousePressEvent"),
        (Interactive1dSpectrumComponent, "addMouseReleaseEventListener", "mouseReleaseEvent"),
        (Interactive2dSpectrumComponent, "addMouseMoveEventListener", "mouseMoveEvent"),
        (Interactive2dSpectrumComponent, "addMousePressEventListener", "mousePressEvent"),
        (Interactive2dSpectrumComponent, "addMouseReleaseEventListener", "mouseReleaseEvent"),
    ],
)
def testInteractiveComponentNotifiesRegisteredMouseListener(
    qtbot, componentClass, addMethod, eventMethod
):
    """登録したマウスリスナーへ同じイベントを通知することを確認する。"""
    component = componentClass()
    qtbot.addWidget(component)
    received = []
    event = object()
    getattr(component, addMethod)(received.append)

    getattr(component, eventMethod)(event)

    assert received == [event]


def testMainWindowDisplayPopulatesAllFourPanes(qtbot):
    """MainWindowViewがモデルの4領域を保持・描画することを確認する。"""
    view = MainWindowView()
    qtbot.addWidget(view)
    component = Interactive1dSpectrumComponent()
    source = Image.new("RGB", (8, 6), color=(10, 20, 30))
    power = Image.new("L", (8, 6), color=80)
    inverse = Image.new("RGB", (8, 6), color=(30, 20, 10))
    interactive = np.array([1.0, 2.0, 3.0, 4.0])
    model = SimpleNamespace(
        getImage=lambda: {
            PaneType.SOURCE_DATA: source,
            PaneType.POWER_SPECTRUM: power,
            PaneType.INVERSE_DATA: inverse,
        },
        getData=lambda: {PaneType.INTERACTIVE_POWER_SPECTRUM: interactive},
        getSpectrumComponent=lambda: component,
    )

    view.display(model)
    qtbot.wait(20)

    assert view._originalData is source
    assert view._originalSpectrum is power
    assert view._restoredDataImage is inverse
    assert view.getSpectrumComponent() is component
    assert np.array_equal(component._powerSpectrum, interactive)
    assert view._originalDataLabel.pixmap() is not None
    assert view._originalSpectrumLabel.pixmap() is not None
    assert view._restoredDataImageLabel.pixmap() is not None


def testMainWindowContextMenuEventDelegatesGlobalPosition(qtbot):
    """右クリックイベントのグローバル座標をControllerへ渡すことを確認する。"""
    view = MainWindowView()
    qtbot.addWidget(view)
    positions = []
    view.setContextMenuController(
        SimpleNamespace(showContextMenu=positions.append)
    )
    position = object()
    event = SimpleNamespace(globalPos=lambda: position)

    view.contextMenuEvent(event)

    assert positions == [position]


def testMainWindowUpdateRestoredImageRefreshesView(qtbot, monkeypatch):
    """復元画像を差し替えた直後に再描画することを確認する。"""
    view = MainWindowView()
    qtbot.addWidget(view)
    refreshCalls = []
    monkeypatch.setattr(view, "_refreshImages", lambda: refreshCalls.append(True))
    image = Image.new("RGB", (3, 3), color=(1, 2, 3))

    view.updateRestoredDataImage(image)

    assert view._restoredDataImage is image
    assert refreshCalls == [True]


def testEditDialog1dMapsWidgetEdgesToSpectrumEdges(qtbot):
    """1D表示領域の左右端をスペクトルの先頭・末尾へ変換することを確認する。"""
    component = Interactive1dSpectrumComponent()
    component.renderAll(np.arange(8, dtype=float))
    dialog = EditDialogView1d(spectrumComponent=component)
    qtbot.addWidget(dialog)
    component.resize(650, 480)

    left = FakeMouseEvent(0, 10, Qt.MouseButton.LeftButton)
    right = FakeMouseEvent(component.width(), 10, Qt.MouseButton.LeftButton)

    assert dialog._eventToIndex(left) == 0
    assert dialog._eventToIndex(right) == 7


def testEditDialog1dRoutesScaleAndEraseOperations(qtbot):
    """1D左クリックを倍率変更、右クリックと値0を消去へ振り分ける。"""
    context = MagicMock()
    dialog = EditDialogView1d(modelContext=context)
    qtbot.addWidget(dialog)
    dialog.editValue = 0.75

    dialog._editIndexRange(1, 3, Qt.MouseButton.LeftButton)
    dialog._editIndexRange(4, 5, Qt.MouseButton.RightButton)
    dialog.editValue = 0.0
    dialog._editIndexRange(6, 6, Qt.MouseButton.LeftButton)

    context.scaleSpectrumBetweenIndexes.assert_called_once_with(1, 3, 0.75)
    assert context.eraseSpectrumBetweenIndexes.call_args_list == [
        ((4, 5),),
        ((6, 6),),
    ]


def testEditDialog1dDragStartsEditsAndEndsCompositeCommand(qtbot):
    """1Dドラッグの押下・移動・解放で編集トランザクションを完結する。"""
    context = MagicMock()
    component = Interactive1dSpectrumComponent()
    component.renderAll(np.arange(8, dtype=float))
    component.resize(650, 480)
    dialog = EditDialogView1d(
        modelContext=context,
        spectrumComponent=component,
    )
    qtbot.addWidget(dialog)
    dialog.editValue = 0.5
    press = FakeMouseEvent(100, 10, Qt.MouseButton.LeftButton)
    move = FakeMouseEvent(
        300,
        10,
        Qt.MouseButton.NoButton,
        buttons=Qt.MouseButton.LeftButton,
    )
    release = FakeMouseEvent(300, 10, Qt.MouseButton.LeftButton)

    dialog._onSpectrumPressed(press)
    dialog._onSpectrumMoved(move)
    dialog._onSpectrumReleased(release)

    context.beginSpectrumEdit.assert_called_once_with()
    assert context.scaleSpectrumBetweenIndexes.call_count == 2
    context.endSpectrumEdit.assert_called_once_with()
    assert dialog._isDraggingSpectrum is False


def testEditDialog1dUndoRedoAndResetUseModelContext(qtbot):
    """1D編集ボタンが履歴件数を確認してModelContextを操作する。"""
    context = MagicMock()
    context.getUndoCount.return_value = 1
    context.getRedoCount.return_value = 1
    dialog = EditDialogView1d(modelContext=context)
    qtbot.addWidget(dialog)

    dialog.onUndoClicked()
    dialog.onRedoClicked()
    dialog.onResetClicked()

    context.undo.assert_called_once_with()
    context.redo.assert_called_once_with()
    context.resetSpectrum.assert_called_once_with()


def testEditDialog2dBuildsContinuousLineAndMapsFftshift(qtbot):
    """2Dドラッグ線を連続点へ展開し、表示座標をスペクトル座標へ戻す。"""
    component = Interactive2dSpectrumComponent()
    component.renderAll(np.zeros((4, 4, 3), dtype=float))
    dialog = EditDialogView2d(spectrumComponent=component)
    qtbot.addWidget(dialog)

    assert dialog._displayLinePoints((0, 0), (2, 2)) == [
        (0, 0),
        (1, 1),
        (2, 2),
    ]
    assert dialog._displayPointToSpectrumPoint((0, 0)) == (2, 2)


def testEditDialog2dRoutesPaintAndEraseOperations(qtbot):
    """2D左クリックをペイント、右クリックを消去へ振り分ける。"""
    context = MagicMock()
    component = Interactive2dSpectrumComponent()
    component.renderAll(np.ones((4, 4, 3), dtype=float))
    dialog = EditDialogView2d(
        modelContext=context,
        spectrumComponent=component,
    )
    qtbot.addWidget(dialog)
    dialog.brushSize = 2
    dialog.editValue = 1.0

    dialog._editDisplayLine((0, 0), (1, 1), Qt.MouseButton.LeftButton)
    dialog._editDisplayLine((2, 2), (2, 2), Qt.MouseButton.RightButton)

    paintPoints, radius, color = context.paintRgbSpectrumAtPositions.call_args.args
    assert paintPoints == [(2, 2), (3, 3)]
    assert radius == 2
    assert len(color) == 3
    context.eraseSpectrumAtPositions.assert_called_once_with([(0, 0)], 2)


def testEditDialog2dUndoRedoAndResetUseModelContext(qtbot):
    """2D編集ボタンが履歴件数を確認してModelContextを操作する。"""
    context = MagicMock()
    context.getUndoCount.return_value = 1
    context.getRedoCount.return_value = 1
    dialog = EditDialogView2d(modelContext=context)
    qtbot.addWidget(dialog)

    dialog.onUndoClicked()
    dialog.onRedoClicked()
    dialog.onResetClicked()

    context.undo.assert_called_once_with()
    context.redo.assert_called_once_with()
    context.resetSpectrum.assert_called_once_with()
