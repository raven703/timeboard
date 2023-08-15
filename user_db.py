import json
from datetime import datetime


class UsersDb:
    def __init__(self):
        self.nested_dict = {}
        self.load()

    def add(self, char_ID, char_name, char_alliance):

        c_datetime = datetime.now()
        f_datetime = f"{c_datetime:%d:%m:%Y}"
        self.nested_dict.update(
            {str(char_ID):
                 {'char_name': char_name,
                  'char_alliance': str(char_alliance),
                  'time_stamp': str(f_datetime)

                  }})
        self.save()

    def delete(self, char_ID):
        try:
            del self.nested_dict[char_ID]
        except:
            print('cant delete value from DB')
        self.save()

    def get(self, char_ID):

        try:
            return self.nested_dict[str(char_ID)]
        except KeyError:
            return False

    def print(self, char_ID=None):
        if char_ID is not None:
            try:
                print(self.nested_dict[char_ID])
                return self.nested_dict[char_ID]
            except KeyError:
                print('no ID value in DB')
                return False
        else:
            print(self.nested_dict)
            return self.nested_dict

    def save(self):

        with open('char_db', 'w') as file:
            json.dump(self.nested_dict, file)

    def load(self):
        try:
            with open('char_db', 'r') as file:
                self.nested_dict = json.load(file)
        except:
            print('error loading user DB')
