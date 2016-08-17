import cmd
import re

from Merging import ImageMerge, PixelProcess
from Recognition import peopledetect


class Console(cmd.Cmd):

    def __init__(self, output):
        """
        `Author` : Bill Clark

        The Console class gives a user an interactive way to use the package utilities.
        The class is an extension of the python cmd class, which allows for easy
        command generation and parsing. The Console provides a help command for each
        command based off of the doc string for the method. Each method prefaced with
        do_ is a command that can be run interactively.
        """
        cmd.Cmd.__init__(self)
        self.groups = None
        self.m = ImageMerge.Merger(output)
        self.prompt = '> '

    def do_merge(self, images):
        """
        `Author` : Bill Clark

        Merge any number of images."""
        paths = self.splitPaths(images)
        self.m.merge(*paths)
    def do_testmerge(self, images):
        """
        `Author` : Bill Clark

        Merge any number of images, then reset status to before the merge."""
        paths = self.splitPaths(images)
        self.m.testMerge(*paths)
    def do_exportmerge(self, images):
        """
        `Author` : Bill Clark

        Merge any number of images, save to the outfile, and reset the state."""
        paths = self.splitPaths(images)
        self.m.exportMerge(paths[0], *paths[1:])
    def do_mergeas(self, images):
        """
        `Author` : Bill Clark

        Change the outfile to a new one, then merge any number of images."""
        paths = self.splitPaths(images)
        self.m.mergeAs(paths[0], *paths[1:])

    def do_redhighlight(self, arg):
        """
        `Author` : Bill Clark

        When a pixel is checked true, make it red."""
        self.m.processor.setActorCommand(PixelProcess.RedHighlightCommand())
    def do_takesecond(self, arg):
        """
        `Author` : Bill Clark

        When a pixel is checked true, make it the new pixel."""
        self.m.processor.setActorCommand(PixelProcess.TakeSecondCommand())
    def do_colordiff(self, checknum):
        """
        `Author` : Bill Clark

        Check a pair of pixels as true if the color difference is less than <number>."""
        self.m.processor.setCheckCommand(PixelProcess.ColorDiffCommand())
        if checknum: self.m.processor.checkcmd.diffnum = int(checknum)
        else: self.m.processor.checkcmd.diffnum = 0
    def do_resetcommands(self, arg):
        """
        `Author` : Bill Clark

        Set the check and act commands to empty commands."""
        self.m.processor.setActorCommand(PixelProcess.PixelCommand())
        self.m.processor.setCheckCommand(PixelProcess.PixelCommand())
    def do_takenonemptysecond(self):
        """
        `Author` : Bill Clark

        When a pixel is checked true, take the new pixel, if it's not (0,0,0)"""
        self.m.processor.setActorCommand(PixelProcess.TakeNonEmptySecondCommand())

    def do_extractremote(self, arg):
        """
        `Author` : Bill Clark

        Set the processor's remote to record changed pixels. Enables group commands."""
        self.m.processor = PixelProcess.ExtractPixelRemote()
    def do_regularremote(self, arg):
        """
        `Author` : Bill Clark

        Set the remote to a basic one."""
        self.m.processor = PixelProcess.PixelRemote()

    def do_gengroups(self, arg):
        """
        `Author` : Bill Clark

        Generate the groups from the extract remote. Requires a merge to have happened."""
        if isinstance(self.m.processor, PixelProcess.ExtractPixelRemote) \
          and self.m.processor.pixels is not None:
            self.groups = self.m.processor.getGroupedPixels()
    def do_showgroups(self, arg):
        """
        `Author` : Bill Clark

        Print all the groups via the container print method."""
        if self.groups:
           for group in self.groups.generator():
               print group
    def do_filtergroups(self, arg):
        """
        `Author` : Bill Clark

        Filter the groups with the filter command in the groups container."""
        if self.groups: self.groups.filter()
    def do_countsortgroups(self, arg):
        """
        `Author` : Bill Clark

        Sort the groups by the number of pixels within the area."""
        if self.groups: self.groups.sortCount()
    def do_ratiosortgroups(self, arg):
        """
        `Author` : Bill Clark

        Sort the groups by the ratio of modified pixels to unmodified."""
        if self.groups: self.groups.sortRatio()
    def do_savefirstgroup(self, path):
        """
        `Author` : Bill Clark

        Save the first group in the list to the output path."""
        if not path: print 'Specify the save path.'
        if self.groups and path: self.groups.first().save(path, self.m.processor.pixels)

    def do_detect(self, images):
        """
        `Author` : Bill Clark

        Detect people in any number of images."""
        paths = self.splitPaths(images)
        peopledetect.detect(paths)
    def do_cropfind(self, images):
        """
        `Author` : Bill Clark

        Given an image thats a subset of this image, find where that image fits into the other."""
        paths = self.splitPaths(images)
        print self.m.cropFind(paths[0], paths[1])

    def do_save(self, arg):
        """
        `Author` : Bill Clark

        Save the image."""
        self.m.save()
        print self.m.outfile
    def do_show(self, arg):
        """
        `Author` : Bill Clark

        Show the image."""
        self.m.show()

    def splitPaths(self, string):
        """
        `Author` : Bill Clark

        Split the string by extensions."""
        return re.findall('([^ ][^.]*\..{3})', string)

if __name__ == "__main__":
    con = Console('Output\ImFuse.jpg')
    con.onecmd('?')
    con.cmdloop()

