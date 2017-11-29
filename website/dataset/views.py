from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from .models import Dataset
from .forms import UploadFileForm
from django.contrib.auth.models import User
import re

@login_required
def index(request):
    if request.method == 'POST':
        if 'delete-dataset' in request.POST:
            form = UploadFileForm()
            Dataset.objects.get(id=request.POST['delete-dataset']).delete()
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                for dataset_file in ['training_input_file','training_output_file','testing_input_file','testing_output_file']:
                    form_data[dataset_file].name = re.sub('_file','.csv',dataset_file)
                print(form_data)
                newfile = Dataset(title=form_data['title'],training_input_file=request.FILES['training_input_file'],training_output_file=request.FILES['training_output_file'],testing_input_file=request.FILES['testing_input_file'],testing_output_file=request.FILES['testing_output_file'],user=request.user)
                newfile.save()
                return HttpResponseRedirect(reverse("dataset:index"))
    else:
        form = UploadFileForm()
    datasets = Dataset.objects.filter(user_id = request.user.id)
    return render(request, 'dataset/index.html', {'datasets':datasets, 'form':form})

@login_required
def dataset_detail(request, dataset_id):
    context = {}
    return render(request,'dataset/dataset.html',context)
    dataset = get_object_or_404(Dataset, pk=dataset_id)
    import pandas as pd
    training_dataset = pd.read_csv(dataset.training_input_file)
    context['features'] = list(training_dataset.columns)
    context['dataset'] = dataset
    return render(request,'dataset/dataset.html',context)

