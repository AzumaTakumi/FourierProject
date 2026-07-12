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
