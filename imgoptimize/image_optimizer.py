# coding=utf-8
import logging
import os
from io import BytesIO
from PIL import Image
from werkzeug.datastructures import FileStorage

from tinify import tinify
import boto3

__author__ = ['ThucNC', 'QuyPN']
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

    def _do_optimize(self, source, width, height, make_thumb,
                     make_cover):
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
        return source

    def image_optimize(self, from_file_path, to_file_path=None, width=None, height=None, make_thumb=False,
                       make_cover=False):
        """
        support png and jpeg
        :param to_file_path:
        :param make_cover:
        :param height:
        :param width:
        :param make_thumb:
        :param from_file_path:
        :return:
        """
        if self._tinify_api_key:
            tf = tinify.get_instance()
            tf.key = self._tinify_api_key
            source = tf.from_file(from_file_path)
            if not to_file_path:
                to_file_path = from_file_path
            source = self._do_optimize(source, width, height, make_thumb, make_cover)
            source.to_file(to_file_path)
        else:
            raise Exception("Only tinify backend is currently supported!")

    def image_optimize_from_buffer(self, file, width=None, height=None, make_thumb=False,
                                   make_cover=False):
        """
        support png and jpeg
        :param file:
        :param make_cover:
        :param height:
        :param width:
        :param make_thumb:
        :return:
        """
        if self._tinify_api_key:
            tf = tinify.get_instance()
            tf.key = self._tinify_api_key
            source = tf.from_file(file)
            source = self._do_optimize(source, width, height, make_thumb, make_cover)
            return source.to_buffer()
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
        return to_file_path

    def s3_upload(self, file, file_path, bucket_name, width=None, height=None, make_thumb=False, make_cover=False):
        s3 = boto3.resource(service_name='s3')
        obj = BytesIO(self.image_optimize_from_buffer(file, width, height, make_thumb, make_cover))
        s3.Bucket(bucket_name).upload_fileobj(Fileobj=obj, Key=file_path,
                                              ExtraArgs={"ACL": "public-read", "ContentType": file.content_type})
        return f'https://{bucket_name}.s3.amazonaws.com/{file_path}'

    def s3_upload_cover(self, file, file_path, bucket_name, suffix='_cover'):
        file_name, file_extension = os.path.splitext(file_path)
        file_path = file_name + suffix + file_extension
        return self.s3_upload(file, file_path, bucket_name, width=1280, height=720, make_cover=True)

    def s3_upload_thumb(self, file, file_path, bucket_name, suffix='_thumb'):
        file_name, file_extension = os.path.splitext(file_path)
        file_path = file_name + suffix + file_extension
        return self.s3_upload(file, file_path, bucket_name, width=640, height=360, make_thumb=True)

    # def image_convert_buf(self, file, max_width=0, max_height=0, quality=70):
    #     image = Image.open(file)
    #     if image.mode != 'RGB':
    #         image = image.convert('RGB')
    #     if max_width or max_height:
    #         image.thumbnail((max_width, max_height))
    #     buf = BytesIO()
    #     image.save(buf, 'JPEG', quality=quality)
    #     return buf


if __name__ == "__main__":
    img_opti = ImageOptimizer(tinify_api_key="8kStJZxfd9FprXb9cDL2mtkmN421XCqD")
    ifile = "/home/quypn/Pictures/testtest.jpg"
    # ofile = "/home/thuc/Documents/blog_opti.png"
    # image_convert(ifile, ofile, 1280, 360)
    # with open(ifile, 'rb') as fp:
    #     img = FileStorage(fp, content_type='image/jpg')
    #     img.filename = 'a.jpg'
    #     print(img_opti.s3_upload(img, 'uploads/8/test/quy1.png', 'ucode-dev'))

    # with open(ifile, 'rb') as fp:
    #     img = FileStorage(fp, content_type='image/jpg')
    #     img.filename = 'a.jpg'
    #     print(img_opti.s3_upload_thumb(img, 'uploads/8/test/quy1.png', 'ucode-dev'))
    #
    # with open(ifile, 'rb') as fp:
    #     img = FileStorage(fp, content_type='image/jpg')
    #     img.filename = 'a.jpg'
    #     print(img_opti.s3_upload_cover(img, 'uploads/8/test/quy1.png', 'ucode-dev'))

    # img_opti.image_to_jpg(ifile)
    # img_opti.make_cover(ifile)
    # img_opti.make_thumbnail(ifile)
    #
    # jpg_file = img_opti.image_to_jpg(ifile)
    # img_opti.make_cover(jpg_file)
    # img_opti.make_thumbnail(jpg_file)
    #
    # img_opti.image_to_jpg("/home/thuc/Documents/blog.png", quality=50)
    # img_opti.image_to_jpg("/home/thuc/Documents/blog_thumb.png", quality=50)
    # img_opti.image_optimize(ifile, ofile, width=630, height=480, make_thumb=True)
