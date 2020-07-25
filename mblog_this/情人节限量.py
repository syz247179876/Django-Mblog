from PIL import Image, ImageDraw, ImageFont
import os
font_size = 6  # 一个字所占像素的大小
text = "文文我爱你！"  # 文本


# 生成器函数
def character_generator(text):
    """
    不断读取text中的每个字
    :param text:
    :return:
    """
    while True:
        for i in range(len(text)):
            yield text[i]


def create_single_image(img_raw, font_size, generator_, img_array, index, font, draw, img_new):
    for y in range(0, img_raw.size[1], font_size):
        """对纵轴每隔font_size像素大小绘制字体"""
        for x in range(0, img_raw.size[0], font_size):
            draw.text((x, y), next(generator_), font=font, fill=img_array[x, y], direction=None)  # 用文字填充画布,对应的rgb颜色填充
    img_new.save("D:/syz/image2/wenwen_{}.jpeg".format(index))  # 转化为RGB类型，保存图片，因为每个图像都是由RGB组成


def create_all_image():
    font = ImageFont.truetype('D:/syz/方正黑体简体.TTF', font_size)  # 设置字体类型
    for i in range(1, len(os.listdir('D:/syz/image'))+1):
        img_path = "D:/syz/image/{}.jpg".format(i)  # 图像路径
        img_raw = Image.open(img_path)  # 读取图像对象
        img_array = img_raw.load()  # 捕获图像对象每一个像素值，是一个二位数组
        img_new = Image.new("RGB", img_raw.size, (0, 0, 0))  # 创建一个新的空白画布
        draw = ImageDraw.Draw(img_new)  # 绘制空白画布图像
        generator_ = character_generator(text)  # 生成器
        create_single_image(img_raw, 6, generator_, img_array, i, font, draw, img_new)


create_all_image()
