from PIL import Image
from PIL import ImageDraw
import math

image_path = '/Users/xingoo/PycharmProjects/AdvancedEAST/data/MSRA-TD500/train/IMG_0064.JPG'
gt_path = '/Users/xingoo/PycharmProjects/AdvancedEAST/data/MSRA-TD500/train/IMG_0064.gt'

with open(gt_path, 'r') as f:
    lines = f.readlines()


def rotate(angle, x, y):
    """
    基于原点的弧度旋转

    :param angle:   弧度
    :param x:       x
    :param y:       y
    :return:
    """
    rotatex = math.cos(angle) * x - math.sin(angle) * y
    rotatey = math.cos(angle) * y + math.sin(angle) * x
    return rotatex, rotatey

def xy_rorate(theta, x, y, centerx, centery):
    """
    针对中心点进行旋转

    :param theta:
    :param x:
    :param y:
    :param centerx:
    :param centery:
    :return:
    """
    r_x, r_y = rotate(theta, x - centerx, y - centery)
    return centerx+r_x, centery+r_y

def rec_rotate(x, y, width, height, theta):
    """
    传入矩形的x,y和宽度高度，弧度，转成QUAD格式
    :param x:
    :param y:
    :param width:
    :param height:
    :param theta:
    :return:
    """
    centerx = x + width / 2
    centery = y + height / 2

    x1, y1 = xy_rorate(theta, x, y, centerx, centery)
    x2, y2 = xy_rorate(theta, x+width, y, centerx, centery)
    x3, y3 = xy_rorate(theta, x, y+height, centerx, centery)
    x4, y4 = xy_rorate(theta, x+width, y+height, centerx, centery)

    return x1, y1, x2, y2, x3, y3, x4, y4



with Image.open(image_path) as im:
    draw = ImageDraw.Draw(im)
    for line in lines:
        line = line.strip('\n').split(' ')
        x = int(line[2])
        y = int(line[3])
        width = int(line[4])
        height = int(line[5])

        theta = float(line[6])

        x1, y1, x2, y2, x3, y3, x4, y4 = rec_rotate(x, y, width, height, theta)


        draw.line([tuple([x1, y1]),
                   tuple([x2, y2]),
                   tuple([x4, y4]),
                   tuple([x3, y3]),
                   tuple([x1, y1])
                   ],
                  width=2, fill='green')
    im.show()