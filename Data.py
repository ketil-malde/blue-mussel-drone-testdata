
import os
import os.path

import cv2
import numpy as np
import matplotlib.pyplot as plt

H, W = 3078, 5472

datasrc = 'dedun:/data/deep/data//blue_mussel_drone_images/Bildeserie_2.zip'

def group_annotations(polys):
    '''Generator for images with all polygon annotations'''
    imgname = polys[0][1]
    cur = [polys[0][-1]]

    for pt in polys[1:]:
        if pt[1] == imgname:
            cur.append(pt[-1])
        else:
            print('Writing: ', imgname, end='\r')
            yield ((imgname,cur))
            imgname = pt[1]
            cur = [pt[-1]]
    print()

class Data:
    def __init__(self, conf, mypath):
        self.config = conf
        self.mypath = mypath

    def get(self):
        '''Download and upack the data'''
        if os.path.exists('images'):
            print('The "images" directory exists already - skipping data download!')
            return

        os.system(f'scp {datasrc} .')
        os.system(f'unzip {os.path.basename(datasrc)}')
        with open(f'Bildeserie_2/output_tracks.csv') as file:
            lines = [line.rstrip() for line in file.readlines() if line[0] != '#']

        annotations = []
        for line in lines:
            fields = line.split(',')
            no, imgname, bbox, anno = int(fields[0]), fields[1], [int(f) for f in fields[3:7]], fields[9]
            if anno != 'M.edulis': continue
            poly = fields[11].split()
            polytype = poly[0]
            points = [[int(poly[2*i+1]), int(poly[2*i+2])] for i in range((len(poly)-1)//2)]
            assert(points[0]==points[-1])
            annotations.append( (no, imgname, bbox, anno, polytype, points) )

        os.mkdir('masks')
        os.mkdir('images')
        for (im, polys) in group_annotations(annotations):
            os.system(f'cp Bildeserie_2/{im} images/')
            mask = np.zeros((H,W))
            for poly in polys:
                cv2.fillPoly(mask, [np.array(poly)], 1)
            cv2.imwrite('masks/'+im+'.png', mask * 255)

    def validate(self):
        '''Check data completeness and integrity'''
        pass

if __name__ == '__main__':
    d = Data()
    d.get()
    d.validate()
