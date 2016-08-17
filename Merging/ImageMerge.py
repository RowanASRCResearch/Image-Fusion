from PIL import Image

import PixelProcess

debug = 0


class Merger:

    def __init__(self, outfile):
        """
        `Author`: Bill Clark

        A merger is a class that allows for a number of images to merged sequentially. It is designed to
        merge each image incrementally, outputting to an outfile when requested. There are a variety of
        ways to preform the merges for different circumstance. The class contains an autosave feature that
        will save the image after each merge, which is defaulted to off. There is also a contained PixelChecker
        and PixelActor, which define how the merges process.
        Merger works off an internal state. Each merge operation (irrelevant of number merged in that operation)
        changes the state of the output data. Merge and MergeAs change the state permanently. ExportMerge and
        TestMerge do not change the state of the output data.

        `outfile`: The file address to save the output to.
        """

        self.initialized = 0
        self.autoSave = 0

        self.outfile = outfile

        self.processor = PixelProcess.PixelRemote()
        self.mergedFiles = []

    def setup(self, file):
        """
        `Author`: Bill Clark

        This method is called if a merge is activated and no prior merges have been done. It sets the image to
        be merged as the output result, as nothing cannot be merged with an image object. This method is
        internal and does not need to be called by a user. It is called if necessary from the merge methods.

        `file`: A path to an image to initialize the Merge with.
        """
        self.outimage = Image.open(file)
        self.processor.outdata = self.outimage.load()
        if self.autoSave: self.save()
        self.initialized = 1

    def merge(self, *images):
        """
        `Author`: Bill Clark

        The main merge method. All other variants actually call this merge at some point in execution. The
        method calls setup if no merges have been done prior so that merges can be done against the first.
        This uses the checkandact method to operate on each image given to it. That method covers all the
        actual pixel processing.
        When debug is enabled, merge prints the percentage of different and same pixels.

        `images`: Any number of image paths to merge together.
        """

        if not self.initialized:
            self.setup(images[0])
            images = images[1:]

        if len(images) > 0:
            for image in images:
                changed = self.checkAndAct(image)

            self.mergedFiles.append(image)
            if debug: self.printDiffSame(changed)
            if debug: self.show()

        if self.autoSave: self.save()
        
    def testMerge(self, *images):
        """
        `Author`: Bill Clark

        A test merge is a merge that doesn't save state. Each call to merge changes the internal data.
        In the case a user wants to see the result of a merge without modifying the data, test merge will
        do the job. Test merge is actually a call to exportmerge taking advantage of it's outfile variable.

        `images`: Any number of image paths to be merged.
        """

        self.exportMerge(None, *images)

    def exportMerge(self, outfile, *images):
        """
        `Author`: Bill Clark

        Export merge is a merge operation that does not change state. Unlike TestMerge, this merge will
        write the temporary image to a given outfile. If the outfile is None, export will not write anything.
        This side effect is how TestMerge works. Export merge turns off the autosave feature to be sure that
        doesn't modify the main output file.

        `images`: the image paths to be merged.

        `outfile`: Where to set the new output path to.
        """

        # Make a backup of the outimage if one has been initialized.
        orig = None
        if self.initialized: orig = self.outimage.copy()

        # Saves the autosave state and merges.
        state = self.autoSave
        self.autoSave = 0
        self.merge(*images)
        self.autoSave = state

        # If the outfile is None, show the image and continue. If an outfile exists, save the image instead.
        if outfile is not None: self.save(self.outimage, outfile)
        else:  self.show()

        # If the back up was made, restore the status to before the last merge. Else, reset the object.
        if orig is not None:
            self.outimage = orig
            self.processor.outdata = self.outimage.load()
        else:
            self = Merger(self.outfile)

    def mergeAs(self, outfile, *images):
        """
        `Author`: Bill Clark

        This is a variant of the main merge method. It changes the outfile permanently, functioning like
        a save as option. Otherwise it differs completely to merge.

        `images`: the image paths to be merged.

        `outfile`: Where to set the new output path to.
        """

        self.outfile = outfile
        self.merge(*images)

    def _tupleSub(self, t, tt):
        """
        `Author`: Bill Clark

        Finds the difference of each RGB value in two pixels. The difference has to be
        greater than 5 to fail.

        `t`: The first pixel to compare.

        `tt`: The second to compare.

        `return`: False if the difference between any RGB is greater than 5, else true.
        """
        for one, two in zip(t, tt):
            if abs(one - two) > 5:
                return False
        return True


    def cropFind(self, outfile, smallImage):
        """
        `Author`: Bill Clark

        Finds where a subimage of the tracked image fits in the tracked image.
        This is done by comparing the sides of the outfile image with each
        row of pixels in the tracked image. This acommodates for rotation. The match
        is as close to exact as is practical. Saving and cropping images can sometimes
        cause small differences such as 1 or or 2 values.
        The if result not none section can be replaced later to change what is done
        with the result.

        `outfile`: path to save the merged crop to.

        `smallImage`: A subimage of the tracked image.

        `return`: None if no match is found, the result is one is.
        """
        smim = Image.open(smallImage)
        smdata = smim.load()
        xlen, ylen = smim.size
        result = None

        # Create Sides, and generate Hashes of them.
        sides = [[],[],[],[]]
        for x in range(xlen): #Top Side, Bottom Side
           sides[0].append(smdata[(x, 0)])
           sides[2].append(smdata[((xlen-1)-x, ylen-1)])
        for y in range(ylen): # Right Side, Left Side
           sides[1].append(smdata[(xlen-1, y)])
           sides[3].append(smdata[(0, (ylen-1)-y)])
        for side in sides:
            side = tuple(side)
        sides = tuple(sides)

        for y in range(self.outimage.size[1]):
            row = []
            for x in range(self.outimage.size[0]):
                if result is not None:
                    break

                if (x + xlen) <= self.outimage.size[0]: #Top and Bottom check.
                    while len(row) != xlen: #get the row to match the size.
                        if len(row) > xlen:
                            del row[-1]
                        elif len(row) < xlen:
                           row.append(self.processor.outdata[x+len(row),y])
                    for s in range(0, 4, 2):
                        flag = 1
                        for sm, lg in zip(sides[s], row):
                            if not self._tupleSub(sm, lg):
                                flag = 0
                                break
                        if flag: result =  x, y, s

                if (x + ylen) <= self.outimage.size[0]:
                    while len(row) != ylen: #get the row to match the size.
                        if len(row) > ylen:
                            del row[-1]
                        elif len(row) < ylen:
                           row.append(self.processor.outdata[x+len(row),y])
                    for s in range(1, 4, 2):
                        flag = 1
                        for sm, lg in zip(sides[s], row):
                            if not self._tupleSub(sm, lg):
                                flag = 0
                                break
                        if flag: result =  x, y, s
                del row[0]
        if result is not None:
            im = Image.new("RGBA", (self.outimage.size[0], self.outimage.size[0]))
            imdata = im.load()

            for y in range(smim.size[1]):
                for x in range(smim.size[0]):
                    newx = result[0] + x
                    newy = result[1] + y
                    imdata[newx, newy] = smdata[x,y]

            im.save(outfile)
            return result
        self.exportMerge(outfile, outfile)

    def checkAndAct(self, img):
        """
        `Author`: Bill Clark

        The primary action method. This method takes an image and merges it onto the output data stored
        in the class. For every pixel in each image, the class's pixelChecker is used to compare them.
        If the check returns true, the class's pixelActor is called to act on the pixels. For every acted on
        pixel pair, the method's counter is increased. This count is returned as a statistic.

        `img`: An image file to be merged onto the class's image.

        `return`: The number of modified pixels.
        """
        compareimage = Image.open(img)
        self.processor.comparedata = compareimage.load()

        counter = 0
        for y in range(self.outimage.size[1]):
            for x in range(self.outimage.size[0]):
                counter += self.processor.run(x, y, x, y)
        return counter

    def convert(self, *images):
        """
        `Author`: Bill Clark

        This method converts any number of given images to RGBA color format. Pixel comparision is done via
        the rgb values, and requires the images to be in that format. The converted files are saved to
        a Converts folder as to not fill ones input folder with temporary files.

        `images`: The images that need to be converted.

        `return`: A list of file paths leading to the convert images, which can passed to further methods.
        """
        ret = []
        count = 0
        for image in images:
            img = Image.open(image)
            im = img.convert("RGBA")

            split = image.split('/')
            path = '/'.join(split[:-1]) + '/Converts/' + ''.join(split[-1:])

            ret.append(path)
            im.save(path)
            count += 1
        return ret

    def show(self, image=None):
        """
        `Author`: Bill Clark

        Shows the image if an image is given, otherwise defaults to the class's image.

        `image`: The image to show, defaults to the image contained in the class.
        """
        if not image: image = self.outimage
        image.show()

    def save(self, image=None, outfile=None):
        """
        `Author`: Bill Clark

        Saves an image to disk. The image can be specified, other wise the class's image is defaulted to.
        The outfile can also be optionally specified.

        `image`: Defaults to the class's image unless specified. The image to be saved.

        `outfile`: The location to save to. Defaults to the class's output path.
        """
        if not image: image = self.outimage
        if not outfile: outfile = self.outfile
        image.save(outfile)

    def printDiffSame(self, counter):
        """
        `Author`: Bill Clark

        Prints the different pixel percentage and the same pixel percentage.

        `counter`: The count of changed pixels in a merge operation. Obtained from checkandact.
        """
        print "Different Pixels:", counter, repr(round((counter/360000.)*100,2)) + '%', " Same Pixels:", \
            360000-counter, repr(round(((360000-counter)/360000.)*100,2)) + '%'+ '\n'


if __name__ == "__main__":
    debug = 0
    inputs = ['Input/Camera 1.jpg', 'Input\Camera crop.jpg']
    m = Merger('Output/ImFuse.jpg')

    m.processor = PixelProcess.ExtractPixelRemote()
    m.processor.setActorCommand(PixelProcess.TakeNonEmptySecondCommand())
    m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())
    m.processor.checkcmd.diffnum = 0

    m.merge(inputs[0])
    print m.cropFind('foo.jpg', inputs[1])
    print "Number of pixels recorded.", len(m.processor.pixels)

    post = m.processor.getGroupedPixels()

    post.sortCount()
    post.filter()

    for p in post.generator():
        print p

    f = post.first()
    print f

    # for group in post:  # Post the groups to the outimage.
    #     for p in group.pixels:
    #         imdata[p[0], p[1]] = m.processor.pixels[p]

    #Output the first group to it's own image.
    f.save('Output/Only Pixels.png', m.processor.pixels)

    m.processor.setActorCommand(PixelProcess.RedHighlightCommand())

    # m.exportMerge('Output/DifferenceFile.jpg', 'Output/One Fused Provided.jpg')

    m.save()
