import matplotlib.pyplot as plt
import numpy as np
import math


def rotate(angle, x, y):
    rotatex = math.cos(angle) * x - math.sin(angle) * y
    rotatey = math.cos(angle) * y + math.sin(angle) * x
    return rotatex, rotatey

print(math.radians(90))
print(math.radians(180))
print(math.radians(360))
a = math.radians(90)
print(a)
print(rotate(a, 6, 0))