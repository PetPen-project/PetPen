from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.core.files import File
from model.models import NN_model
from dataset.models import Dataset
from petpen.settings import MEDIA_ROOT

import shutil, os, re
import os.path as op

def main(request):
    user = request.user
    context={'user':user}
    if user.is_authenticated:
        used_space = 0
        for dataset in user.dataset_set.all():
            used_space += dataset.train_input_size
            used_space += dataset.train_output_size
            used_space += dataset.test_input_size
            used_space += dataset.test_output_size
        context.update({'project_count':user.nn_model_set.count(),'dataset_count':user.dataset_set.count(),'used_space':used_space})
    return render(request, 'petpen/main.html', context)

@login_required
def examples(request):
    projects = NN_model.objects.filter(user=User.objects.get(pk=17))
    context = {'projects':projects}
    if request.GET.get('description'):
        return HttpResponse(projects.get(pk=request.GET['description']).description)
    if request.method == "POST":
        project = NN_model.objects.get(pk=request.POST['id'])
        if NN_model.objects.filter(user=request.user,title=project.title):
            context['error_message'] = 'project with title {} already exists!'.format(project.title)
            return render(request, 'petpen/example.html', context)
        model_dir = "models/{}/{}/".format(request.user.id,project.title)
        newModel = NN_model(title=project.title,user=request.user,state_file=model_dir+"state.json",structure_file=model_dir+"result.json")
        newModel.save()
        shutil.copytree(op.join(MEDIA_ROOT,"models/{}/{}/".format(17,project.title)),op.join(MEDIA_ROOT,model_dir))
        context['info'] = 'The example project {} is copied into your account.'.format(project.title)
    return render(request, 'petpen/example.html', context)

@login_required
def examples_dataset(request):
    datasets = Dataset.objects.filter(user=User.objects.get(pk=17))
    context = {'datasets':datasets}
    if request.GET.get('description'):
        return HttpResponse(datasets.get(pk=request.GET['description']).description)
    if request.method == "POST":
        dataset = Dataset.objects.get(pk=request.POST['id'])
        if Dataset.objects.filter(user=request.user,title=dataset.title):
            context['error_message'] = 'dataset with title {} already exists!'.format(dataset.title)
            return render(request, 'petpen/example_dataset.html', context)
        dataset_dir = "datasets/{}/{}/".format(request.user.id,dataset.title)
        newDataset = Dataset(
            title=dataset.title,
            user=request.user,
            training_input_file=File(dataset.training_input_file,op.split(dataset.training_input_file.name)[1]),
            training_output_file=File(dataset.training_output_file,op.split(dataset.training_output_file.name)[1]),
            testing_input_file=File(dataset.testing_input_file,op.split(dataset.testing_input_file.name)[1]),
            testing_output_file=File(dataset.testing_output_file,op.split(dataset.testing_output_file.name)[1]),
            train_input_size = dataset.train_input_size,
            test_input_size = dataset.test_input_size,
            train_output_size = dataset.train_output_size,
            test_output_size = dataset.test_output_size,
            train_samples = dataset.train_samples,
            test_samples = dataset.test_samples,
            input_shape = dataset.input_shape,
            output_shape = dataset.output_shape,
            description = dataset.description,
            filetype = dataset.filetype,
            is_image = dataset.is_image
            )
        newDataset.save()
        # shutil.copytree(op.join(MEDIA_ROOT,"models/{}/{}/".format(17,project.title)),op.join(MEDIA_ROOT,model_dir))
        context['info'] = 'The example dataset {} is copied into your account.'.format(dataset.title)
    return render(request, 'petpen/example_dataset.html', context)

@login_required
def feature_list(request):
    context = {}
    return render(request, 'petpen/feature_list.html', context)
