from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from django.core.urlresolvers import reverse
import re
import os

from model.utils import bokeh_plot

from .forms import UploadFileForm, DatasetForm, FeatureForm
# from .forms import handle_uploaded_file
from .models import Document
from dataset.models import Dataset
from django.conf import settings

def index(request):
    context = {'model': 1}
    if request.GET.get('mybtn'):
        # history = NN_model.model.train(x_train, y_train)
        history = 100
        context['history'] = history
    return render(request, 'model/index.html', context)

def build_model(request):
    return render(request, 'model/model.html', {})

def dataset_detail(request, dataset_id):
    dataset = get_object_or_404(Document, pk=dataset_id)
    datafile = dataset.docfile.open()
    data_name = dataset.docfile.name
    import pandas as pd
    dataframe = pd.read_csv('~/Documents/'+data_name)
    return render(request, 'model/dataset.html', {'dataset': dataset,'dataframe':dataframe,'data_html':dataframe.to_html()})

def results(request):
    context={}
    if request.method == 'GET':
        print(request.GET)
    if request.GET.get('type') == 'train':
        import json
        with open('/home/plash/petpen/state.json','r+') as f:
            info = json.load(f)
            print(info)
            info['status']='loading model'
            print(info)
            f.seek(0)
            json.dump(info,f)
        os.system('python /home/plash/petpen/git/backend/petpen0.1.py -n mnist -m /home/plash/demo1 -d 1 -w model')
        file_path='/home/plash/demo1/logs/'
        script, div = bokeh_plot(file_path)
        context={'plot':script,'plotDiv':div}
    return render(request, 'model/results.html', context)

def configure(request):
    import pandas as pd
    context = {}
    datasets = Dataset.objects.all()
    datasets_name = [dataset.title for dataset in datasets]
    context['datasets'] = datasets_name
    if request.method == 'POST':
        dataset_form = DatasetForm(request.POST)
        if dataset_form.is_valid():
            selected = dataset_form.cleaned_data.get('dataset')
            dataset = Dataset.objects.get(title=selected)
            print(os.path.join(settings.MEDIA_ROOT,dataset.csvfile.name))
            dataset = pd.read_csv(os.path.join(settings.MEDIA_ROOT,dataset.csvfile.name))
            if request.method == 'POST':
                io_form = FeatureForm(request.POST, features=dataset.columns.values)
                if io_form.is_valid():
                    return HttpResponse(io_form.cleaned_data.get(input_features))
            return HttpResponse(selected)
    else:
        dataset_form = DatasetForm()
    context['form'] = dataset_form
    return render(request, 'model/configure.html', context)

def api(request):
    import json
    # url = request.form['url']
    # title, article = ArticleParser(url)
    # data = {'title': title, 'article': article}
    file_path="/home/plash/petpen/state.json"
    # with open(file_path) as f:
    # with open("/home/saturn/research/petpen/models/state.json") as f:
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
    import pandas as pd
    from bokeh.plotting import figure
    from bokeh.embed import components

    file_path='/home/plash/demo1/logs/'
    script, div = bokeh_plot(file_path)
    print(script,div)

    logs = {}
    train_log = pd.read_csv(file_path+'train_log')
    train_log.index = [str(i) for i in train_log.index]
    logs['train'] = train_log.to_dict()
    test_log = pd.read_csv(file_path+'test_log')
    test_log.index = [str(i) for i in test_log.index]
    logs['test'] = test_log.to_dict()
    train_log = pd.read_csv(file_path+'train_logfull')
    train_log.index = [str(i) for i in train_log.index]
    logs['train_full'] = train_log.to_dict()
    test_log = pd.read_csv(file_path+'test_logfull')
    test_log.index = [str(i) for i in test_log.index]
    logs['test_full'] = test_log.to_dict()

    return HttpResponse(json.dumps({"script":script, "div":div}), content_type="application/json")
    # return JsonResponse(logs['train'])
    # return HttpResponse(json.dumps(logs['train_full']))
    # return HttpResponse(logs['train'])
