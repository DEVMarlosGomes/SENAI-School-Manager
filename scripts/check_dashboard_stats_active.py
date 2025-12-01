import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_manager.settings')
django.setup()

from apps.academico.models import Aluno, Historico
from django.db.models import Avg

# 1) Stats de históricos por aluno (ativos)
stats = list(Historico.objects.filter(id_aluno__status_matricula='Ativo').values('id_aluno').annotate(avg_media=Avg('media_final'), avg_freq=Avg('frequencia_percentual')))
risco = [s for s in stats if ((s['avg_media'] or 0) < 5 or (s['avg_freq'] or 0) < 75)]
print('Alunos com historico (únicos, ativos):', len(stats))
print('Alunos em risco (ativos, criterio atual):', len(risco))
print('Exemplo (primeiros 10):')
print(json.dumps([{'id_aluno': s['id_aluno'], 'avg_media': float(s['avg_media'] or 0), 'avg_freq': float(s['avg_freq'] or 0)} for s in stats[:10]], indent=2, ensure_ascii=False))
