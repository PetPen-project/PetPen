from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from .models import Dataset
from .forms import UploadFileForm
from django.contrib.auth.models import User
from petpen.settings import MEDIA_ROOT

import re,os,shutil
import os.path as op
import pandas as pd

@login_required
def index(request):
    if request.method == 'POST':
        if 'delete-dataset' in request.POST:
            form = UploadFileForm()
            dataset = Dataset.objects.get(id=request.POST['delete-dataset'])
            shutil.rmtree(os.pahth.join(MEDIA_ROOT,'datasets/{}/{}'.format(request.user.id,dataset.title)))
            dataset.delete()
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                for dataset_file in ['training_input_file','training_output_file','testing_input_file','testing_output_file']:
                    form_data[dataset_file].name = re.sub('_file',op.splitext(request.FILES[dataset_file].name)[1],dataset_file)
                print(form_data)
                newfile = Dataset(title=form_data['title'],training_input_file=request.FILES['training_input_file'],training_output_file=request.FILES['training_output_file'],testing_input_file=request.FILES['testing_input_file'],testing_output_file=request.FILES['testing_output_file'],user=request.user)
                newfile.save()
                return HttpResponseRedirect(reverse("dataset:index"))
    else:
        form = UploadFileForm()
    datasets = Dataset.objects.filter(user_id = request.user.id)
    return render(request, 'dataset/index.html', {'datasets':datasets, 'form':form})

# class datasetDetailView(DetailView):
    # model = Dataset
    # template_name = 'dataset/dataset.html'
    # def open_file(self,dataset_name):
        # dataset_path = op.join(MEDIA_ROOT,dataset_name)
        # ext = op.splitext(dataset_name)[1]
        # if ext == '.csv':
            # dataset = pd.read_csv(dataset_path)
        # elif ext == '.pickle':
            # dataset = pd.read_pickle(dataset_path)

@login_required
def dataset_detail(request, dataset_id):
    context = {}
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    training_dataset = pd.read_csv(os.path.join(MEDIA_ROOT,str(dataset.training_input_file)),header=None)
    context['train_sample_size'] = training_dataset.shape[0]
    testing_dataset = pd.read_csv(os.path.join(MEDIA_ROOT,str(dataset.testing_input_file)),header=None)
    context['test_sample_size'] = testing_dataset.shape[0]
    context['train_input_size'] = os.stat(os.path.join(MEDIA_ROOT,str(dataset.training_input_file))).st_size
    context['train_output_size'] = os.stat(os.path.join(MEDIA_ROOT,str(dataset.training_output_file))).st_size
    context['test_input_size'] = os.stat(os.path.join(MEDIA_ROOT,str(dataset.testing_input_file))).st_size
    context['test_output_size'] = os.stat(os.path.join(MEDIA_ROOT,str(dataset.testing_output_file))).st_size
    return render(request,'dataset/dataset.html',context)

