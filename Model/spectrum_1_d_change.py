from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from dataclasses import dataclass
import numpy as np
from .spectrum_change import SpectrumChange

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

@dataclass
class Spectrum1dChange(SpectrumChange):
    # GENERATED CODE AREA: class.header ˅
    """
    1次元スペクトルの変更情報を表すクラスである。変更されたインデックスと変更後のパワースペクトル情報を保持し、Viewの部分更新に利用される。
    """

    # SAFE CODE AREA ˅
    # dataclassのフィールドだけで通知情報を表せるため、追加処理は定義しない。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: class.attributes ˅
    # 変更された周波数成分のインデックスを保持する。
    index: int = 0

    # 変更後のパワースペクトル情報を保持する。
    changedPowerSpectrum: np.ndarray = None

    # GENERATED CODE AREA: class.attributes ˄

    # GENERATED CODE AREA: class.body ˅
    # SAFE CODE AREA ˅
    # 1D変更通知はindexと変更後スペクトルを運ぶだけの値オブジェクトとして扱う。
    pass
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.body ˄
