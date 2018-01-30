from collections import OrderedDict

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

        wnf = OrderedDict()
        for field_name in wnf_names:
            # populating writable nested fields
            wnf.update({field_name: fields[field_name]})
        return wnf

    @property
    def writable_nested_field_mapping(self):
        return getattr(self.Meta, 'writable_nested_fields')

    def run_validation(self, data=empty):
        wnf_mapping = self.writable_nested_field_mapping

        for field in wnf_mapping:
            # remove related fields from nested serializer fields before validating

            ser = self.writable_nested_fields[field]

            if isinstance(ser, serializers.ListSerializer):
                ser.child.fields.pop(wnf_mapping[field], None)
            else:
                ser.fields.pop(wnf_mapping[field], None)

        return super(WritableNestedModelSerializer, self).run_validation(data)

    def create(self, validated_data):
        wnf = self.writable_nested_fields
        wnf_data = {field: validated_data.pop(field) for field in wnf}
        wnf_mapping = self.writable_nested_field_mapping

        # creating instance
        instance = self.Meta.model.objects.create(**validated_data)

        for field in wnf:
            field_data = wnf_data.get(field)

            if isinstance(wnf[field], serializers.ListSerializer):

                # for 'one-to-many' relation

                for individual_data in field_data:

                    # insert relation in data
                    individual_data.update({wnf_mapping[field]: instance})

                    wnf[field].child.Meta.model.objects.create(**individual_data)

            else:

                # for 'one-to-one relation

                # insert relation in data
                field_data.update({wnf_mapping[field]: instance})

                wnf[field].Meta.model.objects.create(**field_data)

        return instance

    def update(self, instance, validated_data):
        wnf = self.writable_nested_fields

        # data for nested serializers
        wnf_data = {field: self.initial_data.get(field) for field in wnf}

        for field in wnf:
            # delete nested data from validated data
            validated_data.pop(field, None)

        wnf_mapping = self.writable_nested_field_mapping

        for field in wnf:

            field_data = wnf_data.get(field)

            if field_data:
                # if data is sent for a field to update

                if isinstance(wnf[field], serializers.ListSerializer):

                    # for 'one-to-many' relation

                    for individual_data in field_data:

                        data_id = individual_data.get('id')
                        # id of data to be updated

                        if data_id:
                            try:
                                # instance to be updated
                                obj = wnf[field].child.Meta.model.objects.get(id=data_id)

                                sr = wnf[field].child.__class__(instance=obj, data=individual_data,
                                                                partial=self.partial)
                                if sr.is_valid():
                                    sr.save()
                                else:
                                    raise serializers.ValidationError(sr.errors)

                            except wnf[field].child.Meta.model.DoesNotExist:
                                # if given id does not exist
                                raise serializers.ValidationError('No object found to update for id={}'.format(data_id))

                            except serializers.ValidationError as e:
                                raise e
                        else:
                            # if no id is supplied then create new object

                            individual_data.update({wnf_mapping[field]: instance})
                            wnf[field].child.Meta.model.objects.create(album=instance, **individual_data)
                else:

                    # for 'one-to-one' relation

                    data_id = field_data.get('id')

                    if data_id:
                        try:
                            obj = wnf[field].child.Meta.model.objects.get(id=data_id)

                            sr = wnf[field].child.__class__(instance=obj, data=field_data, partial=self.partial)

                            # update instance
                            if sr.is_valid():
                                sr.save()
                            else:
                                raise serializers.ValidationError(sr.errors)

                        except wnf[field].Meta.model.DoesNotExist:
                            raise serializers.ValidationError('No object found to update for id={}'.format(data_id))

                        except serializers.ValidationError as e:
                            raise e

                    else:

                        # create new field if not supplied

                        field_data.update({wnf_mapping[field]: instance})
                        wnf[field].Meta.model.objects.create(**field_data)

            instance = super().update(instance, validated_data)

            return instance
