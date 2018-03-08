from django.shortcuts import render
from model.models import NN_model
from dataset.models import Dataset

def main(request):
    user = request.user
    context={'user':user}
    if user.is_authenticated():
        used_space = 0
        for dataset in user.dataset_set.all():
            used_space += dataset.train_input_size
            used_space += dataset.train_output_size
            used_space += dataset.test_input_size
            used_space += dataset.test_output_size
        context.update({'project_count':user.nn_model_set.count(),'dataset_count':user.dataset_set.count(),'used_space':used_space})
    return render(request, 'petpen/main.html', context)
