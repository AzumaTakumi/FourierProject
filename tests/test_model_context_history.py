import numpy as np
import pytest

from src.model.fourier_model_context import FourierModelContext


def testUndoRedoResetAndEmptyHistoryBehavior():
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


def test2dCompositeUndoRestoresRectAndInverseOnce():
    """2Dドラッグ編集のUndoでは矩形復元と逆FFTを1回だけ実行する"""
    context = FourierModelContext(lambda _change: None)
    context.set2dSourceData(np.arange(64, dtype=float).reshape(8, 8))
    model = context.currentModel

    beforeReal = np.copy(model.interactiveRealPart)
    beforeImaginary = np.copy(model.interactiveImaginaryPart)
    beforePower = np.copy(model.interactivePowerSpectrum)
    beforeInverse = np.copy(model.inverseData)

    context.beginSpectrumEdit()
    context.paintRgbSpectrumAtPositions([(2, 2)], radius=1, rgbColor=[10.0, 8.0, 6.0])
    context.paintRgbSpectrumAtPositions([(2, 3)], radius=1, rgbColor=[4.0, 5.0, 6.0])
    context.eraseSpectrumAtPositions([(3, 3)], radius=1)
    context.paintRgbSpectrumAtPositions([(4, 4), (4, 5)], radius=1, rgbColor=[7.0, 7.0, 7.0])
    context.endSpectrumEdit()

    command = context.undoStack[-1]
    assert len(command.commands) == 4

    calls = {"restore": 0, "inverse": 0}
    originalRestore = model.restoreInteractiveSpectrumAtRect
    originalComputeInverse = model.computeInverseData

    def countedRestore(*args, **kwargs):
        calls["restore"] += 1
        return originalRestore(*args, **kwargs)

    def countedComputeInverse():
        calls["inverse"] += 1
        return originalComputeInverse()

    model.restoreInteractiveSpectrumAtRect = countedRestore
    model.computeInverseData = countedComputeInverse

    assert context.undo() is True
    assert calls == {"restore": 1, "inverse": 1}
    assert np.allclose(model.interactiveRealPart, beforeReal)
    assert np.allclose(model.interactiveImaginaryPart, beforeImaginary)
    assert np.allclose(model.interactivePowerSpectrum, beforePower)
    assert np.allclose(model.inverseData, beforeInverse)
