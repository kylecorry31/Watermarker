import os.path
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

def manipulate_image(image):
    current_image = PIL.Image.open(os.getcwd() + '\\' + image)
    current_image = current_image.convert("RGBA")
    logo = PIL.Image.open(os.getcwd() + "\\" + raw_input("What is the logo file name?\n"))
    corner = int(raw_input("Location of the logo bottom left (0), buttom right (1), top left (2), top right (3)\n"))
    current_image = convert_to_black_and_white(current_image)
    current_image = add_logo(current_image, logo, corner)
    show_image(current_image)

def combine_images(images):
    for image in images:
        print os.getcwd()

def main():
    image = raw_input("What is the image file name?\n")
    option = int(raw_input("Do you want to manipulate a single image (1) or combine images (2)?\n"))
    if option == 1:
        manipulate_image(image)
    else:
        images = []
        while True:
            image = raw_input("What is the image file name or 1 to continue to the combination\n")
            if image == "1":
                break
            images.append(image)
        combine_images(images)
        
if __name__ == "__main__":
    main()