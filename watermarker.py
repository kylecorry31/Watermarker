import os
import math
import PIL
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageStat
import argparse

class ShouldInvertAlgorithm(object):
    def should_invert(self, image, region):
        pass

class AlwaysInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        return True

class NeverInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        return False

class AutoInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        l1 = self.__get_luminance(image, region)[0] / 255.0

        return l1 <= 0.5
        # TODO: See why this doesn't work as well
        # luminance1 = (l1 + 0.05) / 0.05
        # luminance2 = 1.05 / (l1 + 0.05)
        # if min([luminance1, luminance2]) >= 14:
        #     return luminance1 <= luminance2
        # elif luminance1 >= 14:
        #     return False
        # elif luminance2 >= 14:
        #     return True
        # else:
        #     return l1 <= 0.5

    def __get_luminance(self, image, region):
        image_l = image.convert("L")
        (width, height) = image_l.size
        mask = PIL.Image.new('L', (width, height), 0)
        drawing_layer = PIL.ImageDraw.Draw(mask)
        drawing_layer.rectangle(region, fill=255)
        return PIL.ImageStat.Stat(image_l, mask=mask).mean


class Watermarker(object):
    """An object to add watermarks to images"""
    def __init__(self, watermark, inverter):
        super(Watermarker, self).__init__()
        self.watermark = watermark
        self.inverter = inverter

    def add_watermark(self, image, location, proportion=0.015, border_padding=0.02):
        (width, height) = self.watermark.size

        # Resize the logo
        watermark_max = max(self.watermark.size)
        watermark_aspect_ratio = height / float(width)

        image_max = max(image.size)

        image_area = image.size[0] * image.size[1]
        watermark_area = int(proportion * image_area)

        width = int(math.sqrt(watermark_area / watermark_aspect_ratio))
        height = int(width * watermark_aspect_ratio)

        watermark_mod = self.watermark.resize((width, height))

        # Calculate watermark padding / positioning based on corner
        if location == "bottom-left":
            padding = tuple(map(lambda x: int(x), [border_padding * image.size[0], image.size[1] - height - border_padding * image.size[1]]))
        elif location == "bottom-right":
            padding = tuple(map(lambda x: int(x), [image.size[0] - width - border_padding * image.size[0], image.size[1] - height - border_padding * image.size[1]]))
        elif location == "top-left":
            padding = tuple(map(lambda x: int(x), [border_padding * image.size[0], border_padding * image.size[0]]))
        elif location == "top-right":
            padding = tuple(map(lambda x: int(x), [image.size[0] - width - border_padding * image.size[0], border_padding * image.size[1]]))
        else:
            padding = tuple(map(lambda x: int(x), [image.size[0]/2 - width/2, image.size[1] - height - border_padding * image.size[1]]))
        needs_invert = self.inverter.should_invert(image, [padding, (padding[0] + width, padding[1] + height)])
        if needs_invert:
            watermark_mod = invert_rgba(watermark_mod)
        image.paste(watermark_mod, padding, mask=watermark_mod)
        return image

# Image helpers
def resize_image(image, percent):
    if percent == 100:
        return image
    prop = percent / 100.0
    (width, height) = image.size
    return image.resize( (int(width * prop), int(height * prop)) )

def invert_rgba(image):
    r, g, b, a = image.split()
    r, g, b = map(lambda i: i.point(lambda p: 255 - p), (r, g, b))
    return PIL.Image.merge(image.mode, (r, g, b, a))

def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.

    If directory is not specified, uses current directory.
    Returns a 2-tuple containing
    a list with a  PIL.Image object for each image file in root_directory, and
    a list with a string filename for each image file in root_directory
    """
    if directory == None:
        return [], []
    image_list = []
    file_list = []
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


def manipulate_image(current_image, watermarker, corner, resize_amt):
    current_image = resize_image(current_image, resize_amt)
    current_image = watermarker.add_watermark(current_image, corner)
    return current_image

def main(input_dir, output_dir, watermark, corner, resize_amt, inverted):
    """ The main function of the program. It is used to get the client's preferences and manipulate each image in the images directory.
    """

    # Create output directory
    new_directory = os.path.join(os.getcwd(), output_dir)
    try:
        os.mkdir(new_directory)
    except OSError:
        pass # if the directory already exists, proceed

    images = get_images(input_dir)
    logo = PIL.Image.open(os.path.join(os.getcwd(), watermark))

    inverter = AutoInvert()

    if inverted == "auto":
        inverter = AutoInvert()
    elif inverted == "inverted":
        inverter = AlwaysInvert()
    elif inverted == "not-inverted":
        inverter = NeverInvert();

    watermarker = Watermarker(logo, inverter)
    for n in range(len(images[0])):
        current_image = images[0][n]
        current_filename = images[1][n]
        print "Processing image:", current_filename, "(" + str(n + 1) + "/" + str(len(images[0]))+ ")"
        current_image = manipulate_image(current_image, watermarker, corner, resize_amt)
        try:
            current_image.save(os.path.join(output_dir, current_filename), 'JPEG')
        except Exception as e:
            print "Could not write image:", current_filename


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

    main(args.input, args.output, args.watermark, args.location, args.resize, args.inverted)
