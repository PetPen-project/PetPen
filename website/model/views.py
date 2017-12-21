from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse,Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os,json
import os.path as op 
import subprocess,signal
import time,datetime
import docker

from model.utils import bokeh_plot
# from dataset.models import Dataset
from django.conf import settings
from .models import NN_model, History
from dataset.models import Dataset
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
    projects = NN_model.objects.filter(user_id = request.user.id)
    for project in projects:
        if op.exists(op.join(MEDIA_ROOT,project.state_file)):
            with open(op.join(MEDIA_ROOT,project.state_file)) as f:
                status = json.load(f)['status']
        else:
            status = 'idle'
        if status=='start training model' or status =='start testing':
            project.status = 'running'
        else:
            project.status = 'idle'
        project.save()
    context['projects'] = projects
    context['form'] = form
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
    histories = History.objects.filter(project = project)
    context = {
            'histories':histories,
            'project_id':project_id
            }

    return render(request,'model/detail.html',context)

def history_detail(request):
    if request.POST.get('project_id'):
        print(request.POST.get('project_id'))
        histories = History.objects.filter(project__id=request.POST.get('project_id'))
        return render(request,'model/history_detail.html',{'histories':histories})
    history_id = request.POST.get('history')
    history = History.objects.get(pk=history_id)
    histories = History.objects.filter(project=history.project)
    print('action:',request.POST.get('action'))
    history_path = op.join(MEDIA_ROOT,op.dirname(history.project.structure_file),history.save_path)
    if request.POST.get('action') == 'delete':
        history.delete()
        return render(request,'model/history_detail.html',{'histories':histories})
    elif request.POST.get('action') == 'download':
        pass
    elif history.status == "running":
        if not op.exists(history_path):
            history.status = 'execute log missing'
            history.save()
        else:
            if op.exists(op.join(history_path,'weights.h5')):
                history.status = 'success'
                history.save()
    if history.status !='success':
        return render(request,'model/history_detail.html',{'histories':histories,'save_path':history.save_path,'status':history.status,'executed':history.executed})
    import pandas as pd
    log_data = pd.read_csv(op.join(history_path,'logs','train_log'))
    chartdata = {}
    chartdata['x'] = range(1,log_data.shape[0]+1)
    for index in range(log_data.shape[1]):
        chartdata['name{}'.format(index)] = log_data.columns[index]
        chartdata['y{}'.format(index)] = log_data.iloc[:,index]
    print(chartdata)
    charttype = "lineChart"
    chartcontainer = 'linechart_container'
    best_epoch = log_data['val_loss'].argmin()
    best_val = log_data['val_loss'][best_epoch]
    context = {
        'history':history,
        'histories':histories,
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
    return render(request,'model/history_detail.html',context)

def api(request):
    project = get_object_or_404(NN_model,user=request.user,pk=request.POST['project_id'])
    file_path=op.join(MEDIA_ROOT, project.state_file)
    if request.POST.get('type') == 'init':
        print('back to idle')
        try:
            with open(file_path,'r+') as f:
                info = json.load(f)
                if info['status'] != 'start training model' and info['status'] != 'start testing':
                    info['status'] = 'system idle'
                f.seek(0)
                json.dump(info,f)
                f.truncate()
        except:
            with open(file_path,'w') as f:
                info = {'status':'system idle'}
                json.dump(info,f)
        return JsonResponse(info)
    try:
        with open(file_path) as f:
            json_response = JsonResponse(json.load(f))
    except:
        import time
        time.sleep(0.1)
        with open(file_path) as f:
            json_response = JsonResponse(json.load(f))
    print((json_response.content))
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
    user_container = list(filter(lambda container:container.attrs['Config']['Image']=='noderedforpetpen' and container.name==str(request.user), client.containers.list()))
    if user_container: user_container = user_container[0]
    if action == '':
        if user_container:
            return render(request,'model/editor.html',{'port':request.user.id+1880})
        else:
            return HttpResponse('No project opened for editing.')
    #function to open/close nodered container
    if action == 'close':
        print('close')
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
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            return HttpResponse('no')
        return HttpResponse('')

def backend_api(request):
    if request.method == "POST":
        script_path = op.abspath(op.join(__file__,op.pardir,op.pardir,op.pardir,'backend/petpen0.1.py'))
        executed = datetime.datetime.now()
        save_path = executed.strftime('%y%m%d_%H%M%S')
        history_name = request.POST['name'] or save_path
        project = NN_model.objects.filter(user=request.user).get(id=request.POST['project'])
        if not project:
            return Http404('project not found')
        print((history_name,save_path,executed))
        print(request.POST['project'],project.title)
        structure_file = op.join(MEDIA_ROOT,project.structure_file)
        project_path = op.dirname(structure_file)
        #----- file path transformation -----
        with open(structure_file,'r') as f:
            structure = json.load(f)
            import pprint
            pprint.pprint(structure)
            # inputs = list(filter(lambda name,value: value['type'] == 'Input', structure['layers']))
            # print(inputs)
            inputs = [k for (k,v) in structure['layers'].items() if v['type']=='Input']
            outputs = [k for (k,v) in structure['layers'].items() if v['type']=='Output']
            dataset_setting = structure['dataset']
            missing_dataset = []
            for i in inputs:
                if i not in dataset_setting:
                    missing_dataset.append(i)
                else:
                    try:
                        dataset = Dataset.objects.filter(user=request.user).get(title=dataset_setting[i][0])
                    except:
                        missing_dataset.append(i)
                        continue
                    dataset_setting[i] = {
                        'train_x':op.join(MEDIA_ROOT,str(dataset.training_input_file)),
                        'valid_x':op.join(MEDIA_ROOT,str(dataset.testing_input_file))
                        }
            for o in outputs:
                if o not in dataset_setting:
                    missing_dataset.append(o)
                else:
                    try:
                        dataset = Dataset.objects.filter(user=request.user).get(title=dataset_setting[o][0])
                    except:
                        missing_dataset.append(o)
                        continue
                    dataset_setting[o] = {
                        'train_y':op.join(MEDIA_ROOT,str(dataset.training_output_file)),
                        'valid_y':op.join(MEDIA_ROOT,str(dataset.testing_output_file))
                        }
            structure['dataset'] = dataset_setting
            pretrains = [k for (k,v) in structure['layers'].items() if v['type']=='Pretrained']
            for p in pretrains:
                pretrain_project_name = structure['layers'][p]['params']['project_name']
                pretrain_history_name = structure['layers'][p]['params']['weight_file']
                try:
                    pretrain_project = NN_model.objects.get(user=request.user,title=pretrain_project_name)
                    pretrain_history = History.objects.filter(project=pretrain_project,name=pretrain_history_name,status='success').latest('id')
                except:
                    missing_dataset.append(p)
                    continue
                structure['layers'][p]['params']['weight_file'] = op.join(MEDIA_ROOT,op.dirname(pretrain_project.structure_file),pretrain_history.save_path,'weights.h5')
            pprint.pprint(structure)
            preprocessed_dir = op.join(project_path,'preprocessed')
            if not op.exists(preprocessed_dir):
                os.makedirs(preprocessed_dir)
            with open(op.join(preprocessed_dir,'result.json'),'w') as pre_f:
                json.dump(structure,pre_f)
        if missing_dataset:
            print(missing_dataset)
            return HttpResponse('missing')
        p = subprocess.Popen(['python',script_path,'-m',project_path,'-t',save_path,'train'],)
        history = History(project=project,name=history_name,executed=executed,save_path=save_path,status='running')
        history.save()
        # project.status='running'
        # project.save()
        return HttpResponse("running")
