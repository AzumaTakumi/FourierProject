import numpy as np

from src.view.edit_dialog_view_2d import EditDialogView2d


class _SpectrumComponentStub:
    def __init__(self, value_range):
        self._displayValueRange = value_range
        self._powerSpectrum = None


def test_2d_paint_value_maps_to_display_range():
    """2Dペイントの数値を、表示レンジ上の明るさとしてFFT実部値へ変換する"""
    dialog = EditDialogView2d.__new__(EditDialogView2d)
    dialog.spectrumComponent = _SpectrumComponentStub((0.0, float(np.log1p(100.0))))

    dialog.editValue = 0.0
    assert dialog._paint_color_from_edit_value() == [0.0, 0.0, 0.0]

    dialog.editValue = 1.0
    assert np.allclose(dialog._paint_color_from_edit_value(), [10.0, 10.0, 10.0])
