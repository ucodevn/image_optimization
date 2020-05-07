# coding=utf-8
import logging

__author__ = 'ThucNC'

import os

from PIL import Image

from tinify import tinify

_logger = logging.getLogger(__name__)


class ImageOptimizer:
    """
    For best result:
        1. use png as source file,
        2. make cover and thumbnail and optimize them,
        3. convert to jpg if needed as the last step

    For facebook Images in Link Shares
        Use images that are at least 1200 x 630 pixels for the best display on high resolution devices.
        At the minimum, you should use images that are 600 x 315
    """
    def __init__(self, tinify_api_key=None):
        self._tinify_api_key = tinify_api_key
        pass

    def make_thumbnail(self, from_file_path, to_file_path=None, suffix="_thumb", width=640, height=360):
        if not to_file_path:
            filename, file_extension = os.path.splitext(from_file_path)
            to_file_path = filename + suffix + file_extension
        self.image_optimize(from_file_path, to_file_path, width=width, height=height, make_thumb=True)

    def make_cover(self, from_file_path, to_file_path=None, suffix="_cover", width=1280, height=720):
        if not to_file_path:
            filename, file_extension = os.path.splitext(from_file_path)
            to_file_path = filename + suffix + file_extension
        self.image_optimize(from_file_path, to_file_path, width=width, height=height, make_cover=True)

    def image_optimize(self, from_file_path, to_file_path=None,
                       width=None, height=None,
                       make_thumb=False, make_cover=False):
        """
        support png and jpeg
        :param file_path:
        :return:
        """
        if self._tinify_api_key:
            tf = tinify.get_instance()
            tf.key = self._tinify_api_key
            source = tf.from_file(from_file_path)
            if not to_file_path:
                to_file_path = from_file_path

            if make_thumb:
                source = source.resize(
                    method="thumb",
                    width=width,
                    height=height
                )
            elif make_cover:
                source = source.resize(
                    method="cover",
                    width=width,
                    height=height
                )
            else:
                if width or height:
                    if width and height:
                        source = source.resize(
                            method="fit",
                            width=width,
                            height=height
                        )
                    elif width:
                        source = source.resize(
                            method="scale",
                            width=width,
                        )
                    else:
                        source = source.resize(
                            method="scale",
                            height=height
                        )

            source.to_file(to_file_path)
        else:
            raise Exception("Only tinify backend is currently supported!")

    def image_to_jpg(self, from_file_path, to_file_path=None, max_width=0, max_height=0, quality=70):
        if not to_file_path:
            filename, file_extension = os.path.splitext(from_file_path)
            to_file_path = filename + '.jpg'

        return self.image_convert(from_file_path, to_file_path, max_width, max_height, quality)

    def image_convert(self, from_file_path, to_file_path=None, max_width=0, max_height=0, quality=70):
        image = Image.open(from_file_path)

        to_file_name, to_file_extension = os.path.splitext(to_file_path)
        if to_file_extension == ".jpg":
            if image.mode != 'RGB':
                image = image.convert('RGB')

        if not to_file_path:
            to_file_path = from_file_path
        if max_width or max_height:
            image.thumbnail((max_width, max_height))
        image.save(to_file_path, quality=quality)
        return  to_file_path


if __name__ == "__main__":
    img_opti = ImageOptimizer(tinify_api_key="8kStJZxfd9FprXb9cDL2mtkmN421XCqD")
    ifile = "/home/thuc/Documents/blog.png"
    # ofile = "/home/thuc/Documents/blog_opti.png"
    # image_convert(ifile, ofile, 1280, 360)

    # img_opti.image_to_jpg(ifile)
    img_opti.make_cover(ifile)
    img_opti.make_thumbnail(ifile)

    jpg_file = img_opti.image_to_jpg(ifile)
    img_opti.make_cover(jpg_file)
    img_opti.make_thumbnail(jpg_file)

    # img_opti.image_to_jpg("/home/thuc/Documents/blog.png", quality=50)
    # img_opti.image_to_jpg("/home/thuc/Documents/blog_thumb.png", quality=50)
    # img_opti.image_optimize(ifile, ofile, width=630, height=480, make_thumb=True)
