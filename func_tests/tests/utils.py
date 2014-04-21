def get_subject_short_code(flash_message):
    #Assumes that the word before "successfully registered" is the short code
    message = flash_message.split()
    try:
        return message[message.index('successfully') -1]
    except Exception:
        return ''
