import json
import requests

def change_status(status, id, test=False):
    if test:
        print(status)
        print(id)
    else:
        url = 'http://140.109.18.113:8000/model/api/' + str(id) + '/'
        r = requests.get(url, auth=('petpenadmin', 'cr31qrh5ev'))
        data = json.loads(r.text)
        data['status'] = str(status)
        r = requests.put(url, auth=('petpenadmin', 'cr31qrh5ev'), data=data)


class Status():
    def __init__(self,file_path):
        self.file_path = file_path
        self.info['status'] = 'system idle'

    def status_logger(func):
        def logging(self,*args,**kwargs):
            func(*args,**kwargs)
            with open(self.file_path,'w') as f:
                json.dump(self.info, f)
        return logging

    @status_logger
    def building_model():
        self.info['status'] = 'building model'


