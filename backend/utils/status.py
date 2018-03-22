import json

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


