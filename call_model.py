#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
call_model_sync.py

本程式示範如何使用同一個共享 Queue，同步調用兩個不同模型進行推理：
    1. 從共享 Queue 取得任務，任務格式為字典，例如：
       {"model": "modelA", "data": ...} 或 {"model": "modelB", "data": ...}
    2. 根據任務中的 "model" 欄位，直接同步呼叫對應的推理函式。
    
注意：
    - 若收到 None 則退出程式。
    - 推理函式內部皆採用同步呼叫方式，調用完畢才會處理下一筆任務。
"""

import os
import sys
import time
import logging
import numpy as np
from multiprocessing.managers import BaseManager
import tritonclient.grpc as grpcclient

# 設定 logging 輸出格式
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# 定義連線共享 Queue 的 Manager 類別
class QueueManager(BaseManager):
    pass

def connect_shared_queue():
    """
    連線至共享 Queue，透過環境變數取得連線資訊
    """
    queue_address = os.environ.get("QUEUE_ADDRESS", "localhost")
    queue_port = int(os.environ.get("QUEUE_PORT", "50000"))
    queue_authkey = os.environ.get("QUEUE_AUTHKEY", "abc").encode()

    QueueManager.register('get_queue')
    try:
        manager = QueueManager(address=(queue_address, queue_port), authkey=queue_authkey)
        manager.connect()
        logging.info("成功連線至共享 Queue")
        return manager.get_queue()
    except Exception as e:
        logging.error(f"連線共享 Queue 失敗: {e}")
        sys.exit(1)

def inference_model_a(data):
    """
    同步調用模型 A 進行推理
    參數:
        data: 輸入資料 (假設為 NumPy 陣列)
    回傳:
        推理結果 (NumPy 陣列)
    """
    triton_url = os.environ.get("TRITON_URL_A", "localhost:8001")
    model_name = os.environ.get("TRITON_MODEL_A", "model_a")
    model_version = os.environ.get("TRITON_MODEL_VERSION_A", "")

    try:
        client = grpcclient.InferenceServerClient(url=triton_url)
    except Exception as e:
        logging.error(f"建立 Triton 客戶端 (模型 A) 失敗: {e}")
        return None

    try:
        input_name = "INPUT_A"   # 請依實際模型修改
        output_name = "OUTPUT_A" # 請依實際模型修改
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        infer_input = grpcclient.InferInput(input_name, data.shape, "FP32")
        infer_input.set_data_from_numpy(data)
        infer_output = grpcclient.InferRequestedOutput(output_name)
        result = client.infer(
            model_name=model_name,
            inputs=[infer_input],
            outputs=[infer_output],
            model_version=model_version if model_version else None
        )
        output_data = result.as_numpy(output_name)
        logging.info("模型 A 推理成功")
        return output_data
    except Exception as e:
        logging.error(f"模型 A 推理失敗: {e}")
        return None

def inference_model_b(data):
    """
    同步調用模型 B 進行推理
    參數:
        data: 輸入資料 (假設為 NumPy 陣列)
    回傳:
        推理結果 (NumPy 陣列)
    """
    triton_url = os.environ.get("TRITON_URL_B", "localhost:8001")
    model_name = os.environ.get("TRITON_MODEL_B", "model_b")
    model_version = os.environ.get("TRITON_MODEL_VERSION_B", "")

    try:
        client = grpcclient.InferenceServerClient(url=triton_url)
    except Exception as e:
        logging.error(f"建立 Triton 客戶端 (模型 B) 失敗: {e}")
        return None

    try:
        input_name = "INPUT_B"   # 請依實際模型修改
        output_name = "OUTPUT_B" # 請依實際模型修改
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        infer_input = grpcclient.InferInput(input_name, data.shape, "FP32")
        infer_input.set_data_from_numpy(data)
        infer_output = grpcclient.InferRequestedOutput(output_name)
        result = client.infer(
            model_name=model_name,
            inputs=[infer_input],
            outputs=[infer_output],
            model_version=model_version if model_version else None
        )
        output_data = result.as_numpy(output_name)
        logging.info("模型 B 推理成功")
        return output_data
    except Exception as e:
        logging.error(f"模型 B 推理失敗: {e}")
        return None

def main():
    """
    主程式流程：
        1. 連線共享 Queue
        2. 從共享 Queue 取得任務，依據 "model" 欄位同步呼叫對應的推理函式
        3. 推理結果可進一步處理或回傳
    """
    shared_queue = connect_shared_queue()

    logging.info("開始同步監聽共享 Queue 以取得任務...")
    while True:
        try:
            # 從共享 Queue 取得任務，設定 timeout 避免無限等待
            task = shared_queue.get(timeout=10)
        except Exception as e:
            logging.error(f"從共享 Queue 取得任務失敗或逾時: {e}")
            break

        # 收到 None 表示退出訊號
        if task is None:
            logging.info("收到退出訊號，結束同步推理服務")
            break

        model_type = task.get("model")
        data = task.get("data")
        if model_type == "modelA":
            logging.info("同步調用模型 A")
            result = inference_model_a(data)
            logging.info(f"模型 A 推理結果: {result}")
        elif model_type == "modelB":
            logging.info("同步調用模型 B")
            result = inference_model_b(data)
            logging.info(f"模型 B 推理結果: {result}")
        else:
            logging.error(f"未知的模型類型: {model_type}")

        # 根據需求，可在處理下一筆任務前加入延遲
        time.sleep(0.1)

if __name__ == "__main__":
    main()
