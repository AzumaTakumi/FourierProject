from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from dataclasses import dataclass
import numpy as np
from .spectrum_change import SpectrumChange

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

@dataclass
class Spectrum2dChange(SpectrumChange):
    # GENERATED CODE AREA: class.header ˅
    """
    2次元スペクトルの変更情報を表すクラスである。変更された範囲の位置、大きさ、変更後のパワースペクトル情報を保持し、Viewの部分更新に利用される。
    """

    # SAFE CODE AREA ˅
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: class.attributes ˅
    # 変更範囲の左上位置または基準位置のx座標を保持する。
    x: int = 0

    # 変更範囲の左上位置または基準位置のy座標を保持する。
    y: int = 0

    # 変更範囲の横幅を保持する。
    width: int = 0

    # 変更範囲の高さを保持する。
    height: int = 0

    # 変更範囲に対応する変更後のパワースペクトル情報を保持する。
    changedPowerSpectrum: np.ndarray = None

    # GENERATED CODE AREA: class.attributes ˄

    # GENERATED CODE AREA: class.body ˅
    # SAFE CODE AREA ˅
    pass
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.body ˄

