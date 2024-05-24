import argparse
import os
import cv2
import statistics
import random

DIR = "/home/ubuntu/exp"
# DIR = "/tmp"

parser = argparse.ArgumentParser()
parser.add_argument('dirname')
args = parser.parse_args()

if __name__ == "__main__":
    DIR = DIR + "/" + args.dirname
    files = os.listdir(DIR)
    random.shuffle(files)
    num_images = 0
    diff_sum = 0
    measurements = []
    with open(args.dirname + ".csv", 'w') as outfd:
        outfd.write("frame#,groundtruth,detection,diff\n")
        for f in files:
            img = cv2.imread(os.path.join(DIR, f), 1)
            cv2.namedWindow('window', cv2.WINDOW_KEEPRATIO)
            cv2.imshow('window', img)
            cv2.resizeWindow('window', 1200, 1200)
            cv2.waitKey(50)
            try:
                gt_ts = int(input("Enter the timestamp: "))
            except ValueError:
                continue
            
            try:
                det_ts = round(float(f.split('.')[0]))
            except:
                print(f"Unable to process {f}")
                continue

            if num_images > 10:
                curr_avg = diff_sum / num_images
                stddev = statistics.stdev(measurements)
                diff = det_ts - gt_ts
                if abs(diff - curr_avg) > 2 * stddev:
                    try:
                        gt_ts_1 = str(input(f"Are you sure the timestamp is {gt_ts}? {curr_avg=} {stddev=} (y/n)"))
                    except ValueError:
                        continue
                    if gt_ts_1 == 'n':
                        try:
                            gt_ts = int(input("Enter the correct timestamp: "))
                        except ValueError:
                            continue

            diff = det_ts - gt_ts

            # det_ts = round(float(f.split('.')[0] + '.' + f.split('.')[1]) * 1000)
            print(gt_ts)

            measurements.append(diff)
            diff_sum += diff
            num_images += 1
            print(f"{num_images} images have been processed")
            print(f"Time difference: {diff} milliseconds.")
            print(f"Running average: {diff_sum / num_images}")
            line = f"{num_images},{gt_ts},{det_ts},{diff}\n"
            outfd.write(line)

