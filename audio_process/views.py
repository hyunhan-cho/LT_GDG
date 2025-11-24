from django.shortcuts import render

def upload_page(request):
    return render(request, 'audio/upload.html')

def detail_page(request, session_id):
    return render(request, 'audio/detail.html', {'session_id': session_id})