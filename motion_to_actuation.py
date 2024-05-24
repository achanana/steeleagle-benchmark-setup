import time

if __name__ == "__main__":
    while True:
        print(f"{round(time.time() * 1000)}", end='\r')

