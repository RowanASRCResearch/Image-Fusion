import cv2
from matplotlib import pyplot as plt
import PIL
from PIL import Image
from PIL import ImageFilter


image = PIL.Image.open('Input/Two Infrared test.png')
image = image.filter(ImageFilter.FIND_EDGES)
image.show()

image = PIL.Image.open('Input/Two Crop test.png')
image = image.filter(ImageFilter.FIND_EDGES)
image.show()

img = cv2.imread('Input/Two Infrared.jpg')
edges = cv2.Canny(img,50,200,apertureSize = 3)

plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Edge Image'), plt.xticks([]), plt.yticks([])

plt.show()