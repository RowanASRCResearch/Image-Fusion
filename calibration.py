from __future__ import division

import json
import math
import os
import sys

from PIL import Image

from Merging import ImageMerge, PixelProcess

"""
Example ARGS:
"/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_base.jpg" "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_calib.jpg" 0.124 1.0
...produces JSON of following format:
{
    "calibration_image": "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_calib.jpg",
    "height_object_in_question": 0.124,
    "focal_len": 556.4516129032259,
    "base_image": "/Users/robertseedorf/PycharmProjects/Image-Fusion/Input/IMG_base.jpg",
    "dist_object_in_question": 1.0
}

  OR

Example ARGS:
69 0.124 1.0
...produces JSON of following format:
{
    "height_object_in_question": 0.124,
    "focal_len": 556.4516129032259,
    "dist_object_in_question": 1.0
}
"""

def find_object_px(base_file, calib_file):
    """
    This method should will be finished to find the height of the found object in pixels
    to be used essential to every distance method

    `return` (obj_height, img_height) the height of teh object in px, and the height of the image in pixels
    """

    inputs = [base_file, calib_file]
    m = ImageMerge.Merger('Output/ImF.png')

    m.processor = PixelProcess.ExtractPixelRemote()
    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())

    m.merge(inputs[0])
    m.merge(inputs[1])
    print "Number of pixels recorded.", len(m.processor.pixels)

    post = m.processor.getGroupedPixels()

    print "object @", post[0]
    ratio = post[0].height / Image.open(inputs[0]).height
    print "image height", Image.open(inputs[0]).height
    print "pct of height", ratio

    im = Image.new("RGBA", (post[0].width, post[0].height))
    imdata = im.load()

    for p in post[0].pixels:
        imdata[p[0] - post[0].x[0], p[1] - post[0].y[0]] = m.processor.pixels[p]

    im.show()
    im.save('Output/Only Pixels.png')

    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())

    m.processor.checkcmd.diffnum = 50

    i = Image.new('RGB', Image.open(inputs[0]).size)
    i.save('Output/One Fused Provided.jpg')

    m.exportMerge('Output/DifferenceFile.png', 'Output/One Fused Provided.jpg')

    m.save()

    print "obj height px", post[0].height, "\nvert px pct", ratio

    return post[0].height

def calibrate_focal_len(control_object_distance, control_object_height, control_object_height_px):
    """
    this method will find the necessary value for focal length using the founding principles of similar angles applied using trigonometry
    When the known distance of the object, and the fixed, known height of the object are used to calibrate for the arbitrary angle, control angle
    they can be used to find the focal length, assuming the same percent of the sensor is occupied by the object as is occupied in the photograph

    `control_object_distance` the fixed, measured distance used for calibration
    `control_object_height_px` the fixed, measured height in pixels of teh object's visage in the digital photo
    `return` focal length in pixels
    """
    control_angle = math.atan(float(control_object_height) / float(control_object_distance))  # achieve theta for this controlled case
    focal_len_px = control_object_height_px / math.tan(control_angle)
    print "focal len found,", focal_len_px, "px"
    return focal_len_px

def run_me():
    print "Calibrating focal length"

    global dist_object_in_question
    global height_object_in_question
    global object_height_px

    # running methods
    if len(sys.argv) > 4:
        base_image = sys.argv[1]
        calib_image = sys.argv[2]
        height_object_in_question = float(sys.argv[3])
        dist_object_in_question = float(sys.argv[4])    # get args from command line, see example args at top of file

        object_height_px = find_object_px(base_image, calib_image)

        focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)   # find focal len px

        directory = os.path.dirname(os.path.realpath(__file__))
        calib_file = os.path.join(directory, 'json', 'calib_info.json') # destination of calibration storage

        with open(calib_file, 'w') as fp:   # write all pre-conditions and focal len post-condition to calib_file
            json.dump({"height_object_in_question" : height_object_in_question,
                        "dist_object_in_question" : dist_object_in_question,
                       "base_image" : base_image,
                        "calibration_image" : calib_image,
                       "focal_len" : focal_len}, fp, indent=4)

    else:
        object_height_px = float(sys.argv[1])
        height_object_in_question = float(sys.argv[2])
        dist_object_in_question = float(sys.argv[3])

        focal_len = calibrate_focal_len(dist_object_in_question, height_object_in_question, object_height_px)   # find focal len px

        directory = os.path.dirname(os.path.realpath(__file__))
        calib_file = os.path.join(directory, 'json', 'calib_info.json') # destination of calibration storage

        with open(calib_file, 'w') as fp:   # write all pre-conditions and focal len post-condition to calib_file
            json.dump({"height_object_in_question" : height_object_in_question,
                        "dist_object_in_question" : dist_object_in_question,
                        "focal_len" : focal_len}, fp, indent=4)

    print "calibration finished, see", calib_file

run_me()
sys.exit(0)


