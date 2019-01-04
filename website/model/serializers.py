from rest_framework import serializers
from model.models import NN_model

class NN_modelSerializer(serializers.ModelSerializer):
    class Meta:
        model = NN_model
        fields = ('user','title','training_counts','description','status',)
        read_only_fields = ('user',)
