from rest_framework import serializers
from django.shortcuts import get_object_or_404
from django.http import Http404


def create_serializer_class(name, fields):
    """source : Hacksoftware Django styleguide"""
    return type(name, (serializers.Serializer,), fields)


def inline_serializer(*, fields, data=None, **kwargs):
    """source : Hacksoftware Django styleguide"""
    serializer_class = create_serializer_class(name='', fields=fields)

    if data is not None:
        return serializer_class(data=data, **kwargs)

    return serializer_class(**kwargs)


def get_object(model_or_queryset, **kwargs):
    """return None in case of 404"""
    try:
        return get_object_or_404(model_or_queryset, **kwargs)
    except Http404:
        return None
