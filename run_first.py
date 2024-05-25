import os
import cv2
import argparse

path = 'maps'
out_path = 'output'
os.makedirs(path, exist_ok=True)
os.makedirs(out_path, exist_ok=True)

for file in os.listdir(path):
    fname = file.split('.')[0]
    fext = file.split('.')[1]
    if fext == 'pgw':

        img = cv2.imread(os.path.join(path, fname + '.png'))
        y, x, _ = img.shape
        with open(path + '/' + file) as fread:
            trans = fread.readlines()
        
        a, d, b, e, c, f = trans

        scale_lot, scale_lat = float(a), float(e)
        upper_lot, upper_lat = float(c), float(f)
        lower_lot, lower_lat = scale_lot * x + upper_lot, scale_lat * y + upper_lat

        print((upper_lot, upper_lat), (lower_lot, lower_lat))
        new_name = str(lower_lat) + '_' + str(upper_lot) + '__' + str(upper_lat) + '_' + str(lower_lot) + '.png'
        cv2.imwrite(os.path.join(out_path, new_name), img)
