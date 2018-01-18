import time
import subprocess
from queue import pop, jobs

def initial_gpu():
    ngpu = int(subprocess.check_output('nvidia-smi -L | wc -l', shell=True))
    return [1 for _ in range(ngpu)]

def is_any_idle_gpu(gpus):
    return (sum(gpus) > 0)

def get_gpu(gpus):
    return gpus.index(1)

if __name__ == '__main__':
    gpus = initial_gpu()
    jobstatus = {}
    while True:
        print(gpus)
        print jobstatus
        if jobs() > 0 and is_any_idle_gpu(gpus):
            prefer_gpu = get_gpu(gpus)
            command = pop()
            gpus[prefer_gpu] = 0 # mark busy
            jobstatus[prefer_gpu] = subprocess.Popen(command, stdout=subprocess.PIPE)

        will_delete = []
        for i in jobstatus:
            if jobstatus[i].poll() != None:
                # job is done
                will_delete.append(i)

        for i in will_delete:
            del jobstatus[i]
            gpus[i] = 1 # mark available

        time.sleep(1) # prevent cpu load 100%



