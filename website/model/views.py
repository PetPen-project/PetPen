from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse,Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

import os,json,shutil
import os.path as op 
import subprocess,signal
import time,datetime
import docker

from model.utils import bokeh_plot, update_status
# from dataset.models import Dataset
from django.conf import settings
from .models import NN_model, History
from dataset.models import Dataset
from model.serializers import NN_modelSerializer
from .forms import NN_modelForm
from petpen.settings import MEDIA_ROOT

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler(op.join(op.abspath(op.dirname(op.dirname(__name__))),'website.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

@login_required
def index(request):
    context = {}
    if request.method == 'POST':
        if 'delete-project' in request.POST:
            form = NN_modelForm()
            deleted_model = NN_model.objects.get(id=request.POST['delete-project'])
            shutil.rmtree(op.join(MEDIA_ROOT,op.dirname(deleted_model.structure_file)))
            deleted_model.delete()
        else:
            form = NN_modelForm(request.POST)
            if form.is_valid():
                duplicate = NN_model.objects.filter(user=request.user.id,title=request.POST['title']).count()
                if duplicate != 0:
                    messages.error(request, 'title "{}" already exists!'.format(request.POST['title']))
                    error_message = 'title "{}" already exists!'.format(request.POST['title'])
                    context['error_message'] = error_message
                else:
                    model_dir = "models/{}/{}".format(request.user.id,request.POST['title'])
                    newModel = NN_model(title=request.POST['title'],user=request.user,state_file=model_dir+"/state.json",structure_file=model_dir+"/result.json")
                    newModel.save()
                    os.makedirs(op.join(MEDIA_ROOT,model_dir))
                    update_status(newModel.state_file,'system idle')
                    shutil.copy2(op.abspath(op.join(op.abspath(__file__),'../../../.config.json')),op.join(MEDIA_ROOT,model_dir))
                return HttpResponseRedirect(reverse("model:index"))
    elif request.method == 'GET':
        form = NN_modelForm()
    projects = NN_model.objects.filter(user_id = request.user.id)
    for project in projects:
        status = update_status(project.state_file)['status']
        # state_path = op.join(MEDIA_ROOT,project.state_file)
        # if op.exists(state_path):
            # with open(state_path) as f:
                # status = json.load(f)['status']
        # else:
            # with open(state_path,'w') as f:
                # json.dump({'status':'system idle'},f)
            # status = 'idle'
        if status == 'start training model' or status == 'start testing':
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

    project_path = op.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
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
    try:
        info = update_status(project.state_file)
    except:
        return HttpResponse('failed parsing status')
    if info['status'] in ['error','finish training']:
        if request.POST.get('type') == 'init':
            logger.info('back to idle')
        # if info['status'] not in ['start training model', 'start testing', 'loading model']:
            info['status'] = 'system idle'
            update_status(project.state_file,info['status'])
        elif info['status'] == 'error':
            if info.get('error_log_file'):
                with open(info['error_log_file']) as f:
                    info['detail'] = f.read()
        project.status = 'idle'
        project.save()
    return JsonResponse(info)
    # else if request.method == 'POST':
        
    # file_path = op.join(MEDIA_ROOT, project.state_file)
    # if request.POST.get('type') == 'init':
        # logger.info('back to idle')
        # try:
            # with open(file_path,'r+') as f:
                # info = json.load(f)
                # if info['status'] != 'start training model' and info['status'] != 'start testing' and info['status'] != 'loading model':
                    # info['status'] = 'system idle'
                # f.seek(0)
                # json.dump(info,f)
                # f.truncate()
        # except:
            # with open(file_path,'w') as f:
                # info = {'status':'system idle'}
                # json.dump(info,f)
        # return JsonResponse(info)
    # try:
        # with open(file_path) as f:
            # info = json.load(f)
            # json_response = JsonResponse(info)
    # except:
        # return HttpResponse('failed parsing status')
        # import time
        # time.sleep(0.1)
        # with open(file_path) as f:
            # json_response = JsonResponse(json.load(f))
    # print(json_response.content)
    # return json_response

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
    port = request.user.id+2880
    action = request.GET.get('action','')
    client = docker.from_env()
    user_container = list(filter(lambda container:container.attrs['Config']['Image']=='noderedforpetpen' and container.name==str(request.user), client.containers.list()))
    if user_container: user_container = user_container[0]
    if action == '':
        if user_container:
            return render(request,'model/editor.html',{'port':port})
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
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            user_container.stop(timeout=0)
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        return HttpResponse('running')

def preprocess_structure(file_path):
    if not op.exists(file_path):
        update_status(op.join(op.dirname(file_path),'state.json'),'error: missing model structure')
        return 'file missing'
        # with open(op.join(op.dirname(file_path),'state.json'),'r+') as f:
            # info = json.load(f)
            # info['status'] = 'error: missing model structure'
            # f.seek(0)
            # json.dump(info,f)
            # f.truncate()
        # return 'file missing'
            
    with open(file_path,'r') as f:
        structure = json.load(f)
        import pprint
        pprint.pprint(structure)
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
    if missing_dataset:
        print(missing_dataset)
        return missing_dataset
    preprocessed_dir = op.join(project_path,'preprocessed')
    if not op.exists(preprocessed_dir):
        os.makedirs(preprocessed_dir)
    with open(op.join(preprocessed_dir,'result.json'),'w') as pre_f:
        json.dump(structure,pre_f)
    return 'successed'

def backend_api(request):
    if request.method == "POST":
        script_path = op.abspath(op.join(__file__,op.pardir,op.pardir,op.pardir,'backend/petpen0.1.py'))
        executed = datetime.datetime.now()
        save_path = executed.strftime('%y%m%d_%H%M%S')
        history_name = request.POST['name'] or save_path
        project = NN_model.objects.filter(user=request.user).get(id=request.POST['project'])
        if not project:
            return Http404('project not found')
        history = History(project=project,name=history_name,executed=executed,save_path=save_path,status='running')
        history.save()
        project.training_counts += 1
        project.status = 'running'
        project.save()
        logger.debug((history_name,save_path,executed))
        logger.debug(request.POST['project'],project.title)
        structure_file = op.join(MEDIA_ROOT,project.structure_file)
        info = update_status(project.state_file)
        if info['status'] != 'system idle':
            return HttpResponse('waiting back to idle')
        else:
            # update_status(project.state_file,'loading model')
            pass
        # state_file = op.join(MEDIA_ROOT,project.state_file)
        # with open(state_file,'r+') as f:
            # info = json.load(f)
            # if info['status'] != 'system idle':
                # return HttpResponse('waiting back to idle')
            # info['status'] = 'loading model'
            # f.seek(0)
            # json.dump(info,f)
            # f.truncate()
        project_path = op.dirname(structure_file)
        shutil.copy2(structure_file,op.join(project_path,save_path))
        #----- file path transformation -----
        prcs = preprocess_structure(structure_file)
        print(prcs)
        if prcs != 'successed':
            history.status = 'aborted'
            project.status = 'idle'
            project.save()
            history.save()
            if prcs != 'file missing':
                update_status(project.state_file,status='error',detail='structure assignment error found on nodes {}'.format(', '.join(prcs)))
                return JsonResponse({'missing':prcs})
            else:
                update_status(project.state_file,status='error',detail='please depoly your model structure before running')
                return JsonResponse({'missing':'no structure file'})
        try:
            p = subprocess.Popen(['python',script_path,'-m',project_path,'-t',save_path,'train'],)
        except Exception as e:
            logger.error('Failed to run the backend', exc_info=True)
        # project.status='running'
        # project.save()
        return HttpResponse("running")
