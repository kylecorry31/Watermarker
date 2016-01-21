import os
import PIL
import PIL.ImageDraw
import matplotlib.pyplot as plt
    
def convert_to_grayscale(image):
    """ Converts a PIL.Image to grayscale

    image: A PIL.Image

    Returns a PIL.Image in grayscale.
    """
    image = image.convert('LA')
    return image.convert("RGBA")
    
def add_logo(image, logo, corner):
    """ Adds a logo to a PIL.Image

    image: A PIL.Image which will receive a logo
    logo: A PIL.Image which will be used as a logo
    corner: The number corresponding to the corner that the logo will be placed
            Bottom left: 0
            Bottom right: 1
            Top left: 2
            Top right: 3

    Returns a PIL.Image with the logo applied to the correct corner.
    """
    (width, height) = logo.size

    # Resize the logo
    logo_max = max([height, width])
    logo_aspect_ratio = height / float(width)
    if logo_max == height:
        height = int(0.22 * image.size[1])
        width = int(height / logo_aspect_ratio)
        logo = logo.resize((width, height))
    else:
        width = int(0.22 * image.size[0])
        height = int(width *  logo_aspect_ratio)
        logo = logo.resize((width, height))
        
    # Calculate logo padding / positioning based on corner
    btm_left = 0
    btm_right = 1
    top_left = 2
    percent = 0.08
    if corner == btm_left:
        padding = tuple(map(lambda x: int(x), [percent * image.size[0], image.size[1] - height - percent * image.size[1]]))
    elif corner == btm_right:
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - percent * image.size[0], image.size[1] - height - percent * image.size[1]]))
    elif corner == top_left:
        padding = tuple(map(lambda x: int(x), [percent * image.size[0], percent * image.size[0]]))
    else:
        padding = tuple(map(lambda x: int(x), [image.size[0] - width - percent * image.size[0], percent * image.size[1]]))
    image.paste(logo, padding, mask=logo)
    return image
    
def add_triangle_corners(original_image, wide, color):
    """ Adds triangles to the corners of a PIL.Image. Should be used after a border is applied

    original_image: A PIL.Image which will receive the triangle corners
    wide: The width and height of the triangle
    color: The color of the triangle

    Returns a PIL.Image with triangles in the corners
    """
    draw = PIL.ImageDraw.Draw(original_image)
    draw.polygon([(0, 0), (0, wide), (wide, 0)], fill=color) # top left
    draw.polygon([(original_image.size[0], 0),
                  (original_image.size[0], wide),
                  (original_image.size[0] - wide, 0)], fill=color) # top right
    draw.polygon([(0, original_image.size[1]),
                  (0, original_image.size[1] - wide),
                  (wide, original_image.size[1])], fill=color) # bottom left
    draw.polygon([(original_image.size[0], original_image.size[1]),
                  (original_image.size[0], original_image.size[1] - wide),
                  (original_image.size[0] - wide, original_image.size[1])], fill=color) # bottom right
    return original_image    
    
def frame_image(original_image, color, wide):
    """ Frames a PIL.Image
    
    original_image: A PIL.Image which will receive a frame
    color: The color of the border as a 3-tuple of RGB color (R, G, B)
    wide: The width in pixels of the border.
    
    Returns a PIL.Image with borders.
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

def add_border(image, size, color):
    image = frame_image(image, color, size)
    return image

def manipulate_image(current_image, current_filename, corner, gray):
    #current_image = PIL.Image.open(os.getcwd() + '/' + image)
    current_image = current_image.convert("RGBA")
    logo = PIL.Image.open(os.path.join(os.getcwd(), 'logo.png'))
    if gray:
        current_image = convert_to_grayscale(current_image)
    current_image = add_logo(current_image, logo, corner)
    current_image = add_border(current_image, 0.05 * current_image.size[0], (255, 255, 255))
    current_image = add_triangle_corners(current_image, 0.05 * current_image.size[0], (0, 0, 0))
    current_image.save(os.path.join(os.getcwd(), 'modified', current_filename), 'JPEG')


def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.
    
    If directory is not specified, uses current directory.
    Returns a 2-tuple containing 
    a list with a  PIL.Image object for each image file in root_directory, and
    a list with a string filename for each image file in root_directory
    """
    
    if directory == None:
        directory = os.path.join(os.getcwd(), "Images") # Use working directory if unspecified
    image_list = []
    file_list = []
    new_directory = os.path.join(os.getcwd(), 'modified')
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
    corner = int(raw_input("Location of the logo: bottom left (0), bottom right (1), top left (2), top right (3)\n"))
    gray = bool(int(raw_input("Make image grayscale? (1 = yes, 0 = no)\n")))
    for n in range(len(images[0])):
        manipulate_image(images[0][n], images[1][n], corner, gray)
        
if __name__ == "__main__":
    main()
