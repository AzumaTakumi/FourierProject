from __future__ import annotations

# GENERATED CODE AREA: module.imports ˅
from dataclasses import dataclass
import numpy as np

# GENERATED CODE AREA: module.imports ˄

# SAFE CODE AREA ˅
# SAFE CODE AREA ˄

@dataclass
class Snapshot(object):
    # GENERATED CODE AREA: class.header ˅
    """
    Modelの状態を一時保存するためのデータクラスである。Undo処理やRedo処理で以前の状態へ戻すために、元データ、フーリエ変換結果、編集用スペクトル、逆変換結果を保持する。
    """

    # SAFE CODE AREA ˅
    # dataclassのフィールド定義だけで状態保存に必要な処理は足りるため、追加メソッドは定義しない。
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.header ˄

    # GENERATED CODE AREA: class.attributes ˅
    # 元データを保存する。1次元の場合は信号データ、2次元の場合は画像データを保持する。
    sourceData: np.ndarray = None

    # フーリエ変換結果の実部を保存する。
    realPart: np.ndarray = None

    # フーリエ変換結果の虚部を保存する。
    imaginaryPart: np.ndarray = None

    # フーリエ変換結果から計算されたパワースペクトルを保存する。
    powerSpectrum: np.ndarray = None

    # 編集操作を反映したスペクトル実部を保存する。
    interactiveRealPart: np.ndarray = None

    # 編集操作を反映したスペクトル虚部を保存する。
    interactiveImaginaryPart: np.ndarray = None

    # 編集操作を反映したパワースペクトルを保存する。
    interactivePowerSpectrum: np.ndarray = None

    # 編集用スペクトルを逆変換して得られた復元データを保存する。
    inverseData: np.ndarray = None

    # GENERATED CODE AREA: class.attributes ˄

    # GENERATED CODE AREA: class.body ˅
    # SAFE CODE AREA ˅
    # Snapshotは値を運ぶだけのデータクラスとして扱う。配列のcopyはModel側で行う。
    pass
    # SAFE CODE AREA ˄

    # GENERATED CODE AREA: class.body ˄
