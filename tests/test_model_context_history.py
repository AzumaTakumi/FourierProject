import numpy as np
import pytest

from src.model.fourier_model_context import FourierModelContext


def test_undo_redo_reset_and_empty_history_behavior():
    """1D編集のUndo/Redo/Resetと履歴が尽きたときの振る舞いを確認する"""
    context = FourierModelContext(lambda _change: None)
    context.set1dSourceData(np.array([0.0, 1.0, 0.0, -1.0], dtype=float))

    before = np.copy(context.currentModel.interactiveRealPart)

    context.editSpectrumValueAtIndex(1, 2.0, 0.0)
    assert context.currentModel.interactiveRealPart[1] == 2.0
    assert context.getUndoCount() == 1

    assert context.undo() is True
    assert np.allclose(context.currentModel.interactiveRealPart, before)
    assert context.getRedoCount() == 1

    assert context.redo() is True
    assert context.currentModel.interactiveRealPart[1] == 2.0

    context.resetSpectrum()
    assert np.allclose(context.currentModel.interactiveRealPart, context.currentModel.realPart)

    assert context.undo() is True
    assert context.currentModel.interactiveRealPart[1] == 2.0

    assert context.undo() is True
    assert np.allclose(context.currentModel.interactiveRealPart, before)

    with pytest.raises(IndexError):
        context.undo()


def test_2d_composite_undo_restores_rect_and_inverse_once():
    """2Dドラッグ編集のUndoでは矩形復元と逆FFTを1回だけ実行する"""
    context = FourierModelContext(lambda _change: None)
    context.set2dSourceData(np.arange(64, dtype=float).reshape(8, 8))
    model = context.currentModel

    before_real = np.copy(model.interactiveRealPart)
    before_imaginary = np.copy(model.interactiveImaginaryPart)
    before_power = np.copy(model.interactivePowerSpectrum)
    before_inverse = np.copy(model.inverseData)

    context.beginSpectrumEdit()
    context.paintRgbSpectrumAtPositions([(2, 2)], radius=1, rgbColor=[10.0, 8.0, 6.0])
    context.paintRgbSpectrumAtPositions([(2, 3)], radius=1, rgbColor=[4.0, 5.0, 6.0])
    context.eraseSpectrumAtPositions([(3, 3)], radius=1)
    context.paintRgbSpectrumAtPositions([(4, 4), (4, 5)], radius=1, rgbColor=[7.0, 7.0, 7.0])
    context.endSpectrumEdit()

    command = context.undoStack[-1]
    assert len(command.commands) == 4

    calls = {"restore": 0, "inverse": 0}
    original_restore = model.restoreInteractiveSpectrumAtRect
    original_compute_inverse = model.computeInverseData

    def counted_restore(*args, **kwargs):
        calls["restore"] += 1
        return original_restore(*args, **kwargs)

    def counted_compute_inverse():
        calls["inverse"] += 1
        return original_compute_inverse()

    model.restoreInteractiveSpectrumAtRect = counted_restore
    model.computeInverseData = counted_compute_inverse

    assert context.undo() is True
    assert calls == {"restore": 1, "inverse": 1}
    assert np.allclose(model.interactiveRealPart, before_real)
    assert np.allclose(model.interactiveImaginaryPart, before_imaginary)
    assert np.allclose(model.interactivePowerSpectrum, before_power)
    assert np.allclose(model.inverseData, before_inverse)
