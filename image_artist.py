import os
import PIL
import matplotlib.pyplot as plt


def show_image(image):
    plt.imshow(image)
    plt.show()
    
def convert_to_black_and_white(image):
    return image.convert('LA')
    
def add_logo(image, logo, corner):
    (width, height) = logo.size
    logo_max = max([height, width])
    logo_aspect_ratio = height / float(width)
    if logo_max == height:
        height = int(0.25 * image.size[1])
        width = int(height / logo_aspect_ratio)
        logo = logo.resize((width, height))
    else:
        width = int(0.25 * image.size[0])
        height = int(width *  logo_aspect_ratio)
        logo = logo.resize((width, height))
    btm_left = 0
    btm_right = 1
    top_left = 2
    if corner == btm_left:
        padding = tuple(map(lambda x: int(x), [0.05 * image.size[0], image.size[1] - height - 0.05 * image.size[1]]))
    elif corner == btm_right:
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - 0.05 * image.size[0], image.size[1] - height - 0.05 * image.size[1]]))
    elif corner == top_left:
        padding = tuple(map(lambda x: int(x), [0.05 * image.size[0], 0.05 * image.size[1]]))
    else:
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - 0.05 * image.size[0], 0.05 * image.size[1]]))
    image.paste(logo, padding, mask=logo)
    return image

def frame_image(original_image, color, wide):
    """ Rounds the corner of a PIL.Image
    
    original_image must be a PIL.Image
    color: The color of the border as a 3-tuple of RGB color (R, G, B)
    wide: The width in pixels of the border.
    
    Returns a new PIL.Image with borders.
    """
    width, height = original_image.size
    border_mask = PIL.Image.new('RGBA', (width, height), (127,0,127,0))
    drawing_layer = PIL.ImageDraw.Draw(border_mask)
    drawing_layer.polygon([(wide,wide),(width-wide,wide),
                            (width-wide,height-wide),(wide,height-wide)],
                            fill=(127,0,127,255))
    result = PIL.Image.new('RGBA', original_image.size, color)
    result.paste(original_image, (0,0), mask=border_mask)
    return result

def add_border(image, size, brand_primary_color, brand_secondary_color):
    image = frame_image(image, brand_primary_color, size)
    return image

def manipulate_image(current_image):
    #current_image = PIL.Image.open(os.getcwd() + '/' + image)
    current_image = current_image.convert("RGBA")
    logo = PIL.Image.open(os.path.join(os.getcwd(), 'logo.png'))
    # corner = int(raw_input("Location of the logo bottom left (0), buttom right (1), top left (2), top right (3)\n"))
    current_image = convert_to_black_and_white(current_image)
    current_image = current_image.convert("RGBA")
    current_image = add_logo(current_image, logo, 1)
    # current_image = add_border(current_image, 0.05 * current_image.size[0], (11, 117, 43), (0, 152, 18))
    show_image(current_image)


def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.
    
    If directory is not specified, uses current directory.
    Returns a 2-tuple containing 
    a list with a  PIL.Image object for each image file in root_directory, and
    a list with a string filename for each image file in root_directory
    """
    
    if directory == None:
        directory = os.path.join(os.getcwd(), "Images") # Use working directory if unspecified
    image_list = [] # Initialize aggregaotrs
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

def main():
    images = get_images()
    for image in images[0]:
        manipulate_image(image)
        
if __name__ == "__main__":
    main()
