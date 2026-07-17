import pytest

from src.view.edit_dialog_view_2d import EditDialogView2d


def testThicknessSliderAndSpinboxStaySynced(qtbot):
    """太さスライダーと数値入力ボックスが双方向に同期することを確認する"""
    dialog = EditDialogView2d()
    qtbot.addWidget(dialog)

    dialog.thicknessSlider.setValue(7)
    assert dialog.thicknessSpin.value() == 7

    dialog.thicknessSpin.setValue(3)
    assert dialog.thicknessSlider.value() == 3


def testValueSliderAndSpinboxStaySynced(qtbot):
    """値スライダーと小数入力ボックスが双方向に同期することを確認する"""
    dialog = EditDialogView2d()
    qtbot.addWidget(dialog)

    dialog.valueSlider.setValue(4)
    assert dialog.valueSpin.value() == pytest.approx(0.4)

    dialog.valueSpin.setValue(0.7)
    assert dialog.valueSlider.value() == 7
