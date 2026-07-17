import numpy as np

from src.model.fourier_model_context import FourierModelContext
from src.model.fourier_1_d_model import Fourier1dModel
from src.model.fourier_2_d_model import Fourier2dModel
from src.model.spectrum_1_d_change import Spectrum1dChange


def testModelSwitchingClearsHistoryAndKeeps1dAnd2dSeparate():
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


def testModelSwitchDoesNotEmitDirtyRegionNotification():
    """モデル差し替えでは部分更新通知を出さず、編集時だけ通知することを確認する"""
    notifications = []
    context = FourierModelContext(notifications.append)

    context.set1dSourceData(np.array([0.0, 1.0, 0.0, -1.0], dtype=float))
    assert notifications == []

    context.editSpectrumValueAtIndex(1, 2.0, 0.0)
    assert len(notifications) == 1
    assert isinstance(notifications[0], Spectrum1dChange)

    notifications.clear()
    context.set2dSourceData(np.zeros((4, 4, 3), dtype=float))
    assert notifications == []
