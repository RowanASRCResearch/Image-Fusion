import cv2, sys, os
import numpy as np
import PIL
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter, ImageFont, ImageDraw
import images2gif
from pprint import pprint
from Tkinter import *
from gif_player import gifPlayer
import ntpath
from rotation_script import autorotate
import base64
import Tkinter
import ImageMerge, PixelProcess


#https://pypi.python.org/pypi/images2gif

# image = Image.open('Input/Two Infrared test.png')
# image = image.filter(ImageFilter.FIND_EDGES)
# image.show()
#
# image = Image.open('Input/Two Crop test.png')
# image = image.filter(ImageFilter.FIND_EDGES)
# image.show()

# img = cv2.imread('Input/Two Infrared.jpg')
# edges = cv2.Canny(img,50,200,apertureSize = 3)
#
# plt.subplot(121),plt.imshow(img,cmap = 'gray')
# plt.title('Original Image'), plt.xticks([]), plt.yticks([])
# plt.subplot(122),plt.imshow(edges,cmap = 'gray')
# plt.title('Edge Image'), plt.xticks([]), plt.yticks([])
#
# plt.show()

def homograhpy(base_img, clear_dir=None, save_first_frame=None, *test_imgs):
    args_count = 0

    im_dst = cv2.imread(base_img)

    # TODO insert ability to capture object dimensions
    pts_dst = np.array([[179, 196], [179, 205], [198, 196], [198, 205]])

    h, status = cv2.findHomography(pts_dst, pts_dst)
    im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

    if save_first_frame is not None:
        cv2.imwrite('gif_test/frames/frame' + str(args_count) + '.png', im_out)

    for img_path in test_imgs:
        args_count += 1

        im_dst = cv2.imread(img_path)

        # TODO insert ability to capture object dimensions
        pts_dst = np.array([[179, 196], [179, 205], [198, 196], [198, 205]])

        h, status = cv2.findHomography(pts_dst, pts_dst)
        im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

        cv2.imwrite('gif_test/frames/frame' + str(args_count) + '.png', im_out)

    print 'file args processed', args_count

    apply_names(os.path.dirname(os.path.realpath(__file__)) + '\gif_test\\frames')

    file_names = sorted(
        ('gif_test/frames/' + fn for fn in os.listdir(os.path.dirname(os.path.realpath(__file__)) + '\gif_test\\frames') if
         fn.endswith('.png')))

    print 'frames:'
    pprint(file_names)

    images = [PIL.Image.open(fn) for fn in file_names]

    filename = 'gif_test/my_gif.GIF'
    images2gif.writeGif(filename, images, duration=0.5)

    root = Tk()
    anim = gifPlayer(root, 'gif_test/my_gif.gif')
    anim.pack()
    anim.run(root)
    return

def apply_image_merge(base_file, obj_file):
    im = PIL.Image.open(obj_file)
    img_width, img_height = im.size

    inputs = [base_file, obj_file]
    m = ImageMerge.Merger('Output/ImF.png')

    m.processor = PixelProcess.ExtractPixelRemote()
    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())

    m.merge(inputs[0])
    m.merge(inputs[1])
    print "Number of pixels recorded.", len(m.processor.pixels)

    post = m.processor.getGroupedPixels()

    print "object @", post[0]
    ratio = post[0].height / PIL.Image.open(inputs[0]).height
    print PIL.Image.open(inputs[0]).height
    print "pct of height", ratio

    im = PIL.Image.new("RGBA", (post[0].width, post[0].height))
    imdata = im.load()

    for p in post[0].pixels:
        imdata[p[0] - post[0].x[0], p[1] - post[0].y[0]] = m.processor.pixels[p]

    # im.show()
    im.save('Output/Only Pixels.png')

    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())

    m.processor.checkcmd.diffnum = 50

    m.exportMerge('Output/DifferenceFile.png', 'Output/One Fused Provided.jpg')

    m.save()

    print "obj height px", post[0].height, "\nimage height px", img_height

def apply_names(direc):
    for fn in os.listdir(direc):
        if fn.endswith('.png'):
            text_on_image(direc + '\\' + fn)

def text_on_image(path):
    img = PIL.Image.open(path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 15)
    draw.text((0, 0), ntpath.basename(path), (255, 255, 255), font=font)
    img.save(path)

if __name__ == '__main__' :

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    frames_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gif_test', 'frames')
    inp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input')

    apply_image_merge(os.path.join(inp_dir, 'IMG_0991.jpg'), os.path.join(inp_dir, 'IMG_0993.jpg'))

    im_dst = cv2.imread('Input/IMG_0993.png')
    pts_dst = np.array([[179, 196], [179, 205], [198, 196], [198, 205]])
    h, status = cv2.findHomography(pts_dst, pts_dst)
    im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

    if len(sys.argv) > 1 and sys.argv[1] is not '0':
        cv2.imwrite(os.path.join(frames_dir, 'frame0.png'), im_out)

    im_src1 = cv2.imread('Input/IMG_1004.png')
    pts_src1 = np.array([[1623,1149], [1623,1405],[2282,1149],[2282,1405]])
    h, status = cv2.findHomography(pts_src1, pts_dst)
    im_out = cv2.warpPerspective(im_src1, h, (im_dst.shape[1],im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame1.png'), im_out)


    im_src2 = cv2.imread('Input/IMG_0991.png')
    pts_src2 = np.array([[116, 155], [116, 125], [179, 155], [179, 125]])
    h, status = cv2.findHomography(pts_src2, pts_dst)
    im_out = cv2.warpPerspective(im_src2, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame2.png'), im_out)

    apply_names(frames_dir)

    file_names = sorted((os.path.join('gif_test', 'frames', fn) for fn in os.listdir(frames_dir) if fn.endswith('.png')))
    pprint(file_names)

    images = [PIL.Image.open(fn) for fn in file_names]

    gif_file = os.path.join(os.path.dirname(os.path.realpath(frames_dir)), 'my_gif.GIF')
    images2gif.writeGif(gif_file, images, duration=0.5)

    root = Tk()
    anim = gifPlayer(root, gif_file)
    anim.pack()
    anim.run(root)


