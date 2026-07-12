import pytest

from src.view.edit_dialog_view_2d import EditDialogView2d


def test_thickness_slider_and_spinbox_stay_synced(qtbot):
    """太さスライダーと数値入力ボックスが双方向に同期することを確認する"""
    dialog = EditDialogView2d()
    qtbot.addWidget(dialog)

    dialog.thickness_slider.setValue(7)
    assert dialog.thickness_spin.value() == 7

    dialog.thickness_spin.setValue(3)
    assert dialog.thickness_slider.value() == 3


def test_value_slider_and_spinbox_stay_synced(qtbot):
    """値スライダーと小数入力ボックスが双方向に同期することを確認する"""
    dialog = EditDialogView2d()
    qtbot.addWidget(dialog)

    dialog.value_slider.setValue(4)
    assert dialog.value_spin.value() == pytest.approx(0.4)

    dialog.value_spin.setValue(0.7)
    assert dialog.value_slider.value() == 7
