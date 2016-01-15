import os.path
import PIL

def get_images(directory=None):
    """ Returns PIL.Image objects for all the images in directory.
    
    If directory is not specified, uses current directory.
    Returns a 2-tuple containing 
    a list with a  PIL.Image object for each image file in root_directory, and
    a list with a string filename for each image file in root_directory
    """
    
    if directory == None:
        directory = os.getcwd() # Use working directory if unspecified
        
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

def manipulate_image(image):
    print os.getcwd() + image

def combine_images(images):
    for image in images:
        print os.getcwd

def main():
    image = raw_input("What is the image file name?")
    option = int(raw_input("Do you want to manipulate a single image (1) or combine images (2)?\n"))
    if option == 1:
        manipulate_image(image)
    else:
        images = []
        while True:
            image = raw_input("What is the image file name or 1 to continue to the combination/n")
            if image == "1":
                break
            images.append(image)
        combine_images(images)
        
if __name__ == "__main__":
    main()