import os
import sys
import cv2
import glob
import numpy as np

def img2mp4(paths, pathOut, fps):
	frame_array = []
	for idx, path in enumerate(paths): 
		ff = np.fromfile(path, np.uint8)
		img = cv2.imdecode(ff,1)
		height, width, layers = img.shape
		size = (width, height)
		frame_array.append(img)
	out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'mp4v'), fps, size)
	for i in range(len(frame_array)):
		out.write(frame_array[i])
	out.release()

input_path = 'C:\\Users\\sgh20\\OneDrive\\바탕 화면\\motion'
output_path = 'C:\\Users\\sgh20\\OneDrive\\바탕 화면\\motion\\results.mp4'
set_fps = 60

paths = sorted(glob.glob(input_path + '\\*.jpg'))
paths = [os.path.join(input_path, path) for path in paths]
print(str(len(paths)))
print('[Timelapser] Strat!...')
if len(paths) == 0:
	print('[Timelapser] No File. Drop.')
else:
	img2mp4(paths, output_path, set_fps)
print('[Timelapser] Done!')