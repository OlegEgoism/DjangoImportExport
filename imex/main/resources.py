from django.db.models import QuerySet
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from .models import Skill, City, People


class ForeignKeyWidgetWithCreation(ForeignKeyWidget):
    def __init__(self, model, field="pk", create=False, **kwargs):
        self.model = model
        self.field = field
        self.create = create
        super(ForeignKeyWidgetWithCreation, self).__init__(model, field=field, **kwargs)

    def clean(self, value, **kwargs):
        print(value)
        if not value:
            return None
        if self.create:
            self.model.objects.get_or_create(**{self.field: value})
        val = super(ForeignKeyWidgetWithCreation, self).clean(value, **kwargs)
        return self.model.objects.get(**{self.field: val}) if val else None


class ManyToManyWidgetWithCreation(ManyToManyWidget):
    def __init__(self, model, field="pk", create=False, **kwargs):
        self.model = model
        self.field = field
        self.create = create
        super(ManyToManyWidgetWithCreation, self).__init__(model, field=field, **kwargs)

    def clean(self, value, **kwargs):
        if not value:
            return self.model.objects.none()
        cleaned_value: QuerySet = super(ManyToManyWidgetWithCreation, self).clean(value, **kwargs)
        object_list = value.split(self.separator)
        if len(cleaned_value.all()) == len(object_list):
            return cleaned_value
        if self.create:
            for object_value in object_list:
                _instance, _new = self.model.objects.get_or_create(**{self.field: object_value})
        model_objects = self.model.objects.filter(**{f"{self.field}__in": object_list})
        return model_objects


class PeopleResource(resources.ModelResource):
    city = fields.Field(column_name='city', attribute='city',
                        widget=ForeignKeyWidgetWithCreation(City, field='name', create=True))
    skill = fields.Field(column_name='skill', attribute='skill',
                         widget=ManyToManyWidgetWithCreation(Skill, field='name', separator=', ', create=True))

    class Meta:
        model = People
        fields = ('name', 'age', 'email', 'city', 'skill',)
        export_order = ('name', 'age', 'email', 'city', 'skill',)  # порядок экспорта полей
        import_id_fields = ('name',)  # поля для определения идентификатора
        force_init_instance = False  # Если установлено значение True, этот параметр предотвратит проверку базы данных на наличие существующих экземпляров при импорте. Включение этого параметра повышает производительность, если ваш набор данных импорта гарантированно содержать новые экземпляры.
        # exclude = ('id',)  # исключить поле