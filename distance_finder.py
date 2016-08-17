from __future__ import division

import json
import math
import os
import sys
import traceback
import warnings
from pprint import pprint

from PIL import Image
from PIL.ExifTags import TAGS

from Merging import ImageMerge, PixelProcess


# EXAMPLE ARGS
# 1.82 "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_base.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_two.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_onehalf.jpg" "C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\IMG_half.jpg"
#
# INDEPENDENT CALL EXAMPLE:
# method = Primary(1.82, base.jpg, input.jpg)
# method.find(distance)

class Solution:
    """
    This class represents one solution given a single case of image distance finding.
    Given the parametrized vargs, index 1: image to be examined, and index 2: the known height in meters of highlighted object,
    The solution's constructor and find distance command will return the distance of the object highlighted in the image
    Four variations of this task exist, The primary, Secondary, Tertiary, and Quaternary.
    Each works based on the capability of the pre-conditioned machine (Primary), or as fail-safe, the exif tags of the test image (Secondary, Tertiary, and Quaternary).
    The Primary reads in from the calib_info file, the calibrated info used to find the focal length and the focal length determined,
    then using trigonometric principals of similar angles, the distance of the object, whose height is known, is found.
    The Secondary, and Tertiary methods use the exif tags to find the focal length of the lens in the camera that was used, and apply that focal length to the trigonometry.
    The final method, investigates the tags for a special 'subject distance' tag that assumes the accurate region of focus and returns that distance fom the camera
    """

    def __init__(self, base_file, obj_file, known_height):
        self.base_file = base_file
        self.obj_file = obj_file
        self.height_object_in_question = known_height
        self.focal_len = None

        directory = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(directory, 'json', 'cameras.json'), 'r') as data_file:
            data = json.load(data_file)
            self.camera_dict = data

    def get_object_height_px(self, base_file, obj_file):
        """
        This method should will be finished to find the height of the found object in pixels
        to be used essential to every distance method

        `path` the path to the image file being investigated
        `return` (obj_height, img_height) the height of the object in px, and the height of the image in pixels
        """
        im = Image.open(obj_file)
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
        ratio = post[0].height / Image.open(inputs[0]).height
        print Image.open(inputs[0]).height
        print "pct of height", ratio

        im = Image.new("RGBA", (post[0].width, post[0].height))
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
        return (post[0].height, img_height)

    def get_exif(self, path):
        """
        Method to return the exif tags of the file at path

        `path` the path to local file that is opened and parsed for exif tags
        `return` ret, the dictionary of all tags and their values
        """
        ret = {}
        i = Image.open(path)
        info = i._getexif()
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            ret[decoded] = value
        return ret

    def find_distance_given_height_primary(self, obj_height_px, focal_len_px):
        """
        This method takes the height of the object in pixels and the determined focal_length in pixels to find the distance to that object

        `obj_height_px` the height of the object in pixels
        `return` the determined distance of the object from the camera in units of height_object_in_question
        """
        test_angle = math.atan(obj_height_px / focal_len_px)
        goal_dist = float(self.height_object_in_question) / math.tan(test_angle)
        return goal_dist

    def find_key(self, eq_focal_len, act_focal_len):
        """
        This method determines the key to be used to access the dictionary, camera_dict, of the commonly used camera sizes and their info
        Using the 35 mm equivalent focal length (read in through EXIF tags) and the actual focal length (also read in through EXIF tags) are used to find the crop factor where...

        crop factor = 35mm eq / actual focal length

        NOTE, the accuracy of the sensor height being yielded are dependent on the secondary value, crop factor
        crop factor will fall with +- 0.3 units of the desired key to yield the result

        :param eq_focal_len: 35 mm equivalent focal length
        :param act_focal_len: actual focal length in mm
        :return: the key to be used for later dictionary indexing
        """
        global key
        crop_fact = eq_focal_len / act_focal_len
        for k, v in self.camera_dict.iteritems():
            if v[1] + 0.3 > crop_fact and v[
                1] - 0.3 < crop_fact:  # If calculated crop factor is with +- 0.3 units of the known than it is accepted
                return str(k)

    def find_distance(self):
        """
        inherited method to be used by each subclass in a particular way
        :return: distance, in meters of object from aperture, if solution available, else None
        """
        pass

class Primary(Solution):
    """
    The described primary method of finding object distance
    Requires config file (calib_info) to be established for accurate functionality
    """

    def __init__(self, base_file, obj_file, known_height):
        Solution.__init__(self, base_file, obj_file, known_height)

        with open(os.path.join(directory, 'json', 'calib_info.json'), 'r') as fp:
            json_data = json.load(fp)
            try:
                self.focal_len = json_data["focal_len"]
            except KeyError as ke:
                sys.stderr.write("WARNING no focal length found, primary method will fail.\n")
                sys.stderr.write(str(ke))
    
    def find_distance(self):
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            # print "perceived object height", dimensions[0]

            dist = self.find_distance_given_height_primary(dimensions[0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Primary Method Failed.\n")
            traceback.print_exc()

class Secondary(Solution):
    """
    The described secondary method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """
    def __init__(self, base_file, obj_file, known_height):
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            pix_pct = dimensions[0] / dimensions[1]
            # print "pix pct", pix_pct

            tags = self.get_exif(self.obj_file)
            # pprint(tags)

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            self.focal_len = int(tags['FocalLength'][0]) / int(tags['FocalLength'][1])
            # print "focal len mm", self.focal_len

            key = self.find_key(tags['FocalLengthIn35mmFilm'], int(tags['FocalLength'][0]) / int(tags['FocalLength'][1]))
            print "determined key", key

            dist = self.find_distance_given_height_primary(pix_pct * self.camera_dict[key][0], self.focal_len)
            return dist

        except Exception as e:
            sys.stderr.write("Secondary Method Failed.\n")
            traceback.print_exc()

class Tertiary(Solution):
    """
    The penultimate method of finding object distance
    Requires only proper file format, with exif tags, to run appropriately
    """
    def __init__(self, base_file, obj_file, known_height):
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        print str(self.__class__.__name__), "Solving..."
        try:
            dimensions = self.get_object_height_px(self.base_file, self.obj_file)
            # print "perceived object height", dimensions[0]

            tags = self.get_exif(self.obj_file)
            # pprint(tags)

            # focal_len = float([s for s in str.split(str(tags['LensModel'])) if s.__contains__('mm')][0][0:4])
            self.focal_len = float(tags['FocalLength'][0]) / float(tags['FocalLength'][1])
            # print "focal len mm", focal_len

            key = self.find_key(tags['FocalLengthIn35mmFilm'],
                                     int(tags['FocalLength'][0]) / int(tags['FocalLength'][1]))
            # print "determined key", key

            dist = (self.focal_len * self.height_object_in_question * dimensions[1]) / (
                dimensions[0] * self.camera_dict[key][0])
            return dist

        except Exception as e:
            sys.stderr.write("Tertiary Method Failed.\n")
            traceback.print_exc()

class Quaternary(Solution):
    """
    The last method of finding object distance, characterized by unreliability
    Requires proper file format, with exif tags, as well as exif tag 'SubjectDistance' and assumes the object is in field of focus
    """
    def __init__(self, base_file, obj_file, known_height):
        Solution.__init__(self, base_file, obj_file, known_height)
    
    def find_distance(self):
        try:
            dist = self.get_exif(self.obj_file)['SubjectDistance']  # maybe useful, determined from center of focus in digital cameras
            return dist

        except Exception as e:
            sys.stderr.write("Quaternary Method Failed.")
            traceback.print_exc()

class Macro:
    """
    This class holds the capability of running several 'commands,' as instances of subclasses, to be readily used in extension
    """
    def __init__(self, *args):
        self.commands = []
        for arg in args:
            self.commands.append(arg)

    def add(self, command):
        self.commands.append(command)

    def run(self):
        ret = []
        for c in self.commands:
            ret.append((str(c.__class__.__name__), os.path.split(c.obj_file)[1], c.find_distance()))
        return ret

def main(known_height, base_file, infiles):

    # run me

    # df = Macro(Primary(infile, known_height), Secondary(infile, known_height), Tertiary(infile, known_height))
    # df = Macro(Primary(os.path.join(directory, 'Input', 'IMG_onehalf.jpg'), known_height))

    df = Macro()
    for file in infiles:
        df.add(Secondary(base_file, file, known_height))

    results = df.run()
    return results

if __name__ == '__main__':
    warnings.filterwarnings('ignore')

    directory = os.path.dirname(os.path.realpath(__file__))

    infiles = sys.argv[3:]                                  # argv[2:] = all of the files for the script to be run over
    res = main(float(sys.argv[1]), sys.argv[2], infiles)    # argv[1] =  0.124, height of object in meters, argv[2] = base image file pathname (absolute)
    pprint(res)

    sys.exit(0)