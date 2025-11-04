from django.shortcuts import render, redirect

def cadastro_aluno_view(request):
    # Renderiza o formulário de cadastro de aluno
    return render(request, 'academico/cadastro_aluno.html')

def salvar_aluno_view(request):
    # Lógica para salvar um novo aluno
    if request.method == 'POST':
        # Aqui você integraria a lógica de salvar o aluno
        return redirect('secretaria_dashboard')
    return render(request, 'academico/cadastro_aluno.html')
