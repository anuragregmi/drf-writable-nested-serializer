from rest_framework import serializers
from rest_framework.fields import empty


class WritableNestedModelSerializer(serializers.ModelSerializer):
    """
    Writable Nested Serializer

    Handles create and update of nested serializers

    Usage: Extend this class and define a meta property like

        Meta.writable_nested_fields = {
            'field': 'related_name',
            ...
        }
    """

    def __init__(self, instance=None, data=empty, **kwargs):
        super(WritableNestedModelSerializer, self).__init__(instance, data, **kwargs)
        assert hasattr(self.Meta, 'writable_nested_fields'), (
            'Class {serializer_class} missing "Meta.writable_nested_fields" attribute'.format(
                serializer_class=self.__class__.__name__
            )
        )
        self.writable_nested_fields = self.get_writable_nested_fields()

    def get_writable_nested_fields(self):
        """
        Get writable nested fields

        :return: list of fields with type `WritableNestedField`
        """

        wnf_names = getattr(self.Meta, 'writable_nested_fields')
        fields = self.fields

        wnf = {}
        for field_name in wnf_names:
            wnf.update({field_name: fields[field_name]})
        return wnf

    @property
    def writable_nested_field_mapping(self):
        return getattr(self.Meta, 'writable_nested_fields')

    def create(self, validated_data):
        wnf = self.writable_nested_fields
        wnf_data = {field: validated_data.pop(field) for field in wnf}
        wnf_mapping = self.writable_nested_field_mapping
        instance = self.Meta.model.objects.create(**validated_data)

        for field in wnf:
            field_data = wnf_data.get(field)
            if isinstance(wnf[field], serializers.ListSerializer):
                for individual_data in field_data:
                    individual_data.update({wnf_mapping[field]: instance})

                    wnf[field].child.Meta.model.objects.create(**individual_data)
            else:
                field_data.update({wnf_mapping[field]: instance})
                wnf[field].Meta.model.objects.create(**field_data)
        return instance

    def update(self, instance, validated_data):
        wnf = self.writable_nested_fields
        wnf_data = {field: self.initial_data.get(field) for field in wnf}

        for field in wnf:
            try:
                validated_data.pop(field)
            except KeyError:
                pass
        wnf_mapping = self.writable_nested_field_mapping

        for field in wnf:
            field_data = wnf_data.get(field)
            if field_data:
                if isinstance(wnf[field], serializers.ListSerializer):
                    for individual_data in field_data:
                        data_id = individual_data.get('id')
                        if data_id:
                            try:
                                obj = wnf[field].child.Meta.model.objects.get(id=data_id)
                                sr = wnf[field].child.__class__(instance=obj, data=individual_data, partial=self.partial)
                                if sr.is_valid():
                                    sr.save()
                                else:
                                    raise serializers.ValidationError(sr.errors)
                            except wnf[field].child.Meta.model.DoesNotExist:
                                raise serializers.ValidationError('No object found to update for id={}'.format(data_id))
                            except serializers.ValidationError as e:
                                raise e
                        else:
                            individual_data.update({wnf_mapping[field]: instance})
                            wnf[field].child.Meta.model.objects.create(album=instance, **individual_data)
                else:
                    data_id = field_data.get('id')
                    if data_id:
                        try:
                            obj = wnf[field].child.Meta.model.objects.get(id=data_id)
                            sr = wnf[field].child.__class__(instance=obj, data=field_data, partial=self.partial)
                            if sr.is_valid():
                                sr.save()
                            else:
                                raise serializers.ValidationError(sr.errors)
                        except wnf[field].Meta.model.DoesNotExist:
                            raise serializers.ValidationError('No object found to update for id={}'.format(data_id))
                        except serializers.ValidationError as e:
                            raise e
                    else:
                        field_data.update({wnf_mapping[field]: instance})
                        wnf[field].Meta.model.objects.create(**field_data)

            instance = super().update(instance, validated_data)

            return instance
