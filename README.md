# re-lego workbook

main 主要是由multi_process 啟動 每個process都有一個自己的直譯器

-

pyqt.py -> 登入後 自動關閉 於db中 留一個 player_status == true

後面由multi_process.py啟動 (待完善)

pygame.py -> 啟動，於遊戲關閉時將db內 player_status == flase 關閉其餘process 包含自己 (待完善)

start_infer.sh -> 啟動docker推理服務 (待創建)

opencv.py -> 啟動 (待創建)

call_model.py -> 啟動 (待創建)

-

腳本內之物件描述 可用python寫成物件導向實現 (可用，待創建)
