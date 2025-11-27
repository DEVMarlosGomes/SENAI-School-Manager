import os
import sys
import django
import random
from datetime import date

# Configura o ambiente Django para rodar script externo
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "school_manager.settings")
django.setup()

from django.contrib.auth.models import User
from apps.academico.models import (
    Turma, Aluno, Disciplina, Professor, 
    TurmaDisciplinaProfessor, Historico, Curso, Departamento
)

def run():
    print("--- 📊 GERADOR DE DADOS PARA DASHBOARD ---")
    
    # 1. GARANTIR QUE EXISTEM PROFESSORES E DISCIPLINAS BÁSICAS
    # Se sua base estiver zerada, cria o mínimo necessário
    if not Disciplina.objects.exists():
        print("Criando disciplinas padrão...")
        Disciplina.objects.create(cod_disciplina="MAT", nome="Matemática Aplicada", carga_horaria=80)
        Disciplina.objects.create(cod_disciplina="POR", nome="Comunicação Técnica", carga_horaria=60)
        Disciplina.objects.create(cod_disciplina="LOG", nome="Lógica de Programação", carga_horaria=100)
    
    if not Professor.objects.exists():
        print("Criando professor padrão...")
        u = User.objects.create_user("prof_auto", "prof@senai.com", "123")
        dept, _ = Departamento.objects.get_or_create(nome_departamento="Geral", cod_departamento="GERAL")
        Professor.objects.create(user=u, registro_funcional="P001", formacao="Licenciatura", tipo_vinculo="CLT", data_contratacao=date.today(), cod_departamento=dept)

    # 2. RECUPERAR DADOS EXISTENTES
    turmas = list(Turma.objects.all())
    disciplinas = list(Disciplina.objects.all())
    professor = Professor.objects.first() # Pega o primeiro professor para vincular

    if not turmas:
        print("❌ Nenhuma TURMA encontrada. Crie turmas no sistema ou rode o seed completo.")
        return

    print(f"✅ Encontradas {len(turmas)} turmas e {len(disciplinas)} disciplinas.")

    # 3. GERAR HISTÓRICO PARA CADA TURMA
    total_notas = 0
    
    for turma in turmas:
        print(f"Processando turma: {turma.nome}...")
        
        # Busca alunos dessa turma
        alunos = Aluno.objects.filter(turma_atual=turma)
        if not alunos.exists():
            print(f"   ⚠️ Turma {turma.nome} não tem alunos. Pulando.")
            continue

        # Para cada disciplina, garante que existe alocação e lança notas
        for disciplina in disciplinas:
            # Garante vínculo Turma-Disciplina-Professor
            alocacao, created = TurmaDisciplinaProfessor.objects.get_or_create(
                turma=turma,
                disciplina=disciplina,
                defaults={'professor': professor}
            )

            # Lança notas para os alunos
            for aluno in alunos:
                # Simula perfil de aluno variado para o gráfico ficar bonito
                # 20% de chance de ser aluno "Risco", 30% "Médio", 50% "Bom"
                perfil = random.random()
                
                if perfil < 0.2: # Risco (Notas baixas ou faltas)
                    nota = random.uniform(2.0, 5.5)
                    freq = random.uniform(60.0, 80.0)
                    status = "Reprovado"
                elif perfil < 0.5: # Atenção
                    nota = random.uniform(5.0, 7.0)
                    freq = random.uniform(75.0, 85.0)
                    status = "Recuperação" if nota < 6 else "Aprovado"
                else: # Bom
                    nota = random.uniform(7.0, 10.0)
                    freq = random.uniform(85.0, 100.0)
                    status = "Aprovado"

                # Cria ou Atualiza o Histórico
                Historico.objects.update_or_create(
                    id_aluno=aluno,
                    turma_disciplina_professor=alocacao,
                    defaults={
                        'nota_final': round(nota, 1),
                        'media_final': round(nota, 1),
                        'frequencia_percentual': round(freq, 1),
                        'total_faltas': int(80 * (1 - freq/100)),
                        'status_aprovacao': status,
                        'periodo_realizacao': f"{turma.ano_letivo}.1"
                    }
                )
                total_notas += 1

    print(f"\n✨ CONCLUÍDO! {total_notas} registros de histórico gerados/atualizados.")
    print("Agora atualize a página do dashboard para ver os gráficos.")

if __name__ == "__main__":
    run()