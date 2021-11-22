
import os
import os.path
import subprocess

import cv2
import numpy as np
import matplotlib.pyplot as plt

H, W = 3078, 5472

datasrc = 'dedun:/data/prosjekt/15619-04-Blaskjellbestand/BILDER TIL MASKINLÆRING/VIAME Output Data'

defaultconfig = {}

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
    def __init__(self, conf):
        self.config = conf

    def get(self):
        '''Download and upack the data'''
        if os.path.exists('images'):
            print('The "images" directory exists already - skipping!')
            return

        sp = subprocess.Popen(['rsync','-au',f'{datasrc}/'.replace(' ','\ '), 'tmp/'], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = sp.communicate()[0]

        datadirs = os.listdir('tmp')
        os.mkdir('masks')
        os.mkdir('images')

        for d in datadirs:
            with open(f'tmp/{d}/output_tracks.csv') as file:
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

            for (im, polys) in group_annotations(annotations):
                os.system(f'cp tmp/{d}/{im} images/')
                # TODO: get H,W from im
                mask = np.zeros((H,W))
                for poly in polys:
                    cv2.fillPoly(mask, [np.array(poly)], 1)
                cv2.imwrite('masks/'+im+'.png', mask * 255)

    def validate(self):
        '''Check data completeness and integrity'''
        pass

if __name__ == '__main__':
    d = Data(defaultconfig)
    d.get()
    d.validate()
