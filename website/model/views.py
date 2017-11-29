from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os
import subprocess
import signal
import time
import docker

from model.utils import bokeh_plot
# from dataset.models import Dataset
from django.conf import settings
from .models import NN_model, History
from model.serializers import NN_modelSerializer
from .forms import NN_modelForm
from petpen.settings import MEDIA_ROOT

@login_required
def index(request):
    context = {}
    if request.method == 'POST':
        if 'delete-project' in request.POST:
            form = NN_modelForm()
            print(request.POST['delete-project'])
            print(NN_model.objects.get(id=request.POST['delete-project']))
            NN_model.objects.get(id=request.POST['delete-project']).delete()
        else:
            form = NN_modelForm(request.POST)
            if form.is_valid():
                duplicate = NN_model.objects.filter(user=request.user.id).filter(title=request.POST['title']).count()
                if duplicate != 0:
                    messages.error(request, 'title "{}" already exists!'.format(request.POST['title']))
                    error_message = 'title "{}" already exists!'
                    context['error_message'] = error_message
                else:
                    newModel = NN_model(title=request.POST['title'],user=request.user,state_file="models/{}/{}/state.json".format(request.user.id,request.POST['title']),structure_file="models/{}/{}/result.json".format(request.user.id,request.POST['title']))
                    newModel.save()
                return HttpResponseRedirect(reverse("model:index"))
    elif request.method == 'GET':
        form = NN_modelForm()
    nn_models = NN_model.objects.filter(user_id = request.user.id)
    context['projects'] = nn_models
    context['form'] = form
    return render(request, 'model/index.html', context)

    user_id = request.user.id
    port = user_id+1880
    model_path = os.path.join('/media/disk1/petpen/models/{}'.format(user_id))
    if not os.path.exists(model_path):
        os.makedirs(model_path)
    nodered_process = subprocess.Popen(['node-red','-p',str(port),'-u',model_path])
    context = {'port':port, 'pid':nodered_process.pid}
    time.sleep(0.3)
    return render(request, 'model/index.html', context)

@login_required
def project_detail(request, project_id):
    '''
    run nodered of this project
    '''
    try:
        project = NN_model.objects.filter(user=request.user).get(id=project_id)
    except:
        return HttpResponseRedirect(reverse("model:index"))
    try:
        running_project = NN_model.objects.filter(user=request.user).get(status='editing')
        if running_project.id != int(project_id):
            return HttpResponse('another project editor is running! please close it first.')
    except:
        pass

    project_path = os.path.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
    project.status = 'idle'
    project.save()
    print(project_path)
    # if not os.path.exists(project_path):
        # os.makedirs(project_path)
    # port = user_id+1880
    histories = History.objects.filter(project = project)
    context = {'histories':histories}

    return render(request,'model/detail.html',context)

def history_detail(request):
    history_id = request.POST.get('history')
    history = History.objects.get(id=history_id)
    history_path = os.path.join(os.path.dirname(history.project.structure_file),history.save_path)
    import pandas as pd
    log_data = pd.read_csv(os.path.join(MEDIA_ROOT,history_path,'logs','train_log'))
    chartdata = {}
    chartdata['x'] = range(1,log_data.shape[0]+1)
    for index in range(log_data.shape[1]):
        chartdata['name{}'.format(index)] = log_data.columns[index]
        chartdata['y{}'.format(index)] = log_data.iloc[:,index]
    charttype = "lineChart"
    chartcontainer = 'linechart_container'
    best_epoch = log_data['val_loss'].argmin()
    best_val = log_data['val_loss'][best_epoch]
    context = {
        'history':history,
        'epochs':log_data.shape[0],
        'best_epoch':best_epoch,
        'best_val':best_val,
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': False,
            'x_axis_format': '',
            'tag_script_js': True,
            'jquery_on_ready': False,
        }
    }
    # return render_to_response('model/history_detail.html',data)
    return render(request,'model/history_detail.html',context)

def api(request):
    import json
    file_path=os.path.join(MEDIA_ROOT, "models/2/state.json")
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

@login_required
def manage_nodered(request):
    action = request.GET.get('action','')
    client = docker.from_env()
    user_container = list(filter(lambda container:container.attrs['Config']['Image']=='noderedforpetpen' and container.name==str(request.user), client.containers.list()))[0]
    if action == '':
        if user_container:
            return render(request,'model/editor.html',{'port':request.user.id+1880})
        else:
            return HttpResponse('No project opened for editing.')
    #function to open/close nodered container
    if action == 'close':
        print("close")
        print(user_container.name)
        if user_container:
            user_container.stop(timeout=0)
        return HttpResponse('Editor closed.')
    elif action == 'open':
        try:
            project = NN_model.objects.filter(user=request.user).get(title=request.GET['target'])
        except:
            return HttpResponse('No available project found for editing.')
        project_path = os.path.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        if not user_container:
            port = request.user.id+1880
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='test',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            return HttpResponse('no')
        return HttpResponse('')

def backend_api(request):
    if request.method == "POST":
        # p = subprocess.Popen(['python','/home/plash/petpen/git/backend/petpen0.1.py','-m','/media/disk1/petpen/models/{}/'.format(request.user.id),'-d','/media/disk1/petpen/datasets/{}/{}/'.format(request.user.id,request.GET.get('dataset')),'train'], stderr=subprocess.PIPE)
        
        print("yes!")
        return HttpResponse("good")
