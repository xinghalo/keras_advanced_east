import os,sys
from PIL import Image
from PIL import ImageDraw

with open('/Users/xingoo/PycharmProjects/AdvancedEAST/data/msra/txt/IMG_0030.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(lines)

with Image.open('/Users/xingoo/PycharmProjects/AdvancedEAST/data/msra/image/IMG_0030.JPG') as im:
    draw = ImageDraw.Draw(im)
    for line in lines:
        line = line.strip('\n').split(',')

        draw.line([tuple([float(line[0]), float(line[1])]),
                   tuple([float(line[2]), float(line[3])]),
                   tuple([float(line[6]), float(line[7])]),
                   tuple([float(line[4]), float(line[5])]),
                   tuple([float(line[0]), float(line[1])])
                   ],
                  width=2, fill='green')
    im.show()