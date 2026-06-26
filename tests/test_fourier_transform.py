import numpy as np

from src.model.fourier_transform import FourierTransform


def assert_round_trip(original: np.ndarray, atol: float = 1e-8, rtol: float = 1e-8) -> None:
    """フーリエ変換と逆フーリエ変換を通した信号の往復（Round-trip）検証を行う"""
    transform = FourierTransform(original)
    spectrum = transform.transform()
    transform.setIfftInputSpectrum(spectrum)
    restored = transform.inverseTransform()

    assert restored.shape == original.shape
    assert np.allclose(np.real(restored), original, rtol=rtol, atol=atol), "復元信号の実部が元の信号と一致しません"
    assert np.allclose(np.imag(restored), 0.0, atol=atol), "復元信号の虚部が十分に小さくありません"


def test_1d_round_trip_real() -> None:
    """1次元の実数配列に対してフーリエ変換・逆フーリエ変換の往復が正しく動作するか確認"""
    original = np.linspace(-1.0, 1.0, 16, dtype=float)
    assert_round_trip(original)


def test_2d_round_trip_real() -> None:
    """2次元の実数配列に対してフーリエ変換・逆フーリエ変換の往復が正しく動作するか確認"""
    original = np.arange(16, dtype=float).reshape(4, 4)
    assert_round_trip(original)


def test_2d_round_trip_with_channels() -> None:
    """チャンネル表現を含む多次元配列に対してフーリエ変換・逆フーリエ変換の往復が正しく動作するか確認"""
    original = np.arange(24, dtype=float).reshape(2, 3, 4)
    assert_round_trip(original)
