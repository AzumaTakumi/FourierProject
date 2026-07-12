import numpy as np

from src.model.fourier_model_context import FourierModelContext
from src.model.fourier_1_d_model import Fourier1dModel
from src.model.fourier_2_d_model import Fourier2dModel


def test_model_switching_clears_history_and_keeps_1d_and_2d_separate():
    """モデル切り替えで履歴がリセットされ、1D/2Dの状態が独立していることを確認する"""
    context = FourierModelContext(lambda _change: None)

    context.set1dSourceData(np.array([0.1, 0.2, 0.3, 0.4], dtype=float))
    assert context.is1dModel()
    assert isinstance(context.currentModel, Fourier1dModel)

    context.editSpectrumValueAtIndex(0, 1.0, 0.0)
    assert context.getUndoCount() == 1

    context.set2dSourceData(np.arange(9, dtype=float).reshape(3, 3))
    assert context.is2dModel()
    assert isinstance(context.currentModel, Fourier2dModel)
    assert context.getUndoCount() == 0
    assert context.getRedoCount() == 0

    context.beginSpectrumEdit()
    context.paintRgbSpectrumAtPositions([(0, 0)], radius=0, rgbColor=[0.5, 0.5, 0.5])
    context.endSpectrumEdit()
    assert context.currentModel.interactiveRealPart.shape == (3, 3, 3)

    context.set1dSourceData(np.array([1.0, 2.0, 3.0], dtype=float))
    assert context.is1dModel()
    assert isinstance(context.currentModel, Fourier1dModel)
    assert context.currentModel.interactiveRealPart.shape == (3,)
