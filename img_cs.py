# coding:utf-8
__author__ = 'xxj'

import cv2
import numpy as np
import time

bg_img_rgb = cv2.imread("bg_img.jpg", 1)    # np.array类型（1,3,4均为彩色图片）
bg_img_gray = cv2.cvtColor(bg_img_rgb, cv2.COLOR_BGR2GRAY)    # cvtColor()对背景图片进行色彩空间的转换方法(转换为灰度)
# cv2.imwrite('bg_img_gray.jpg', bg_img_gray)    # 保存图片
slider_img_rgb = cv2.imread('slider_img.png', 0)    # 滑块图片也是灰度图片（用于在背景图片中查询）

w, h = slider_img_rgb.shape[::-1]
print '滑块图片的宽和高：', w, h
res = cv2.matchTemplate(bg_img_gray, slider_img_rgb, cv2.TM_CCOEFF_NORMED)    # cv2.matchTemplate()方法从背景图片中查找缺陷图片的位置

# 适用于单独的图片或者阈值一样的图片
# threshold = 0.3299 #res大于70% threshold就是阈值（阈值越低匹配出来的越多，阈值越高匹配出来的越少，所以需要一个精准的阈值来获取准确的位置）
# loc = np.where(res >= threshold)

# 由于验证码的图片不是单一的一种背景，是多样化的背景图片，所以背景不一样，缺陷位置的颜色也不一样，所以阈值也是不一样（总而言之，就是阈值是变动的，不是固定的，所以需要一种方法获取准确的阈值：就是二分法）
# 使用二分法查找阈值的精确值   (阈值的精确值是准确查找到目标图像的核心)
run = 1
L = 0
R = 1

while run < 20:
    run += 1
    threshold = (R + L) / 2.0
    print 'threshold：', threshold
    if threshold < 0:
        print('Error')
        # return None
    loc = np.where(res >= threshold)
    print 'loc[1]的长度：', len(loc[1])
    if len(loc[1]) > 1:
        L += (R - L) / 2.0
    elif len(loc[1]) == 1:
        print('目标区域起点x坐标为：%d' % loc[1][0])
        break
    elif len(loc[1]) < 1:
        R -= (R - L) / 2.0

# cv2.imshow("bg_img_rgb", bg_img_rgb)    # 显示图片

for pt in zip(*loc[::-1]):
    # print 'pt值：', pt     # pt代表的是左上角的坐标
    cv2.rectangle(bg_img_rgb, pt, (pt[0] + w, pt[1] + h), (7, 279, 151), 2)
cv2.imshow('Dectected', bg_img_rgb)    # 查找出来类似的所有背景图片
cv2.imshow("slider_img_rgb", slider_img_rgb)    # 灰度的滑块图片

cv2.imwrite('bg_img_gray_yellow.jpg', bg_img_rgb)

print 'loc：', loc
print 'loc[1][0]：', loc[1][0]
cv2.waitKey(0)