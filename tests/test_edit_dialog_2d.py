import numpy as np

from src.view.edit_dialog_view_2d import EditDialogView2d


class _SpectrumComponentStub:
    def __init__(self, valueRange):
        self._displayValueRange = valueRange
        self._powerSpectrum = None


def test2dPaintValueMapsToDisplayRange():
    """2Dペイントの数値を、表示レンジ上の明るさとしてFFT実部値へ変換する"""
    dialog = EditDialogView2d.__new__(EditDialogView2d)
    dialog.spectrumComponent = _SpectrumComponentStub((0.0, float(np.log1p(100.0))))

    dialog.editValue = 0.0
    assert dialog._paintColorFromEditValue() == [0.0, 0.0, 0.0]

    dialog.editValue = 1.0
    assert np.allclose(dialog._paintColorFromEditValue(), [10.0, 10.0, 10.0])
