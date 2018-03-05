from django.shortcuts import render

def main(request):
    context={'user':request.user}
    return render(request, 'petpen/main.html', context)
