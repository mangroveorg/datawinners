from string import upper

default_non_chargable_map = ['ACCEPTED', 'UNKNOWN', "REJECTD"]
not_chargable_map = {
    'infobip': default_non_chargable_map
}

def is_chargable(status, smsc):
    if upper(status)=="DELIVRD":
        return True
    return upper(status) not in not_chargable_map.get(smsc, default_non_chargable_map)
