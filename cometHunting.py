import os
import math
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import glob
import skimage
import cv2
plt.style.use('default')

images = []
final_list = []

def functionname(img1, img2, distance):
    matches1_2 = []
    vectors_list = []
    coords1 = list(zip(*np.where(img1 > 0)))
    for x, y in coords1:        
        xmin = max(0, x - distance)
        xmax = min(img2.shape[0], x + distance)
        ymin = max(0, y - distance)
        ymax = min(img2.shape[1], y + distance)  
        region = img2[xmin:xmax, ymin:ymax]
        rows, cols = np.where(region)
        if len(rows) > 0:
            for r, col in zip(rows, cols):
                newx = xmin + r
                newy = ymin + col
                if newx == x and newy == y:
                    pass
                else:
                    star_distance = (math.sqrt((y-newy)**2+(x-newx)**2))
                    matches1_2.append((y, x))
                    star_angle = (math.atan2((newy - y),(newx - x)))
                    vectors_list.append([x, y, newx, newy, star_angle, star_distance])
    return vectors_list

def paint_sky(matched_vectors, dilation):
    image1 = np.zeros((1024, 1024), dtype=np.uint8)
    image2 = np.zeros((1024, 1024), dtype=np.uint8)
    image3 = np.zeros((1024, 1024), dtype=np.uint8)
    image4 = np.zeros((1024, 1024), dtype=np.uint8)

    coordinates1 = []
    coordinates2 = []
    coordinates3 = []
    coordinates4 = []

    for span in matched_vectors:
        coordinates1.append((int(span[0][0]), int(span[0][1])))
        coordinates2.append((int(span[1][0]), int(span[1][1])))
        coordinates3.append((int(span[2][0]), int(span[2][1])))
        coordinates4.append((int(span[2][2]), int(span[2][3])))

    for coord in coordinates1:
        image1[coord[1], coord[0]] = 1
    for coord in coordinates2:
        image2[coord[1], coord[0]] = 1
    for coord in coordinates3:
        image3[coord[1], coord[0]] = 1
    for coord in coordinates4:
        image4[coord[1], coord[0]] = 1

    kernel = np.ones((dilation, dilation), np.uint8)

    image1_dilated = cv2.dilate(image1, kernel, iterations=1)
    image2_dilated = cv2.dilate(image2, kernel, iterations=1)
    image3_dilated = cv2.dilate(image3, kernel, iterations=1)
    image4_dilated = cv2.dilate(image4, kernel, iterations=1)
    return image1_dilated, image2_dilated, image3_dilated, image4_dilated

def matrix_movie(frames, output_file, fps, scalar):
    height, width = 1024, 1024
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
    print("VideoWriter opened:", out.isOpened())


    for comet in frames:
        comet_bgr = cv2.cvtColor(comet, cv2.COLOR_GRAY2BGR)
        comet_bgr = comet_bgr * scalar
        comet_bgr = np.clip(comet_bgr, 0, 255)
        comet_unit8 = comet_bgr.astype(np.uint8)
        out.write(comet_unit8)
    out.release()
    cv2.destroyAllWindows()
    print("Saving to:", os.path.abspath(output_file))
    print(f"Video saved as {output_file}")
np.set_printoptions(threshold=100)

Mask= Image.open('Images/mask.png')

os.chdir('Images/images')
# You will need to change the path to the one with your images

SOHO_images = sorted(glob.glob('*.gif'))


for file in SOHO_images:
    images.append(file)


final = []
#MaskVince = np.array(Mask)
#Mask = Image.open('/fs/ess/PZS1154/mask.png')
MaskArray = np.array(Mask)
#MaskArray = MaskArray - 1
#print(MaskArray.sum())

if len(MaskArray.shape) == 3:
    MaskArray = np.mean(MaskArray, axis=2)

for i in images[5:10]:
    img = Image.open(i)
    #plt.imshow(img)
    #plt.show()
    imgArray = np.array(img)
    #pngimage = Image.fromarray(imgArray)
    #pngimage.save(f"output{i}.png")
    binary = imgArray > 160
    #final = (binary * MaskArray)
    #final = (final).astype(np.uint8)
    #img = Image.fromarray(final)
    #img.save(f"mask(i).gif")
    #plt.imshow(final)
    #plt.show()
   
    mask2 = skimage.morphology.remove_small_objects(binary, min_size = 20)
    mask2 = ~skimage.morphology.dilation(mask2, skimage.morphology.disk(20))
    hold = binary & mask2
    comets_only = hold * MaskArray * imgArray
    comets_only = skimage.morphology.skeletonize(comets_only)
    final_list.append(comets_only)
    #plt.imshow(comets_only)
    #plt.show()
    comets_only = np.where(comets_only)
    comets_only = list(zip(*comets_only))
    print(i)

exit = (functionname(final_list[0], final_list[1], 10))
fig, ax = plt.subplots()
ax.imshow(final_list[0])
ax.invert_yaxis()
# for x, y, x1, x2, angle, distance in exit:
#     square = patches.Rectangle((x - 10, y - 10), 30, 30, fill = False, edgecolor = 'white')
#     ax.add_patch(square)
# plt.show()

# x and y need to be switched

for x, y, *_ in exit:
    ax.add_patch(
        patches.Rectangle(
            (y - 10, x - 10),
            20,
            20,
            fill=False,
            edgecolor='white'
        )
    )
plt.show()

exit = (functionname(final_list[1], final_list[2], 10))
fig, ax = plt.subplots()
ax.imshow(final_list[1])
ax.invert_yaxis()
# for x, y, x1, x2, angle, distance in exit:
#     square = patches.Rectangle((x - 10, y - 10), 30, 30, fill = False, edgecolor = 'white')
#     ax.add_patch(square)
# plt.show()

# 
for x, y, *_ in exit:
    ax.add_patch(
        patches.Rectangle(
            (y - 10, x - 10),
            20,
            20,
            fill=False,
            edgecolor='white'
        )
    )
plt.show()


vec1 = functionname(final_list[0], final_list[1], 10)
vec2 = functionname(final_list[1], final_list[2], 10)
vec3 = functionname(final_list[2], final_list[3], 10)
vec4 = functionname(final_list[3], final_list[4], 10)

valid_comets = []
for i in vec1:
    x1,y1 = i[2],i[3]
    for j in vec2:
        x2,y2 = j[0],j[1]
        x3,y3 = j[2],j[3]
        for k in vec3:
            x4,y4 = k[0],k[1]

            if x1 == x2 and y1 == y2 and x3 == x4 and y3 == y4:
                valid_comets.append((i,j,k))

print(len(valid_comets))
frames = paint_sky(valid_comets, 10)
matrix_movie(frames, "output_file2.mp4", 1, 255)

