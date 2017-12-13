from django.shortcuts import render

def main(request):
    context={}
    return render(request, 'petpen/main.html', context)
