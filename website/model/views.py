from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
import os
import subprocess
import signal
import time

from model.utils import bokeh_plot
from dataset.models import Dataset
from django.conf import settings

def index(request):
    user_id = request.user.id
    port = user_id+1880
    model_path = os.path.join('/media/disk1/petpen/models/{}'.format(user_id))
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    nodered_process = subprocess.Popen(['node-red','-p',str(port),'-u',model_path])
    context = {'port':port, 'pid':nodered_process.pid}
    time.sleep(0.3)
    return render(request, 'model/index.html', context)

def results(request):
    context={}
    if request.method == 'GET':
        print(request.GET)
    if request.GET.get('type') == 'train':
        import json
        with open('/home/plash/petpen/state.json','r+') as f:
            info = json.load(f)
            info['status']='loading model'
            f.seek(0)
            json.dump(info,f)
            f.truncate()
        p = subprocess.Popen(['python','/home/plash/petpen/git/backend/petpen0.1.py','-m','/media/disk1/petpen/models/{}/'.format(request.user.id),'-d','/media/disk1/petpen/datasets/{}/{}/'.format(request.user.id,request.GET.get('dataset')),'train'], stderr=subprocess.PIPE)
        # if p.stderr:
            # error_message = p.stderr.read().splitlines()[-1]
            # print(error_message)
            # context['error'] = error_message
        # file_path='/home/plash/demo1/logs/'
        # script, div = bokeh_plot(file_path)
        # context={'plot':script,'plotDiv':div}
    # context["datasets"]=Dataset.objects.filter(user_id=request.user)
    return render(request, 'model/results.html', context)

# def configure(request):
    # import pandas as pd
    # context = {}
    # datasets = Dataset.objects.all()
    # datasets_name = [dataset.title for dataset in datasets]
    # context['datasets'] = datasets_name
    # if request.method == 'POST':
        # dataset_form = DatasetForm(request.POST)
        # if dataset_form.is_valid():
            # selected = dataset_form.cleaned_data.get('dataset')
            # dataset = Dataset.objects.get(title=selected)
            # print(os.path.join(settings.MEDIA_ROOT,dataset.csvfile.name))
            # dataset = pd.read_csv(os.path.join(settings.MEDIA_ROOT,dataset.csvfile.name))
            # if request.method == 'POST':
                # io_form = FeatureForm(request.POST, features=dataset.columns.values)
                # if io_form.is_valid():
                    # return HttpResponse(io_form.cleaned_data.get(input_features))
            # return HttpResponse(selected)
    # else:
        # dataset_form = DatasetForm()
    # context['form'] = dataset_form
    # return render(request, 'model/configure.html', context)

def api(request):
    import json
    file_path="/home/plash/petpen/state.json"
    if request.GET.get('type') == 'init':
        print('back to idle')
        with open(file_path,'r+') as f:
            info = json.load(f)
            info['status'] = 'system idle'
            f.seek(0)
            json.dump(info,f)
            f.truncate()
    try:
        with open(file_path) as f:
            json_response = JsonResponse(json.load(f))
    except:
        import time
        time.sleep(0.1)
        with open(file_path) as f:
            json_response = JsonResponse(json.load(f))
    return json_response

def plot_api(request):
    import json
    import re
    from bokeh.plotting import figure
    from bokeh.embed import components

    file_path='/media/disk1/petpen/models/2'
    latest_excution = os.path.join(file_path,max([f for f in os.listdir(file_path) if re.match(r'\d{6}_\d{6}',f)]),'logs')
    script, div = bokeh_plot(latest_excution)
    with open('/home/plash/petpen/state.json','r+') as f:
        info = json.load(f)
        info['status'] = 'system idle'
        f.seek(0)
        json.dump(info,f)
        f.truncate()

    return HttpResponse(json.dumps({"script":script, "div":div}), content_type="application/json")

def closenodered(request):
    pid = request.POST.get('pid',False)
    if pid:
        print(pid)
        os.kill(int(pid),signal.SIGINT)
    return HttpResponse('closed')

