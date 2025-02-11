import subprocess
import multiprocessing
import time

def run_pygame():
    subprocess.run(["python", "pygame.py"])

def run_opencv():
    subprocess.run(["python", "opencv.py"])

def run_call_model():
    subprocess.run(["python", "call_model.py"])

def run_docker_command():
    subprocess.run(["bash", "-c", "your_docker_command_here"])

if __name__ == "__main__":
    # 先執行 PyQt，等待其結束
    subprocess.run(["python", "main.py"])

    # 使用 multiprocessing 啟動其餘四個功能
    processes = [
        multiprocessing.Process(target=run_pygame),
        multiprocessing.Process(target=run_opencv),
        multiprocessing.Process(target=run_call_model),
        multiprocessing.Process(target=run_docker_command)
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()  # 等待所有子程序結束
