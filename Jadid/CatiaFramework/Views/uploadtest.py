from django.shortcuts import render, redirect
from django import forms
from django.shortcuts import render, redirect

class FileUploadForm(forms.Form):
    file = forms.FileField()


def upload_file(request):
    template_name = 'CatiaFramework/uploadtest.html'
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return redirect('success')
    else:
        form = FileUploadForm()
    return render(request, template_name, {'form': form})

def handle_uploaded_file(file):
    with open('uploaded_files/' + file.name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)

def upload_success(request):
    return render(request, 'CatiaFramework/uploadtest_success.html')

def request_to_plain_text(request):

    # Convert request properties to plain text    
    request_text = f"Method: {request.method}\n"    
    request_text += f"Path: {request.path}\n"   
    request_text += "Headers:\n"
    for header, value in request.headers.items():
        request_text += f"{header}: {value}\n"
        request_text += f"Body:\n{request.body.decode('utf-8')}\n"
    return request_text