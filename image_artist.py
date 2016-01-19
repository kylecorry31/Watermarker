import os.path
import PIL


def manipulate_image(image):
    current_image = PIL.Image.open(os.getcwd() + '\\' + image)
    print current_image

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