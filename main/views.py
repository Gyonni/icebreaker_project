from django.shortcuts import render

def index(request):
    """
    대문 페이지를 렌더링하는 뷰입니다.
    특별한 로직 없이 main/index.html 템플릿을 보여줍니다.
    """
    return render(request, 'main/index.html')
