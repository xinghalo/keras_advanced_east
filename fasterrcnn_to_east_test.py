import os,sys
from PIL import Image
from PIL import ImageDraw

with open('/Users/xingoo/PycharmProjects/AdvancedEAST/data/labels/img_1016.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(lines)

with Image.open('/Users/xingoo/PycharmProjects/AdvancedEAST/data/images2/img_1016.jpg') as im:
    draw = ImageDraw.Draw(im)
    for line in lines:
        line = line.strip('\n').split(',')

        draw.line([tuple([int(line[0]), int(line[1])]),
                   tuple([int(line[2]), int(line[3])]),
                   tuple([int(line[6]), int(line[7])]),
                   tuple([int(line[4]), int(line[5])]),
                   tuple([int(line[0]), int(line[1])])
                   ],
                  width=5, fill='green')
    im.show()
