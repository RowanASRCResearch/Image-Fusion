from __future__ import division
from PIL import Image
import os
from pprint import pprint
import numpy

class un_crop():

    def __init__(self):
        pass

    def color_separator(self, im):
        if im.getpalette():
            im = im.convert('RGB')

        colors = im.getcolors()
        width, height = im.size
        colors_dict = dict((val[1],Image.new('RGB', (width, height), (0,0,0)))
                            for val in colors)
        pix = im.load()
        for i in xrange(width):
            for j in xrange(height):
                colors_dict[pix[i,j]].putpixel((i,j), pix[i,j])
        return colors_dict

    def find_height(self, infile):

        # im = Image.open(infile)
        colors_dict = self.color_separator(infile)
        # pprint(colors_dict)
        out = colors_dict[self.color]
        # out.show()

        pixels = list(out.getdata())
        width, height = infile.size
        pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]

        first = next(row for row in pixels if row.__contains__(self.color))
        top = pixels.index(first)
        print "first @ ln", top

        pixels.reverse()
        last = next(row for row in pixels if row.__contains__(self.color))
        bot = pixels.index(last)
        print "last @ ln", bot

        return bot- top, (bot - top) / height

    def pixel_write(self,infile):
        # this wil be replaced by the results of the operations of image merging and highlighting

        directory = os.path.dirname(os.path.realpath(__file__))
        temp = os.path.join(directory, 'Input', 'temp.jpg')
        im = Image.open(infile).convert("L")
        im.save(temp)
        im = Image.open(temp).convert("RGB")
        os.remove(temp)
        pixels = im.load()  # create the pixel map

        for i in range(127, 161):
            for j in range(132, 134):
                pixels[i, j] = self.color

        return im

    def exe(self, original, img):

        pixels = list(img.getdata())
        width, height = img.size
        img_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
        # pprint(img_pixels)

        pixels = list(original.getdata())
        width, height = original.size
        orig_pixels = [pixels[i * width:(i + 1) * width] for i in xrange(height)]
        # pprint(orig_pixels)

        first_row_img = img_pixels[0]
        top_left_img = first_row_img[0]
        top_right_img = first_row_img[-1]

        row_count = 0
        for row in orig_pixels:
            if sublistExists(row, first_row_img):
                break
            row_count +=1

        print row_count

        # row_count = 0
        # for row in orig_pixels:
        #     col_count = 0
        #     for pixel in row:
        #         if pixel == top_left_img:
        #             index_of_opposite = row.index(pixel) + len(img_pixels[0])
        #             if top_right_img == row[index_of_opposite]:
        #                 print "found @", row_count, col_count
        #         col_count += 1
        #     row_count += 1

def sublistExists(list, sublist):
    for i in range(len(list)-len(sublist)+1):
        if sublist == list[i:i+len(sublist)]:
            return True #return position (i) if you wish
    return False #or -1

if __name__ == '__main__':

    orig = Image.open('Input/two Infrared.jpg')
    img = orig.crop((100, 100, 200, 200))
    img.show()
    uc = un_crop()
    print uc.exe(orig, img)