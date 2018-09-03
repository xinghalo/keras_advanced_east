import math
import glob
import cv2

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
    return centerx + r_x, centery + r_y


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
    x2, y2 = xy_rorate(theta, x + width, y, centerx, centery)
    x3, y3 = xy_rorate(theta, x, y + height, centerx, centery)
    x4, y4 = xy_rorate(theta, x + width, y + height, centerx, centery)

    return [x1, y1, x2, y2, x3, y3, x4, y4]

def format(origin_path, target_path):
    for filename in glob.glob(origin_path+'*.gt'):
        name = "".join(filename.strip('\n').split('/')[-1][:-3])

        with open(origin_path+name+'.gt', 'r', encoding='utf-8') as f:
            lines = f.readlines()

        labels = []
        for line in lines:
            content = line.strip('\n').split(' ')
            x = float(content[2])
            y = float(content[3])
            w = float(content[4])
            h = float(content[5])
            theta = float(content[6])

            labels.append(','.join(map(str, rec_rotate(x, y, w, h, theta)))+',###\n')

        with open(target_path+'txt/'+name+'.txt', 'w', encoding='utf-8') as f:
            for label in labels:
                f.write(label)

        img = cv2.imread(origin_path+name+'.JPG')
        cv2.imwrite(target_path+'image/'+name+'.JPG', img)



if __name__ == '__main__':
    format('/Users/xingoo/PycharmProjects/AdvancedEAST/data/MSRA-TD500/train/', '/Users/xingoo/PycharmProjects/AdvancedEAST/data/msra/')
    format('/Users/xingoo/PycharmProjects/AdvancedEAST/data/MSRA-TD500/test/', '/Users/xingoo/PycharmProjects/AdvancedEAST/data/msra/')