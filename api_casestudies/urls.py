from django.conf.urls import url
from api_casestudies import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # url(r'^list/', views.ListCasestudies.as_view() ),
    url(r'^list/', views.ListCasestudies.as_view() ,  name='api_casestudies_list'),
    url(r'^run/', login_required(views.RunCaseStudies.as_view()) ,  name='api_casestudies_run'),
    url(r'^casestudyrun/', login_required(views.RunCaseStudy.as_view()) ,  name='api_casestudy_run'),
    # url(r'^create/', login_required(views.CreateCaseStudy.as_view()) ,  name='api_casestudy_create'),
    url(r'^clone/', login_required(views.CloneCaseStudy.as_view()) ,  name='api_casestudy_clone'),
    url(r'^edit/', login_required(views.EditCaseStudy.as_view()) ,  name='api_casestudy_edit'),
    url(r'^delete/', login_required(views.DeleteCaseStudy.as_view()) ,  name='api_casestudy_delete'),
    url(r'^delete-layers/', login_required(views.DeleteLayersCaseStudy.as_view()) ,  name='api_casestudy_delete_layers'),
    url(r'^read/(?P<id>[^/]*)/$' , views.ReadCasestudies.as_view(), name='api_casestudies_detail'),
    url(r'^codedlabels/' , views.ListCodedlabels.as_view(), name='api_codedlabels_list'),
    url(r'^inputs/' , login_required(views.ListInputs.as_view()), name='api_inputs_list'),
    url(r'^create_and_upload/' , login_required(views.CreateAndUpload.as_view()), name='api_create_and_upload'),
    url(r'^set_context/' , login_required(views.SetContext.as_view()), name='api_casestudy_set_context'),
    url(r'^create_and_upload_json_matrix/' , login_required(views.CreateAndUploadJsonMatrix.as_view()), name='create_and_upload_json_matrix'),
    #url(r'^upload_input/' , login_required(views.upload_input), name='api_casestudy_upload_input'),
    # url(r'^upload/(?P<id>[^/]*)/$' , views.UploadLayersCasestudies.as_view(), name='api_casestudies_upload'),
]