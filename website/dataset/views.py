from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from .forms import UploadFileForm
from .models import Dataset

MEDIA_ROOT = '/media/disk1/petpen/datasets'

def index(request):
    if request.method == 'POST':
        if 'delete-dataset' in request.POST:
            form = UploadFileForm()
            Dataset.objects.get(id=request.POST['delete-dataset']).delete()
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                newfile = Dataset(csvfile=request.FILES['csvfile'],title=request.POST['title'])
                newfile.save()
                return HttpResponseRedirect(reverse("index"))
    elif 'delete-dataset' in request.GET:
        print(request.GET)
    else:
        form = UploadFileForm()
    documents = Dataset.objects.all()
    return render(request, 'dataset/index.html', {'documents':documents, 'form':form})

def dataset_detail(request, dataset_id):
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    # dataset_file = dataset.csvfile.open()
    # dataset_name = dataset.csvfile.name
    # import pandas as pd
    # dataframe = pd.read_csv(MEDIA_ROOT+dataset_name)
    return render(request,'dataset/nav.html',{})

