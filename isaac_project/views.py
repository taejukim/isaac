from django.shortcuts import redirect

def main(request):
    if request.session.get('status'):
        return redirect('project_main')
    else:
        return redirect('login')
