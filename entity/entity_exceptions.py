# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


class InvalidFileFormatException(Exception):

    def __str__(self):
        return self.message