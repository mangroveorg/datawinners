from logging.handlers import RotatingFileHandler
import os
import gzip

COMPRESSION_SUPPORTED = {'gz': gzip}

class CompressRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=0):
        super(CompressRotatingFileHandler, self).__init__(filename, mode, maxBytes, backupCount, encoding, delay)
        self.compress_mode = 'gz'
        self.compress_cls = COMPRESSION_SUPPORTED[self.compress_mode]

    def doRollover(self):
        if self.stream:
            self.stream.close()
        if self.backupCount > 0:
            self._rotating()
            self._compress_file()
        self.mode = 'w'
        self.stream = self._open()

    def shouldRollover(self, record):
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            if os.stat(self.baseFilename).st_size + len(msg) >= self.maxBytes:
                return 1
        return 0

    def _rotating(self):
        for i in range(self.backupCount - 1, 0, -1):
            sfn = "%s.%d.%s" % (self.baseFilename, i, self.compress_mode)
            dfn = "%s.%d.%s" % (self.baseFilename, i + 1, self.compress_mode)
            if os.path.exists(sfn):
                #print "%s -> %s" % (sfn, dfn)
                if os.path.exists(dfn):
                    os.remove(dfn)
                os.rename(sfn, dfn)

    def _compress_file(self):
        dfn = "%s.%d.%s" % (self.baseFilename, 1, self.compress_mode)
        with open(self.baseFilename) as log:
            with self.compress_cls.open(dfn, 'wb') as comp_log:
                comp_log.writelines(log)
                #print "%s -> %s" % (self.baseFilename, dfn)


