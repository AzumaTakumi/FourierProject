import os
import numpy as np
import pytest
from PIL import Image

from src.model.fourier_transform import FourierTransform
from src.model.fourier_1_d_model import Fourier1dModel
from src.model.fourier_2_d_model import Fourier2dModel
from src.model.fourier_renderer import FourierRenderer
from src.model.pane_type import PaneType
from src.controller.file_saver import FileSaver


def testFftSpectrumMatchesNumpyFft():
    """単純な信号でFourierTransform.transformがnumpyのFFTと一致することを検証する"""
    x = np.array([1.0, 0.0, 0.0, 0.0], dtype=float)
    ft = FourierTransform(x)
    spec = ft.transform()
    expected = np.fft.fftn(x)
    assert spec.shape == expected.shape
    assert np.allclose(spec, expected)


def test1dEditSingleIndexUpdatesInverseAndUndo():
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


def test1dInverseRendererKeepsNegativeValues():
    """複素型の逆変換結果を1D波形として描いても、負値が絶対値表示に変わらないことを確認する"""
    data = np.array([0.0, 1.5, 3.0, 1.5, 0.0, -1.5, -3.0, -1.5])
    model = Fourier1dModel(data)

    sourceImage = np.array(FourierRenderer.imageFrom1dData(data))
    inverseImage = np.array(FourierRenderer.imageFrom1dData(model.inverseData))

    assert np.allclose(np.real(model.inverseData), data)
    assert np.array_equal(inverseImage, sourceImage)


def test1dSpectrumRendererUsesStemPlot():
    """1Dスペクトルは折れ線ではなく、離散成分を表す縦棒として描画する"""
    data = np.sin(2.0 * np.pi * np.arange(32) / 32.0)
    model = Fourier1dModel(data)

    spectrumImage = np.array(model.getImage()[PaneType.POWER_SPECTRUM])
    lineImage = np.array(FourierRenderer.imageFrom1dData(model.powerSpectrum))

    assert np.array_equal(
        spectrumImage,
        np.array(FourierRenderer.imageFromSpectrum(model.powerSpectrum)),
    )
    assert not np.array_equal(spectrumImage, lineImage)


def test2dPaintAndEraseChangeInverse():
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


def testFileSaverWriteAndPermissionError(tmp_path):
    """FileSaver.saveSignalData がファイルを書き出し、書き込み不可ディレクトリでは例外を出すことを確認する"""
    img = Image.new("RGB", (2, 2), color=(10, 20, 30))
    saver = FileSaver(aView=None)

    outPath = tmp_path / "out.png"
    saver.saveSignalData(str(outPath), img)
    assert outPath.exists()

    # 書き込み権限のないディレクトリへ保存しようとすると例外が発生する
    noWriteDir = tmp_path / "no_write_dir"
    noWriteDir.mkdir()
    # remove write permission for the directory
    origMode = noWriteDir.stat().st_mode
    try:
        os.chmod(noWriteDir, 0o500)
        badPath = noWriteDir / "fail.png"
        with pytest.raises(Exception):
            saver.saveSignalData(str(badPath), img)
    finally:
        # restore permissions so pytest can clean up
        os.chmod(noWriteDir, origMode)
