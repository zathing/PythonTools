from django.shortcuts import render

# Create your views here.
from threading import Thread
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from upload_app.forms import FileUploadForm
from upload_app.models import FileSimpleModel
from engine import log_api

@login_required
def home(request):
    username = request.user
    if str(username) == 'admin':
        logs = FileSimpleModel.objects.all()
    else:
        logs = FileSimpleModel.objects.filter(file_username=username)
    page = request.GET.get('page', 1)
    # 设置每页显示条数
    paginator = MyPaginator(logs, 10)
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)
    return render(request, 'home.html', {'logs':logs})

@login_required
def upload_7z(request):
    username = request.user
    if request.method == 'POST':
        my_form = FileUploadForm(request.POST, request.FILES)
        if my_form.is_valid():
            file_model = FileSimpleModel()
            file_model.file_name = my_form.cleaned_data['my_file']
            file_model.file_field = my_form.cleaned_data['my_file']
            file_model.file_time = timezone.now()
            file_model.file_username = username
            file_model.save()
            zip_file = str(file_model.file_field)
            t = Thread(target=log_api.deal_log, args=(zip_file,))
            t.start()
            # log_api.deal_log(zip_file)
        return HttpResponseRedirect('/')
    else:
        my_form = FileUploadForm()
    return render(request, 'upload_7z.html', {'username':username, 'form':my_form})

@login_required
def upload_text(request):
    username = request.user
    if request.method == 'POST':
        my_form = FileUploadForm(request.POST, request.FILES)
        if my_form.is_valid():
            file_model = FileSimpleModel()
            file_model.file_name = my_form.cleaned_data['my_file']
            file_model.file_field = my_form.cleaned_data['my_file']
            file_model.file_time = timezone.now()
            file_model.file_username = username
            file_model.save()
        return HttpResponse('Upload Success!')
    else:
        my_form = FileUploadForm()
    return render(request, 'upload_text.html', {'username':username, 'form':my_form})

@login_required
def download(request, report_file):
    response = StreamingHttpResponse(file_iterator(report_file))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format(report_file.split('/')[-1])
    return response

@login_required
def report(request, report_file):
    return render(request, 'report.html')

def handle_uploaded_file(f):
    with open(f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def file_iterator(file_name, chunk_size=512):
    with open(file_name, 'rb') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break

# 重写 Paginator 隐藏过多的页数
class MyPaginator(Paginator):
    # range_num 表示当前页前后各保留多少页，3表示总共显示 1+3+3=7 页
    def __init__(self, object_list, per_page, range_num=3, orphans=0, allow_empty_first_page=True):
        Paginator.__init__(self, object_list, per_page, orphans, allow_empty_first_page)
        self.range_num = range_num
    def page(self, number):
        # 异常处理，避免 /?page=99' 等问题
        try:
            self.page_num = int(number)
            return super(MyPaginator, self).page(number)
        except:
            self.page_num = 1
            return super(MyPaginator, self).page(1)
    def _page_range_ext(self):
        num_count = 2 * self.range_num + 1
        if self.num_pages <= num_count:
            return range(1, self.num_pages + 1)
        num_list = []
        num_list.append(self.page_num)
        for i in range(1, self.range_num + 1):
            if self.page_num - i <= 0:
                num_list.append(num_count + self.page_num - i)
            else:
                num_list.append(self.page_num - i)

            if self.page_num + i <= self.num_pages:
                num_list.append(self.page_num + i)
            else:
                num_list.append(self.page_num + i - num_count)
        num_list.sort()
        return num_list
    page_range_ext = property(_page_range_ext)