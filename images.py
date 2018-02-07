# coding: utf-8
"""
IMAGES:

    A module for modifying images.
"""
from PIL import Image, ImageDraw, ImageFont, ImageChops


def equate_images(img1, img2):
    """
    Returns a 2-tuple of the given images but
    set to the same size as each other.

    :param img1: Image, first image to set equal in size
    :param img2: Image, second image to set equal in size
    :return: 2-tuple(Image, Image), images set to equal sizes
    """
    img1 = img1.convert('RGBA')
    img2 = img2.convert('RGBA')
    w1, h1 = img1.size
    w2, h2 = img2.size

    if w1 != w2 or h1 != h2:
        bg_size = max(w1, w2), max(h1, h2)
        bg = Image.new(mode='RGBA', size=bg_size, color=(255, 255, 255, 0))

        if img1.size == bg_size:
            x = w1/2 - w2/2
            y = h1/2 - h2/2
            bg.paste(img2, (x, y))
            img2 = bg
        elif img2.size == bg_size:
            x = w2/2 - w1/2
            y = h2/2 - h1/2
            bg.paste(img1, (x, y))
            img1 = bg
        else:
            bg_img1 = bg
            bg_img2 = bg_img1.copy()
            x_mid = bg_size[0]/2
            y_mid = bg_size[1]/2
            x1 = x_mid - img1.size[0]/2
            y1 = y_mid - img1.size[1]/2
            x2 = x_mid - img2.size[0]/2
            y2 = y_mid - img2.size[1]/2
            bg_img1.paste(img1, (x1, y1))
            bg_img2.paste(img2, (x2, y2))
            img1 = bg_img1
            img2 = bg_img2

    return img1, img2


def overlay(front, back, equate=True):
    """
    Overlays front image on top of back image.
    ~
    Preserves alpha values of both images.
    ~
    If equate is set to True, equates both images in
    size before overlaying.  Otherwise, overlays
    front image on top of back image.

    :param front: Image, image to place in front
    :param back: Image, image to place in back
    :param equate: bool, whether to equate images before overlaying
    :return: Image, foreground overlaid on background
    """
    if equate:
        front, back = equate_images(front, back)
        img = Image.alpha_composite(back, front)
    else:
        w, h = max(front.size[0], back.size[0]), max(front.size[1], back.size[1])
        img = make_blank_img(w, h, alpha=0)
        img.paste(back, (w/2 - back.size[0]/2, h/2 - back.size[1]/2))
        img.paste(front, (w/2 - front.size[0]/2, h/2 - front.size[1]/2))
    return img


def beside(left, right, align='bottom'):
    """
    Places left image beside right image.
    ~
    Preserves alpha values of both images.
    ~
    Align can be set to 'center', 'top', or 'bottom'.

    :param left: Image, image to place to left
    :param right: Image, image to place to right
    :param align: str, alignment of right image relative to left
    :return: Image, foreground overlaid on background
    """
    left, right = trim(left), trim(right)
    w, h = left.size[0] + right.size[0], max(left.size[1], right.size[1])
    img = Image.new(mode="RGBA", size=(w, h))

    if align == 'top':
        ly, ry = 0, 0
    elif align == 'bottom':
        ly = h - left.size[1]
        ry = h - right.size[1]
    else:  # center or otherwise
        ly = (h/2 - left.size[1]/2)
        ry = (h/2 - right.size[1]/2)

    img.paste(left, (0, ly))
    img.paste(right, (left.size[0], ry))
    return img


def above(top, bottom, align='center'):
    """
    Places top image above bottom image.
    ~
    Preserves alpha values of both images.

    :param top: Image, image to place on top
    :param bottom: Image, image to place on bottom
    :param align: str, alignment of top image relative to bottom
    :return: Image, top image overlaid on bottom image
    """
    top, bottom = trim(top), trim(bottom)
    top_w, top_h = top.size
    bottom_w, bottom_h = bottom.size
    w, h = max(top_w, bottom_w), top_h + bottom_h
    img = Image.new(mode="RGBA", size=(w, h))

    if align == 'left':
        x1, x2 = 0, 0
    elif align == 'right':
        x1 = w - top_w
        x2 = w - bottom_w
    else:
        x1 = w/2 - top_w/2
        x2 = w/2 - bottom_w/2

    img.paste(top, (x1, 0))
    img.paste(bottom, (x2, top.size[1]))
    return img


def make_blank_img(x, y, colour=(255, 255, 255), alpha=255):
    """
    Returns a blank image of dimensions x and y with optional
    background colour and transparency (alpha) values.

    :param x: int, x-dimension of image
    :param y: int, y-dimension of image
    :param colour: tuple(int,int,int), RBG value for background colour
    :param alpha: int[0,255], transparency value
    :return: Image, blank image
    """
    return Image.new("RGBA", (x, y), colour + (alpha,))


def trim(img, bbox=None):
    """
    Trims the input image's whitespace.
    ~
    For a custom crop specify the x1, y1,
    x2, and y2 coordinates in a 4-tuple.
    ~
    Taken from http://stackoverflow.com/questions/10615901/trim-whitespace-using-pil/29192070.

    :param img: Image, image to be trimmed
    :param bbox: tuple(int,int,int,int), dimensions to trim
    :return: Image, trimmed image
    """
    if 0 in img.size:
        return img

    if bbox is None:
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()

    if bbox:
        return img.crop(bbox)
    else:
        return img


def trim_horizontal(img):
    """
    Trims the input image's whitespace only
    in the x-dimension.

    :param img: Image, image to be trimmed
    :return: Image, trimmed image

    Adapted from http://stackoverflow.com/questions/10615901/trim-whitespace-using-pil/29192070.
    """
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()

    if bbox:
        bbox = (bbox[0], 0, bbox[2], img.height)
        return img.crop(bbox)
    else:
        return img


def circle(width, fill='white', outline=None, alpha=0):
    img = make_blank_img(width, width, alpha=alpha)
    draw = ImageDraw.Draw(img)
    outline = fill if outline is None else outline
    draw.ellipse((0, 0, width-1, width-1), fill, outline)
    return img


def rectangle(width, height, fill='white', outline=None, alpha=0):
    img = make_blank_img(width, height, alpha=alpha)
    draw = ImageDraw.Draw(img)
    #outline = fill if outline is None else outline
    draw.rectangle((0, 0, width-1, height-1), fill, outline)
    return img


def triangle(width, height, fill='white', vertical=True, outline=None, alpha=0):
    img = make_blank_img(width, height, alpha=alpha)
    draw = ImageDraw.Draw(img)
    outline = fill if outline is None else outline
    width, height = width-1, height-1
    min_w, max_w = sorted([0, width])
    min_h, max_h = sorted([0, height])
    if vertical:
        dims = [(0, min_h), (width/2, max_h), (width, min_h)]
    else:
        dims = [(min_w, 0), (min_w, height), (max_w, height/2)]
    draw.polygon(dims, fill, outline)
    return img


def load_default_font(size=12):
    return ImageFont.truetype(font="/Library/Fonts/Arial Bold.ttf", size=size)


def text(message, size=12, colour="black", bg_fill=(255,255,255), alpha=255, bg_alpha=0):
    font = load_default_font(size)
    w, h = font.getsize(message)
    img = make_blank_img(w, h, bg_fill, alpha=bg_alpha)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), message, fill=colour, font=font, alpha=alpha)
    return img #trim(img)


def arrow(width, height, fill='black', angle=0, label=None, font_size=0, alpha=0):
    max_dim = max(width, height)
    up = max_dim == height
    w, h = (3 * (width if up else height),) * 2
    stem = rectangle(abs(width), abs(height), fill)
    point = triangle(w, h, fill, up, alpha=alpha)

    if up:
        top, bottom = (point, stem) if height > 0 else (stem, point)
        img = above(top, bottom)
    else:
        left, right = (stem, point) if width > 0 else (point, stem)
        img = beside(left, right, align='center')

    if label is not None:
        img = overlay(text(label, alpha=0, size=font_size), img)

    img = rotate(img, angle)
    return img


def rotate(img, angle):
    """
    Rotates img by the given angle and
    returns the result.

    :param img: Image, image to rotate
    :param angle: int, angle to rotate img
    :return: Image, image rotated by angle
    """
    if angle != 0:
        max_dim = max(img.size)
        img = overlay(img,
                      make_blank_img(max_dim*2, max_dim*2, alpha=0)).rotate(angle)
    return trim(img)

