import os
import math
import PIL
import PIL.ImageDraw
import PIL.ImageOps
import PIL.ImageStat
import argparse

class ShouldInvertAlgorithm(object):
    def should_invert(self, image, region):
        """ Determines if the watermark should be inverted (assuming watermark is black).

        image: (PIL.Image) The image the watermark will be on.

        region: (array) The region in which the watermark will be placed, in the form [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]

        Returns True if the logo should be inverted, False otherwise. (Bool)
        """
        pass

class AlwaysInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        """ Always returns True, meaning the watermark should always be inverted.

        image: (PIL.Image) Not used.

        region: (array) Not used.

        Returns True
        """
        return True

class NeverInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        """ Always returns False, meaning the watermark should never be inverted.

        image: (PIL.Image) Not used.

        region: (array) Not used.

        Returns False
        """
        return False

class AutoInvert(ShouldInvertAlgorithm):
    def should_invert(self, image, region):
        """ Automatically determines if the watermark should be inverted (assuming watermark is black).

        image: (PIL.Image) The image the watermark will be on.

        region: (array) The region in which the watermark will be placed, in the form [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]

        Returns True if the logo should be inverted, False otherwise. (Bool)
        """
        l1 = self.__get_luminance(image, region) / 255.0

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
        """ Get the average luminance of the region.

        image: (PIL.Image) The image to get the luminance of.

        region: (array) The region to get the luminance of, in the form [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]

        Returns the average luminance of the region. (float)
        """
        image_l = image.convert("L")
        (width, height) = image_l.size
        mask = PIL.Image.new('L', (width, height), 0)
        drawing_layer = PIL.ImageDraw.Draw(mask)
        drawing_layer.rectangle(region, fill=255)
        return PIL.ImageStat.Stat(image_l, mask=mask).mean[0]


class Watermarker(object):
    """An object to add watermarks to images"""
    def __init__(self, watermark, inverter):
        """ Create a watermarker object.

        watermark: (PIL.Image) The watermark to add to images.

        inverter: (ShouldInvertAlgorithm) The algorithm which determines if the watermark should be inverted.
        """
        super(Watermarker, self).__init__()
        self.watermark = watermark
        self.inverter = inverter

    def add_watermark(self, image, location, proportion=0.015, border_padding=0.02):
        """ Adds a watermark to an image.

        image: (PIL.Image) The image to add a watermark to.

        location: (str) The location of the watermark. Either top_left, top_right, bottom_left, bottom_right, or bottom_center.

        proportion: (float) The proportion of the watermark area to the image area.

        border_padding: (float) The proportion of padding to add around the border of the image.

        Returns an image with a watermark. (PIL.Image)

        """
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

        if location == "auto":
            location = find_best_location(image, width, height, border_padding)

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

def find_best_location(image, logo_width, logo_height, border_padding):
    bl_padding = tuple(map(lambda x: int(x), [border_padding * image.size[0], image.size[1] - logo_height - border_padding * image.size[1]]))
    br_padding = tuple(map(lambda x: int(x), [image.size[0] - logo_width - border_padding * image.size[0], image.size[1] - logo_height - border_padding * image.size[1]]))
    tl_padding = tuple(map(lambda x: int(x), [border_padding * image.size[0], border_padding * image.size[0]]))
    tr_padding = tuple(map(lambda x: int(x), [image.size[0] - logo_width - border_padding * image.size[0], border_padding * image.size[1]]))
    bc_padding = tuple(map(lambda x: int(x), [image.size[0]/2 - logo_width/2, image.size[1] - logo_height - border_padding * image.size[1]]))

    paddings = [bl_padding, br_padding, tl_padding, tr_padding, bc_padding]

    vars = list(map(lambda padding: get_luminance_variance(image, [padding, (padding[0] + logo_width, padding[1] + logo_height)]), paddings))

    minimum = min(vars)

    index = vars.index(minimum)

    locations = ["bottom-left", "bottom-right", "top-left", "top-right", "bottom-center"]

    return locations[index]

# Image helpers
def resize_image(image, percent):
    """ Resize an image to a scale amount.

    image: (PIL.Image) The image to scale.

    percent: (float) The percentage of the original size to scale to.

    Returns the scaled image.
    """
    if percent == 100:
        return image
    prop = percent / 100.0
    (width, height) = image.size
    return image.resize( (int(width * prop), int(height * prop)) )

def invert_rgba(image):
    """ Invert the RGB values of an RGBA image.

    image: (PIL.Image) The image to invert as type RGBA.

    Returns the inverted RGBA image.
    """
    r, g, b, a = image.split()
    r, g, b = map(lambda i: i.point(lambda p: 255 - p), (r, g, b))
    return PIL.Image.merge(image.mode, (r, g, b, a))

def set_opacity(image, alpha):
    """ Sets the opacity of an image.

    image: (PIL.Image) The image to set the opacity of.

    alpha: (float) The opacity alpha from 0 to 1 inclusive.

    Returns the image with the opacity applied.
    """
    alpha_image = image.convert("RGBA")

    r, g, b, a = alpha_image.split()
    a = a.point(lambda p: int(255 * alpha) if p else 0)
    return PIL.Image.merge(alpha_image.mode, (r, g, b, a))

def get_luminance_variance(image, region):
    """ Get the variance of luminance of the region.

    image: (PIL.Image) The image to get the luminance of.

    region: (array) The region to get the luminance of, in the form [(x0, y0), (x1, y1)] or [x0, y0, x1, y1]

    Returns the variance of the luminance of the region. (float)
    """
    image_l = image.convert("L")
    (width, height) = image_l.size
    mask = PIL.Image.new('L', (width, height), 0)
    drawing_layer = PIL.ImageDraw.Draw(mask)
    drawing_layer.rectangle(region, fill=255)
    return PIL.ImageStat.Stat(image_l, mask=mask).var[0]


def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.

    If directory is not specified, it will return a tuple of empty lists.
    Returns a 2-tuple containing
    a list with a  PIL.Image object for each image file in the directory, and
    a list with a string filename for each image file in the directory
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
    """Manipulates a single image, resizing it and adding a watermark.

    current_image: (PIL.Image) The image to manipulate as a PIL.Image.

    watermarker: (Watermarker) The watermarker, which will add a watermark to an image.

    corner: (str) The location of the watermark on the image. Either top_left, top_right, bottom_left, bottom_right, or bottom_center.

    resize_amt: (float) The amount to scale the image to, as a percent.

    Returns the modified image.
    """
    current_image = resize_image(current_image, resize_amt)
    current_image = watermarker.add_watermark(current_image, corner)
    return current_image

def main(input_dir, output_dir, watermark, corner, resize_amt, inverted, opacity):
    """ The main function of the program, doing what the program is specified to do.

        input_dir: (str) The input directory, containing images.

        output_dir: (str) The ouput directory to put the modified images in. Does not need to exist.

        watermark: (str) The path of the watermark file.

        corner: (str) The location of the watermark on the image. Either top_left, top_right, bottom_left, bottom_right, or bottom_center.

        resize_amt: (float) The amount to scale the image to, as a percent.

        inverted: (str) The inversion algorithm as a str. Either auto, inverted, or not-inverted.

        opacity: (float) The opacity alpha of the watermark, None means no change.
    """

    # Create output directory
    try:
        os.mkdir(output_dir)
    except OSError:
        pass # if the directory already exists, proceed

    images = get_images(input_dir)
    logo = PIL.Image.open(watermark).convert("RGBA")
    if opacity is not None:
        logo = set_opacity(logo, min(1, max(0, opacity)))

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
    parser.add_argument("--location", "-l", help="The location of the watermark. Defaults to auto.", type=str,
                        choices=["top-left", "top-right", "bottom-left", "bottom-right", "bottom-center", "auto"], default="auto")
    parser.add_argument("--inverted", "-i", help="Choose whether the watermark is inverted. Defaults to auto.", type=str,
                        choices=["inverted", "not-inverted", "auto"], default="auto")
    parser.add_argument("--opacity", "-o", help="Sets the opacity alpha of the watermark, between 0 and 1 inclusive. Defaults to no change.", type=float, default=None)
    args = parser.parse_args()

    main(args.input, args.output, args.watermark, args.location, args.resize, args.inverted, args.opacity)
