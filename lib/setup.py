from setuptools import setup, find_packages

setup(
    name='self-portrait',  # パッケージ名（pip listで表示される）
    version="0.0.1",  # バージョン
    description="津田塾大学学芸学部情報科学科の講義「情報科学C」で用いる似顔絵描画クラス",  # 説明
    author='Shohei Yokoyama',  # 作者名
    packages=find_packages(),  # 使うモジュール一覧を指定する
    license='MIT'  # ライセンス
)