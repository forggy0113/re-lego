# re-lego workbook
Yet another lego helper

## Installation
I. 先安裝 conda 環境。

II. 使用 ```conda create -n {名稱} python=3.12``` 建立虛擬環境，再用 ```conda activate {名稱}``` 啟動環境。

III. 從 [Pytorch](https://pytorch.org/get-started/locally/) 網站安裝 `torch`。

IV. 執行 ```pip install -r requirements.txt``` 安裝所需依賴。

V. 執行 ```python run.py``` 開始遊戲。

## Known Issue
I. 需要將監控螢幕畫面設定為1920x1080，投影機畫面設定為1280x768，否則會導致畫面非預期錯誤。

II. 如果PyQt出現找不到icon/font資源時，請進入到 `./re-lego/src/ui/Ui_main.py` 更改路徑。

III. 著急開發，程式寫很爛，請多擔待。

