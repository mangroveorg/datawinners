import random
import string
import time

class OrganizationIdCreator(object):

    def get_random_three_digit_string(self):
        return''.join(random.choice(string.ascii_uppercase) for x in range(3))

    def epoch_last_six_digit(self):
        epoch = long(time.time() * 100)
        epoch_last_six_digit = divmod(epoch, 1000000)[1]
        return epoch_last_six_digit

    def generateId(self):
        epoch_last_six_digit = self.epoch_last_six_digit()
        return self.get_random_three_digit_string()+ str(epoch_last_six_digit)