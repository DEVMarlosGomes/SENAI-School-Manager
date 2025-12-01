import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from apps.academico.models import Aluno, Professor, Turma, Historico, Curso
from django.db.models import Avg

# 1) Stats de históricos por aluno
stats = list(Historico.objects.values('id_aluno').annotate(avg_media=Avg('media_final'), avg_freq=Avg('frequencia_percentual')))
risco = [s for s in stats if ((s['avg_media'] or 0) < 5 or (s['avg_freq'] or 0) < 75)]
print('Alunos com historico (únicos):', len(stats))
print('Alunos em risco (criterio atual):', len(risco))
print('Exemplo (primeiros 10):')
print(json.dumps([{'id_aluno': s['id_aluno'], 'avg_media': float(s['avg_media'] or 0), 'avg_freq': float(s['avg_freq'] or 0)} for s in stats[:10]], indent=2, ensure_ascii=False))

# 2) Scatter sample (primeiros 20)
print('\n--- Scatter sample (primeiros 20) ---')
for s in stats[:20]:
    aid = s['id_aluno']
    nome = ''
    try:
        nome = Aluno.objects.get(pk=aid).user.get_full_name()
    except Exception:
        nome = ''
    print(aid, '|', nome, '| media:', round(float(s['avg_media'] or 0),1), '| freq:', round(float(s['avg_freq'] or 0),1))

# 3) Eficiência por curso
print('\n--- Eficiência por Curso ---')
for c in Curso.objects.all().order_by('nome_curso'):
    alunos = Aluno.objects.filter(turma_atual__id_curso=c)
    ids = [a.user.id for a in alunos]
    apro=rec=rep=0
    if ids:
        stats_c = list(Historico.objects.filter(id_aluno__user__id__in=ids).values('id_aluno').annotate(avg_media=Avg('media_final')))
        for st in stats_c:
            m = float(st['avg_media'] or 0)
            if m >= 7.0:
                apro += 1
            elif m >= 5.0:
                rec += 1
            else:
                rep += 1
    print(c.nome_curso, '-> Aprovados:', apro, 'Recuperacao:', rec, 'Reprovados:', rep, '(Alunos no curso:', len(ids), ')')
