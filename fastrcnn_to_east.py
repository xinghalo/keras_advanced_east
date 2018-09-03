import sys
import os
import xmltodict
import numpy as np
from tqdm import tqdm

FILE_PATH = '/Users/xingoo/PycharmProjects/AdvancedEAST/data/labels2'

def readxml(path):
    gtboxes=[]
    imgfile = ''
    with open(path,'rb') as f :
        xml = xmltodict.parse(f)
        bboxes = xml['annotation']['object']
        if(type(bboxes)!=list):
            x1 = bboxes['bndbox']['xmin']
            y1 = bboxes['bndbox']['ymin']
            x2 = bboxes['bndbox']['xmax']
            y2 = bboxes['bndbox']['ymax']
            gtboxes.append((int(x1),int(y1),int(x2),int(y2)))
        else:
            for i in bboxes:
                x1 = i['bndbox']['xmin']
                y1 = i['bndbox']['ymin']
                x2 = i['bndbox']['xmax']
                y2 = i['bndbox']['ymax']
                gtboxes.append((int(x1),int(y1),int(x2),int(y2)))

        imgfile = xml['annotation']['filename']
    return np.array(gtboxes),imgfile

if __name__ == '__main__':
    file_list = os.listdir(FILE_PATH)
    for file, _ in zip(file_list, tqdm(range(len(file_list)))):
        name = "".join(file[:-4])
        boxes, _ = readxml(FILE_PATH+'/'+file)

        with open('/Users/xingoo/PycharmProjects/AdvancedEAST/data/labels/'+name+'.txt', 'w', encoding='utf-8') as f:
            for box in boxes:
                line = map(str,[box[0], box[1], box[2], box[1], box[0], box[3], box[2], box[3]])
                f.write(",".join(line)+',\n')