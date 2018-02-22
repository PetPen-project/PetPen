import time, os
import subprocess
from job_queue import pop_, jobs_

def initial_gpu():
    ngpu = int(subprocess.check_output('nvidia-smi -L | wc -l', shell=True))
    ngpu = [1 for _ in range(ngpu)]
    if not len(ngpu):
        ngpu = [1]
    return ngpu

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
        if jobs_('petpen_wait') > 0 and is_any_idle_gpu(gpus):
            prefer_gpu = get_gpu(gpus)
            id, command = pop_('petpen_wait')
            print(command)
            gpus[prefer_gpu] = 0 # mark busy
            sandbox_env = os.environ.copy()
            sandbox_env['CUDA_VISIBLE_DEVICES'] = str(prefer_gpu)
            jobstatus[prefer_gpu] = (id, subprocess.Popen(command, env=sandbox_env, shell=True))

        will_delete = []
        for i in jobstatus:
            if jobstatus[i][1].poll() != None:
                # job is done
                will_delete.append(i)

        # If kill queue is not empty
        if jobs_('petpen_terminate') > 0:
            id, _ = pop_('petpen_terminate')
            for i in jobstatus:
                if id == jobstatus[i][0]:
                    jobstatus[i][1].kill()
                    will_delete.append(i)


        for i in will_delete:
            del jobstatus[i]
            gpus[i] = 1 # mark available

        time.sleep(1) # prevent cpu load 100%



