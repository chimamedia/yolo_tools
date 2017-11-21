# yoloの学習用ツール
Yoloの学習用のToolsです。自己責任でご使用ください。
PythonはPython 3で書いています。

+ BBox-Label-Tool.py：アノテーションソフト
+ inflate_images.py：画像を増やすプログラム
+ convert.py：Yoloで訓練するためのセットを作成
+ base.cfg：cfgファイルを構成するためのベースとなるもの（エポック数など変更するならここで）

# Usage
## BBox-Label-Tool.py
 python BBox-Label-Tool.py Folder

## inflate_image.py
 python inflate_image.py  InFolder (OutFolder)
 
※OutFolderを指定しない場合はobjフォルダが作成される。

## convert.py
 python convert.py InFolder (OutFolder) (LearningRatio)

※OutFolderはinflate_image.pyと同じ（指定していないときはobj）
※LearningRatioは0～1の値で指定しない場合は1:1

※ほかにYoloのプログラムなどもありますが、各自でビルドを推奨。一応、ディレクトリを構成例として。
