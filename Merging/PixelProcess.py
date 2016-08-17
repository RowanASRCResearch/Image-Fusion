from PIL import Image

class PixelCommand(object):
    """
    `Author`: Bill Clark

    An interface for a command object, within the Command pattern. A command contains
    an execute method with runs on a pixel from the tracked image and the merged image.
    As an interface, it doesn't work if used directly.
    """

    def __init__(self):
        pass

    def execute(self, p1, p2):
        pass


class RedHighlightCommand(PixelCommand):
    """
    `Author`: Bill Clark

    A command that handles the action side of the remote. When executed, it returns a
    solid red pixel, making all changed pixels red.
    """

    def execute(self, p1, p2):
        return (255, 0, 0)


class TakeSecondCommand(PixelCommand):
    """
    `Author`: Bill Clark

    A command that handles the action side of the remote. When executed, it returns
    the second pixel.
    """

    def execute(self, p1, p2):
        return p2

class TakeNonEmptySecondCommand(PixelCommand):
    """
    `Author`: Bill Clark

    A command that handles the action side of the remote. When executed, it returns the
    second pixel if the pixel isn't (0,0,0), or white. If it's white the original pixel
    is returned.
    """

    def execute(self, p1, p2):
        if p2 == (0, 0, 0): return p1
        return p2


class ColorDiffCommand(PixelCommand):
    """
    `Author`: Bill Clark

    A command that handles the check side of the remote. the execute returns true if the
    difference between the RGB values is greater than the difference number. Modifying
    the difference number allows for more or less accuracy.
    """

    diffnum = 120

    def __init__(self):
        pass

    def execute(self, p1, p2):
        return abs(p1[0] - p2[0]) > self.diffnum \
           or abs(p1[1] - p2[1]) > self.diffnum \
           or abs(p1[2] - p2[2]) > self.diffnum


class PixelRemote(object):
    """
    `Author`: Bill Clark

    The pixel remote contains two command implementations, one that should return a boolean
    value and the other which will return what to save to the tracked output image. These
    commands can be switched as needed. The remote also contains the pixel access objects
    for both the tracked image and the data to be compared.
    """

    def __init__(self):
        self.outdata = None
        self.comparedata = None

        self.checkcmd = None
        self.actcmd = None

    def run(self, x1, y1, x2, y2):
        """
        `Author`: Bill Clark

        Compares two pixels, as referenced by location. The check command is run,
        and if it's returned true the act command is used to modify the tracked image.

        `x1`: X value of the tracked image.
        `y1`: Y value of the tracked image.
        `x2`: X value of the merging image.
        `y2`: Y value of the merging image.
        """
        currpixel = self.outdata[x1, y1]
        comparepixel = self.comparedata[x2, y2]
        if self.checkcmd.execute(currpixel, comparepixel):
            self.outdata[x1, y1] = self.actcmd.execute(currpixel, comparepixel)
            return 1
        return 0

    def setCheckCommand(self, command):
        """
        `Author`: Bill Clark

        Sets the internal check command to the command parameter.

        `command`: command to be used.
        """
        self.checkcmd = command

    def setActorCommand(self, command):
        """
        `Author`: Bill Clark

        Sets the internal action command to the command parameter.

        `command`: command to be used.
        """
        self.actcmd = command


class ExtractPixelRemote(PixelRemote):

    def __init__(self):
        """
        `Author`: Bill Clark

        A extended pixel remote. This remote is used to track changes to tracked image
        on pixel by pixel basis. Each changed pixel is saved for reporting.
        """
        super(ExtractPixelRemote, self).__init__()
        self.pixels = {}

    def run(self, x1, y1, x2, y2):
        currpixel = self.outdata[x1, y1]
        comparepixel = self.comparedata[x2, y2]
        if self.checkcmd.execute(currpixel, comparepixel):
            ret = self.actcmd.execute(currpixel, comparepixel)
            self.outdata[x1, y1] = ret
            self.pixels[(x1, y1)] = ret
            return 1
        return 0

    def getGroupedPixels(self):
        """
        `Author`: Bill Clark

        Using the list of pixels that have been modified, generate connected groups.
        Each groups is made up of adjacent pixels. The groups are stored in a
        PixelGroup class, and the groups are stored in a group container. These classes
        allow for more information to be stored about each group.

        `return`: A group container object.
        """

        groups = GroupContainer()
        processed = []

        for point in self.pixels:
            if point not in processed: explore = [point]
            else: continue

            subprocess = []

            while explore:
                e = explore.pop()
                subprocess.append(e)

                nearby = (e[0]+1, e[1]), \
                         (e[0]-1, e[1]), \
                         (e[0], e[1]+1), \
                         (e[0], e[1]-1)  # E,W,S,N points.

                explore.extend([n for n in nearby if n not in subprocess and n not in explore and n in self.pixels])
            processed.extend(subprocess)
            groups.add(PixelGroup(subprocess))
            # groups.append(subprocess)
        return groups

class GroupContainer(object):

    def __init__(self):
        """
        `Author`: Bill Clark

        A group container is a container class for a list of PixelGroups.
        The class provides additional features that can be useful in analyzing
        the groups.
        """
        self.groups = []

    def generator(self):
        """
        `Author`: Bill Clark

        Creates a generator for the groups list.

        `yield`: PixelGroups
        """
        for group in self.groups:
            yield group

    def add(self, group):
        """
        `Author`: Bill Clark

        Adds a pixelgroup to the groups list.

        `group`: To be added.
        """
        self.groups.append(group)

    def sortRatio(self, reverse=True):  # Normal is low value first.
        """
        `Author`: Bill Clark

        Sorts the PixelGroups with the ratio value contained in each of them.

        `reverse`: Defaults to True, if false the sort goes incrementally.
        """
        self.groups = sorted(self.groups, key=lambda x: x.ratio, reverse=reverse)

    def sortCount(self, reverse=True):  # Normal is low value first.
        """
        `Author`: Bill Clark

        Sorts the PixelGroups with the count value contained in each of them.

        `reverse`: Defaults to True, if false the sort goes incrementally.
        """
        self.groups = sorted(self.groups, key=lambda x: x.count, reverse=reverse)

    def filter(self):
        """
        `Author`: Bill Clark

        Uses a list comprehension to filter out any unwanted groups. It calls the
        _filter method (_ being a hidden method) which can be modified to add
        more filters. This method shouldn't be modified.
        """
        self.groups = [group for group in self.groups if self._filter(group)]

    def _filter(self, group):
        """
        `Author`: Bill Clark

        A method that looks at a group and return if it should be pruned. Multiple
        filtering methods can be added, as long as the logic is done in this method.

        `group`: The group to look at.

        `return`: True keeps the group, false removes it.
        """
        return self._greaterThanOne(group)

    def _greaterThanOne(self, group):
        """
        `Author`: Bill Clark

        Returns true if the height and width of the given group are both greater than one.

        `group`: The group to be looked at.
        """
        return group.height > 1 and group.width > 1


    def first(self):
        """
        `Author`: Bill Clark

        returns the first group in the list.

        `return`: The first group in the container.
        """
        return self.groups[0]


class PixelGroup(object):

    def __str__(self):
        """
        `Author`: Bill Clark

        Overrides the __str__ to prints the internal values of the group.

        `return`: To string.
        """
        return 'x:' + repr(self.x) + ' ' + 'y:' + repr(self.y) + ' ' + 'height:' + \
               repr(self.height) + ' ' + 'width:' + repr(self.width) + ' ' + repr(self.ratio) + '%'

    def __init__(self, groups):
        """
        `Author`: Bill Clark

        A container for a list of pixels. The container provides additional stats
        about the group.

        `groups`: The list of pixels that define the group.
        """
        self.pixels = groups
        self.count = len(self.pixels)
        self.x, self.y, self.height, self.width, self.ratio = self._size()

    def generator(self):
        """
        `Author`: Bill Clark

        Creates a generator for the pixel list.

        `yield`: pixel locations.
        """
        for p in self.pixels:
            yield p

    def _size(self):
        """
        `Author`: Bill Clark

        Generates the stats about the group, including the min and max XY values, the width
        and height of the group, and the ratio of marked pixels to not.

        `return`: The values above.
        """

        if self.count <= 1:
            x = [self.pixels[0][0], self.pixels[0][0]]
            y = [self.pixels[0][1], self.pixels[0][1]]
            return x, y, 1, 1, 100

        x = []
        y = []

        sort = sorted(self.pixels, key=lambda x: x[0])
        x.append(sort[0][0])
        x.append(sort[-1][0])
        sort = sorted(self.pixels, key=lambda x: x[1])
        y.append(sort[0][1])
        y.append(sort[-1][1])

        w = (x[1]-x[0])+1
        h = (y[1]-y[0])+1
        ratio = int((len(self.pixels) / float(w*h))*100)

        return x, y, h, w, ratio

    def save(self, file, pixelDict):
        """
        `Author`: Bill Clark

        Saves the pixel group to a file. It requires the actual pixel access object
        from the file the group is pulled from. This is not internal to this class,
        which is an extra connection. The group is not saved at the same size as the
        original, at the size of the group.

        `file`: Path to save to.

        `pixelDict`: Pixel access object to write the group to.
        """
        im = Image.new("RGBA", (self.width, self.height))
        imdata = im.load()

        for pixel in self.generator():
            imdata[pixel[0]-self.x[0], pixel[1]-self.y[0]] = pixelDict[pixel]

        im.show()
        im.save(file)