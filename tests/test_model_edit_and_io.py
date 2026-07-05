import os
import numpy as np
import pytest
from PIL import Image

from src.model.fourier_transform import FourierTransform
from src.model.fourier_1_d_model import Fourier1dModel
from src.model.fourier_2_d_model import Fourier2dModel
from src.model.fourier_renderer import FourierRenderer
from src.controller.file_saver import FileSaver


def test_fft_spectrum_matches_numpy_fft():
    """単純な信号でFourierTransform.transformがnumpyのFFTと一致することを検証する"""
    x = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
    ft = FourierTransform(x)
    spec = ft.transform()
    expected = np.fft.fftn(x)
    assert spec.shape == expected.shape
    assert np.allclose(spec, expected)


def test_1d_edit_single_index_updates_inverse_and_undo():
    """1次元モデルでスペクトルを編集すると逆変換結果が変化し、Snapshotで復元できることを確認する"""
    data = np.linspace(0.0, 1.0, 8)
    model = Fourier1dModel(data)

    assert model.inverseData is not None
    before = np.copy(model.inverseData)

    snap = model.createSnapshot()

    # 任意のインデックスをゼロにして逆変換が変わることを確認
    idx = 1
    model.editSpectrumValueAtIndex(idx, 0.0, 0.0)
    assert not np.allclose(model.inverseData, before)

    # Snapshotから復元して元に戻る
    model.restoreSnapshot(snap)
    assert np.allclose(model.inverseData, before)


def test_1d_inverse_renderer_keeps_negative_values():
    """複素型の逆変換結果を1D波形として描いても、負値が絶対値表示に変わらないことを確認する"""
    data = np.array([0.0, 1.5, 3.0, 1.5, 0.0, -1.5, -3.0, -1.5])
    model = Fourier1dModel(data)

    source_image = np.array(FourierRenderer.imageFrom1dData(data))
    inverse_image = np.array(FourierRenderer.imageFrom1dData(model.inverseData))

    assert np.allclose(np.real(model.inverseData), data)
    assert np.array_equal(inverse_image, source_image)


def test_2d_paint_and_erase_change_inverse():
    """2次元モデルでペイント・消去操作が逆変換結果に反映されることを確認する"""
    data = np.arange(16, dtype=float).reshape(4, 4)
    model = Fourier2dModel(data)

    before = np.copy(model.inverseData)

    pos = [(1, 1)]
    model.paintRgbSpectrumAtPositions(pos, radius=0, rgbColor=[100.0, 50.0, 25.0])
    painted = np.copy(model.inverseData)
    assert not np.allclose(painted, before)

    # 消去して再度逆変換が変わることを確認
    model.eraseSpectrumAtPositions(pos, radius=0)
    erased = np.copy(model.inverseData)
    assert not np.allclose(erased, painted)


def test_file_saver_write_and_permission_error(tmp_path):
    """FileSaver.saveSignalData がファイルを書き出し、書き込み不可ディレクトリでは例外を出すことを確認する"""
    img = Image.new("RGB", (2, 2), color=(10, 20, 30))
    saver = FileSaver(aView=None)

    out_path = tmp_path / "out.png"
    saver.saveSignalData(str(out_path), img)
    assert out_path.exists()

    # 書き込み権限のないディレクトリへ保存しようとすると例外が発生する
    no_write_dir = tmp_path / "no_write_dir"
    no_write_dir.mkdir()
    # remove write permission for the directory
    orig_mode = no_write_dir.stat().st_mode
    try:
        os.chmod(no_write_dir, 0o500)
        bad_path = no_write_dir / "fail.png"
        with pytest.raises(Exception):
            saver.saveSignalData(str(bad_path), img)
    finally:
        # restore permissions so pytest can clean up
        os.chmod(no_write_dir, orig_mode)
