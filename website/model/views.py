from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse,Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import django.utils.timezone as timezone
from django.core.files import File
from django.contrib import messages
from django.views.generic import ListView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from job_queue import push, kill

import os,json,shutil,re,fnmatch
import os.path as op 
import subprocess,signal
import time,datetime
import docker
import numpy as np
import pandas as pd

from model.utils import bokeh_plot, update_status
# from dataset.models import Dataset
from django.conf import settings
from .models import NN_model, History
from dataset.models import Dataset
from model.serializers import NN_modelSerializer
from model.permissions import IsOwner
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

@api_view(['GET','POST'])
@permission_classes((permissions.IsAuthenticatedOrReadOnly,))
def project_list(request, format=None):
    if request.method == 'GET':
        projects = NN_model.objects.all()
        serializer = NN_modelSerializer(projects, many=True)
        # return JsonResponse(serializer.data, safe=False)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = NN_modelSerializer(data=request.data)
        if serializer.is_valid():
            pass
            # serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NN_model_list(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    def get(self, request, format=None):
        projects = NN_model.objects.filter(user=request.user)
        serializer = NN_modelSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = NN_modelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NN_model_detail(APIView):
    # permission_classes = (IsOwner,)
    permission_classes = (permissions.IsAdminUser,)
    def get_object(self, pk):
        try:
            return NN_model.objects.get(pk=pk)
        except NN_model.DoseNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = NN_modelSerializer(project)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        project = self.get_object(pk)
        serializer = NN_modelSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        project = self.get_object(pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def index(request):
    context = {}
    if request.method == 'POST':
        if 'delete-project' in request.POST:
            form = NN_modelForm()
            deleted_model = NN_model.objects.get(pk=request.POST['delete-project'])
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
                    newModel = NN_model(title=request.POST['title'],user=request.user)
                    newModel.save(create=True)
                    update_status(newModel.state_file,'system idle')
                return HttpResponseRedirect(reverse("model:index"))
    elif request.method == 'GET':
        form = NN_modelForm()
    projects = NN_model.objects.filter(user_id = request.user.id)
    # for project in projects:
        # status = update_status(project.state_file)['status']
        # if status == 'start training model' or status == 'start testing':
            # project.status = 'running'
        # else:
            # project.status = 'idle'
        # project.save()
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
    # try:
        # running_project = NN_model.objects.filter(user=request.user).get(status='editing')
        # if running_project.id != int(project_id):
            # return HttpResponse('another project editor is running! please close it first.')
    # except:
        # pass

    project_path = op.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
    histories = History.objects.filter(project = project)
    context = {
            'histories':histories,
            'project_id':project_id,
            'project_title': project.title
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
            raise Http404('Query failed on the given model id.')

    def get_context_data(self):
        context = {}
        context['project_id'] = self.kwargs['project_id']
        context['histories'] = self.object_list
        context['project_title'] = self.object_list[0].project.title
        context['history'] = self.object
        if self.object:
            if self.object.status == "running":
                if not op.exists(self.kwargs['history_path']):
                    self.object.status = 'execute log missing'
                elif op.exists(op.join(self.kwargs['history_path'],'weights.h5')):
                    self.object.status = 'success'
                elif op.exists(op.join(self.kwargs['history_path'],'logs/error_log')):
                    self.object.status = 'error'
                self.object.save()
            if self.object.status in ['error','aborted']:
                with open(op.join(self.kwargs['history_path'],'logs/error_log'),'r') as f:
                    context['message'] = f.read()
                context.update({'save_path':self.object.save_path,'status':self.object.status,'executed':self.object.executed})
                return context
            elif self.object.status !='success':
                context.update({'save_path':self.object.save_path,'status':self.object.status,'executed':self.object.executed})
                return context
            log_data = pd.read_csv(op.join(self.kwargs['history_path'],'logs/train_log'))
            if self.object.execution_type == 'classification':
                chartdata_loss = {}
                chartdata_acc = {}
                chartdata_loss['x'] = range(1,log_data.shape[0]+1)
                chartdata_acc['x'] = range(1,log_data.shape[0]+1)
                chartdata_loss['name0'] = 'training'
                chartdata_loss['name1'] = 'validation'
                chartdata_acc['name0'] = 'training'
                chartdata_acc['name1'] = 'validation'
                chartdata_loss['y0'] = log_data['loss'].values
                chartdata_loss['y1'] = log_data['val_loss'].values
                chartdata_acc['y0'] = log_data['acc'].values
                chartdata_acc['y1'] = log_data['val_acc'].values
                charttype_loss = "lineChart"
                charttype_acc = "lineChart"
                chartcontainer_loss = 'linechart_container_loss'
                chartcontainer_acc = 'linechart_container_acc'
                best_epoch_loss = log_data['val_loss'].argmin()
                best_loss_value = log_data['val_loss'][best_epoch_loss]
                best_epoch_acc = log_data['val_acc'].argmin()
                best_acc_value = log_data['val_acc'][best_epoch_acc]
                context.update({
                    'epochs':log_data.shape[0],
                    'best_epoch_loss':best_epoch_loss,
                    'best_loss_value':best_loss_value,
                    'charttype_loss': charttype_loss,
                    'chartdata_loss': chartdata_loss,
                    'chartcontainer_loss': chartcontainer_loss,
                    'best_epoch_acc':best_epoch_acc,
                    'best_acc_value':best_acc_value,
                    'charttype_acc': charttype_acc,
                    'chartdata_acc': chartdata_acc,
                    'chartcontainer_acc': chartcontainer_acc,
                    'extra': {
                        'x_is_date': False,
                        'x_axis_format': '',
                        'tag_script_js': True,
                        'jquery_on_ready': False,
                    }
                })
                return context
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
        self.object_list = self.get_queryset()
        self.object = self.object_list.get(pk=request.POST.get('history'))
        self.kwargs['history_path'] = op.join(MEDIA_ROOT,op.dirname(self.object.project.structure_file),self.object.save_path)
        if request.POST.get('action') == 'delete':
            print(self.object.save_path)
            print(self.object.id)
            self.object_list = self.object_list.exclude(pk=self.object.id)
            try:
                shutil.rmtree(op.join(MEDIA_ROOT,op.dirname(self.object.project.structure_file),self.object.save_path))
            except:
                pass
            self.object.delete()
            self.object = None
        elif request.POST.get('action') == 'download':
            return self.generateAttachFile()
        context = self.get_context_data()
        return self.render_to_response(context)

    def generateAttachFile(self):
        if self.object.status == 'success':
            import tempfile
            f = tempfile.TemporaryFile(mode='w+b')
            with open(op.join(self.kwargs['history_path'],'weights.h5'),'rb') as h5:
                shutil.copyfileobj(h5,f)
            f.seek(0)
            response = HttpResponse(f,content_type='application/x-binary') 
            response['Content-Disposition'] = 'attachment; filename=model.h5'
        else:
            response = HttpResponse('error: request model on unsuccessful training.')

        return response

@login_required
def predict(request, *args, **kwargs):
    try:
        project = NN_model.objects.get(pk=kwargs['project_id'],user=request.user)
        history = History.objects.get(project=project,save_path=kwargs['history_path'])
    except:
        context = {}
        return HttpResponse('404: not an availble model for prediction')
    predict_dir = op.join(MEDIA_ROOT,op.dirname(project.structure_file),'result/')
    if request.method == 'POST':
        import tempfile
        f = tempfile.TemporaryFile(mode='w+b')
        with open(op.join(predict_dir,'result'),'rb') as result:
            shutil.copyfileobj(result,f)
        f.seek(0)
        response = HttpResponse(f,content_type='application/x-binary')
        response['Content-Disposition'] = 'attachment; filename=result.csv'
        return response
    context = {'project_id':project.id,'history_id':history.id}
    if 'error_log' in os.listdir(predict_dir):
        with open(op.join(predict_dir,'error_log'),'r') as f:
            context.update(json.load(f))
        return render(request,'model/predict.html',context)
    context_dataset = {}
    image = [n for n in os.listdir(predict_dir) if n in ['input.jpeg','input.jpg','input.img','input.png','input.svg']]
    if image:
        from PIL import Image
        with Image.open(op.join(predict_dir,image[0])) as img:
            width, height = img.size
        context_dataset['type'] = 'image'
        context_dataset['content'] = {
            'source': op.join(op.dirname(project.structure_file),'result',image[0]),
            'width': width,
            'height': height,
            }
        context['sample_size'] = 1
    else:
        context_dataset['type'] = 'numeric'
        dataset = np.load(op.join(predict_dir,'input.npy'))
        context_dataset['content'] = []
        with open(op.join(MEDIA_ROOT,op.dirname(project.structure_file),history.save_path,'preprocessed/result.json'),'r') as f:
            structure = json.load(f)
            input_shape = [v['params']['shape'] for v in structure['layers'].values() if v['type']=='Input'][0]
        if len(dataset.shape)==len(input_shape):
            context['sample_size'] = 1
        else:
            context['sample_size'] = dataset.shape[0]
    if not op.exists(predict_dir+'type') and not op.exists(predict_dir+'logs/error_log'):
        context['running'] = True
        return render(request,'model/predict.html',context)
    elif op.exists(predict_dir+'logs/error_log'):
        context['error_type'] = 'runTimeError'
        with open(predict_dir+'logs/error_log') as f:
            context['error_message'] = f.read()
    with open(op.join(predict_dir,'type'),'r') as f:
        problem_type = f.readline()
    result = pd.read_csv(op.join(predict_dir,'result'),header=None)
    if problem_type == 'classification' and context['sample_size'] == 1:
        if result.shape[1] > 1:
            decimal_l = max(int(np.floor(np.log10(result.iloc[0].max()))),1)
            decimal_r = max(0,6-decimal_l)
            print((np.log10(result.iloc[0].max())))
            print(decimal_l,decimal_r)
            xdata = range(result.shape[1])
            chartcontents_output = []
            context_result = {
                'type': 'chart',
                'content': {
                'charttype': 'discreteBarChart',
                'chartdata': {
                    'x': xdata,
                    'name1': 'label',
                    'y1': result.iloc[0],
                    'extra1': {"tooltip": {"y_start": "", "y_end": ""}},
                    },
                'chartcontainer': "classification_container",
                'kw_extra': {'y_axis_format':'.{}f'.format(decimal_r)},
                }}
        else:
            context_result = {
                'type':  'number',
                'content': result
                }
    elif problem_type == 'regression' and context['sample_size'] == 1:
        pass
    else:
        context_result = {
            'type': 'text',
            'content': 'Predict result generated. Click the button to download.'
            }
    # dataset_name = fnmatch.filter(os.listdir(predict_dir),'input.npy')[0]
    # ext = op.splitext(dataset_name)[1]
    # if ext in ['.jpeg','.jpg','.img','.png']:
        # dataset['type'] = 'image'
        # dataset['content'] = op.join(op.dirname(project.structure_file),'result',dataset_name)
    # elif ext in ['.csv','.pickle','.pkl']:
        # dataset['type'] = 'numeric'
        # if ext == '.csv':
            # dataset_value = pd.read_csv(op.join(predict_dir,dataset_name),header=None)
        # elif ext == '.pickle'or ext == '.pkl':
            # dataset_value = pd.read_pickle(op.join(predict_dir,dataset_name))
        # dataset_value
        # dataset['content'] = {}
    context.update({
        'project_name': project.title,
        'history_name': history.name,
        'problem_type': problem_type,
        'dataset': context_dataset,
        'result': context_result,
        })
    print(context)
    return render(request,'model/predict.html',context)

@login_required
def api(request):
    project = get_object_or_404(NN_model,user=request.user,pk=request.POST['project_id'])
    try:
        info = update_status(project.state_file)
    except:
        return HttpResponse('failed parsing status')
    info['status'] = project.get_status_display()
    # if info['status'] in ['error','finish training']:
    if project.status in ['error','finish']:
        if request.POST.get('type') == 'init':
            logger.info('back to idle')
        # # if info['status'] not in ['start training model', 'start testing', 'loading model']:
            info['status'] = 'system idle'
            # update_status(project.state_file,info['status'])
        # elif info['status'] == 'error':
        elif project.status == 'error':
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
    # with open('/home/plash/petpen/state.json','r+') as f:
        # info = json.load(f)
        # info['status'] = 'system idle'
        # f.seek(0)
        # json.dump(info,f)
        # f.truncate()

    return HttpResponse(json.dumps({"script":script, "div":div}), content_type="application/json")

def img_api(request,*args,**kwargs):
    import matplotlib
    # matplotlib.use('Agg')
    import random
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
 
    fig=Figure()
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    now=datetime.datetime.now()
    delta=datetime.timedelta(days=1)
    for i in range(10):
        x.append(now)
        now+=delta
        y.append(random.randint(0, 1000))
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    canvas=FigureCanvas(fig)
    import io
    output = io.BytesIO()
    print(kwargs)
    fig.savefig(output)
    contents = output.getvalue()
    response=HttpResponse(contents,content_type='image/png')
    # response=HttpResponse(content_type='image/png')
    # canvas.print_png(response)
    return response

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
            project_name = user_container.attrs['Mounts'][0]['Source'].split('/')[-1]
            project = NN_model.objects.filter(user=request.user).get(title=project_name)
            project.status = 'idle'
            project.save()
            user_container.stop(timeout=0)
        return HttpResponse('Editor closed.')
    elif action == 'open':
        try:
            project = NN_model.objects.filter(user=request.user).get(title=request.GET['target'])
        except:
            return HttpResponse('No available project found for editing.')
        project.status = 'editing'
        project.save()
        project_path = os.path.join(MEDIA_ROOT,os.path.dirname(project.structure_file))
        if not os.path.exists(project_path):
            os.makedirs(project_path)
        if not user_container:
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,user=os.getuid(),name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            user_container.stop(timeout=0)
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,user=os.getuid(),name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        return HttpResponse('running')

def preprocess_structure(file_path,projects,datasets):
    if not op.exists(file_path):
        update_status(op.join(op.dirname(file_path),'state.json'),'error: missing model structure')
        return 'file missing'
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
        project = NN_model.objects.filter(user=request.user).get(pk=request.POST['project'])
        script_path = op.abspath(op.join(__file__,op.pardir,op.pardir,op.pardir,'backend/petpen0.1.py'))
        executed = datetime.datetime.now()
        save_path = executed.strftime('%y%m%d_%H%M%S')
        if not project:
            return Http404('project not found')
        if request.POST['command']=='predict':
            history = History.objects.filter(project=project).get(pk=request.POST['history'])
            history_dir = op.join(MEDIA_ROOT,op.dirname(history.project.structure_file),history.save_path)
            dataset_type = request.POST['dataset']
            if dataset_type == 'test':
# only support single text input node now, so only read one dataset path
                with open(op.join(history_dir,'preprocessed/result.json'),'r') as f:
                    structure = json.load(f)
                    import pprint
                    pprint.pprint(structure['dataset'])
                    dataset = [v['valid_x'] for v in structure['dataset'].values() if 'valid_x' in v.keys()][0]

                    # p = push(project.id,['python',script_path,'-m',history_dir,'-t',save_path,'-testx',dataset,'-w',op.join(history_dir,'weights.h5'),'predict'])
                # prediction = Prediction(history=history,created=executed,expired=executed+timezone.timedelta(days=7))
                # prediction.save()
                # if not op.exists(prediction.path()): os.mkdir(prediction.path())
                # shutil.copy2(dataset,prediction.path())
            elif dataset_type == 'custom':
                with open(op.join(history_dir,'preprocessed/result.json'),'r') as f:
                    structure = json.load(f)
                    input_shape = [v['params']['shape'] for v in structure['layers'].values() if v['type']=='Input'][0]
                dataset = request.FILES['file']
                predict_dir = op.join(MEDIA_ROOT,op.dirname(project.structure_file),'result')
                if op.exists(predict_dir):
                    shutil.rmtree(predict_dir)
                    os.mkdir(predict_dir)
                ext = op.splitext(dataset.name)[1].lower()
                try:
                    if ext in ['.jpg','.jpeg','.img','.png']:
                        with open(op.join(predict_dir,'input'+ext),'wb') as f:
                            for chunk in dataset.chunks():
                                f.write(chunk)
                        import matplotlib.pyplot as plt
                        data_value = plt.imread(op.join(predict_dir,'input'+ext),format=ext[1:])
                        data_value = data_value.reshape([1]+input_shape)
                        np.save(op.join(predict_dir,'input.npy'), data_value)
                    elif ext == '.csv':
                        # data_value = pd.read_csv(op.join(predict_dir,'input'+ext),header = None).values
                        data_value = pd.read_csv(dataset,header = None).values
                        np.save(op.join(predict_dir,'input.npy'), data_value)
                        if len(data_value.shape) == 3 and data_value.shape[2] in [1,3,4]:
                            plt.imsave(op.join(predict_dir,'input.png'),data_value,format='png')
                    elif ext in ['.pickle','.pkl']:
                        try:
                            data_value = pickle.load( open(dataset, 'rb') )
                        except:
                            data_value = pd.read_pickle(dataset)
                        data_value = np.array(data_value)
                        np.save(op.join(predict_dir,'input.npy'), data_value)
                        if len(data_value.shape) == 3 and data_value.shape[2] in [1,3,4]:
                            plt.imsave(op.join(predict_dir,'input.png'),data_value,format='png')
                except Exception as err:
                    if not op.exists(predict_dir):
                        os.mkdir(predict_dir)
                    with open(op.join(predict_dir,'error_log'),'w') as f:
                        error_info = {
                            'error_type': str(type(err)),
                            'error_message': list(err.args),
                            }
                        json.dump(error_info,f)
                    logger.debug(err)
                    logger.debug(list(err.args))
                    # logger.error(err)
                    return HttpResponseRedirect(reverse('model:predict',kwargs={'project_id':project.id,'history_path':history.save_path}))
                p = push(project.id,['python',script_path,'-m',op.join(MEDIA_ROOT,op.dirname(project.structure_file)),'-testx',op.join(predict_dir,'input.npy'),'-w',op.join(history_dir,'weights.h5'),'predict'])
            return HttpResponseRedirect(reverse('model:predict',kwargs={'project_id':project.id,'history_path':history.save_path}))
        if request.POST['command'] == 'train':
            history_name = request.POST.get('name') or save_path
            logger.debug('start training on model {}, save path: {}'.format(project,save_path))
            structure_file = op.join(MEDIA_ROOT,project.structure_file)
            # info = update_status(project.state_file)
            # if info['status'] != 'system idle':
            if project.status != 'idle':
                return HttpResponse('waiting project back to idle')
            else:
                # update_status(project.state_file,'loading model')
                pass
            with open(structure_file) as f:
                model_parser = json.load(f)

            for key,value in model_parser['layers'].items():
                if value['type'] == 'Output':
                    loss = value['params']['loss']

            if 'entropy' in loss:
                problem = 'classification'
            else:
                problem = 'regression'
            history = History(project=project,name=history_name,executed=executed,save_path=save_path,status='running',execution_type=problem)
            history.save()
            project.training_counts += 1
            project.status = 'loading'
            project.save()
            project_path = op.dirname(structure_file)
            os.mkdir(op.join(project_path,save_path))
            shutil.copy2(structure_file,op.join(project_path,save_path))
            #----- file path transformation -----
            prcs = preprocess_structure(structure_file,NN_model.objects.filter(user=request.user),Dataset.objects.filter(user=request.user))
            print(prcs)
            if prcs != 'successed':
                os.makedirs(op.join(project_path,save_path,'logs/'))
                history.status = 'aborted'
                project.status = 'error'
                project.save()
                history.save()
                if prcs != 'file missing':
                    # update_status(project.state_file,status='error',detail='structure assignment error found on nodes {}'.format(', '.join(prcs)))
                    with open(op.join(project_path,save_path,'logs/error_log'),'w') as f:
                        f.write('Structure assignment error found on nodes {}'.format(', '.join(prcs)))
                    return JsonResponse({'missing':prcs})
                else:
                    # update_status(project.state_file,status='error',detail='please depoly your model structure before running')
                    with open(op.join(project_path,save_path,'logs/error_log'),'w') as f:
                        f.write('No deployed neural network found. Finish your neural network editing before running experiments.')
                    return JsonResponse({'missing':'no structure file'})
            else:
                os.mkdir(op.join(project_path,save_path,'preprocessed'))
                shutil.copy2(op.join(op.dirname(structure_file),'preprocessed/result.json'),op.join(project_path,save_path,'preprocessed'))
            try:
                p = push(project.id,['python',script_path,'-m',project_path,'-t',save_path,'train'])
            except Exception as e:
                logger.error('Failed to run the backend', exc_info=True)
        elif request.POST['command'] == 'stop':
            p = kill(project.id)
            project.status = 'idle'
            project.save()
            history = project.history_set.latest('id')
            history.status = 'aborted'
            history.save()
        return HttpResponse("response sent from backend")
