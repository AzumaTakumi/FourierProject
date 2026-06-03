# fourier_model_context.py 利用仕様

この仕様書は、ViewやControllerを作成するときに`FourierModelContext`をどのように扱うかを示すものです。

ViewやControllerは、現在のModelインスタンスを直接取得しません。
表示用データや画像を取得するときも、必ず`FourierModelContext`の公開メソッドを使います。

```python
data_map = self.context.getData()
image_map = self.context.getImage()
```

`model()`は外部から使わない前提のため、View/Controllerから呼ぶとエラーになります。

## 基本形

Controllerは`FourierModelContext`を1つ保持します。

```python
from Model.fourier_model_context import FourierModelContext


class AppController:
    def __init__(self, view):
        self.view = view
        self.context = FourierModelContext(self.on_spectrum_changed)

    def on_spectrum_changed(self, change):
        self.view.update_spectrum(change)
```

Modelの状態を表示したい場合も、編集したい場合も、Controllerは`self.context`を通して操作します。

## View更新用listener

`FourierModelContext`の初期化時に渡した関数は、スペクトルが変わったときに呼ばれます。

```python
self.context = FourierModelContext(self.on_spectrum_changed)
```

```python
def on_spectrum_changed(self, change):
    self.view.update_spectrum(change)
```

listenerには、変更された部分を表す`Spectrum1dChange`または`Spectrum2dChange`が渡されます。
Viewは`change`の中身を見て、スペクトル表示の変更範囲だけを更新してください。
スペクトル全体を毎回更新する必要はありません。

1Dの場合、`change`は`Spectrum1dChange`です。

```python
from Model.spectrum_1_d_change import Spectrum1dChange


def on_spectrum_changed(self, change):
    if isinstance(change, Spectrum1dChange):
        start = change.index
        changed_values = change.changedPowerSpectrum
        self.view.update_1d_spectrum(start, changed_values)
```

`changedPowerSpectrum`は1要素とは限りません。
ドラッグなどで複数indexが変更された場合は、`index`から始まる連続範囲のデータが渡されます。

2Dの場合、`change`は`Spectrum2dChange`です。
`changedPowerSpectrum`には、変更されたスペクトル画像を長方形に切り取った部分のデータが入ります。
`x`と`y`はCanvas表示上の座標ではなく、Contextへ渡した`row`/`col`と同じModel内部のスペクトル配列座標系です。

```python
from Model.spectrum_2_d_change import Spectrum2dChange


def on_spectrum_changed(self, change):
    if isinstance(change, Spectrum2dChange):
        self.view.update_2d_spectrum_rect(
            x=change.x,
            y=change.y,
            width=change.width,
            height=change.height,
            changed_data=change.changedPowerSpectrum,
        )
```

`set1dSourceData()`、`set2dSourceData()`、`resetSpectrum()`のように全体が変わる操作では、全範囲を表すchangeが渡されます。
1Dでは`index=0`で全スペクトル配列、2Dでは`x=0`、`y=0`で全矩形データが渡されます。

Viewは、部分changeを受け取った場合、少なくとも未変更の`SOURCE_DATA`と`POWER_SPECTRUM`は再描画しないでください。
2D編集では`INTERACTIVE_POWER_SPECTRUM`は`change`の矩形だけ更新できます。
一方で`INVERSE_DATA`は周波数成分の変更が画像全体へ影響するため、通常はInverseペイン全体を再描画してください。

## ドラッグ時の線分編集

マウス移動イベントは、ペンを動かす速度や処理速度によって間引かれることがあります。
その場合、取得できた座標だけを編集すると線ではなく点が並んだように見えます。

この問題を避けるため、Controllerは前回取得した座標と今回取得した座標をContextへ渡し、Context側でその間を線として補間して編集します。

1Dの場合は、前回indexと今回indexを渡します。

```python
def erase_1d_drag(self, previous_index, current_index):
    self.context.eraseSpectrumBetweenIndexes(previous_index, current_index)
```

```python
def restore_1d_drag(self, previous_index, current_index):
    self.context.restoreSpectrumBetweenIndexes(previous_index, current_index)
```

2Dの場合は、前回の`row`/`col`と今回の`row`/`col`を渡します。

```python
def erase_2d_drag(self, previous_row, previous_col, current_row, current_col, radius):
    self.context.eraseSpectrumLineAtPosition(
        previous_row,
        previous_col,
        current_row,
        current_col,
        radius,
    )
```

```python
def paint_2d_drag(self, previous_row, previous_col, current_row, current_col, radius, rgb):
    self.context.paintRgbSpectrumLineAtPosition(
        previous_row,
        previous_col,
        current_row,
        current_col,
        radius,
        rgb,
    )
```

これらの線分編集メソッドは、線分上の複数点を編集してもView通知は1回にまとめます。
1Dでは変更された連続index範囲、2Dでは線分とブラシ半径をすべて含む矩形範囲が`change`として渡されます。
2Dの線分編集では、線分上の複数点を1つのCommandでまとめてModelへ渡すため、逆FFTは線分編集1回につき最後に1回だけ実行されます。

## 表示用データを取得する

数値配列を取得する場合は`context.getData()`を使います。

```python
from Model.pane_type import PaneType


data_map = self.context.getData()

source_data = data_map[PaneType.SOURCE_DATA]
power_spectrum = data_map[PaneType.POWER_SPECTRUM]
editable_spectrum = data_map[PaneType.INTERACTIVE_POWER_SPECTRUM]
inverse_data = data_map[PaneType.INVERSE_DATA]
```

`getData()`は、`PaneType`をキー、numpy配列または`None`を値にした辞書を返します。

注意点として、取得した配列をView/Controller側で直接書き換えないでください。
スペクトル編集は必ずContextの編集メソッドで行います。

## 表示用画像を取得する

画像表示用の`PIL.Image`を取得する場合は`context.getImage()`を使います。

```python
from Model.pane_type import PaneType


image_map = self.context.getImage()

source_image = image_map[PaneType.SOURCE_DATA]
power_spectrum_image = image_map[PaneType.POWER_SPECTRUM]
editable_spectrum_image = image_map[PaneType.INTERACTIVE_POWER_SPECTRUM]
inverse_image = image_map[PaneType.INVERSE_DATA]
```

Viewの再描画処理例です。

```python
def refresh(self):
    image_map = self.controller.context.getImage()

    self.draw_source(image_map[PaneType.SOURCE_DATA])
    self.draw_power_spectrum(image_map[PaneType.POWER_SPECTRUM])
    self.draw_editable_spectrum(image_map[PaneType.INTERACTIVE_POWER_SPECTRUM])
    self.draw_inverse(image_map[PaneType.INVERSE_DATA])
```

`None`が返るペインは、まだ表示できるデータがない状態です。

## 1Dデータを設定する

1D信号を設定するときは`set1dSourceData()`を使います。

```python
import numpy as np


def load_1d_array(self, values):
    data = np.asarray(values, dtype=float).reshape(-1)
    self.context.set1dSourceData(data)
```

CSVファイルから読み込む例です。

```python
import numpy as np


def load_csv(self, path):
    data = np.loadtxt(path, delimiter=",")
    data = np.asarray(data, dtype=float).reshape(-1)
    self.context.set1dSourceData(data)
```

この呼び出しにより、Context内部でFFT、編集用スペクトル初期化、逆変換、Undo履歴登録、変更通知が行われます。

## 2Dデータを設定する

画像を設定するときは`set2dSourceData()`を使います。

```python
import numpy as np
from PIL import Image


def load_image(self, path):
    image = Image.open(path).convert("RGB")
    data = np.asarray(image, dtype=float)
    self.context.set2dSourceData(data)
```

グレースケール画像は`(height, width)`の2次元配列、RGB画像は`(height, width, 3)`の3次元配列として渡します。

```python
gray = np.zeros((128, 128), dtype=float)
self.context.set2dSourceData(gray)

rgb = np.zeros((128, 128, 3), dtype=float)
self.context.set2dSourceData(rgb)
```

## 現在のModel種類を判定する

View/ControllerからModelインスタンスは取得しません。
1D/2Dの判定が必要な場合は、Contextの判定メソッドを使います。

```python
if self.context.is1dModel():
    print("1D操作が可能")

if self.context.is2dModel():
    print("2D操作が可能")
```

ステータス表示用のModel名は`getModelName()`で取得します。

```python
model_name = self.context.getModelName()
```

## 1Dスペクトルを編集する

1Dスペクトルでは、周波数成分の`index`を指定します。

```python
def erase_1d_index(self, index):
    self.context.eraseSpectrumAtIndex(index)
```

```python
def restore_1d_index(self, index):
    self.context.restoreSpectrumAtIndex(index)
```

```python
def edit_1d_value(self, index, real_part, imaginary_part):
    self.context.editSpectrumValueAtIndex(index, real_part, imaginary_part)
```

1D値入力欄の値を取得する場合は、Context経由で現在の編集用スペクトル値を読みます。

```python
def refresh_1d_value_inputs(self, index):
    if not self.context.is1dModel():
        return

    real_part, imaginary_part = self.context.getInteractiveSpectrumAtIndex(index)
    self.view.set_real_input(float(real_part))
    self.view.set_imag_input(float(imaginary_part))
```

## 2Dスペクトルを編集する

2Dスペクトルでは、`row`、`col`、`radius`を指定します。

```python
def erase_2d_position(self, row, col, radius):
    self.context.eraseSpectrumAtPosition(row, col, radius)
```

```python
def paint_2d_position(self, row, col, radius, rgb):
    self.context.paintRgbSpectrumAtPosition(row, col, radius, rgb)
```

RGBペイントの呼び出し例です。

```python
self.context.paintRgbSpectrumAtPosition(
    row=120,
    col=80,
    radius=5,
    rgbColor=[255.0, 0.0, 0.0],
)
```

## 1D Canvas座標からindexへ変換する

1Dスペクトル画像をクリック編集する場合は、クリック位置の横座標をindexへ変換します。

```python
def canvas_x_to_1d_index(click_x, displayed_width, spectrum_length):
    index = int((click_x / max(1, displayed_width)) * spectrum_length)
    index = max(0, min(index, spectrum_length - 1))
    return index
```

Contextを使った例です。

```python
def erase_1d_at_canvas_point(self, click_x, displayed_width):
    spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]
    index = canvas_x_to_1d_index(click_x, displayed_width, spectrum.shape[0])
    self.context.eraseSpectrumAtIndex(index)
```

ドラッグでは前回Canvas座標から得たindexと今回Canvas座標から得たindexを使い、線分編集メソッドを呼びます。

```python
def erase_1d_drag_at_canvas_point(self, previous_x, current_x, displayed_width):
    spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]
    previous_index = canvas_x_to_1d_index(previous_x, displayed_width, spectrum.shape[0])
    current_index = canvas_x_to_1d_index(current_x, displayed_width, spectrum.shape[0])
    self.context.eraseSpectrumBetweenIndexes(previous_index, current_index)
```

## 2D Canvas座標からスペクトル座標へ変換する

2Dスペクトル画像をクリック編集する場合は、Canvas上のクリック座標をModel内部のスペクトル座標へ変換してからContextへ渡します。

`context.getImage()`で取得したスペクトル画像は、表示のために`fftshift`されています。
そのため、表示上のクリック座標をそのまま`eraseSpectrumAtPosition()`へ渡すと、編集位置がずれます。

次の変換を使ってください。

```python
def canvas_point_to_spectrum_position(
    click_x,
    click_y,
    displayed_width,
    displayed_height,
    spectrum_shape,
):
    spectrum_height, spectrum_width = spectrum_shape

    display_row = int((click_y / max(1, displayed_height)) * spectrum_height)
    display_col = int((click_x / max(1, displayed_width)) * spectrum_width)

    display_row = max(0, min(display_row, spectrum_height - 1))
    display_col = max(0, min(display_col, spectrum_width - 1))

    model_row = (display_row + spectrum_height // 2) % spectrum_height
    model_col = (display_col + spectrum_width // 2) % spectrum_width

    return model_row, model_col
```

Contextを使った例です。

```python
def erase_2d_at_canvas_point(self, click_x, click_y, displayed_width, displayed_height, radius):
    spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]

    row, col = canvas_point_to_spectrum_position(
        click_x,
        click_y,
        displayed_width,
        displayed_height,
        spectrum.shape[:2],
    )

    self.context.eraseSpectrumAtPosition(row, col, radius)
```

ドラッグでは前回Canvas座標と今回Canvas座標をそれぞれModel内部座標へ変換し、線分編集メソッドを呼びます。

```python
def erase_2d_drag_at_canvas_point(
    self,
    previous_x,
    previous_y,
    current_x,
    current_y,
    displayed_width,
    displayed_height,
    radius,
):
    spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]

    previous_row, previous_col = canvas_point_to_spectrum_position(
        previous_x,
        previous_y,
        displayed_width,
        displayed_height,
        spectrum.shape[:2],
    )
    current_row, current_col = canvas_point_to_spectrum_position(
        current_x,
        current_y,
        displayed_width,
        displayed_height,
        spectrum.shape[:2],
    )

    self.context.eraseSpectrumLineAtPosition(
        previous_row,
        previous_col,
        current_row,
        current_col,
        radius,
    )
```

Canvas内で画像を中央配置している場合は、Canvas座標から画像左上座標を引いたローカル座標を渡してください。

```python
local_x = event.x - image_left
local_y = event.y - image_top
```

## ドラッグ編集を1回のUndoにまとめる

ドラッグ開始時に`beginSpectrumEdit()`、ドラッグ終了時に`endSpectrumEdit()`を呼びます。

```python
def on_mouse_press(self, event):
    self.context.beginSpectrumEdit()
    self.previous_point = self.event_to_local_point(event)
    self.edit_at_event(event)


def on_mouse_drag(self, event):
    current_point = self.event_to_local_point(event)
    self.edit_line_between(self.previous_point, current_point)
    self.previous_point = current_point


def on_mouse_release(self, event):
    self.context.endSpectrumEdit()
    self.previous_point = None
```

`beginSpectrumEdit()`から`endSpectrumEdit()`までに実行された編集は、1つのUndo単位として扱われます。

## Undo / Redo

Undoは`undo()`、Redoは`redo()`を呼びます。

```python
def undo(self):
    changed = self.context.undo()
    if not changed:
        self.view.show_status("Undo履歴がありません")


def redo(self):
    changed = self.context.redo()
    if not changed:
        self.view.show_status("Redo履歴がありません")
```

戻り値は`bool`です。

| 戻り値 | 意味 |
| --- | --- |
| `True` | UndoまたはRedoが実行された |
| `False` | 履歴が空で何も実行されなかった |

## スペクトルをリセットする

編集用スペクトルをFFT直後の状態へ戻す場合は、`resetSpectrum()`を呼びます。

```python
def reset_spectrum(self):
    self.context.resetSpectrum()
```

この操作もUndo対象です。

## ステータス表示に使う情報

Undo/Redo数やModel名はContextから取得します。

```python
model_name = self.context.getModelName()
undo_count = self.context.getUndoCount()
redo_count = self.context.getRedoCount()

self.view.show_status(
    f"Model: {model_name} | Undo: {undo_count} | Redo: {redo_count}"
)
```

## 保存用画像を取得する

表示中の4ペイン画像を保存したい場合も、`context.getImage()`を使います。

```python
def save_images(self, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    image_map = self.context.getImage()

    for pane_type, image in image_map.items():
        if image is None:
            continue

        file_path = output_dir / f"{pane_type.name.lower()}.png"
        image.save(file_path)
```

## Controllerの最小実装例

```python
import numpy as np
from PIL import Image

from Model.fourier_model_context import FourierModelContext
from Model.pane_type import PaneType


class FourierController:
    def __init__(self, view):
        self.view = view
        self.context = FourierModelContext(self.on_spectrum_changed)

    def on_spectrum_changed(self, change):
        self.view.update_spectrum(change)

    def load_csv(self, path):
        data = np.loadtxt(path, delimiter=",")
        data = np.asarray(data, dtype=float).reshape(-1)
        self.context.set1dSourceData(data)

    def load_image(self, path):
        image = Image.open(path).convert("RGB")
        data = np.asarray(image, dtype=float)
        self.context.set2dSourceData(data)

    def images_for_view(self):
        return self.context.getImage()

    def data_for_view(self):
        return self.context.getData()

    def erase_at_canvas_point(self, click_x, click_y, displayed_width, displayed_height, radius):
        spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]

        if self.context.is1dModel():
            index = int((click_x / max(1, displayed_width)) * spectrum.shape[0])
            index = max(0, min(index, spectrum.shape[0] - 1))
            self.context.eraseSpectrumAtIndex(index)
            return

        if self.context.is2dModel():
            height, width = spectrum.shape[:2]
            display_row = int((click_y / max(1, displayed_height)) * height)
            display_col = int((click_x / max(1, displayed_width)) * width)
            display_row = max(0, min(display_row, height - 1))
            display_col = max(0, min(display_col, width - 1))

            row = (display_row + height // 2) % height
            col = (display_col + width // 2) % width
            self.context.eraseSpectrumAtPosition(row, col, radius)

    def erase_drag_segment(self, previous_x, previous_y, current_x, current_y, displayed_width, displayed_height, radius):
        spectrum = self.context.getData()[PaneType.INTERACTIVE_POWER_SPECTRUM]

        if self.context.is1dModel():
            previous_index = int((previous_x / max(1, displayed_width)) * spectrum.shape[0])
            current_index = int((current_x / max(1, displayed_width)) * spectrum.shape[0])
            previous_index = max(0, min(previous_index, spectrum.shape[0] - 1))
            current_index = max(0, min(current_index, spectrum.shape[0] - 1))
            self.context.eraseSpectrumBetweenIndexes(previous_index, current_index)
            return

        if self.context.is2dModel():
            height, width = spectrum.shape[:2]

            previous_display_row = int((previous_y / max(1, displayed_height)) * height)
            previous_display_col = int((previous_x / max(1, displayed_width)) * width)
            current_display_row = int((current_y / max(1, displayed_height)) * height)
            current_display_col = int((current_x / max(1, displayed_width)) * width)

            previous_display_row = max(0, min(previous_display_row, height - 1))
            previous_display_col = max(0, min(previous_display_col, width - 1))
            current_display_row = max(0, min(current_display_row, height - 1))
            current_display_col = max(0, min(current_display_col, width - 1))

            previous_row = (previous_display_row + height // 2) % height
            previous_col = (previous_display_col + width // 2) % width
            current_row = (current_display_row + height // 2) % height
            current_col = (current_display_col + width // 2) % width

            self.context.eraseSpectrumLineAtPosition(
                previous_row,
                previous_col,
                current_row,
                current_col,
                radius,
            )

    def begin_drag(self):
        self.context.beginSpectrumEdit()

    def end_drag(self):
        self.context.endSpectrumEdit()

    def undo(self):
        return self.context.undo()

    def redo(self):
        return self.context.redo()

    def reset(self):
        self.context.resetSpectrum()
```

## 呼び出し時の注意

1D専用メソッドは、現在の状態が1Dのときだけ呼んでください。

```python
if self.context.is1dModel():
    self.context.eraseSpectrumAtIndex(index)
```

2D専用メソッドは、現在の状態が2Dのときだけ呼んでください。

```python
if self.context.is2dModel():
    self.context.eraseSpectrumAtPosition(row, col, radius)
```

## 直接触らないもの

ViewやControllerでは、Model内部の配列を直接変更しないでください。

```python
sourceData
realPart
imaginaryPart
powerSpectrum
interactiveRealPart
interactiveImaginaryPart
interactivePowerSpectrum
inverseData
```

表示のために読む場合は`context.getData()`または`context.getImage()`を使います。
編集する場合は、必ず`FourierModelContext`の編集メソッドを使います。

## よく使うContextメソッド一覧

| やりたいこと | 呼ぶメソッド |
| --- | --- |
| 表示用数値取得 | `context.getData()` |
| 表示用画像取得 | `context.getImage()` |
| 現在Model名取得 | `context.getModelName()` |
| Undo数取得 | `context.getUndoCount()` |
| Redo数取得 | `context.getRedoCount()` |
| 1D判定 | `context.is1dModel()` |
| 2D判定 | `context.is2dModel()` |
| 1Dデータ設定 | `context.set1dSourceData(data)` |
| 2Dデータ設定 | `context.set2dSourceData(data)` |
| 1D成分削除 | `context.eraseSpectrumAtIndex(index)` |
| 1D成分復元 | `context.restoreSpectrumAtIndex(index)` |
| 1D範囲削除 | `context.eraseSpectrumBetweenIndexes(start, end)` |
| 1D範囲復元 | `context.restoreSpectrumBetweenIndexes(start, end)` |
| 1D値直接編集 | `context.editSpectrumValueAtIndex(index, real, imag)` |
| 1D現在値取得 | `context.getInteractiveSpectrumAtIndex(index)` |
| 2D成分削除 | `context.eraseSpectrumAtPosition(row, col, radius)` |
| 2D RGBペイント | `context.paintRgbSpectrumAtPosition(row, col, radius, rgb)` |
| 2D線分削除 | `context.eraseSpectrumLineAtPosition(startRow, startCol, endRow, endCol, radius)` |
| 2D線分RGBペイント | `context.paintRgbSpectrumLineAtPosition(startRow, startCol, endRow, endCol, radius, rgb)` |
| スペクトルリセット | `context.resetSpectrum()` |
| Undo | `context.undo()` |
| Redo | `context.redo()` |
| ドラッグ編集開始 | `context.beginSpectrumEdit()` |
| ドラッグ編集終了 | `context.endSpectrumEdit()` |
