import os
import math
import PIL
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageStat
import matplotlib.pyplot as plt
import argparse

watermark = ""
corner = "bottom-center"
resize_amt = 100
inverted = "auto"
input_dir = ""
output_dir = ""

def get_brightness(image, rect):
    image_l = image.convert("L")
    (width, height) = image_l.size
    mask = PIL.Image.new('L', (width, height), 0)
    drawing_layer = PIL.ImageDraw.Draw(mask)
    drawing_layer.rectangle(rect, fill=255)
    return PIL.ImageStat.Stat(image_l, mask=mask).mean

def get_needs_invert(image, rect):
    brightness = get_brightness(image, rect)[0]
    return brightness <= 127

def invert_rgba(image):
    r, g, b, a = image.split()
    r, g, b = map(lambda i: i.point(lambda p: 255 - p), (r, g, b))
    return PIL.Image.merge(image.mode, (r, g, b, a))

def add_logo(image, logo):
    """ Adds a logo to a PIL.Image

    image: A PIL.Image which will receive a logo
    logo: A PIL.Image which will be used as a logo

    Returns a PIL.Image with the logo applied to the correct corner.
    """

    global corner
    global inverted

    (width, height) = logo.size

    # Resize the logo
    logo_max = max([height, width])
    logo_aspect_ratio = height / float(width)

    image_max = max(image.size)

    area_pct = 0.015
    image_area = image.size[0] * image.size[1]
    logo_area = int(area_pct * image_area)

    width = int(math.sqrt(logo_area / logo_aspect_ratio))
    height = int(width * logo_aspect_ratio)

    logo = logo.resize((width, height))

    # Calculate logo padding / positioning based on corner
    percent = 0.02
    if corner == "bottom-left":
        padding = tuple(map(lambda x: int(x), [percent * image.size[0], image.size[1] - height - percent * image.size[1]]))
    elif corner == "bottom-right":
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - percent * image.size[0], image.size[1] - height - percent * image.size[1]]))
    elif corner == "top-left":
        padding = tuple(map(lambda x: int(x), [percent * image.size[0], percent * image.size[0]]))
    elif corner == "top-right":
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - percent * image.size[0], percent * image.size[1]]))
    else:
        padding = tuple(map(lambda x: int(x), [image.size[0]/2 - width/2, image.size[1] - height - percent * image.size[1]]))
    needs_invert = get_needs_invert(image, [padding, (padding[0] + width, padding[1] + height)])
    if (inverted == "inverted") or (needs_invert and inverted == "auto"):
        logo = invert_rgba(logo)
    image.paste(logo, padding, mask=logo)
    return image

def manipulate_image(current_image, current_filename):
    global output_dir
    global watermark
    global resize_amt
    print "Processing image:", current_filename
    resize_pct = resize_amt / 100.0
    current_image = current_image.resize((int(current_image.size[0] * resize_pct), int(current_image.size[1] * resize_pct)))
    logo = PIL.Image.open(os.path.join(os.getcwd(), watermark))
    current_image = add_logo(current_image, logo)
    current_image.save(os.path.join(os.getcwd(), output_dir, current_filename), 'JPEG')


def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.

    If directory is not specified, uses current directory.
    Returns a 2-tuple containing
    a list with a  PIL.Image object for each image file in root_directory, and
    a list with a string filename for each image file in root_directory
    """

    global input_dir
    global output_dir

    if directory == None:
        directory = os.path.join(os.getcwd(), input_dir) # Use working directory if unspecified
    image_list = []
    file_list = []
    new_directory = os.path.join(os.getcwd(), output_dir)
    try:
        os.mkdir(new_directory)
    except OSError:
        pass # if the directory already exists, proceed
    directory_list = os.listdir(directory) # Get list of files
    for entry in directory_list:
        absolute_filename = os.path.join(directory, entry)
        try:
            image = PIL.Image.open(absolute_filename)
            file_list += [entry]
            image_list += [image]
        except IOError:
            pass # do nothing with errors tying to open non-images
    return image_list, file_list

def main():
    """ The main function of the program. It is used to get the client's preferences and manipulate each image in the images directory.
    """


    images = get_images()
    for n in range(len(images[0])):
        manipulate_image(images[0][n], images[1][n])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input",
                        help="The input image directory.", type=str)
    parser.add_argument("output", help="The output image directory.", type=str)
    parser.add_argument("watermark", help="The watermark to put on images.", type=str)
    parser.add_argument("--resize", "-r", help="The percent to scale the image to.", type=float, default=100)
    parser.add_argument("--location", "-l", help="The location of the watermark. Defaults to bottom-center.", type=str,
                        choices=["top-left", "top-right", "bottom-left", "bottom-right", "bottom-center"], default="bottom-center")
    parser.add_argument("--inverted", "-i", help="Choose whether the watermark is inverted. Defaults to auto.", type=str,
                        choices=["inverted", "not-inverted", "auto"], default="auto")
    args = parser.parse_args()

    inverted = args.inverted
    watermark = args.watermark

    corner = args.location

    input_dir = args.input
    output_dir = args.output

    resize_amt = args.resize

    main()
