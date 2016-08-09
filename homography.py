import cv2, os
import numpy as np
import PIL
from PIL import Image, ImageFont, ImageDraw
import images2gif
from pprint import pprint
from Tkinter import *
from gif_player import gifPlayer
import ntpath
import ImageMerge, PixelProcess

def homograhpy(dest_index, base_imgs, test_imgs, save_first_frame=None):

    args_count = 0

    frames_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gif_test', 'frames')

    im_dst = cv2.imread(base_imgs[dest_index])

    pts_dst = np.array(obtain_dimensions(base_imgs[dest_index], test_imgs[dest_index]))

    h, status = cv2.findHomography(pts_dst, pts_dst)
    im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

    if save_first_frame is not None:
        cv2.imwrite(os.path.join(frames_dir, 'frame' + str(args_count) + '.png'), im_out)

    for index in xrange(0, len(base_imgs)):
        args_count += 1

        im_src = cv2.imread(test_imgs[index])

        # PIL.Image.open(base_imgs[index]).show()
        # PIL.Image.open(test_imgs[index]).show()

        pts_src = np.array(obtain_dimensions(base_imgs[index], test_imgs[index]))

        h, status = cv2.findHomography(pts_src, pts_dst)
        im_out = cv2.warpPerspective(im_src, h, (im_dst.shape[1], im_dst.shape[0]))

        cv2.imwrite(os.path.join(frames_dir, 'frame' + str(args_count) + '.png'), im_out)

    print 'file args processed', args_count

    apply_names(frames_dir)

    file_names = sorted(
        ('gif_test/frames/' + fn for fn in os.listdir(frames_dir) if
         fn.endswith('.png')))

    print 'frames:'
    pprint(file_names)

    images = [PIL.Image.open(fn) for fn in file_names]

    filename = 'gif_test/my_gif.GIF'
    images2gif.writeGif(filename, images, duration=0.5)

    return

def obtain_dimensions(base_file, obj_file):
    res = apply_image_merge(base_file, obj_file)

    # corners of object from merge
    top_right = [res[0][0], res[1][0]]
    bottom_left = [res[0][1], res[1][1]]
    top_left = [res[0][1], res[1][0]]
    bottom_right = [res[0][0], res[1][1]]

    return top_left, top_right, bottom_right, bottom_left

def apply_image_merge(base_file, obj_file):

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

    print 'res of imgs', inputs[0], inputs[1]
    PIL.Image.open('Output/Only Pixels.png').show()

    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())

    m.processor.checkcmd.diffnum = 50

    m.exportMerge('Output/DifferenceFile.png', 'Output/One Fused Provided.jpg')

    m.save()

    ret = post[0]
    return ret.x, ret.y, ret.width, ret.height

def apply_names(direc):
    for fn in os.listdir(direc):
        if fn.endswith('.png'):
            text_on_image(os.path.join(direc, fn))

def clear_frames(direc):
    # ex
    # clear_frames(frames_dir)

    for f in os.listdir(direc):
        os.remove(os.path.join(direc, f))

def resize_by_image(destination, source):
    resize_by_size(destination, *PIL.Image.open(source).size)

def resize_by_size(file, new_w, new_h):
    # ex
    # resize_by_size(os.path.join(inp_dir, 'IMG_1004.png'), PIL.Image.open(os.path.join(inp_dir, 'IMG_0993.png')).size[0], PIL.Image.open(os.path.join(inp_dir, 'IMG_0993.png')).size[1])

    img = PIL.Image.open(file)
    img = img.resize((new_w, new_h), PIL.Image.ANTIALIAS)
    img.save(file)

def text_on_image(path):
    img = PIL.Image.open(path)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 15)
    draw.text((0, 0), ntpath.basename(path), (255, 255, 255), font=font)
    img.save(path)

def debug_main():

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    frames_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'gif_test', 'frames')
    inp_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Input')

    # apply_image_merge(os.path.join(inp_dir, 'IMG_0991.jpg'), os.path.join(inp_dir, 'IMG_0993.jpg'))

    im_dst = cv2.imread('Input/IMG_0993.png')
    pts_dst = np.array([[179, 196], [179, 205], [198, 196], [198, 205]])
    h, status = cv2.findHomography(pts_dst, pts_dst)
    im_out = cv2.warpPerspective(im_dst, h, (im_dst.shape[1], im_dst.shape[0]))

    if len(sys.argv) > 1 and sys.argv[1] is not '0':
        cv2.imwrite(os.path.join(frames_dir, 'frame0.png'), im_out)

    im_src1 = cv2.imread('Input/IMG_1004.png')
    pts_src1 = np.array([[1623, 1149], [1623, 1405], [2282, 1149], [2282, 1405]])
    h, status = cv2.findHomography(pts_src1, pts_dst)
    im_out = cv2.warpPerspective(im_src1, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame1.png'), im_out)

    im_src2 = cv2.imread('Input/IMG_0991.png')
    pts_src2 = np.array([[116, 155], [116, 125], [179, 155], [179, 125]])
    h, status = cv2.findHomography(pts_src2, pts_dst)
    im_out = cv2.warpPerspective(im_src2, h, (im_dst.shape[1], im_dst.shape[0]))

    cv2.imwrite(os.path.join(frames_dir, 'frame2.png'), im_out)

    apply_names(frames_dir)

    file_names = sorted(
        (os.path.join('gif_test', 'frames', fn) for fn in os.listdir(frames_dir) if fn.endswith('.png')))
    pprint(file_names)

    images = [PIL.Image.open(fn) for fn in file_names]

    gif_file = os.path.join(os.path.dirname(os.path.realpath(frames_dir)), 'my_gif.GIF')
    images2gif.writeGif(gif_file, images, duration=0.5)

    return

if __name__ == '__main__' :

    # applicable run-me
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    frames_dir = os.path.join(cur_dir, 'gif_test', 'frames')
    inp_dir = os.path.join(cur_dir, 'Input')

    bases = [os.path.join(inp_dir, 'IMG_1022.jpg'), os.path.join(inp_dir, 'IMG_1024.jpg'), os.path.join(inp_dir, 'IMG_1026.jpg')]
    tests = [os.path.join(inp_dir, 'IMG_1021.jpg'), os.path.join(inp_dir, 'IMG_1023.jpg'), os.path.join(inp_dir, 'IMG_1025.jpg')]
    dest = (os.path.join(inp_dir, 'IMG_1024.jpg'), os.path.join(inp_dir, 'IMG_1023.jpg'))

    homograhpy(dest_index=1, base_imgs=bases, test_imgs=tests)

    root = Tk()
    anim = gifPlayer(root, 'gif_test/my_gif.gif')
    anim.pack()
    anim.run(root)