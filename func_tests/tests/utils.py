import os
import tempfile
import zipfile


def get_subject_short_code(flash_message):
    #Assumes that the word before "successfully registered" is the short code
    message = flash_message.split()
    try:
        return message[message.index('successfully') -1]
    except Exception:
        return ''

def get_xlsfile_from_zipped_response(project_name, response):
    temp_zip_file = tempfile.NamedTemporaryFile()
    temp_zip_file.write(response.content)
    temp_zip_file.seek(0)
    zf = zipfile.ZipFile(temp_zip_file.name)
    data = zf.read(project_name+"_all_log.xls")
    xlfile_fd, xlfile_name = tempfile.mkstemp(".xls")
    os.write(xlfile_fd, data)
    os.close(xlfile_fd)
    return xlfile_name