from Tkinter import *
from PIL import Image, ImageTk

class gifPlayer(Label):

    def __init__(self, master, filename, duration=None):
        self.master = master
        self.filename = filename
        self.duration = duration
        self.start(self.master, self.filename, self.duration)

    def start(self, master, filename, duration=None):
        self.im = Image.open(filename)
        seq =  []
        try:
            while 1:
                seq.append(self.im.copy())
                self.im.seek(len(seq)) # skip to next frame
        except EOFError:
            pass # we're done

        if duration is None:
            try:
                self.delay = self.im.info['duration']
            except KeyError:
                self.delay = 100
        else:
            self.delay = int(duration)

        self.frames = [ImageTk.PhotoImage(seq[0].convert('RGBA'))]

        for image in seq[1:]:
            self.frames.append(ImageTk.PhotoImage(image.convert('RGBA')))

        Label.__init__(self, master, image=self.frames[0])
        self.idx = 0
        self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.frames[self.idx % len(self.frames)])
        self.idx += 1
        self.cancel = self.after(self.delay, self.play)

    def ffwd(self):
        self.play()

    def slow(self):
        self.after_cancel(self.cancel)

    def run(self, root):
        Button(root, text='slow down', command=self.slow).pack()
        Button(root, text='speed up', command=self.ffwd).pack()
        root.mainloop()