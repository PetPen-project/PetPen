from django.shortcuts import render
from django.views.generic import ListView

from django.contrib.auth.models import User
from model.models import NN_model
from dataset.models import Dataset

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

def dataset_examples(request):
    projects = NN_model.objects.filter(user=User.objects.get(pk=2))
    datasets = Dataset.objects.filter(user=User.objects.get(pk=2))
    context = {'datasets':datasets}
    return render(request, 'petpen/example.html', context)

def examples(request):
    projects = NN_model.objects.filter(user=User.objects.get(pk=17))
    datasets = Dataset.objects.filter(user=User.objects.get(pk=17))
    context = {'projects':projects}
    return render(request, 'petpen/example.html', context)
