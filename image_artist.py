import os.path
import PIL
import matplotlib.pyplot as plt


def show_image(image):
    plt.imshow(image)
    plt.show()

def manipulate_image(image):
    current_image = PIL.Image.open(os.getcwd() + '\\' + image)
    current_image = current_image.convert("RGBA")
    logo = PIL.Image.open(os.getcwd() + "\\" + raw_input("What is the logo file name?\n"))
    logo_position = [0, 0]
    logo_position[0] = int(raw_input("X location of the logo\n"))
    logo_position[1] = int(raw_input("Y location of the logo\n"))
    logo_max = max([logo.height, logo.width])
    logo_aspect_ratio = logo.height / float(logo.width)
    if logo_max == logo.height:
        height = int(0.25 * current_image.height)
        width = int(height / logo_aspect_ratio)
        logo.resize((width, height))
    else:
        width = int(0.25 * current_image.width)
        height = int(width *  logo_aspect_ratio)
        logo.resize((width, height))
    current_image.paste(logo, tuple(logo_position), mask=logo)
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