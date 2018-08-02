#!/usr/bin/env python3

"""Script to compile images into a PDF with each image cut into
appropriate size pieces, and with every second image forming the
second side of each page."""

import argparse
import logging
import math
import os.path
import tempfile

import img2pdf
from PIL import Image


DESCRIPTION = '''
Compile a double-sided PDF from images, tiling as necessary to fit the
paper size. Requires an even number of images.'''
DIFFERENT_SIZE_IMAGES_ERROR = 'The supplied images have different dimensions.'
DPI_HELP = 'DPI of images'
HEIGHT_HELP = 'height of printable area in millimetres'
IMAGES_HELP = 'image file'
OUTPUT_HELP = 'path to output file'
UNEVEN_NUMBER_IMAGES_ERROR = 'Script requires an even number of images.'
WIDTH_HELP = 'width of printable area in millimetres'


logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def main():
    parser = generate_parser()
    args = parser.parse_args()
    dpi = args.dpi
    print_size = (mm_to_px(args.width, dpi), mm_to_px(args.height, dpi))
    images, image_size = prepare_images(parser, args.images, dpi)
    parts = collate_images(images, image_size, print_size, dpi)
    logging.debug('Printable paper size (width x height):')
    logging.debug('Pixels: {} x {}'.format(print_size[0], print_size[1]))
    logging.debug('Points: {} x {}'.format(
        img2pdf.px_to_pt(print_size[0], dpi),
        img2pdf.px_to_pt(print_size[1], dpi)))
    with tempfile.TemporaryDirectory() as tmp_dir:
        paths = []
        for i, image in enumerate(parts):
            path = os.path.join(tmp_dir, '{:0>4}.jpg'.format(i))
            paths.append(path)
            image.save(path)
        page_size = (img2pdf.px_to_pt(print_size[0], dpi),
                     img2pdf.px_to_pt(print_size[1], dpi))
        layout = img2pdf.get_layout_fun(page_size)
        with open(args.output, 'wb') as fh:
            fh.write(img2pdf.convert(paths, layout_fun=layout))


def check_size(image_size, paper_size):
    """Returns the number of pieces that are required to fit `image_size`
    into `paper_size`.

    The return value is a 2-tuple of horizontal and vertical pieces.

    """
    if image_size[0] <= paper_size[0] and image_size[1] <= paper_size[1]:
        return (1, 1)
    else:
        return (math.ceil(image_size[0] / paper_size[0]),
                math.ceil(image_size[1] / paper_size[1]))


def collate_images(images, image_size, print_size, dpi):
    number_pieces = check_size(image_size, print_size)
    pieces = []
    for i in range(0, len(images), 2):
        if number_pieces != (1, 1):
            pieces.extend(split_images(images[i], images[i+1], number_pieces,
                                       print_size, dpi))
        else:
            pieces.extend((images[i], images[i+1]))
    return pieces


def generate_parser():
    """Returns an argparse parser for the script."""
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dpi', default=300, help=DPI_HELP, metavar='DPI',
                        type=int)
    parser.add_argument('--height', default=440, help=HEIGHT_HELP, type=int)
    parser.add_argument('--width', default=312, help=WIDTH_HELP, type=int)
    parser.add_argument('output', metavar='DEST', help=OUTPUT_HELP)
    parser.add_argument('images', metavar='IMAGE', nargs='+', help=IMAGES_HELP)
    return parser


def mm_to_px(size, dpi):
    """Returns `size` converted from mm to px according to the `dpi`."""
    # 25.4 mm to an inch.
    return math.floor(size / 25.4 * dpi)


def prepare_images(parser, image_paths, dpi):
    """Returns the images specified in `image_paths`, rotating them as
    needed for common alignment.

    If the images are not all the same size, or if there are an odd
    number of images, an error is raised and the script ends.

    """
    if len(image_paths) % 2 != 0:
        parser.exit(status=1, message=UNEVEN_NUMBER_IMAGES_ERROR)
    images = []
    image_size = None
    for image_path in image_paths:
        image = Image.open(image_path)
        size = image.size
        if image.height < image.width:
            image = image.rotate(90, expand=True)
            image = image.resize((size[1], size[0]))
        if image_size is None:
            image_size = image.size
        elif image.size != image_size:
            parser.exit(status=2, message=DIFFERENT_SIZE_IMAGES_ERROR)
        images.append(image)
    logging.debug('Image sizes (width x height):')
    logging.debug('Pixels: {} x {}'.format(image_size[0], image_size[1]))
    logging.debug('Points: {} x {}'.format(
        img2pdf.px_to_pt(image_size[0], dpi),
        img2pdf.px_to_pt(image_size[1], dpi)))
    return images, image_size


def split_images(image1, image2, number_pieces, paper_size, dpi):
    splits = []
    for i in range(number_pieces[0]):
        for j in range(number_pieces[1]):
            start_x = i * paper_size[0]
            start_y = j * paper_size[1]
            end_x = min((i + 1) * paper_size[0], image1.width)
            end_y = min((j + 1) * paper_size[1], image1.height)
            box = (start_x, start_y, end_x, end_y)
            part1 = image1.crop(box)
            part2 = image2.crop(box)
            splits.extend((part1, part2))
            logging.debug('Image piece sizes (width x height):')
            logging.debug('Pixels: {} x {}'.format(
                part1.width, part1.height))
            logging.debug('Points: {} x {}'.format(
                img2pdf.px_to_pt(part1.width, dpi),
                img2pdf.px_to_pt(part1.height, dpi)))
    return splits


if __name__ == '__main__':
    main()
