from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.db import transaction
from faker import Faker
from datetime import date, datetime, timedelta
import random

from apps.academico.models import (
    Endereco,
    Departamento,
    Coordenacao,
    Secretaria,
    Professor,
    Curso,
    Disciplina,
    CursoDisciplina,
    Turma,
    TurmaDisciplinaProfessor,
    Responsavel,
    Telefone,
    Aluno,
    Historico,
    RegistroOcorrencia,
)

from apps.usuarios.models import Profile

class Command(BaseCommand):
    help = 'Popula o banco SQLite do SENAI School Manager com dados dinâmicos e consistentes.'

    def __init__(self):
        super().__init__()
        self.fake = Faker('pt_BR')
        Faker.seed(42)

    def add_arguments(self, parser):
        parser.add_argument(
            '--alunos',
            type=int,
            default=80,
            help='Número de alunos a criar (padrão: 80)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpar banco antes de popular'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        num_alunos = options['alunos']

        self.stdout.write(self.style.WARNING('=' * 70))
        self.stdout.write(self.style.WARNING('🚀 SENAI School Manager - Script de População'))
        self.stdout.write(self.style.WARNING('=' * 70))

        if options['clear']:
            self.limpar_banco()

        self.stdout.write(f'\n📊 Configuração: {num_alunos} alunos\n')

        enderecos = self.criar_enderecos(num_alunos + 70)
        coordenadores = self.criar_coordenadores(enderecos[:3])
        departamentos = self.criar_departamentos(coordenadores)
        secretarias = self.criar_secretarias(enderecos[3:6])
        professores = self.criar_professores(enderecos[6:18], departamentos)
        cursos = self.criar_cursos(departamentos)
        disciplinas = self.criar_disciplinas()
        self.associar_curso_disciplina(cursos, disciplinas)
        turmas = self.criar_turmas(cursos, coordenadores)
        self.associar_turma_disciplina_professor(turmas, disciplinas, professores)
        telefones, responsaveis = self.criar_responsaveis(enderecos[18:68])
        alunos = self.criar_alunos(enderecos[68:68+num_alunos], turmas, responsaveis, num_alunos)
        self.criar_historicos(alunos)
        self.criar_ocorrencias(alunos, professores, coordenadores, turmas)

        self.exibir_resumo()

    def limpar_banco(self):
        self.stdout.write('\n🗑️  Limpando banco de dados...')

        Historico.objects.all().delete()
        RegistroOcorrencia.objects.all().delete()
        Aluno.objects.all().delete()
        TurmaDisciplinaProfessor.objects.all().delete()
        Turma.objects.all().delete()
        CursoDisciplina.objects.all().delete()
        Disciplina.objects.all().delete()
        Curso.objects.all().delete()
        Professor.objects.all().delete()
        Secretaria.objects.all().delete()
        Coordenacao.objects.all().delete()
        Departamento.objects.all().delete()
        Responsavel.objects.all().delete()
        Telefone.objects.all().delete()
        Endereco.objects.all().delete()
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS('  ✓ Banco limpo\n'))

    def criar_enderecos(self, quantidade):
        self.stdout.write(f'📍 Criando {quantidade} endereços...')
        enderecos = []
        complementos = ['', 'Apto 101', 'Apto 202', 'Casa', 'Bloco A', 'Fundos', 'Casa 2']
        for _ in range(quantidade):
            endereco = Endereco.objects.create(
                cep=self.fake.postcode().replace('-', ''),
                logradouro=self.fake.street_name(),
                numero=str(self.fake.building_number()),
                complemento=random.choice(complementos),
                bairro=self.fake.bairro(),
                cidade=self.fake.city(),
                estado=self.fake.estado_sigla()
            )
            enderecos.append(endereco)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(enderecos)} endereços criados'))
        return enderecos

    def criar_coordenadores(self, enderecos):
        self.stdout.write('\n👔 Criando coordenadores...')
        coordenadores_data = [
            ('Carlos', 'Mendes', 'TOTAL', 'Ensino Técnico'),
            ('Regina', 'Santos', 'PEDAGOGICO', 'Metodologias de Ensino'),
            ('José', 'Ferreira', 'ADMINISTRATIVO', 'Gestão Escolar')
        ]
        coordenadores = []
        for i, (nome, sobrenome, nivel, area) in enumerate(coordenadores_data):
            username = f'{nome.lower()}.{sobrenome.lower()}'
            user = User.objects.create(
                username=username,
                first_name=nome,
                last_name=sobrenome,
                email=f'{username}@senai.br',
                password=make_password('coordenador'),
                is_active=True,
                is_staff=True,
                is_superuser=False,
                date_joined=self.fake.date_time_between(start_date='-2y', end_date='now')
            )
            Profile.objects.create(
                user=user,
                tipo='coordenacao',
                telefone=self.fake.phone_number(),
                cpf=f'{i+1:011d}',
                data_nascimento=self.fake.date_of_birth(minimum_age=35, maximum_age=60),
                endereco=f'{enderecos[i].logradouro}, {enderecos[i].numero} - {enderecos[i].cidade}'
            )
            coord = Coordenacao.objects.create(
                user=user,
                registro_administrativo=f'COORD{i+1:03d}',
                nivel_acesso=nivel,
                area_coordenacao=area,
                data_inicio_funcao=self.fake.date_between(start_date='-5y', end_date='-1y'),
                pode_finalizar_boletim=True,
                pode_aprovar_turma=True,
                pode_gerenciar_perfis=True,
                cod_endereco=enderecos[i]
            )
            coordenadores.append(coord)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(coordenadores)} coordenadores criados'))
        return coordenadores

    def criar_departamentos(self, coordenadores):
        self.stdout.write('\n🏢 Criando departamentos...')
        departamentos_data = [
            ('Tecnologia da Informação', 'TI001', coordenadores[0]),
            ('Automação Industrial', 'AUT001', coordenadores[1]),
            ('Mecânica', 'MEC001', coordenadores[2]),
            ('Administração', 'ADM001', coordenadores[0]),
            ('Segurança do Trabalho', 'SEG001', coordenadores[1])
        ]
        departamentos = []
        for nome, codigo, coordenador in departamentos_data:
            dept = Departamento.objects.create(
                nome_departamento=nome,
                cod_departamento=codigo,
                status_ativo=True,
                coordenador=coordenador
            )
            departamentos.append(dept)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(departamentos)} departamentos criados'))
        return departamentos

    def criar_secretarias(self, enderecos):
        self.stdout.write('\n📋 Criando secretárias...')
        secretarias_data = [
            ('Beatriz', 'Lima', 'Secretária Acadêmica'),
            ('Mariana', 'Costa', 'Secretária Administrativa'),
            ('Patricia', 'Oliveira', 'Assistente de Secretaria')
        ]
        secretarias = []
        for i, (nome, sobrenome, cargo) in enumerate(secretarias_data):
            username = f'{nome.lower()}.{sobrenome.lower()}'
            user = User.objects.create(
                username=username,
                first_name=nome,
                last_name=sobrenome,
                email=f'{username}@senai.br',
                password=make_password('secretaria'),
                is_active=True,
                is_staff=True,
                is_superuser=False,
                date_joined=self.fake.date_time_between(start_date='-3y', end_date='now')
            )
            Profile.objects.create(
                user=user,
                tipo='secretaria',
                telefone=self.fake.phone_number(),
                cpf=f'{i+10:011d}',
                data_nascimento=self.fake.date_of_birth(minimum_age=25, maximum_age=50),
                endereco=f'{enderecos[i].logradouro}, {enderecos[i].numero} - {enderecos[i].cidade}'
            )
            sec = Secretaria.objects.create(
                user=user,
                registro_administrativo=f'SEC{i+1:03d}',
                cargo=cargo,
                data_inicio_cargo=self.fake.date_between(start_date='-4y', end_date='-6m'),
                pode_gerenciar_perfis=True,
                pode_acessar_relatorios_financeiros=(cargo == 'Secretária Administrativa'),
                cod_endereco=enderecos[i]
            )
            secretarias.append(sec)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(secretarias)} secretárias criadas'))
        return secretarias

    def criar_professores(self, enderecos, departamentos):
        self.stdout.write('\n👨‍🏫 Criando professores...')
        professores_data = [
            ('Ana', 'Costa', 'Desenvolvimento Web Full Stack'),
            ('Roberto', 'Silva', 'Banco de Dados e BI'),
            ('Fernanda', 'Alves', 'Infraestrutura e Redes'),
            ('Marcos', 'Pereira', 'Automação Industrial'),
            ('Julia', 'Martins', 'Mecatrônica e Robótica'),
            ('Paulo', 'Santos', 'Usinagem CNC'),
            ('Camila', 'Rodrigues', 'Gestão de Projetos'),
            ('Ricardo', 'Oliveira', 'Logística Empresarial'),
            ('Tatiana', 'Souza', 'Segurança do Trabalho'),
            ('Gabriel', 'Lima', 'Programação Python'),
            ('Luciana', 'Ferreira', 'Desenvolvimento Mobile'),
            ('Diego', 'Mendes', 'DevOps e Cloud Computing')
        ]
        professores = []
        for i, (nome, sobrenome, formacao) in enumerate(professores_data):
            username = f'{nome.lower()}.{sobrenome.lower()}'
            user = User.objects.create(
                username=username,
                first_name=nome,
                last_name=sobrenome,
                email=f'{username}@senai.br',
                password=make_password('professor'),
                is_active=True,
                is_staff=False,
                is_superuser=False,
                date_joined=self.fake.date_time_between(start_date='-4y', end_date='-1m')
            )
            Profile.objects.create(
                user=user,
                tipo='professor',
                telefone=self.fake.phone_number(),
                cpf=f'{i+20:011d}',
                data_nascimento=self.fake.date_of_birth(minimum_age=25, maximum_age=55),
                endereco=f'{enderecos[i].logradouro}, {enderecos[i].numero} - {enderecos[i].cidade}'
            )
            prof = Professor.objects.create(
                user=user,
                registro_funcional=f'PROF{i+1:03d}',
                formacao=formacao,
                tipo_vinculo=random.choice(['CLT', 'Terceirizado', 'Temporário']),
                data_contratacao=self.fake.date_between(start_date='-6y', end_date='-1y'),
                status_professor='Ativo',
                is_proponente_turma=random.choice([True, False]),
                etnia=random.choice(['Branco', 'Pardo', 'Preto', 'Amarelo', 'Indígena']),
                estado_civil=random.choice(['Solteiro', 'Casado', 'Divorciado']),
                deficiencia=None,
                cod_departamento=departamentos[i % len(departamentos)],
                cod_endereco=enderecos[i]
            )
            professores.append(prof)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(professores)} professores criados'))
        return professores

    def criar_cursos(self, departamentos):
        self.stdout.write('\n🎓 Criando cursos...')
        cursos_data = [
            ('TADS', 'Técnico em Desenvolvimento de Sistemas', 1600, 'Técnico', 'Manhã', departamentos[0]),
            ('REDES', 'Técnico em Redes de Computadores', 1200, 'Técnico', 'Tarde', departamentos[0]),
            ('AUTO', 'Técnico em Automação Industrial', 1600, 'Técnico', 'Manhã', departamentos[1]),
            ('MECA', 'Técnico em Mecatrônica', 1600, 'Técnico', 'Tarde', departamentos[1]),
            ('LOG', 'Técnico em Logística', 1200, 'Técnico', 'Noite', departamentos[3])
        ]
        cursos = []
        for cod, nome, carga, modalidade, turno, dept in cursos_data:
            curso = Curso.objects.create(
                cod_curso=cod,
                nome_curso=nome,
                descricao=self.fake.text(max_nb_chars=200),
                carga_horaria_total=carga,
                modalidade=modalidade,
                turno=turno,
                tipo='Educação Profissional',
                data_inicio_validade=date(2020, 1, 1),
                credenciamento_ativo=True,
                cod_departamento=dept
            )
            cursos.append(curso)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(cursos)} cursos criados'))
        return cursos

    def criar_disciplinas(self):
        self.stdout.write('\n📚 Criando disciplinas...')
        disciplinas_data = [
            ('DISC001', 'Lógica de Programação', 60, 'Obrigatória'),
            ('DISC002', 'Programação em Python', 80, 'Obrigatória'),
            ('DISC003', 'Desenvolvimento Web Django', 120, 'Obrigatória'),
            ('DISC004', 'Banco de Dados SQL', 100, 'Obrigatória'),
            ('DISC005', 'Programação Orientada a Objetos', 80, 'Obrigatória'),
            ('DISC006', 'Fundamentos de Redes', 60, 'Obrigatória'),
            ('DISC007', 'Administração Linux', 80, 'Obrigatória'),
            ('DISC008', 'Segurança da Informação', 60, 'Obrigatória'),
            ('DISC009', 'Controladores Lógicos', 100, 'Obrigatória'),
            ('DISC010', 'Instrumentação Industrial', 80, 'Obrigatória'),
            ('DISC011', 'Redes Industriais', 60, 'Obrigatória'),
            ('DISC012', 'Eletrônica Analógica', 80, 'Obrigatória'),
            ('DISC013', 'Sistemas Hidráulicos', 60, 'Obrigatória'),
            ('DISC014', 'Robótica Industrial', 100, 'Obrigatória'),
            ('DISC015', 'Gestão de Estoques', 60, 'Obrigatória'),
            ('DISC016', 'Transporte e Distribuição', 60, 'Obrigatória'),
            ('DISC017', 'Supply Chain Management', 80, 'Obrigatória'),
            ('DISC018', 'Inglês Técnico', 40, 'Obrigatória'),
            ('DISC019', 'Segurança do Trabalho', 40, 'Obrigatória'),
            ('DISC020', 'Empreendedorismo', 40, 'Optativa')
        ]
        disciplinas = []
        for cod, nome, carga, status in disciplinas_data:
            disc = Disciplina.objects.create(
                cod_disciplina=cod,
                nome=nome,
                carga_horaria=carga,
                ementa=self.fake.text(max_nb_chars=300),
                creditos=carga // 20,
                status_curricular=status,
                pre_requisito_disciplina=None
            )
            disciplinas.append(disc)
        disciplinas[2].pre_requisito_disciplina = disciplinas[1]
        disciplinas[2].save()
        disciplinas[4].pre_requisito_disciplina = disciplinas[0]
        disciplinas[4].save()
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(disciplinas)} disciplinas criadas'))
        return disciplinas

    def associar_curso_disciplina(self, cursos, disciplinas):
        self.stdout.write('\n🔗 Associando disciplinas aos cursos...')
        associacoes = 0
        curso_indices = [
            [0, 1, 2, 3, 4, 17, 18, 19],  # TADS
            [5, 6, 7, 17, 18, 19],        # Redes
            [8, 9, 10, 17, 18, 19],       # Automação
            [11, 12, 13, 17, 18, 19],     # Mecatrônica
            [14, 15, 16, 17, 18, 19],     # Logística
        ]
        for idx, curso in enumerate(cursos):
            for disc_idx in curso_indices[idx]:
                CursoDisciplina.objects.create(
                    curso=curso,
                    disciplina=disciplinas[disc_idx],
                    periodo_curso=random.randint(1, 4),
                    obrigatoria=True,
                    status_na_matriz='Ativa'
                )
                associacoes += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {associacoes} associações criadas'))

    def criar_turmas(self, cursos, coordenadores):
        self.stdout.write('\n🏫 Criando turmas...')
        turmas = []
        anos = [2024, 2025]
        periodos = ['1° Semestre', '2° Semestre']
        dias_por_mes = {
            1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
            7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
        }
        nomes_utilizados = set()
        for curso in cursos:
            for _ in range(random.randint(1, 2)):
                ano = random.choice(anos)
                tentativas = 0
                while True:
                    tentativas += 1
                    nome_turma = f'{curso.cod_curso} {ano}/{random.choice([1, 2])}'
                    if nome_turma not in nomes_utilizados:
                        nomes_utilizados.add(nome_turma)
                        break
                    if tentativas > 10:
                        raise Exception('Não foi possível gerar nomes únicos de turma!')
                mes_fim = random.choice([6, 12])
                dia_fim = dias_por_mes[mes_fim]
                turma = Turma.objects.create(
                    nome=nome_turma,
                    periodo=random.choice(periodos),
                    ano_letivo=ano,
                    data_inicio=date(ano, random.choice([2, 8]), 1),
                    data_fim=date(ano + 2, mes_fim, dia_fim),
                    capacidade_maxima=40,
                    alunos_matriculados=0,
                    status_aprovacao='Aprovada',
                    coordenacao_aprovacao=random.choice(coordenadores),
                    id_curso=curso
                )
                turmas.append(turma)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(turmas)} turmas criadas'))
        return turmas

    def associar_turma_disciplina_professor(self, turmas, disciplinas, professores):
        self.stdout.write('\n👨‍🏫 Associando professores às turmas...')
        associacoes = 0
        for turma in turmas:
            discs_curso = CursoDisciplina.objects.filter(curso=turma.id_curso)
            for cd in discs_curso:
                professor = random.choice(professores)
                TurmaDisciplinaProfessor.objects.create(
                    turma=turma,
                    disciplina=cd.disciplina,
                    professor=professor,
                    status_alocacao='Ativa'
                )
                associacoes += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {associacoes} associações criadas'))

    def criar_responsaveis(self, enderecos):
        self.stdout.write('\n👨‍👩‍👧 Criando responsáveis e telefones...')
        telefones_lista = []
        responsaveis = []
        parentescos = ['Pai', 'Mãe', 'Avô', 'Avó', 'Tio', 'Tia']
        for i, endereco in enumerate(enderecos):
            telefones_resp = []
            for j in range(random.randint(1, 2)):
                tel = Telefone.objects.create(
                    num_telefone=self.fake.phone_number(),
                    tipo_telefone=random.choice(['Celular', 'Residencial', 'Comercial']),
                    contato_principal=(j == 0)
                )
                telefones_lista.append(tel)
                telefones_resp.append(tel)
            resp = Responsavel.objects.create(
                cpf=f"{i+10000:011d}",
                nome_completo_responsavel=self.fake.name(),
                parentesco=random.choice(parentescos),
                contato_principal=telefones_resp[0].num_telefone if telefones_resp else None,
                responsavel_financeiro=random.choice([True, False]),
                cod_endereco=endereco
            )
            resp.telefones.set(telefones_resp)
            responsaveis.append(resp)
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(responsaveis)} responsáveis e {len(telefones_lista)} telefones'))
        return telefones_lista, responsaveis

    def criar_alunos(self, enderecos, turmas, responsaveis, quantidade):
        self.stdout.write(f'\n🎓 Criando {quantidade} alunos...')
        alunos = []
        for i in range(quantidade):
            try:
                genero = random.choice(['Masculino', 'Feminino'])
                if genero == 'Masculino':
                    nome = self.fake.first_name_male()
                else:
                    nome = self.fake.first_name_female()
                sobrenome = self.fake.last_name()
                data_nasc = self.fake.date_of_birth(minimum_age=16, maximum_age=30)
                turma = random.choice(turmas)
                username = f'aluno{i+1:04d}'
                profile_cpf = f"{i+100000:011d}"
                ra_aluno = f"2025{i+1:04d}"
                rg_aluno = f"99{i+1:07d}"
                user = User.objects.create(
                    username=username,
                    first_name=nome,
                    last_name=sobrenome,
                    email=f'{username}@aluno.senai.br',
                    password=make_password('aluno'),
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    date_joined=self.fake.date_time_between(start_date='-1y', end_date='now')
                )
                Profile.objects.create(
                    user=user,
                    tipo='aluno',
                    telefone=self.fake.phone_number(),
                    cpf=profile_cpf,
                    data_nascimento=data_nasc,
                    endereco=f'{enderecos[i].logradouro}, {enderecos[i].numero} - {enderecos[i].cidade}' if i < len(enderecos) else 'Endereço não informado'
                )
                idade = (date.today() - data_nasc).days // 365
                responsavel = random.choice(responsaveis) if idade < 18 else None
                aluno = Aluno.objects.create(
                    user=user,
                    RA_aluno=ra_aluno,
                    RG_aluno=rg_aluno,
                    data_nascimento=data_nasc,
                    genero=genero,
                    etinia=random.choice(['Branco', 'Pardo', 'Preto', 'Amarelo', 'Indígena']),
                    deficiencia=None,
                    estado_civil=random.choice(['Solteiro', 'Casado']),
                    conclusao_EM=self.fake.date_between(start_date='-3y', end_date='-1m') if idade >= 18 else None,
                    status_matricula=random.choice(['Ativo', 'Ativo', 'Ativo', 'Ativo', 'Trancado']),
                    cod_endereco=enderecos[i] if i < len(enderecos) else enderecos[0],
                    responsavel_legal=responsavel,
                    turma_atual=turma
                )
                alunos.append(aluno)
                turma.alunos_matriculados += 1
                turma.save()
            except Exception as e:
                print(f"Erro ao criar aluno {i+1}: {e}")
                continue
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(alunos)} alunos criados'))
        return alunos

    def criar_historicos(self, alunos):
        self.stdout.write('\n📊 Criando históricos escolares...')
        historicos = 0
        status_options = ['Aprovado', 'Aprovado', 'Aprovado', 'Reprovado', 'Cursando']
        for aluno in alunos:
            if not aluno.turma_atual:
                continue
            alocacoes = TurmaDisciplinaProfessor.objects.filter(
                turma=aluno.turma_atual
            )
            num_disciplinas = min(random.randint(2, 4), alocacoes.count())
            if num_disciplinas == 0:
                continue
            alocacoes_aluno = random.sample(list(alocacoes), num_disciplinas)
            for alocacao in alocacoes_aluno:
                status = random.choice(status_options)
                if status == 'Aprovado':
                    nota = round(random.uniform(6.0, 10.0), 2)
                    freq = round(random.uniform(75.0, 100.0), 2)
                    media = nota
                    faltas = int((100 - freq) * alocacao.disciplina.carga_horaria / 100)
                elif status == 'Reprovado':
                    nota = round(random.uniform(0.0, 5.9), 2)
                    freq = round(random.uniform(40.0, 74.9), 2)
                    media = nota
                    faltas = int((100 - freq) * alocacao.disciplina.carga_horaria / 100)
                else:
                    nota = None
                    media = None
                    freq = round(random.uniform(70.0, 100.0), 2)
                    faltas = int((100 - freq) * alocacao.disciplina.carga_horaria / 100)
                Historico.objects.create(
                    id_aluno=aluno,
                    turma_disciplina_professor=alocacao,
                    nota_final=nota,
                    media_final=media,
                    frequencia_percentual=freq,
                    total_faltas=faltas,
                    status_aprovacao=status,
                    periodo_realizacao=f'{aluno.turma_atual.ano_letivo}/{aluno.turma_atual.periodo}'
                )
                historicos += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {historicos} históricos criados'))

    def criar_ocorrencias(self, alunos, professores, coordenadores, turmas):
        self.stdout.write('\n⚠️  Criando ocorrências...')
        tipos = ['Advertência Verbal', 'Advertência Escrita', 'Suspensão', 'Elogio', 'Atraso']
        status = ['Pendente', 'Em Análise', 'Resolvida']
        num_ocorrencias = int(len(alunos) * 0.15)
        if num_ocorrencias == 0:
            self.stdout.write(self.style.SUCCESS('  ✓ 0 ocorrências criadas'))
            return
        alunos_com_ocorrencia = random.sample(alunos, k=num_ocorrencias)
        ocorrencias = 0
        for aluno in alunos_com_ocorrencia:
            for _ in range(random.randint(1, 2)):
                RegistroOcorrencia.objects.create(
                    aluno=aluno,
                    professor=random.choice(professores),
                    turma=aluno.turma_atual,
                    coordenacao_revisou=random.choice(coordenadores) if random.random() > 0.5 else None,
                    tipo_ocorrencia=random.choice(tipos),
                    descricao=self.fake.text(max_nb_chars=200),
                    status_intervencao=random.choice(status)
                )
                ocorrencias += 1
        self.stdout.write(self.style.SUCCESS(f'  ✓ {ocorrencias} ocorrências criadas'))

    def exibir_resumo(self):
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✅ População concluída com sucesso!'))
        self.stdout.write('=' * 70)
        self.stdout.write('\n📊 Resumo do banco de dados:\n')

        dados = [
            ('Coordenadores', Coordenacao.objects.count()),
            ('Secretárias', Secretaria.objects.count()),
            ('Professores', Professor.objects.count()),
            ('Alunos', Aluno.objects.count()),
            ('Profiles (usuarios)', Profile.objects.count()),
            ('Departamentos', Departamento.objects.count()),
            ('Cursos', Curso.objects.count()),
            ('Disciplinas', Disciplina.objects.count()),
            ('Turmas', Turma.objects.count()),
            ('Responsáveis', Responsavel.objects.count()),
            ('Telefones', Telefone.objects.count()),
            ('Históricos', Historico.objects.count()),
            ('Ocorrências', RegistroOcorrencia.objects.count()),
            ('Endereços', Endereco.objects.count()),
        ]
        for nome, count in dados:
            self.stdout.write(f'  • {nome}: {count}')

        self.stdout.write('\n🔑 Credenciais de acesso:')
        self.stdout.write('  • Coordenador: carlos.mendes / regina.santos / jose.ferreira')
        self.stdout.write('    Senha: coordenador')
        self.stdout.write('\n  • Secretária: beatriz.lima / mariana.costa / patricia.oliveira')
        self.stdout.write('    Senha: secretaria')
        self.stdout.write('\n  • Professor: ana.costa / roberto.silva / fernanda.alves / etc.')
        self.stdout.write('    Senha: professor')
        self.stdout.write('\n  • Aluno: aluno0001 / aluno0002 / aluno0003 / etc.')
        self.stdout.write('    Senha: aluno')
        self.stdout.write('\n' + '=' * 70)
