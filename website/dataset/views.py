from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
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
import numpy as np
from io import BytesIO
import zipfile

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler(op.join(op.abspath(op.dirname(op.dirname(__name__))),'website.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
# logger.setLevel(logging.WARNING)

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
        form = self.form_class()
        context.update({'form':form})
        print(request.POST)
        if 'delete-dataset' in request.POST:
            try:
                dataset = self.model.objects.get(pk=request.POST['delete-dataset'],user=request.user)
                shutil.rmtree(op.join(MEDIA_ROOT,'datasets/{}/{}'.format(request.user.id,dataset.title)))
                dataset.delete()
            except BaseException as e:
                logger.warning('failed to DELETE dataset. user:{},title:{}'.format(request.user,dataset.title))
                context.update({'error_message':'failed to delete dataset with id {}'.format(request.POST['delete-dataset'])})
                return self.render_to_response(context)
        elif 'download-dataset' in request.POST:
            try:
                dataset = self.model.objects.get(pk=request.POST['download-dataset'])
                in_memory = BytesIO()
                with zipfile.ZipFile(in_memory,"a") as zf:
                    zf.write(dataset.training_input_file.file.name,op.split(dataset.training_input_file.name)[1])
                    zf.write(dataset.training_output_file.file.name,op.split(dataset.training_output_file.name)[1])
                    zf.write(dataset.testing_input_file.file.name,op.split(dataset.testing_input_file.name)[1])
                    zf.write(dataset.testing_output_file.file.name,op.split(dataset.testing_output_file.name)[1])
                    # for _file in zf.filelist:
                        # _file.create_system = 0
                logger.debug(dataset.title)
                in_memory.seek(0)
                response = HttpResponse(in_memory,content_type='application/zip')
                response['Content-Disposition'] = 'attachment: filename={}.zip'.format(dataset.title)
                return response
            except BaseException as e:
                logger.warning('failed to DOWNLOAD dataset. user:{},title:{}'.format(request.user,dataset.title))
                logger.error(e)
                context.update({'error_message':'failed to download dataset with id {}'.format(request.POST['download-dataset'])})
                return self.render_to_response(context)
        elif 'info-dataset' in request.POST:
            try:
                dataset = self.model.objects.get(user=request.user,pk=request.POST['info-dataset'])
                context.update({'information':dataset})
            except:
                context.update({'error_message':'can\'t get information of dataset with id {}'.format(request.POST['info-dataset'])})
            return self.render_to_response(context)
        elif 'copy-dataset' in request.POST:
            pass
        else:
            form = UploadFileForm(request.POST, request.FILES)
            if form.is_valid():
                form_data = form.cleaned_data
                if not self.model.objects.filter(user=request.user,title=form_data['title']):
                    filetype = None
                    # input_filetype = None
                    # output_filetype = None
                    for dataset_file in ['training_input_file','training_output_file','testing_input_file','testing_output_file']:
                        ext = op.splitext(request.FILES[dataset_file].name)[1]
                        form_data[dataset_file].name = re.sub('_file',ext,dataset_file)
                        # if 'input_file' in dataset_file:
                            # if input_filetype and input_filetype != ext:
                                # context.update({'error_message':'Data type mismatch between training and testing input dataset.'})
                            # else:
                                # input_filetype = input_filetype or ext
                        # else:
                            # if output_filetype and output_filetype != ext:
                                # context.update({'error_message':'Data type mismatch between training and testing output dataset.'})
                            # else:
                                # output_filetype = output_filetype or ext
                        if not filetype:
                            filetype = ext
                        elif filetype != ext:
                            context.update({'error_message':'Found both csv and pickle files. Reformat to the same file type and try again.'})
                    FILE_CHOICES = {
                        '.csv':'CSV',
                        '.pickle':'PKL',
                        '.pkl':'PKL',
                        '.npy':'NPY',
                        '.zip':'IMG',
                    }
                    if filetype == '.csv':
                        filetype = 'CSV'
                    elif filetype == '.pickle' or filetype == '.pkl':
                        filetype = 'PKL'
                    elif filetype == '.npy':
                        filetype = 'NPY'
                    else:
                        context.update({'error_message':'Unsupported filetype found. Please use csv, numpy or pickle file format!'})
                    # input_filetype = FILE_CHOICES[input_filetype]
                    # output_filetype = FILE_CHOICES[output_filetype]
                    if context.get('error_message'):
                        return self.render_to_response(context)
                    has_labels = True if request.POST.get('has_labels') == 'YES' else False
                    newfile = Dataset(title=form_data['title'],
                            training_input_file=request.FILES['training_input_file'],
                            training_output_file=request.FILES['training_output_file'],
                            testing_input_file=request.FILES['testing_input_file'],
                            testing_output_file=request.FILES['testing_output_file'],
                            user=request.user,filetype=filetype,
                            has_labels = has_labels,
                            # input_filetype=input_filetype,output_filetype=output_filetype
                            )
                    newfile.save()

                    if newfile.filetype == 'CSV':
                        if newfile.has_labels:
                            data = pd.read_csv(newfile.training_output_file.file.name)
                        else:
                            data = pd.read_csv(newfile.training_output_file.file.name,header=None)
                        newfile.train_samples = data.shape[0]
                        newfile.output_shape = str(data.shape[1:]) if len(data.shape)>2 else str(data.shape[1])
                        if newfile.has_labels:
                            data = pd.read_csv(newfile.testing_input_file.file.name)
                        else:
                            data = pd.read_csv(newfile.testing_input_file.file.name,header=None)
                        newfile.test_samples = data.shape[0]
                        newfile.input_shape = str(data.shape[1:]) if len(data.shape)>2 else str(data.shape[1])
                    elif newfile.filetype == 'NPY':
                        data = np.load(newfile.training_input_file.file.name)
                        newfile.train_samples = data.shape[0]
                        newfile.input_shape = str(data.shape[1:])
                        data = np.load(newfile.testing_output_file.file.name)
                        newfile.test_samples = data.shape[0]
                    else:
                        data = pd.read_pickle(newfile.training_output_file.file.name)
                        newfile.train_samples = data.shape[0]
                        newfile.output_shape = str(data.shape[1:])
                        data = pd.read_pickle(newfile.training_input_file.file.name)
                        newfile.train_samples = data.shape[0]
                        newfile.input_shape = str(data.shape[1:])
                        data = pd.read_pickle(newfile.testing_output_file)
                        newfile.test_samples = data.shape[0]
                    newfile.train_input_size = newfile.training_input_file.file.size
                    newfile.train_output_size = newfile.training_output_file.file.size
                    newfile.test_input_size = newfile.testing_input_file.file.size
                    newfile.test_output_size = newfile.testing_output_file.file.size
                    if request.POST.get('description'):
                        newfile.description = request.POST.get('description')
                    newfile.save()

                    return HttpResponseRedirect(reverse("dataset:index"))
                else:
                    context.update({'error_message':'dataset title already exists.'})
        return HttpResponseRedirect(reverse('dataset:index'))

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
            raise Http404(("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
            context['train_sample_size'] = self.object.train_samples
            context['test_sample_size'] = self.object.test_samples
            context['train_input_size'] = self.object.training_input_file.size
            context['train_output_size'] = self.object.training_output_file.size
            context['test_input_size'] = self.object.testing_input_file.size
            context['test_output_size'] = self.object.testing_output_file.size
            context['input_shape'] = self.object.input_shape
            context['output_shape'] = self.object.output_shape
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
def dataset_view(request, dataset_id):
    context = {}
    dataset = get_object_or_404(Dataset, pk=dataset_id,user=request.user)
    dataset_type = request.GET.get('type')
    if dataset_type == 'tro':
        dataset_filefield = dataset.training_output_file
    elif dataset_type == 'tsi':
        dataset_filefield = dataset.testing_input_file
    elif dataset_type == 'tso':
        dataset_filefield = dataset.testing_output_file
    else: #default type tri
        dataset_filefield = dataset.training_input_file
    dataset_path = op.join(MEDIA_ROOT,dataset_filefield.name)
    dataset_ext = op.splitext(dataset_filefield.name)[1]
    if dataset_ext == '.pickle':
        try:
            dataset_content = pickle.load( open(dataset_path, 'rb') )
        except:
            dataset_content = pd.read_pickle(dataset_path)
    elif dataset_ext == '.csv':
        if dataset.has_labels:
            dataset_content = pd.read_csv(dataset_path)
        else:
            dataset_content = pd.read_csv(dataset_path,header=None)
    elif dataset_ext == '.npy':
        dataset_content = npy.load(dataset_path)
    print(dataset_content.shape)
    print(type(dataset_content))
    if len(dataset_content.shape)!=2:
        return render(request,'dataset/dataset_no_preview.html')
    if request.GET.get('f') == 'json':
        response = HttpResponse(dataset_content.to_json(),content_type='json')
        return response
    else:
        if not hasattr(dataset_content,'columns'):
            dataset_content = pd.DataFrame(dataset_content)
        columns = [{'field': f, 'title': f} for f in dataset_content.columns]
        context = {
                'columns': columns,
                'data':dataset_content.to_json(orient='records')
                }
        return render(request,'dataset/dataset_table.html',context)

