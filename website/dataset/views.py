from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Dataset
from .forms import UploadFileForm
from django.contrib.auth.models import User

MEDIA_ROOT = '/media/disk1/petpen/datasets'

def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login/')
    
    if request.method == 'POST':
        if 'delete-dataset' in request.POST:
            form = UploadFileForm()
            Dataset.objects.get(id=request.POST['delete-dataset']).delete()
        else:
            if request.POST.get('shared_testing',False):
                request.FILES['testing_csvfile'] = request.FILES['training_csvfile']
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                newfile = Dataset(training_csvfile=request.FILES['training_csvfile'],testing_csvfile=request.FILES['testing_csvfile'],title=request.POST['title'],user=request.user)
                newfile.save()
                return HttpResponseRedirect(reverse("index"))
    else:
        form = UploadFileForm()
    datasets = Dataset.objects.filter(user_id = request.user.id)
    return render(request, 'dataset/index.html', {'datasets':datasets, 'form':form})

def dataset_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    context = {}
    import pandas as pd
    training_dataset = pd.read_csv(dataset.training_csvfile)
    context['features'] = list(training_dataset.columns)
    context['dataset'] = dataset
    return render(request,'dataset/dataset.html',context)

