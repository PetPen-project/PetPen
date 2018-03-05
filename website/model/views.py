from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse,Http404
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.contrib import messages
from django.views.generic import ListView

from job_queue import push, kill

import os,json,shutil,re
import os.path as op 
import subprocess,signal
import time,datetime
import docker
import pandas as pd

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

class HistoryView(ListView):
    model = [NN_model,History]
    template_name = 'model/history.html'

    def get_queryset(self):
        try:
            queryset = self.model[0].objects.get(pk=self.kwargs['project_id'])
            queryset = queryset.history_set.all()
            return queryset
        except:
            raise Http404('query failed.')

    def get_context_data(self):
        context = {}
        context['histories'] = self.object_list
        if self.object:
            if self.object.status == "running":
                if not op.exists(self.kwargs['history_path']):
                    self.object.status = 'execute log missing'
                else:
                    if op.exists(op.join(self.kwargs['history_path'],'weights.h5')):
                        self.object.status = 'success'
                    elif op.exists(op.join(self.kwargs['history_path'],'logs/error_log')):
                        self.object.status = 'error'
                self.object.save()
            if self.object.status !='success':
                context.update({'save_path':self.object.save_path,'status':self.object.status,'executed':self.object.executed})
                return context
            log_data = pd.read_csv(op.join(self.kwargs['history_path'],'logs','train_log'))
            chartdata = {}
            chartdata['x'] = range(1,log_data.shape[0]+1)
            for index in range(log_data.shape[1]):
                chartdata['name{}'.format(index)] = 'training' if log_data.columns[index]=='loss' else 'testing'
                chartdata['y{}'.format(index)] = log_data.iloc[:,index]
            charttype = "lineChart"
            chartcontainer = 'linechart_container'
            best_epoch = log_data['val_loss'].argmin()
            best_val = log_data['val_loss'][best_epoch]
            context.update({
                'history':self.object,
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
            })
        return context 

    def get(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.object_list = self.get_queryset()
        self.object = None
        context = self.get_context_data()
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.kwargs.update(request.POST)
        self.object_list = self.get_queryset()
        self.object = self.object_list.get(pk=request.POST.get('history'))
        self.kwargs['history_path'] = op.join(MEDIA_ROOT,op.dirname(self.object.project.structure_file),self.object.save_path)
        if self.kwargs.get('action') == 'delete':
            self.object_list = self.object_list.exclude(pk=self.object.id)
            self.object.delete()
        elif self.kwargs.get('action') == 'download':
            return self.generateAttachFile()
        context = self.get_context_data()
        return self.render_to_response(context)

    def generateAttachFile(self):
        if self.object.status == 'success':
            import tempfile
            f = tempfile.TemporaryFile(mode='w+b')
            with open(op.join(self.kwargs['history_path'],'weight.h5'),'rb') as h5:
                shutil.copyfileobj(h5,f)
            f.seek(0)
            response = HttpResponse(f,content_type='application/x-binary') 
            response['Content-Disposition'] = 'attachment; filename=model.h5'
        else:
            response = HttpResponse('error: request model on unsuccessful training.')

        return response

@login_required
def history_detail(request):
    print(request.POST)
    if request.POST.get('project_id'):
        histories = History.objects.filter(project__id=request.POST.get('project_id'))
        return render(request,'model/history_detail.html',{'histories':histories})
    history_id = request.POST.get('history')
    history = History.objects.get(pk=history_id)
    histories = History.objects.filter(project=history.project)
    history_path = op.join(MEDIA_ROOT,op.dirname(history.project.structure_file),history.save_path)
    if request.POST.get('action') == 'delete':
        histories = histories.exclude(pk=history.id)
        # history.delete()
        return render(request,'model/history_detail.html',{'histories':histories})
    elif request.POST.get('action') == 'download':
        if history.status == 'success':
            import tempfile
            f = tempfile.TemporaryFile(mode='w+b')
            with open(op.join(history_path,'weights.h5'),'rb') as h5:
                shutil.copyfileobj(h5,f)
            f.seek(0)
            response = HttpResponse(f,content_type='application/x-binary')
            response['Content-Disposition'] = 'attachment; filename=model.h5'
            return response
        else:
            return HttpResponse('error: request model on unsuccessful training.')
    if history.status == "running":
        if not op.exists(history_path):
            history.status = 'execute log missing'
        else:
            if op.exists(op.join(history_path,'weights.h5')):
                history.status = 'success'
            elif op.exists(op.join(history_path,'logs/error_log')):
                history.status = 'error'
        history.save()
    if history.status !='success':
        return render(request,'model/history_detail.html',{'histories':histories,'save_path':history.save_path,'status':history.status,'executed':history.executed})
    import pandas as pd
    log_data = pd.read_csv(op.join(history_path,'logs','train_log'))
    chartdata = {}
    chartdata['x'] = range(1,log_data.shape[0]+1)
    for index in range(log_data.shape[1]):
        chartdata['name{}'.format(index)] = 'training' if log_data.columns[index]=='loss' else 'testing'
        chartdata['y{}'.format(index)] = log_data.iloc[:,index]
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

@login_required
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

def plot_api(request):
    from bokeh.plotting import figure
    from bokeh.embed import components
    
    try:
        project = NN_model.objects.get(user=request.user,pk=request.GET.get('p'))
        if request.GET.get('realtime') == '1':
            plot_data = []
            with open(op.join(MEDIA_ROOT,project.state_file),'r') as f:
                info = json.load(f)
            return HttpResponse(json.dumps(info),content_type='application/json')
    except BaseException as e:
        logger.warning('excepttion occured when calling plot API. user:{}, method GET:{}'.format(request.user,request.GET))
        return HttpResponse('')
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
    port = request.user.id+1880
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
    logger.info('action for nodered:{}'.format(action))
    if action == 'close':
        if user_container:
            user_container.stop(timeout=0)
        return HttpResponse('Editor closed.')
    elif action == 'open':
        try:
            project = NN_model.objects.filter(user=request.user).get(title=request.GET['target'])
        except:
            return HttpResponse('No available project found for editing.')
        project.modified = datetime.datetime.now()
        project.save()
        project_path = os.path.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        if not user_container:
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            user_container.stop(timeout=0)
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        return HttpResponse('running')

def preprocess_structure(file_path,projects,datasets):
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
                    dataset = datasets.get(title=dataset_setting[i][0])
                except:
                    logger.error('Failed to load dataset', exc_info=True)
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
                    dataset = datasets.get(title=dataset_setting[o][0])
                except:
                    logger.error('Failed to load dataset', exc_info=True)
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
                pretrain_project = projects.get(title=pretrain_project_name)
                pretrain_history = History.objects.filter(project=pretrain_project,name=pretrain_history_name,status='success').latest('id')
            except:
                missing_dataset.append(p)
                continue
            structure['layers'][p]['params']['weight_file'] = op.join(MEDIA_ROOT,op.dirname(pretrain_project.structure_file),pretrain_history.save_path,'weights.h5')
    pprint.pprint(structure)
    if missing_dataset:
        print(missing_dataset)
        return missing_dataset
    preprocessed_dir = op.join(op.dirname(file_path),'preprocessed')
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
        project = NN_model.objects.filter(user=request.user).get(pk=request.POST['project'])
        if not project:
            return Http404('project not found')
        if request.POST['command'] == 'train':
            history_name = request.POST.get('name') or save_path
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
                update_status(project.state_file,'loading model')
            project_path = op.dirname(structure_file)
            os.mkdir(op.join(project_path,save_path))
            shutil.copy2(structure_file,op.join(project_path,save_path))
            #----- file path transformation -----
            prcs = preprocess_structure(structure_file,NN_model.objects.filter(user=request.user),Dataset.objects.filter(user=request.user))
            print(prcs)
            if prcs != 'successed':
                os.makedirs(op.join(project_path,save_path,'logs/'))
                history.status = 'aborted'
                project.status = 'idle'
                project.save()
                history.save()
                if prcs != 'file missing':
                    update_status(project.state_file,status='error',detail='structure assignment error found on nodes {}'.format(', '.join(prcs)))
                    with open(op.join(project_path,save_path,'logs/error_log'),'w') as f:
                        f.write('Structure assignment error found on nodes {}'.format(', '.join(prcs)))
                    return JsonResponse({'missing':prcs})
                else:
                    update_status(project.state_file,status='error',detail='please depoly your model structure before running')
                    with open(op.join(project_path,save_path,'logs/error_log'),'w') as f:
                        f.write('No deployed neural network found. Finish your neural network editing before running experiments.')
                    return JsonResponse({'missing':'no structure file'})
            try:
                # p = subprocess.Popen(['python',script_path,'-m',project_path,'-t',save_path,'train'],)
                p = push(project.id,['python',script_path,'-m',project_path,'-t',save_path,'train'])
            except Exception as e:
                logger.error('Failed to run the backend', exc_info=True)
        elif request.POST['command'] == 'stop':
            p = kill(project.id)
            project.status = 'idle'
            project.save()
            update_status(project.state_file,status='system idle')
            history = project.history_set.latest('id')
            history.status = 'aborted'
            history.save()
            os.makedirs(op.join(project_path,save_path,'logs/'))
            with open(op.join(project_path,history.save_path,'logs/error_log'),'w') as f:
                f.write('Training stopped by user.')

        elif request.POST['command'] == evaluate:
            pass
        return HttpResponse("running")
