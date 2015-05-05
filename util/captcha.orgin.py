#!/usr/bin/python
#build by evan
#-*- coding=utf-8 -*-
import random, Image, ImageDraw, ImageFont, ImageFilter


_letter_cases = "23456789abcdefghjkmnpqrstuvwxy"
_upper_cases = _letter_cases.upper()
_numbers = ''.join(map(str, range(3, 10)))
init_chars = ''.join((_letter_cases, _upper_cases, _numbers))

def CreatePPCaptcha(size=(180, 50),
                         chars = init_chars,
                         img_type = "JPG",
                         mode = "RGBA",
                         bg_color = (255, 255, 255),
                         font_size = (50, 60),
                         font_type = './static/assets/fonts/captcha.ttf',
                         length = 4,
                         draw_lines = True,
                         n_line = (3, 6),
                         draw_points = True,
                         point_chance = 2):

    bg_color=(random.randint(157,255), random.randint(157,255), random.randint(157,255))

    width, height = size
    img = Image.new(mode, size, bg_color)
    draw = ImageDraw.Draw(img)

    def get_chars():
        return random.sample(chars, length)

    def create_lines():
        line_num = random.randint(*n_line) 
        for i in range(line_num):
            begin = (random.randint(0, size[0]), random.randint(0, size[1]))

            end = (random.randint(2, size[0]), random.randint(2, size[1]))
            draw.line([begin, end], fill=(random.randint(0,156),random.randint(0,156),random.randint(0,156)), width=random.randint(1,4))

    def create_points():
        for w in xrange(width):
            for h in xrange(height):
                tmp = random.randint(0, 100)
                if tmp < point_chance:
                  font = ImageFont.truetype(font_type, 30)
                  draw.text((w, h), "*", font=font, fill=(random.randint(200,255),random.randint(200,255),random.randint(200,255)))

    def create_strs():
        c_chars = get_chars()
        for i in xrange(length):
            font = ImageFont.truetype(font_type, random.randint(*font_size))
            c = c_chars[i]
            draw.text((random.randint(35,50)*i, random.randint(0,5)), c,
                      font=font, fill=(random.randint(0,156),random.randint(0,156),random.randint(0,156)))

        return ''.join(c_chars)

    if draw_points:
        create_points()

    if draw_lines:
        create_lines()


    params = [1 - float(random.randint(1, 2)) / 100,
              0,
              0,
              0,
              1 - float(random.randint(1, 10)) / 100,
              float(random.randint(1, 2)) / 500,
              0.001,
              float(random.randint(1, 2)) / 500
              ]
    img = img.transform(size, Image.PERSPECTIVE, params)
    #img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)

    strs = create_strs()
    return img, strs


if __name__ == "__main__":
    code_img = CreatePPCaptcha(font_type = '../static/assets/fonts/captcha.ttf', img_type = 'PNG')
    print code_img[1]
    code_img[0].save("mycode.png", "PNG")