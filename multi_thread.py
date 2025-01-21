import threading
import time

# Event object used to signal threads to start
start_event = threading.Event()

def pyqt_thread(is_logged_in):
    print("First thread (pyqt_thread) is running")
    # Simulate some work with sleep
    time.sleep(2)
    if is_logged_in:
        print("Login successful in pyqt_thread")
        start_event.set()  # Signal other threads to start
    else:
        print("Login failed in pyqt_thread")

def pygame_thread():
    # Wait for the pyqt_thread to signal
    start_event.wait()
    print("Second thread (pygame_thread) is running")
    # Simulate some work with sleep
    time.sleep(2)
    print("Second thread (pygame_thread) has finished work")

def cv_thread():
    start_event.wait()
    print("Third thread (cv_thread) is running")
    # Simulate some work with sleep
    time.sleep(2)
    print("Third thread (cv_thread) has finished work")

def call_model_thread():
    start_event.wait()
    print("Fourth thread (call_model_thread) is running")
    # Simulate some work with sleep
    time.sleep(2)
    print("Fourth thread (call_model_thread) has finished work")

# Example usage
is_logged_in = True # Set to True or False based on the login result

# Create threads
thread1 = threading.Thread(target=pyqt_thread, args=(is_logged_in,))
thread2 = threading.Thread(target=pygame_thread)
thread3 = threading.Thread(target=cv_thread)
thread4 = threading.Thread(target=call_model_thread)

# Start and join threads
thread1.start()
thread1.join()

# Start other threads after thread1 has completed
thread2.start()
thread3.start()
thread4.start()

thread2.join()
thread3.join()
thread4.join()

print("All threads have finished")
