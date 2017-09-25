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
    form = UploadFileForm()
    datasets = Dataset.objects.all()
    users = User.objects.all()
    return render(request, 'dataset/index.html', {'datasets':datasets,'form':form})
    
    if request.method == 'POST':
        if 'delete-dataset' in request.POST:
            form = UploadFileForm()
            Dataset.objects.get(id=request.POST['delete-dataset']).delete()
        else:
            if request.POST['shared_testing']:
                request.FILES['testing_csvfile'] = request.FILES['training_csvfile']
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                newfile = Dataset(training_csvfile=request.FILES['training_csvfile'],testing_csvfile=request.FILES['testing_csvfile'],title=request.POST['title'],user=request.user)
                newfile.save()
                return HttpResponseRedirect(reverse("index"))
    else:
        form = UploadFileForm()
    datasets = Dataset.objects.all()
    return render(request, 'dataset/index.html', {'datasets':datasets, 'form':form})

def dataset_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    context = dataset
    # dataset_file = dataset.csvfile.open()
    # dataset_name = dataset.csvfile.name
    # import pandas as pd
    # dataframe = pd.read_csv(MEDIA_ROOT+dataset_name)
    return render(request,'dataset/nav.html',{})

