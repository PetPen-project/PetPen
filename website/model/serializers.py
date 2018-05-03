from rest_framework import serializers
from model.models import NN_model

class NN_modelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NN_model
        fields = ('user','title','state_file','structure_file','modified','training_counts','description','status')
