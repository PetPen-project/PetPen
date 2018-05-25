from django.shortcuts import render,render_to_response,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse,Http404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import django.utils.timezone as timezone
from django.core.files import File
from django.contrib import messages
from django.views.generic import ListView

from job_queue import push, kill

import os,json,shutil,re,fnmatch
import os.path as op 
import subprocess,signal
import time,datetime
import docker
import pandas as pd

from model.utils import bokeh_plot, update_status
# from dataset.models import Dataset
from django.conf import settings
from .models import NN_model, History, Prediction
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
        context['project_id'] = self.kwargs['project_id']
        context['histories'] = self.object_list
        context['history'] = self.object
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
            with open(op.join(self.kwargs['history_path'],'weight.h5'),'rb') as h5:
                shutil.copyfileobj(h5,f)
            f.seek(0)
            response = HttpResponse(f,content_type='application/x-binary') 
            response['Content-Disposition'] = 'attachment; filename=model.h5'
        else:
            response = HttpResponse('error: request model on unsuccessful training.')

        return response

class PredictView(ListView):
    model =  Prediction
    template_name = 'model/predict.html'
    
    def get_queryset(self):
        try:
            queryset = History.objects.filter(project=self.kwargs['project_id'])
            queryset = self.model.objects.filter(history__in=queryset)
            return queryset
        except:
            raise Http404('query failed.')

    def get_context_data(self):
        context = {}
        predict = self.object
        context['project_id'] = self.kwargs['project_id']
        with open(op.join(predict.path(),'logs/type'),'r') as f:
            problem_type = f.readline()
        input_file = [f for f in os.listdir(predict.path()) if fnmatch.fnmatch(f,'*input*')][0]
        context['input_source'] = 'testing dataset' if input_file.startswith('testing') else 'custom input file'
        ext = op.splitext(input_file)[1]
        if ext == '.csv':
            dataset = pd.read_csv(op.join(predict.path(),input_file),header=None)
        elif ext == '.pickle'or ext == '.pkl':
            dataset = pd.read_pickle(op.join(predict.path(),input_file))
        outputs = pd.read_csv(op.join(predict.path(),'logs/result'))
        dataset = dataset.iloc[:10].values
        outputs = outputs.iloc[:10].values
        if self.kwargs.get('img'):
            img_size = [int(l) for l in re.search('(\d+)-*(\d+)*',self.kwargs['img']).groups() if l]
            print(img_size)
            if img_size:
                for index in range(len(dataset)):
                    dataset[index] = dataset[index]
        if problem_type == 'classification':
            if outputs.shape[1]>1:
                xdata = range(outputs.shape[1])
                chartcontents_output = []
                charttype_output = "discreteBarChart"
                for index in range(outputs.shape[0]):
                    chartcontents_output.append({
                        'chartdata': {
                            'x': xdata,
                            'name1': '',
                            'y1': outputs[index],
                            'extra1': {"tooltip": {"y_start": "", "y_end": " cal"}},
                            },
                        'chartcontainer': "discretebarchart_container{}".format(index),
                        })
            # for index in range(len(dataset)):
                # chartdata_output[index] = {
                    # 'x': range(1)
                # }
            # chartdata_loss['x'] = range(1,log_data.shape[0]+1)
            # chartdata_acc['x'] = range(1,log_data.shape[0]+1)
            # chartdata_loss['name0'] = 'training'
            # chartdata_loss['name1'] = 'validation'
            # chartdata_acc['name0'] = 'training'
            # chartdata_acc['name1'] = 'validation'
            # chartdata_loss['y0'] = log_data['loss'].values
            # chartdata_loss['y1'] = log_data['val_loss'].values
            # chartdata_acc['y0'] = log_data['acc'].values
            # chartdata_acc['y1'] = log_data['val_acc'].values
            # charttype_loss = "lineChart"
            # charttype_acc = "lineChart"
            # chartcontainer_loss = 'linechart_container_loss'
            # chartcontainer_acc = 'linechart_container_acc'
            # best_epoch_loss = log_data['val_loss'].argmin()
            # best_loss_value = log_data['val_loss'][best_epoch_loss]
            # best_epoch_acc = log_data['val_acc'].argmin()
            # best_acc_value = log_data['val_acc'][best_epoch_acc]
            # context.update({
                # 'epochs':log_data.shape[0],
                # 'best_epoch_loss':best_epoch_loss,
                # 'best_loss_value':best_loss_value,
                # 'charttype_loss': charttype_loss,
                # 'chartdata_loss': chartdata_loss,
                # 'chartcontainer_loss': chartcontainer_loss,
                # 'best_epoch_acc':best_epoch_acc,
                # 'best_acc_value':best_acc_value,
                # 'charttype_acc': charttype_acc,
                # 'chartdata_acc': chartdata_acc,
                # 'chartcontainer_acc': chartcontainer_acc,
                # 'extra': {
                    # 'x_is_date': False,
                    # 'x_axis_format': '',
                    # 'tag_script_js': True,
                    # 'jquery_on_ready': False,
                # }
            # })
        context.update({
            'problem_type':problem_type,
            'inputs':dataset,
            'outputs':outputs,
            'charttype_output':charttype_output,
            'chartcontents_output':chartcontents_output,
            })
        return context

    def get(self, request, *args, **kwargs):
        self.kwargs = kwargs
        self.kwargs.update(request.GET.dict())
        print(self.kwargs)
        self.object_list = self.get_queryset()
        self.object = self.get_queryset()[0]
        context = self.get_context_data()
        return self.render_to_response(context)
    
    def post(self, request, *args, **kwargs):
        pass

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
    if history.execution_type == 'classification':
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
        chartdata_loss['y1'] = log_data['val_acc'].values
        charttype_loss = "lineChart"
        charttype_acc = "lineChart"
        chartcontainer = 'linechart_container'
        best_epoch_loss = log_data['val_loss'].argmin()
        best_loss_value = log_data['val_loss'][best_epoch]
        best_epoch_acc = log_data['val_acc'].argmin()
        best_acc_value = log_data['val_acc'][best_epoch]
        context = {
            'history':history,
            'histories':histories,
            'epochs':log_data.shape[0],
            'best_epoch':best_epoch_loss,
            'best_val':best_loss_value,
            'charttype': charttype_loss,
            'chartdata': chartdata_loss,
            'chartcontainer': chartcontainer,
            'extra': {
                'x_is_date': False,
                'x_axis_format': '',
                'tag_script_js': True,
                'jquery_on_ready': False,
            }
        }
        return render(request,'model/history_detail.html',context)
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
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
        elif user_container.attrs['HostConfig']['Binds'][0].split(':')[0]!=project_path:
            user_container.stop(timeout=0)
            client.containers.run('noderedforpetpen',stdin_open=True,tty=True,name=str(request.user),volumes={project_path:{'bind':'/app','mode':'rw'}},ports={'1880/tcp':port},remove=True,hostname='petpen',detach=True)
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

                    p = push(project.id,['python',script_path,'-m',history_dir,'-t',save_path,'-testx',dataset,'-w',op.join(history_dir,'weights.h5'),'predict'])
                prediction = Prediction(history=history,created=executed,expired=executed+timezone.timedelta(days=7))
                prediction.save()
                if not op.exists(prediction.path()): os.mkdir(prediction.path())
                shutil.copy2(dataset,prediction.path())
            elif dataset_type == 'custom':
                dataset = request.FILES['file']
<<<<<<< Updated upstream
                print(dataset.name)
                print(dataset.size)
                print(request.FILES)
                # p = push(project.id,['python',script_path,'-m',project_path,'-t',save_path,'predict'])
            return HttpResponse('good')
=======
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
>>>>>>> Stashed changes
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
            update_status(project.state_file,status='system idle')
            history = project.history_set.latest('id')
            history.status = 'aborted'
            history.save()
<<<<<<< Updated upstream
            os.makedirs(op.join(project_path,save_path,'logs/'))
            with open(op.join(project_path,history.save_path,'logs/error_log'),'w') as f:
=======
            # update_status(project.state_file,status='system idle')
            log_dir = op.join(MEDIA_ROOT,op.dirname(project.structure_file),history.save_path,'logs/')
            if not op.exists(log_dir):
                os.makedirs(log_dir)
            with open(log_dir+'error_log','w') as f:
>>>>>>> Stashed changes
                f.write('Training stopped by user.')
        return HttpResponse("running")
