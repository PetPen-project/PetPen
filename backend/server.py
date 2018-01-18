import time, os
import subprocess
from job_queue import pop, jobs

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
        print(jobstatus)
        if jobs() > 0 and is_any_idle_gpu(gpus):
            prefer_gpu = get_gpu(gpus)
            command = pop()
            print(command)
            gpus[prefer_gpu] = 0 # mark busy
            sandbox_env = os.environ.copy()
            sandbox_env['CUDA_VISIBLE_DEVICES'] = str(prefer_gpu)
            jobstatus[prefer_gpu] = subprocess.Popen(command, env=sandbox_env)

        will_delete = []
        for i in jobstatus:
            if jobstatus[i].poll() != None:
                # job is done
                will_delete.append(i)

        for i in will_delete:
            del jobstatus[i]
            gpus[i] = 1 # mark available

        time.sleep(1) # prevent cpu load 100%



