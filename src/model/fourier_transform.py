from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
import numpy as np

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

class FourierTransform(object):
    # GENERATED CODE AREA: class.header ˅
    """
    フーリエ変換および逆フーリエ変換の計算処理を担当するクラスである。
    
    FFT用の入力信号 fftInputSignal、FFT結果 fftResultSpectrum、逆変換用の入力スペクトル ifftInputSpectrum、逆変換結果 ifftResultSignal を保持する。transform により入力信号からスペクトルを計算し、inverseTransform によりスペクトルから信号または画像を復元する。
    
    また、実部・虚部・振幅スペクトル・パワースペクトル・正規化スペクトルなど、フーリエ変換結果から派生するデータを取得する操作も持つ。周波数スペクトルを中心に移動する中心シフト処理もこのクラスが担当する。
    
    このクラスはアプリ全体の表示状態を管理するのではなく、直近の計算対象と計算結果を保持する計算エンジンとして扱う。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: method.__init__ ˅
    def __init__(self, fftInputSignal: np.ndarray | None = None) -> None:
        """
        FFT用の入力データと、IFFT用の入力データをそれぞれフィールドにセットする。
        """

        # FFT（フーリエ変換）の入力信号を保持するフィールド。
        self.fftInputSignal: np.ndarray | None = fftInputSignal

        # FFTの結果（スペクトル）を保持するフィールド。
        self.fftResultSpectrum: np.ndarray | None = None

        # IFFT（逆フーリエ変換）の入力スペクトルを保持するフィールド。
        self.ifftInputSpectrum: np.ndarray | None = None

        # IFFTの結果（復元信号）を保持するフィールド。
        self.ifftResultSignal: np.ndarray | None = None

        # SAFE CODE AREA ˅
        # 初期値の入力信号が渡された場合でも、変換は明示的に呼び出すまで行わない。
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.__init__ ˄


    # GENERATED CODE AREA: method.setFftInputSignal ˅
    def setFftInputSignal(self, fftInputSignal: np.ndarray) -> None:
        """
        fftInputSignalの値を更新する
        """

        # SAFE CODE AREA ˅
        self.fftInputSignal = np.asarray(fftInputSignal)
        self.fftResultSpectrum = None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setFftInputSignal ˄


    # GENERATED CODE AREA: method.setIfftInputSpectrum ˅
    def setIfftInputSpectrum(self, ifftInputSpectrum: np.ndarray) -> None:
        """
        fftInputSpectrumの値を更新する
        """

        # SAFE CODE AREA ˅
        self.ifftInputSpectrum = np.asarray(ifftInputSpectrum)
        self.ifftResultSignal = None
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.setIfftInputSpectrum ˄


    # GENERATED CODE AREA: method.transform ˅
    def transform(self) -> np.ndarray:
        """
        内部の fft_input_signal にFFTを適用し、結果を fft_result_spectrum として保持して返す。
        1次元データ (shape: (N,) または (N, C)) と
        2次元データ (shape: (H, W) または (H, W, C)) に対応。
        """

        # SAFE CODE AREA ˅
        if self.fftInputSignal is None:
            raise ValueError("FFT input signal has not been set.")

        axes = self._get_spatial_axes(self.fftInputSignal)
        self.fftResultSpectrum = np.fft.fftn(self.fftInputSignal, axes=axes)
        return self.fftResultSpectrum
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.transform ˄


    # GENERATED CODE AREA: method.realPart ˅
    def realPart(self) -> np.ndarray:
        """
        内部の fft_result_spectrum から実部配列を取り出して返す。
        """

        # SAFE CODE AREA ˅
        if self.fftResultSpectrum is None:
            raise ValueError("FFT result spectrum has not been computed.")
        return np.real(self.fftResultSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.realPart ˄


    # GENERATED CODE AREA: method.imaginaryPart ˅
    def imaginaryPart(self) -> np.ndarray:
        """
        内部の fft_result_spectrum から虚部配列を取り出して返す。
        """

        # SAFE CODE AREA ˅
        if self.fftResultSpectrum is None:
            raise ValueError("FFT result spectrum has not been computed.")
        return np.imag(self.fftResultSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.imaginaryPart ˄


    # GENERATED CODE AREA: method.amplitudeSpectrum ˅
    def amplitudeSpectrum(self) -> np.ndarray:
        """
        内部の fft_result_spectrum から振幅スペクトル（√(実部^2＋虚部^2)）を計算して返す。
        """

        # SAFE CODE AREA ˅
        if self.fftResultSpectrum is None:
            raise ValueError("FFT result spectrum has not been computed.")
        return np.abs(self.fftResultSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.amplitudeSpectrum ˄


    # GENERATED CODE AREA: method.normalizedSpectrum ˅
    def normalizedSpectrum(self) -> np.ndarray:
        """
        振幅スペクトルを最大値で除算し、0〜1の範囲に正規化して返す。
        """

        # SAFE CODE AREA ˅
        spectrum = self.amplitudeSpectrum()
        max_value = float(np.max(spectrum))
        if max_value <= 0.0:
            return np.zeros_like(spectrum, dtype=float)
        return spectrum.astype(float) / max_value
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.normalizedSpectrum ˄


    # GENERATED CODE AREA: method.normalizedLogSpectrum ˅
    def normalizedLogSpectrum(self) -> np.ndarray:
        """
        振幅スペクトルに対数スケールを適用した後、正規化して返す。
        """

        # SAFE CODE AREA ˅
        spectrum = np.log1p(self.amplitudeSpectrum())
        max_value = float(np.max(spectrum))
        if max_value <= 0.0:
            return np.zeros_like(spectrum, dtype=float)
        return spectrum.astype(float) / max_value
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.normalizedLogSpectrum ˄


    # GENERATED CODE AREA: method.powerSpectrum ˅
    def powerSpectrum(self) -> np.ndarray:
        """
        内部の fft_result_spectrum からパワースペクトル（実部^2＋虚部^2）を計算して返す。
        """

        # SAFE CODE AREA ˅
        if self.fftResultSpectrum is None:
            raise ValueError("FFT result spectrum has not been computed.")
        return np.square(np.abs(self.fftResultSpectrum))
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.powerSpectrum ˄


    # GENERATED CODE AREA: method.normalizedPowerSpectrum ˅
    def normalizedPowerSpectrum(self) -> np.ndarray:
        """
        パワースペクトルを最大値で除算し、0〜1の範囲に正規化して返す。
        """

        # SAFE CODE AREA ˅
        spectrum = self.powerSpectrum()
        max_value = float(np.max(spectrum))
        if max_value <= 0.0:
            return np.zeros_like(spectrum, dtype=float)
        return spectrum.astype(float) / max_value
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.normalizedPowerSpectrum ˄


    # GENERATED CODE AREA: method.normalizedLogPowerSpectrum ˅
    def normalizedLogPowerSpectrum(self) -> np.ndarray:
        """
        パワースペクトルに対数スケールを適用した後、正規化して返す。
        """

        # SAFE CODE AREA ˅
        spectrum = np.log1p(self.powerSpectrum())
        max_value = float(np.max(spectrum))
        if max_value <= 0.0:
            return np.zeros_like(spectrum, dtype=float)
        return spectrum.astype(float) / max_value
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.normalizedLogPowerSpectrum ˄


    # GENERATED CODE AREA: method.shiftSpectrum ˅
    def shiftSpectrum(self) -> np.ndarray:
        """
        内部の fft_result_spectrum のゼロ周波数成分を配列の中央に移動させて返す。
        """

        # SAFE CODE AREA ˅
        if self.fftResultSpectrum is None:
            raise ValueError("FFT result spectrum has not been computed.")
        return np.fft.fftshift(self.fftResultSpectrum)
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.shiftSpectrum ˄


    # GENERATED CODE AREA: method.inverseTransform ˅
    def inverseTransform(self) -> np.ndarray:
        """
        内部の ifft_input_spectrum にFFTを適用し、結果を ifft_result_signal として保持して返す。
        1次元データ (shape: (N,) または (N, C)) と
        2次元データ (shape: (H, W) または (H, W, C)) に対応。
        """

        # SAFE CODE AREA ˅
        if self.ifftInputSpectrum is None:
            raise ValueError("IFFT input spectrum has not been set.")
        axes = self._get_spatial_axes(self.fftInputSignal)
        self.fftResultSpectrum = np.fft.fftn(self.fftInputSignal, axes=axes)
        return self.fftResultSpectrum
        # SAFE CODE AREA ˄
    # GENERATED CODE AREA: method.inverseTransform ˄

    @staticmethod
    def _get_spatial_axes(data: np.ndarray) -> tuple[int, ...]:
        """
        データの次元数からFFTをかける空間軸を返す。
        チャンネル軸（最終軸）は除外する。

        1Dデータ : (N,)    → axes=(0,)  チャンネルなし
        2Dデータ : (H, W)  → axes=(0,1) チャンネルなし
                (H, W, C) → axes=(0,1) 最終軸はチャンネル
        """

        ndim = data.ndim

        if data.ndim == 1:
            return (0,)       # (N,)      空間軸は0のみ
        elif data.ndim == 2:
            return (0, 1)     # (H, W)    空間軸は0,1
        elif data.ndim == 3:
            return (0, 1)     # (H, W, C) チャンネル軸(2)を除いた0,1
        else:
            raise ValueError(f"Unsupported data shape: {data.shape}")