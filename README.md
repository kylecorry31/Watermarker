# Watermarker
A python script for adding a watermark to many images at once.

## Requirements
* Python 3
* Python PIL library (pillow)

## Installation
Clone the project and install the dependencies.

To install PIL use ```pip install pillow```

## Usage
To add a watermark to your images, create a watermark png file and place all of your photos in a folder. Then call watermarker.py as such:

```shell
python watermarker.py input_dir output_dir watermark.png
```
Replace the input_dir with the folder of the photos, output_dir with the folder to store the modified folders, and watermark.png with your watermark.

For advanced options, use the help menu:

```shell
python watermarker.py -h
```

## Contributing
Please fork this repo and submit a pull request to contribute. I will review all changes and respond if they are accepted or rejected (as well as reasons, so it will be accepted).

## Credits
Just me for now, help is always great!

## License
This project is published under the MIT license. Please refer to [LICENSE](LICENSE) for more details.
