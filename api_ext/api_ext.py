# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2016 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import json
import time

from django.db.models import Q
from django.conf.urls import url
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db.models import Count
from django.http.response import HttpResponse
from django.template.response import TemplateResponse
from django.utils.translation import get_language

from avatar.templatetags.avatar_tags import avatar_url
from tastypie import http
from tastypie.exceptions import BadRequest

from guardian.shortcuts import get_objects_for_user
from tastypie.bundle import Bundle

from base_ext.models import MainCategory
from base_ext.models import DomainArea
from base_ext.models import DataPortal
from base_ext.models import ValidationLevel
from geonode.base.models import ResourceBase
from geonode.base.models import TopicCategory
from geonode.base.models import Region
from geonode.base.models import HierarchicalKeyword
from geonode.base.models import ThesaurusKeywordLabel
from geonode.layers.models import Layer, Style
from geonode.maps.models import Map
from geonode.documents.models import Document
from geonode.groups.models import GroupProfile, GroupCategory
from django.core.serializers.json import DjangoJSONEncoder
from tastypie.serializers import Serializer
from tastypie import fields
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.utils import trailing_slash

from geonode.utils import check_ogc_backend
from geonode.security.utils import get_visible_resources

FILTER_TYPES = {
    'layer': Layer,
    'map': Map,
    'document': Document
}

class CountJSONSerializer(Serializer):
    """Custom serializer to post process the api and add counts"""

    def get_resources_counts(self, options):
        if settings.SKIP_PERMS_FILTER:
            resources = ResourceBase.objects.all()
        else:
            resources = get_objects_for_user(
                options['user'],
                'base.view_resourcebase'
            )

        resources = get_visible_resources(
            resources,
            options['user'],
            admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
            unpublished_not_visible=settings.RESOURCE_PUBLISHING,
            private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        if resources and resources.count() > 0:
            if options['title_filter']:
                resources = resources.filter(title__icontains=options['title_filter'])

            if options['type_filter']:
                resources = resources.instance_of(options['type_filter'])

        counts = list(resources.values(options['count_type']).annotate(count=Count(options['count_type'])))

        return dict([(c[options['count_type']], c['count']) for c in counts])

    def to_json(self, data, options=None):
        options = options or {}
        data = self.to_simple(data, options)
        counts = self.get_resources_counts(options)
        if 'objects' in data:
            for item in data['objects']:
                item['count'] = counts.get(item['id'], 0)
        # Add in the current time.
        data['requested_time'] = time.time()

        return json.dumps(data, cls=DjangoJSONEncoder, sort_keys=True)


class TypeFilteredResource(ModelResource):
    """ Common resource used to apply faceting to categories, keywords, and
    regions based on the type passed as query parameter in the form
    type:layer/map/document"""

    count = fields.IntegerField()

    def build_filters(self, filters=None, ignore_bad_filters=False):
        if filters is None:
            filters = {}
        self.type_filter = None
        self.title_filter = None

        orm_filters = super(TypeFilteredResource, self).build_filters(filters)

        if 'type' in filters and filters['type'] in FILTER_TYPES.keys():
            self.type_filter = FILTER_TYPES[filters['type']]
        else:
            self.type_filter = None
        if 'title__icontains' in filters:
            self.title_filter = filters['title__icontains']

        return orm_filters

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['title_filter'] = getattr(self, 'title_filter', None)
        options['type_filter'] = getattr(self, 'type_filter', None)
        options['user'] = request.user

        return super(TypeFilteredResource, self).serialize(request, data, format, options)


class TagResource(TypeFilteredResource):
    """Tags api"""

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'keywords'

        return super(TagResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = HierarchicalKeyword.objects.all().order_by('name')
        resource_name = 'keywords'
        allowed_methods = ['get']
        filtering = {
            'slug': ALL,
        }
        serializer = CountJSONSerializer()


class ThesaurusKeywordResource(TypeFilteredResource):
    """ThesaurusKeyword api"""

    thesaurus_identifier = fields.CharField(null=False)
    label_id = fields.CharField(null=False)

    def build_filters(self, filters={}, ignore_bad_filters=False):
        """adds filtering by current language"""

        id = filters.pop('id', None)

        orm_filters = super(ThesaurusKeywordResource, self).build_filters(filters)

        if id is not None:
            orm_filters['keyword__id'] = id

        orm_filters['lang'] = filters['lang'] if 'lang' in filters else get_language()

        if 'thesaurus' in filters:
            orm_filters['keyword__thesaurus__identifier'] = filters['thesaurus']

        return orm_filters

    def serialize(self, request, data, format, options={}):
        options['count_type'] = 'tkeywords__id'

        return super(ThesaurusKeywordResource, self).serialize(request, data, format, options)

    def dehydrate_id(self, bundle):
        return bundle.obj.keyword.id

    def dehydrate_label_id(self, bundle):
        return bundle.obj.id

    def dehydrate_thesaurus_identifier(self, bundle):
        return bundle.obj.keyword.thesaurus.identifier

    class Meta:
        queryset = ThesaurusKeywordLabel.objects \
                                        .all() \
                                        .order_by('label') \
                                        .select_related('keyword') \
                                        .select_related('keyword__thesaurus')

        resource_name = 'thesaurus/keywords'
        allowed_methods = ['get']
        filtering = {
            'id': ALL,
            'label': ALL,
            'lang': ALL,
            'thesaurus': ALL,
        }
        serializer = CountJSONSerializer()


class RegionResource(TypeFilteredResource):
    """Regions api"""

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'regions'

        return super(RegionResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = Region.objects.all().order_by('name')
        resource_name = 'regions'
        allowed_methods = ['get']
        filtering = {
            'name': ALL,
            'code': ALL,
        }
        if settings.API_INCLUDE_REGIONS_COUNT:
            serializer = CountJSONSerializer()

class MainCategoryResource(TypeFilteredResource):
    """Main Category api"""
    layers_count = fields.IntegerField(default=0)
    documents_count = fields.IntegerField(default=0)
    maps_count = fields.IntegerField(default=0)

    def dehydrate_layers_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Layer) 
        filter_set = bundle.obj.topiccategory_set.filter(identifier__in=obj_with_perms.values('category__identifier'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()
    
    def dehydrate_documents_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Document) 
        filter_set = bundle.obj.topiccategory_set.filter(identifier__in=obj_with_perms.values('category__identifier'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()
    
    def dehydrate_maps_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Map) 
        filter_set = bundle.obj.topiccategory_set.filter(identifier__in=obj_with_perms.values('category__identifier'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()
 
    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'category__main_category'

        return super(MainCategoryResource, self).serialize(request, data, format, options)
 
    class Meta:
        queryset = MainCategory.objects.all()
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL
        }
        serializer = CountJSONSerializer()

class TopicCategoryResource(TypeFilteredResource):
    """Category api"""
    layers_count = fields.IntegerField(default=0)

    main_category = fields.ToOneField(
        MainCategoryResource,
        'main_category',
        null=True,
        full=True)

    def dehydrate_layers_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Layer)
        filter_set = bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'category'

        return super(TopicCategoryResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = TopicCategory.objects.all()
        resource_name = 'categories'
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL,
            'main_category': ALL_WITH_RELATIONS,
        }
        serializer = CountJSONSerializer()

class GroupCategoryResource(TypeFilteredResource):
    detail_url = fields.CharField()
    member_count = fields.IntegerField()
    resource_counts = fields.CharField()

    class Meta:
        queryset = GroupCategory.objects.all()
        allowed_methods = ['get']
        include_resource_uri = False
        filtering = {'slug': ALL,
                     'name': ALL}

    def dehydrate_detail_url(self, bundle):
        return bundle.obj.get_absolute_url()

    def dehydrate_member_count(self, bundle):
        return bundle.obj.groups.all().count()

    def dehydrate(self, bundle):
        """Provide additional resource counts"""

        counts = _get_resource_counts(
            resourcebase_filter_kwargs={
                'group__groupprofile__categories': bundle.obj
            }
        )
        bundle.data.update(resource_counts=counts)
        return bundle


class GroupProfileResource(ModelResource):
    categories = fields.ToManyField(
        GroupCategoryResource,
        'categories',
        full=True
    )
    member_count = fields.CharField()
    manager_count = fields.CharField()
    detail_url = fields.CharField()

    class Meta:
        queryset = GroupProfile.objects.all()
        resource_name = 'group_profile'
        allowed_methods = ['get']
        filtering = {
            'title': ALL,
            'slug': ALL,
            'categories': ALL_WITH_RELATIONS,
        }
        ordering = ['title', 'last_modified']

    def dehydrate_member_count(self, bundle):
        """Provide relative URL to the geonode UI's page on the group"""
        return bundle.obj.member_queryset().count()

    def dehydrate_manager_count(self, bundle):
        """Provide relative URL to the geonode UI's page on the group"""
        return bundle.obj.get_managers().count()

    def dehydrate_detail_url(self, bundle):
        """Return relative URL to the geonode UI's page on the group"""
        return reverse('group_detail', args=[bundle.obj.slug])


class GroupResource(ModelResource):
    group_profile = fields.ToOneField(
        GroupProfileResource,
        'groupprofile',
        full=True,
        null=True,
        blank=True
    )
    resource_counts = fields.CharField()

    class Meta:
        queryset = Group.objects.all()
        resource_name = 'groups'
        allowed_methods = ['get']
        filtering = {
            'name': ALL,
            'group_profile': ALL_WITH_RELATIONS,
        }
        ordering = ['name', 'last_modified']

    def dehydrate(self, bundle):
        """Provide additional resource counts"""

        counts = _get_resource_counts(
            resourcebase_filter_kwargs={'group': bundle.obj})
        bundle.data.update(resource_counts=counts)
        return bundle

    def get_object_list(self, request):
        """
        Overridden in order to exclude the ``anoymous`` group from the list

        """

        qs = super(GroupResource, self).get_object_list(request)
        return qs.exclude(name="anonymous")


class ProfileResource(TypeFilteredResource):
    """Profile api"""
    avatar_100 = fields.CharField(null=True)
    profile_detail_url = fields.CharField()
    email = fields.CharField(default='')
    layers_count = fields.IntegerField(default=0)
    maps_count = fields.IntegerField(default=0)
    documents_count = fields.IntegerField(default=0)
    current_user = fields.BooleanField(default=False)
    activity_stream_url = fields.CharField(null=True)

    def build_filters(self, filters=None, ignore_bad_filters=False):
        """adds filtering by group functionality"""
        if filters is None:
            filters = {}

        orm_filters = super(ProfileResource, self).build_filters(filters)

        if 'group' in filters:
            orm_filters['group'] = filters['group']

        if 'name__icontains' in filters:
            orm_filters['username__icontains'] = filters['name__icontains']
        return orm_filters

    def apply_filters(self, request, applicable_filters):
        """filter by group if applicable by group functionality"""

        group = applicable_filters.pop('group', None)
        name = applicable_filters.pop('name__icontains', None)

        semi_filtered = super(
            ProfileResource,
            self).apply_filters(
            request,
            applicable_filters)

        if group is not None:
            semi_filtered = semi_filtered.filter(
                groupmember__group__slug=group)

        if name is not None:
            semi_filtered = semi_filtered.filter(
                profile__first_name__icontains=name)

        return semi_filtered

    def dehydrate_email(self, bundle):
        email = ''
        if bundle.request.user.is_authenticated():
            email = bundle.obj.email
        return email

    def dehydrate_layers_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Layer)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_maps_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Map)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_documents_count(self, bundle):
        obj_with_perms = get_objects_for_user(bundle.request.user,
                                              'base.view_resourcebase').instance_of(Document)
        return bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id')).distinct().count()

    def dehydrate_avatar_100(self, bundle):
        return avatar_url(bundle.obj, 240)

    def dehydrate_profile_detail_url(self, bundle):
        return bundle.obj.get_absolute_url()

    def dehydrate_current_user(self, bundle):
        return bundle.request.user.username == bundle.obj.username

    def dehydrate_activity_stream_url(self, bundle):
        return reverse(
            'actstream_actor',
            kwargs={
                'content_type_id': ContentType.objects.get_for_model(
                    bundle.obj).pk,
                'object_id': bundle.obj.pk})

    def prepend_urls(self):
        if settings.HAYSTACK_SEARCH:
            return [
                url(r"^(?P<resource_name>%s)/search%s$" % (
                    self._meta.resource_name, trailing_slash()
                ),
                    self.wrap_view('get_search'), name="api_get_search"),
            ]
        else:
            return []

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'owner'

        return super(ProfileResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = get_user_model().objects.exclude(Q(username='AnonymousUser') | Q(is_active=False))
        resource_name = 'profiles'
        allowed_methods = ['get']
        ordering = ['username', 'date_joined']
        excludes = ['is_staff', 'password', 'is_superuser',
                    'is_active', 'last_login']

        filtering = {
            'username': ALL,
        }
        serializer = CountJSONSerializer()


class OwnersResource(TypeFilteredResource):
    """Owners api, lighter and faster version of the profiles api"""
    full_name = fields.CharField(null=True)

    def dehydrate_full_name(self, bundle):
        return bundle.obj.get_full_name() or bundle.obj.username

    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'owner'

        return super(OwnersResource, self).serialize(request, data, format, options)

    class Meta:
        queryset = get_user_model().objects.exclude(username='AnonymousUser')
        resource_name = 'owners'
        allowed_methods = ['get']
        ordering = ['username', 'date_joined']
        excludes = ['is_staff', 'password', 'is_superuser',
                    'is_active', 'last_login']

        filtering = {
            'username': ALL,
        }
        serializer = CountJSONSerializer()


def _get_resource_counts(
        resourcebase_filter_kwargs
):
    """Return a dict with counts of resources of various types

    The ``resourcebase_filter_kwargs`` argument should be a dict with a suitable
    queryset filter that can be applied to select only the relevant
    ``ResourceBase`` objects to use when retrieving counts. For example::

        _get_resource_counts({
            'group__slug': 'my-group',
        })

    The above function call would result in only counting ``ResourceBase``
    objects that belong to the group that has ``my-group`` as slug

    """

    qs = ResourceBase.objects.filter(
        **resourcebase_filter_kwargs
    ).values(
        'polymorphic_ctype__model',
        'is_approved',
        'is_published',
    ).annotate(counts=Count('polymorphic_ctype__model'))
    types = [
        'layer',
        'document',
        'map',
        'all'
    ]
    counts = {}
    for type_ in types:
        counts[type_] = {
            'total': 0,
            'visible': 0,
            'published': 0,
            'approved': 0,
        }
    for record in qs:
        resource_type = record['polymorphic_ctype__model']
        is_visible = all((record['is_approved'], record['is_published']))
        counts['all']['total'] += 1
        counts['all']['visible'] += 1 if is_visible else 0
        counts['all']['published'] += 1 if record['is_published'] else 0
        counts['all']['approved'] += 1 if record['is_approved'] else 0
        section = counts.get(resource_type)
        if section is not None:
            section['total'] += 1
            section['visible'] += 1 if is_visible else 0
            section['published'] += 1 if record['is_published'] else 0
            section['approved'] += 1 if record['is_approved'] else 0
    return counts

class DomainAreaResource(TypeFilteredResource):
    """Domain Area api"""
    
    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'domain_area'

        return super(DomainAreaResource, self).serialize(request, data, format, options)
 
    class Meta:
        queryset = DomainArea.objects.all()
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL,
            'gn_description': ALL
        }
        serializer = CountJSONSerializer()

class DataPortalResource(TypeFilteredResource):
    """Data Portal api"""
    layers_count = fields.IntegerField(default=0)

    def dehydrate_layers_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Layer)
        filter_set = bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()
    
    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'data_portal'

        return super(DataPortalResource, self).serialize(request, data, format, options)
 
    class Meta:
        queryset = DataPortal.objects.all()
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL
        }
        serializer = CountJSONSerializer()

class ValidationLevelResource(TypeFilteredResource):
    """Validation Level api"""

    layers_count = fields.IntegerField(default=0)

    def dehydrate_layers_count(self, bundle):
        request = bundle.request
        obj_with_perms = get_objects_for_user(request.user,
                                              'base.view_resourcebase').instance_of(Layer)
        filter_set = bundle.obj.resourcebase_set.filter(id__in=obj_with_perms.values('id'))

        if not settings.SKIP_PERMS_FILTER:
            filter_set = get_visible_resources(
                filter_set,
                request.user if request else None,
                admin_approval_required=settings.ADMIN_MODERATE_UPLOADS,
                unpublished_not_visible=settings.RESOURCE_PUBLISHING,
                private_groups_not_visibile=settings.GROUP_PRIVATE_RESOURCES)

        return filter_set.distinct().count()
    
    def serialize(self, request, data, format, options=None):
        if options is None:
            options = {}
        options['count_type'] = 'validation_level'

        return super(ValidationLevelResource, self).serialize(request, data, format, options)
 
    class Meta:
        queryset = ValidationLevel.objects.all()
        allowed_methods = ['get']
        filtering = {
            'identifier': ALL
        }
        serializer = CountJSONSerializer()