# coding:utf-8
__author__ = 'xxj'

from PIL import Image, ImageEnhance
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import WebDriverException
import cv2
import easing
import numpy as np
from io import BytesIO
import time, requests
from numpy import array


def get_zoom(bg_io, slider_io):
    bg_img = Image.open(bg_io)  # 背景图片对象
    slider_img = Image.open(slider_io)  # 滑块图片对象

    bg_img.save('bg_img.jpg')    # 保存背景图片
    slider_img.save('slider_img.png')    # 保存滑块图片

    size_loc = bg_img.size
    print '背景图片的大小：', size_loc
    zoom = 480 / int(size_loc[0])  # 320是由于易盾验证码背景图片的宽为320
    print 'zoom的值：', zoom
    return zoom


def get_slider_offset_from_diff_image(diff):    # diff是滑块图片对象(get_slider_offset_from_diff_image()方法中：对于单张图片而言，通过滑块和透明背景图之间的rgb不同获取到单张图片中滑块的偏移量。)
    '''
    获取图片的偏移量()
    :param diff: 图片对象
    :return:滑块图片的偏移量
    '''
    im = array(diff)    # 可以将图片对象通过array()方法转换为图片对象的宽、高、rgb
    # print im
    width, height = diff.size
    # print '宽和高：', width, height
    diff = []     # 存储图片中每一列中属于滑块图片的j值。然后从diff列表中获取最小j值就是该滑块图片的偏移量
    for i in range(height):    # 高
        for j in range(width):    # 宽
            # black is not only (0,0,0)
            # print 'i;j：', i, j
            # print 'im[i, j, 0]：', im[i, j, 0]    # r
            # print 'im[i, j, 1]：', im[i, j, 1]    # g
            # print 'im[i, j, 2]：', im[i, j, 2]    # b
            if im[i, j, 0] > 15 or im[i, j, 1] > 15 or im[i, j, 2] > 15:    # 获取到的每一个像素点对应颜色的rgb值（删选出属于滑块的像素）   （从左边往右边遍历，获取到第一个满足该条件的像素j值）
                diff.append(j)
                break
    print 'diff的值：', diff
    return min(diff)


def slider_offset():
    bg_img = 'bg_img.jpg'
    slider_img = 'slider_img.png'
    bg_img_rgb = cv2.imread(bg_img, 1)  # np.array类型（1,3,4均为彩色图片）
    bg_img_gray = cv2.cvtColor(bg_img_rgb, cv2.COLOR_BGR2GRAY)  # cvtColor()对背景图片进行色彩空间的转换方法(转换为灰度)
    # cv2.imwrite('bg_img_gray.jpg', bg_img_gray)    # 保存图片
    slider_img_rgb = cv2.imread(slider_img, 0)  # 滑块图片也是灰度图片（用于在背景图片中查询）

    w, h = slider_img_rgb.shape[::-1]
    print '滑块图片的宽和高：', w, h
    res = cv2.matchTemplate(bg_img_gray, slider_img_rgb, cv2.TM_CCOEFF_NORMED)  # cv2.matchTemplate()方法从背景图片中查找缺陷图片的位置

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
        # print 'threshold：', threshold
        if threshold < 0:
            print('Error')
            return None
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
    # cv2.imshow('Dectected', bg_img_rgb)  # 查找出来类似的所有背景图片
    # cv2.imshow("slider_img_rgb", slider_img_rgb)  # 灰度的滑块图片
    print 'loc：', loc
    print 'loc[1][0]：', loc[1][0]
    # cv2.waitKey(0)
    return loc[1][0]


# def get_tracks(distance):
#     distance += 20
#     v = 0
#     t = 0.2
#     forward_tracks = []
#     current = 0
#     mid = distance * 3 / 5
#     while current < distance:
#         if current < mid:
#             a = 2
#         else:
#             a = -3
#         s = v * t + 0.5 * a * (t ** 2)
#         v = v + a * t
#         current += s
#         forward_tracks.append(round(s))
#
#     back_tracks = [-3, -3, -2, -2, -2, -2, -2, -1, -1, -1]
#     return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}


def fake_drag(browser, knob, offset):
    '''
    模拟人性的滑动行为（防止被识别为机器行为）
    :param browser: 游览器对象
    :param knob: 移动滑块对象
    :param offset: 移动滑块移动的距离
    :return:
    '''
    offsets, tracks = easing.get_tracks(offset, 20, 'ease_out_expo')    # 获取一种人性行为的滑动规则（总体参试一下几种滑动规则，还是ease_out_expo()该方法正确度比较高）
    print 'offsets：', offsets
    print 'tracks：', tracks    # tracks是运动轨迹列表
    ActionChains(browser).click_and_hold(knob).perform()
    for x in tracks:
        ActionChains(browser).move_by_offset(x, 0).perform()
    # ActionChains(browser).pause(0.5).release().perform()
    ActionChains(browser).release().perform()


def slider_captcha(wait, driver):
    bg_img_obj = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_bg-img')))  # 背景图片
    slider_img_obj = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'yidun_jigsaw')))  # 滑块图片
    bg_img_obj = driver.find_element_by_xpath('//img[@class="yidun_bg-img"]')
    slider_img_obj = driver.find_element_by_xpath('//img[@class="yidun_jigsaw"]')
    bg_picture_link = bg_img_obj.get_attribute('src')    # 背景图片url
    slider_picture_link = slider_img_obj.get_attribute('src')    # 滑块图片url
    print '背景图片的url：', bg_picture_link  # jpg
    print '滑块图片的url：', slider_picture_link  # png

    # print '测试大小：', bg_img_obj.size, bg_img_obj.location, bg_img_obj

    bg_io = BytesIO(requests.get(bg_picture_link).content)
    slider_io = BytesIO(requests.get(slider_picture_link).content)

    zoom = get_zoom(bg_io, slider_io)  # 获取zoom值的接口
    # 对于wangyiyun这个网站而言虽然使用的是易盾验证码，获取到的背景图片大小是488，但是实际出现的验证码的背景图片是355。所以需要通过zoom值来（上面方法无法获取实际背景图大小）
    zoom = 355 / 488.0    # 目的是为了偏移量大小的缩放。

    # im = Image.open(slider_io)
    # slider_offset1 = get_slider_offset_from_diff_image(im)
    # print '滑块偏移量：', slider_offset1

    distance = slider_offset()  # 距离    (核心部分)      获取背景图片的偏移量接口

    # # tracks = get_tracks((distance + 7) * zoom)
    # # print 'tracks：', tracks
    # distance = (distance + 7) * zoom    # 这里为什么要在获取到的缺陷位置的偏移量上再加一个数值(这个值是一个误差值，也可以理解为线框左边线条所占有的长度)（易盾网站测试时的设置方案）
    distance = distance * zoom     # 这里是网易云网站的偏移量的设置方案    （根据实际出现验证码的背景图片大小的偏移量）
    print '偏移量：', distance

    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'yidun_slider')),
                        message='yidun_slider not exist...')  # 滑块对象
    slider = driver.find_element_by_xpath('//div[@class="yidun_slider"]')
    fake_drag(driver, slider, distance)    # 滑块滑动轨迹接口

    # try:
    #     failure = wait.until(
    #         EC.text_to_be_present_in_element((By.CLASS_NAME, 'yidun_tips__text'), '向右滑动滑块填充拼图'))
    #     print('验证成功')
    # except:
    #     print('验证失败')

    time.sleep(2)


def selenium_login():
    url = 'http://dun.163.com/trial/jigsaw'
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        executable_path=r'C:\Users\xj.xu\Downloads\chromedriver_win32\chromedriver.exe',
        chrome_options=chrome_options)
    wait = WebDriverWait(driver, 20)
    driver.get(url)
    time.sleep(5)
    slider_captcha(wait, driver)     # 滑块验证码接口


def main():
    selenium_login()


if __name__ == '__main__':
    main()