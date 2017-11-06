from petpen.settings import MEDIA_ROOT
import os
import re

def save_uploaded_dataset(request):
    dataset_dir = os.path.join(MEDIA_ROOT, 'datasets/{}/{}'.format(request.user.id,request.POST['title']))
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    for dataset_file in request.FILES:
        file_name = re.sub('_file', '.csv', dataset_file)
        with open(os.path.join(dataset_dir,file_name), 'wb+') as destination:
            for chunk in request.FILES[dataset_file].chunks():
                destination.write(chunk)
