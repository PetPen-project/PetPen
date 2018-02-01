from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
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
            shutil.rmtree(op.join(MEDIA_ROOT,'datasets/{}/{}'.format(request.user.id,dataset.title)))
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
    return render(request, 'dataset/index.html', {'dataset_list':datasets, 'form':form})

class DatasetListView(ListView):
    model = Dataset
    template_name = 'dataset/index.html'
    form_class = UploadFileForm

    def get_queryset(self, request):
        """
        return the datasets belong to current user.
        """
        queryset = self.model._default_manager.all()
        queryset = queryset.filter(user=request.user)
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        allow_empty = self.get_allow_empty()

        if not allow_empty:
            # When pagination is enabled and object_list is a queryset,
            # it's better to do a cheap query than to load the unpaginated
            # queryset in memory.
            if self.get_paginate_by(self.object_list) is not None and hasattr(self.object_list, 'exists'):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list
            if is_empty:
                raise Http404(_("Empty list and '%(class_name)s.allow_empty' is False.") % {
                    'class_name': self.__class__.__name__,
                })
        context = self.get_context_data()
        form = self.form_class()
        context.update({'form':form})
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object_list = self.get_queryset(request)
        context = self.get_context_data()
        if 'delete-dataset' in request.POST:
            try:
                dataset = self.model.objects.get(pk=request.POST['delete-dataset'],user=request.user)
                shutil.rmtree(op.join(MEDIA_ROOT,'datasets/{}/{}'.format(request.user.id,dataset.title)))
                dataset.delete()
            except StandardError as e:
                print('failed to remove dataset.')
        elif 'download-dataset' in request.POST:
            print(2)
        elif 'info-dataset' in request.POST:
            try:
                dataset = self.model.objects.get(user=request.user,pk=request.POST['info-dataset'])
                context.update({'information':dataset})
            except:
                context.update({'error_message':'can\'t get information of dataset with id {}'.format(request.POST['info-dataset'])})
            return self.render_to_response(context)
        elif 'copy-dataset' in request.POST:
            print(4)
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                if not self.model.objects.filter(user=request.user,title=form.cleaned_data['title']):
                    for dataset_file in ['training_input_file','training_output_file','testing_input_file','testing_output_file']:
                        form_data[dataset_file].name = re.sub('_file',op.splitext(request.FILES[dataset_file].name)[1],dataset_file)
                    newfile = Dataset(title=form_data['title'],training_input_file=request.FILES['training_input_file'],training_output_file=request.FILES['training_output_file'],testing_input_file=request.FILES['testing_input_file'],testing_output_file=request.FILES['testing_output_file'],user=request.user)
                    newfile.save()
                    return HttpResponseRedirect(reverse("dataset:index"))
                else:
                    context.update({'error_message':'dataset title already exists.'})
                    return self.render_to_response(context)
        return self.render_to_response(context)

class DatasetDetailView(DetailView):
    model = Dataset
    template_name = 'dataset/dataset.html'

    def open_file(self,dataset_name):
        dataset_path = op.join(MEDIA_ROOT,dataset_name)
        ext = op.splitext(dataset_name)[1]
        if ext == '.csv':
            dataset = pd.read_csv(dataset_path,header=None)
        elif ext == '.pickle':
            dataset = pd.read_pickle(dataset_path)
        return dataset
    
    def get_object(self,queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        queryset = queryset.filter(user=self.user)
        try:
            obj = queryset.get(pk=self.kwargs['dataset_id'])
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
            training_dataset = self.open_file(str(self.object.training_input_file))
            context['train_sample_size'] = training_dataset.shape[0]
            testing_dataset = self.open_file(str(self.object.testing_input_file))
            context['test_sample_size'] = testing_dataset.shape[0]
            context['train_input_size'] = os.stat(op.join(MEDIA_ROOT,str(self.object.training_input_file))).st_size
            context['train_output_size'] = os.stat(op.join(MEDIA_ROOT,str(self.object.training_output_file))).st_size
            context['test_input_size'] = os.stat(op.join(MEDIA_ROOT,str(self.object.testing_input_file))).st_size
            context['test_output_size'] = os.stat(op.join(MEDIA_ROOT,str(self.object.testing_output_file))).st_size
        return super().get_context_data(**context)
    
    def get(self, request, *args, **kwargs):
        self.user = request.user
        return super().get(request, *args, **kwargs)

class DatasetUpdateView(UpdateView):
    model = Dataset

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        try:
            obj = queryset.get(pk=self.kwargs.get('dataset_id'))
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") % {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def post(self, request, *args, **kwargs):
        dataset = self.get_object()
        if request.POST.get('new_title'):
            dataset.title = request.POST['new_title']
        dataset.save()
        return redirect('dataset:dataset_detail', dataset_id = dataset.id)

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

