# メモ

## 舞台

```
■■■■■■■■■■■
■□□□□□□□□□■
■□□□□□□□□□■
■□□□□□□□□□■
■□□□□□□□□□■
■□□□□□□□□□■
■■■■■■■■■■■
```

印|特性
--|----
`■`|ぶつかると死ぬ
`□`|移動できる

## どうやってヘビの体の位置を算出するか

　ヘビは常に動く。自動的に移動する。そのたびに体の位置が変化する。どうやってヘビの体の位置を算出するか。以下3要素がキモ。

* ヘビの頭（先頭）
* ヘビの体の長さ
* 進行履歴

1. ヘビ頭の現在位置を記録する
1. ヘビ体は1の位置を追従する

```python
class World:
    W = 32
    H = 24
class Snake:
    Head = (15, 12)
    Body = [Head]
```

* 頭が(15, 12), 体1が(15, 13)にあったとする
* 次は右に一歩進むとする
* 頭が(16, 12), 体1が(15, 12)に移動する

　体1は前回頭がいた場所である。

　つまり、体の長さだけ配列を持ち、それぞれの位置に存在する座標点を代入する。次にどこかへ進んだときは、それぞれの体の座標は、自分のひとつ前の体の座標となる。

# 拡張ルール案

* 餌を1個たべると1個ウンコを出す
    * ウンコに触れると死亡
* ウンコは一定時間で土に還る
    * 一定量のウンコを土に返すと土壌改良される
        * 土壌改良されると1度に出す餌が増える
            * 「土に還る速度＜ウンコ排出速度」になる
                * やがてウンコで満ちて死亡する
* 自分の尾を食べる（ウロボロス）
    * 餌、糞に触れないまま尾を食えばウロボロス・クリアとなる
        * 
    * 
# 必要な画像

* 頭: 上,左
* 体: 上,左
* 尾: 上,左
* 餌
* メニュー用
	* 餌
* 死亡顔

　頭、体、尾は`blt()`の`w`,`h`を負数にすることで下, 右方向の画像を作る。

## 拡張

### ゲーム性

* 糞
* メニュー用
	* 糞

### アニメ

* 目: 上, 左（餌がある方向を向く）
* 口(餌がある一歩手前で口を開ける)
* 舌（餌に絶対届かないとき稀に舌を伸ばす）
* 死亡顔

# ゲームシーン切替

```python
scene.update()
scene.draw()
```
```python
class App:
    def __init__(self):
        pyxel.init()
        pyxel.run(self.update, self.draw)
    def update(self): scene.update()
    def draw(self): scene.draw()
```
```python
Scenes = [Start(), Play(), GameOver()]
```

* Start -> Play
    * 方向キーを渡す
* Play -> GameOver
    * 得点を渡す
* GameOver -> Start
    * プレイモードを渡す

　以下のようなことができる構造であること。

* 各シーンから別シーンへ遷移できること
* 各シーンへ引数を渡せること
