from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta 
from collections import defaultdict 

app = Flask(__name__)
app.secret_key = "secreto-academia"

# --- BANCO DE DADOS EM MEMÓRIA (COM 5+ DADOS PRÉ-CADASTRADOS) ---

db_alunos = {
    1: {
        "nome_completo": "Ana da Silva",
        "cpf": "111.111.111-11",
        "data_nascimento": "1990-05-15",
        "email": "ana.silva@email.com",
        "telefone": "(35) 91111-1111",
        "endereco": "Rua A, 10"
    },
    2: {
        "nome_completo": "Bruno Costa",
        "cpf": "222.222.222-22",
        "data_nascimento": "1995-10-20",
        "email": "bruno.costa@email.com",
        "telefone": "(35) 92222-2222",
        "endereco": "Rua B, 20"
    },
    3: {
        "nome_completo": "Cássia Torres",
        "cpf": "333.333.333-33",
        "data_nascimento": "1998-01-01",
        "email": "cassia.torres@email.com",
        "telefone": "(35) 93333-3333",
        "endereco": "Av. Principal, 50"
    },
    4: {
        "nome_completo": "Daniel Rocha",
        "cpf": "444.444.444-44",
        "data_nascimento": "2000-03-25",
        "email": "daniel.rocha@email.com",
        "telefone": "(35) 94444-4444",
        "endereco": "Rua C, 15"
    },
    5: {
        "nome_completo": "Erica Lima",
        "cpf": "555.555.555-55",
        "data_nascimento": "1992-11-10",
        "email": "erica.lima@email.com",
        "telefone": "(35) 95555-5555",
        "endereco": "Rua D, 100"
    }
}
next_aluno_id = 6

db_planos = {
    1: {
        "nome_plano": "Plano Mensal",
        "descricao": "Acesso a todas as áreas",
        "valor_mensal": "99.90",
        "duracao_meses": "1",
        "status": "Ativo"
    },
    2: {
        "nome_plano": "Plano Anual",
        "descricao": "Acesso com desconto",
        "valor_mensal": "79.90",
        "duracao_meses": "12",
        "status": "Ativo"
    },
    3: {
        "nome_plano": "Plano Trimestral (Antigo)",
        "descricao": "Não disponível",
        "valor_mensal": "89.90",
        "duracao_meses": "3",
        "status": "Inativo"
    },
    4: {
        "nome_plano": "Plano Semestral",
        "descricao": "Acesso a todas áreas, 6 meses",
        "valor_mensal": "89.00",
        "duracao_meses": "6",
        "status": "Ativo"
    },
    5: {
        "nome_plano": "Plano Trimestral Novo",
        "descricao": "Acesso com desconto, 3 meses",
        "valor_mensal": "95.00",
        "duracao_meses": "3",
        "status": "Ativo"
    }
}
next_plano_id = 6

db_funcionarios = {
    1: {
        "nome": "Carlos Gerente",
        "cpf": "111.111.111-11",
        "cargo": "Gerente",
        "data_admissao": "2020-01-10",
        "salario": "3500.00",
        "contato": "gerente@academia.com"
    },
    2: {
        "nome": "Debora Recepcionista",
        "cpf": "222.222.222-22",
        "cargo": "Recepcionista",
        "data_admissao": "2022-03-15",
        "salario": "1800.00",
        "contato": "(35) 94444-4444"
    },
    3: {
        "nome": "Elias Técnico",
        "cpf": "333.333.333-33",
        "cargo": "Técnico de Manutenção",
        "data_admissao": "2021-08-01",
        "salario": "2200.00",
        "contato": "elias.tec@academia.com"
    },
    4: {
        "nome": "Fernanda Instrutora",
        "cpf": "444.444.444-44",
        "cargo": "Instrutor",
        "data_admissao": "2023-05-20",
        "salario": "2500.00",
        "contato": "fe.inst@academia.com"
    },
    5: {
        "nome": "Gustavo Técnico",
        "cpf": "555.555.555-55",
        "cargo": "Técnico de Manutenção",
        "data_admissao": "2024-01-01",
        "salario": "2300.00",
        "contato": "gustavo.tec@academia.com"
    }
}
next_funcionario_id = 6 

db_matriculas = {
    1: {
        "aluno_id": 1, 
        "plano_id": 2, # Plano Anual (12m) - Ana
        "data_inicio": "2024-01-15",
        "data_termino": "2025-01-15", 
        "status": "Ativa" 
    },
    2: {
        "aluno_id": 2, 
        "plano_id": 1, # Plano Mensal (1m) - Bruno
        "data_inicio": "2024-10-01",
        "data_termino": "2024-11-01", 
        "status": "Inativa" 
    },
    3: {
        "aluno_id": 3, 
        "plano_id": 4, # Plano Semestral (6m) - Cássia
        "data_inicio": "2024-06-01",
        "data_termino": "2024-12-01", 
        "status": "Ativa" 
    },
    4: {
        "aluno_id": 4, 
        "plano_id": 5, # Plano Trimestral Novo (3m) - Daniel
        "data_inicio": "2024-11-01",
        "data_termino": "2025-02-01", 
        "status": "Ativa" 
    },
    5: {
        "aluno_id": 5, 
        "plano_id": 1, # Plano Mensal (1m) - Erica
        "data_inicio": "2024-11-20",
        "data_termino": "2024-12-20", 
        "status": "Ativa" 
    }
}
next_matricula_id = 6

db_aparelhos = {
    1: {
        "nome_aparelho": "Esteira X3000",
        "marca": "RunFast",
        "data_compra": "2023-03-01",
        "status": "Em uso"
    },
    2: {
        "nome_aparelho": "Bicicleta Ergométrica S500",
        "marca": "CycleFit",
        "data_compra": "2024-01-20",
        "status": "Em uso"
    },
    3: {
        "nome_aparelho": "Leg Press 45",
        "marca": "HeavyDuty",
        "data_compra": "2022-06-10",
        "status": "Em manutenção" # Ligado à Manutenção 1 (Em Aberto)
    },
    4: {
        "nome_aparelho": "Máquina de Remada",
        "marca": "ErgoRow",
        "data_compra": "2024-05-01",
        "status": "Em uso"
    },
    5: {
        "nome_aparelho": "Halteres Ajustáveis",
        "marca": "PowerSet",
        "data_compra": "2024-08-15",
        "status": "Em uso"
    }
}
next_aparelho_id = 6

db_manutencoes = {
    1: {
        "aparelho_id": 3, # Leg Press 45
        "funcionario_id": 3, # Elias Técnico
        "data_inicio": "2024-11-20",
        "data_conclusao": "", 
        "descricao_problema": "Ruído na polia principal.",
        "custo": "150.50",
        "criacao_timestamp": datetime.now() - timedelta(days=2) 
    },
    2: {
        "aparelho_id": 1, # Esteira X3000
        "funcionario_id": 5, # Gustavo Técnico
        "data_inicio": "2024-11-25",
        "data_conclusao": "2024-11-25", # Concluído
        "descricao_problema": "Ajuste do sensor de velocidade.",
        "custo": "25.00",
        "criacao_timestamp": datetime.now() - timedelta(minutes=30) 
    },
    3: {
        "aparelho_id": 4, # Máquina de Remada
        "funcionario_id": 3, # Elias Técnico
        "data_inicio": "2024-10-05",
        "data_conclusao": "2024-10-06", 
        "descricao_problema": "Lubrificação geral.",
        "custo": "49.99",
        "criacao_timestamp": datetime.now() - timedelta(days=40) 
    },
    4: {
        "aparelho_id": 5, # Halteres
        "funcionario_id": 5, # Gustavo Técnico
        "data_inicio": "2024-11-10",
        "data_conclusao": "2024-11-10", 
        "descricao_problema": "Limpeza e substituição de peças.",
        "custo": "75.00",
        "criacao_timestamp": datetime.now() - timedelta(days=15) 
    },
    5: {
        "aparelho_id": 2, # Bicicleta Ergométrica
        "funcionario_id": 3, # Elias Técnico
        "data_inicio": "2024-09-01",
        "data_conclusao": "2024-09-02", 
        "descricao_problema": "Troca de pneu.",
        "custo": "120.00",
        "criacao_timestamp": datetime.now() - timedelta(days=80) 
    }
}
next_manutencao_id = 6

# --- ROTA PRINCIPAL (DASHBOARD) ---

@app.route('/')
def index():
    total_alunos = len(db_alunos)
    total_planos_ativos = len([p for p in db_planos.values() if p['status'] == 'Ativo'])
    total_funcionarios = len(db_funcionarios)
    total_matriculas_ativas = len([m for m in db_matriculas.values() if m['status'] == 'Ativa'])
    
    stats = {
        "total_alunos": total_alunos,
        "total_planos_ativos": total_planos_ativos,
        "total_funcionarios": total_funcionarios,
        "total_matriculas_ativas": total_matriculas_ativas
    }
    
    return render_template('crud_template.html', titulo="Início", stats=stats)

# *********************************
# ROTAS ALUNOS (MÓDULO 1)
# *********************************

@app.route('/alunos', methods=['GET', 'POST'])
def crud_alunos():
    global next_aluno_id
    
    campos_form_aluno = [
        {'nome': 'nome_completo', 'label': 'Nome Completo*', 'tipo': 'text', 'placeholder': 'Ex: João da Silva'},
        {'nome': 'cpf', 'label': 'CPF*', 'tipo': 'text', 'placeholder': '111.111.111-11'},
        {'nome': 'data_nascimento', 'label': 'Data de Nascimento', 'tipo': 'date', 'placeholder': ''},
        {'nome': 'email', 'label': 'E-mail*', 'tipo': 'email', 'placeholder': 'joao@email.com'},
        {'nome': 'telefone', 'label': 'Telefone*', 'tipo': 'tel', 'placeholder': '(35) 99999-8888'},
        {'nome': 'endereco', 'label': 'Endereço', 'tipo': 'text', 'placeholder': 'Rua Exemplo, 123'}
    ]
    
    if request.method == 'POST':
        nome = request.form['nome_completo']
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']
        data_nasc = request.form['data_nascimento']
        endereco = request.form['endereco']
        
        if not nome or not cpf or not email or not telefone:
            flash('Erro: Todos os campos com * (Nome, CPF, Email, Telefone) são obrigatórios!', 'error')
            
            campos_preenchidos = [
                {'nome': 'nome_completo', 'label': 'Nome Completo*', 'tipo': 'text', 'placeholder': 'Ex: João da Silva', 'valor': nome},
                {'nome': 'cpf', 'label': 'CPF*', 'tipo': 'text', 'placeholder': '111.111.111-11', 'valor': cpf},
                {'nome': 'data_nascimento', 'label': 'Data de Nascimento', 'tipo': 'date', 'placeholder': '', 'valor': data_nasc},
                {'nome': 'email', 'label': 'E-mail*', 'tipo': 'email', 'placeholder': 'joao@email.com', 'valor': email},
                {'nome': 'telefone', 'label': 'Telefone*', 'tipo': 'tel', 'placeholder': '(35) 99999-8888', 'valor': telefone},
                {'nome': 'endereco', 'label': 'Endereço', 'tipo': 'text', 'placeholder': 'Rua Exemplo, 123', 'valor': endereco}
            ]
            return render_template('crud_template.html', 
                titulo="Alunos", items=db_alunos, form_action=url_for('crud_alunos'),
                campos_formulario=campos_preenchidos)
        
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            flash('Erro: Formato de CPF inválido! Use o padrão 111.222.333-44.', 'error')
            return redirect(url_for('crud_alunos'))
            
        for aluno in db_alunos.values():
            if aluno['cpf'] == cpf:
                flash(f'Erro: O CPF {cpf} já está cadastrado!', 'error')
                return redirect(url_for('crud_alunos'))
        
        novo_aluno = {
            "nome_completo": nome,
            "cpf": cpf,
            "data_nascimento": data_nasc,
            "email": email,
            "telefone": telefone,
            "endereco": endereco
        }
        db_alunos[next_aluno_id] = novo_aluno
        next_aluno_id += 1
        
        flash('Aluno cadastrado com sucesso!', 'success') 
        return redirect(url_for('crud_alunos')) 

    search_nome = request.args.get('search_nome', '')
    search_cpf = request.args.get('search_cpf', '')
    
    alunos_filtrados = db_alunos
    
    if search_nome:
        alunos_filtrados = {id: aluno for id, aluno in alunos_filtrados.items() 
                            if search_nome.lower() in aluno['nome_completo'].lower()}
    
    if search_cpf:
        alunos_filtrados = {id: aluno for id, aluno in alunos_filtrados.items() 
                            if search_cpf in aluno['cpf']}
                            
    return render_template('crud_template.html', 
        titulo="Alunos", 
        items=alunos_filtrados, 
        form_action=url_for('crud_alunos'),
        campos_formulario=campos_form_aluno,
        search_nome_value=search_nome,
        search_cpf_value=search_cpf
    )

@app.route('/alunos/remover/<int:aluno_id>', methods=['POST'])
def remover_aluno(aluno_id):
    # REGRA DE NEGÓCIO [RFS04]: Verificar matrículas
    tem_matricula = False
    for matricula in db_matriculas.values():
        if matricula['aluno_id'] == aluno_id and matricula['status'] == 'Ativa':
            tem_matricula = True
            break
            
    if tem_matricula:
        flash('Erro: Aluno possui uma matrícula ativa e não pode ser removido!', 'error')
    elif aluno_id in db_alunos:
        del db_alunos[aluno_id]
        flash('Aluno removido com sucesso!', 'success')
    else:
        flash('Aluno não encontrado!', 'error')
    return redirect(url_for('crud_alunos'))

@app.route('/alunos/editar/<int:aluno_id>', methods=['GET'])
def editar_aluno_form(aluno_id):
    if aluno_id not in db_alunos:
        flash('Aluno não encontrado!', 'error')
        return redirect(url_for('crud_alunos'))
    
    aluno = db_alunos[aluno_id]
    return render_template('edit_template.html',
        titulo=f"Editando Aluno: {aluno['nome_completo']}",
        item=aluno,
        form_action=url_for('editar_aluno_salvar', aluno_id=aluno_id),
        campos_formulario=[
            {'nome': 'nome_completo', 'label': 'Nome Completo*', 'tipo': 'text', 'valor': aluno['nome_completo']},
            {'nome': 'data_nascimento', 'label': 'Data de Nascimento', 'tipo': 'date', 'valor': aluno['data_nascimento']},
            {'nome': 'email', 'label': 'E-mail*', 'tipo': 'email', 'valor': aluno['email']},
            {'nome': 'telefone', 'label': 'Telefone*', 'tipo': 'tel', 'valor': aluno['telefone']},
            {'nome': 'endereco', 'label': 'Endereço', 'tipo': 'text', 'valor': aluno['endereco']}
        ],
        campos_fixos=[
            {'label': 'CPF (Fixo)', 'valor': aluno['cpf']}
        ],
        cancel_url=url_for('crud_alunos')
    )

@app.route('/alunos/editar/<int:aluno_id>', methods=['POST'])
def editar_aluno_salvar(aluno_id):
    if aluno_id not in db_alunos:
        flash('Aluno não encontrado!', 'error')
        return redirect(url_for('crud_alunos'))
    
    nome = request.form['nome_completo']
    email = request.form['email']
    telefone = request.form['telefone']
    
    if not nome or not email or not telefone:
        flash('Erro: Nome, Email e Telefone são obrigatórios na edição!', 'error')
        return redirect(url_for('editar_aluno_form', aluno_id=aluno_id))

    db_alunos[aluno_id]['nome_completo'] = nome
    db_alunos[aluno_id]['data_nascimento'] = request.form['data_nascimento']
    db_alunos[aluno_id]['email'] = email
    db_alunos[aluno_id]['telefone'] = telefone
    db_alunos[aluno_id]['endereco'] = request.form['endereco']
    
    flash('Aluno atualizado com sucesso!', 'success')
    return redirect(url_for('crud_alunos'))


# *********************************
# ROTAS PLANOS (MÓDULO 2)
# *********************************

@app.route('/planos', methods=['GET', 'POST'])
def crud_planos():
    global next_plano_id
    
    campos_form_plano = [
        {'nome': 'nome_plano', 'label': 'Nome do Plano*', 'tipo': 'text', 'placeholder': 'Ex: Plano Mensal'},
        {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'text', 'placeholder': 'Acesso a todas as áreas'},
        {'nome': 'valor_mensal', 'label': 'Valor Mensal (R$)*', 'tipo': 'text', 'placeholder': 'Ex: 99.90'},
        {'nome': 'duracao_meses', 'label': 'Duração (Meses)*', 'tipo': 'number', 'placeholder': 'Ex: 12'},
        {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativo', 'Inativo']}
    ]
    
    if request.method == 'POST':
        nome = request.form['nome_plano']
        valor = request.form['valor_mensal']
        duracao = request.form['duracao_meses']
        status = request.form['status']
        descricao = request.form['descricao']

        if not nome or not valor or not duracao or not status:
            flash('Erro: Todos os campos com * (Nome, Valor, Duração, Status) são obrigatórios!', 'error')
            
            campos_preenchidos = [
                {'nome': 'nome_plano', 'label': 'Nome do Plano*', 'tipo': 'text', 'placeholder': 'Ex: Plano Mensal', 'valor': nome},
                {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'text', 'placeholder': 'Acesso a todas as áreas', 'valor': descricao},
                {'nome': 'valor_mensal', 'label': 'Valor Mensal (R$)*', 'tipo': 'text', 'placeholder': 'Ex: 99.90', 'valor': valor},
                {'nome': 'duracao_meses', 'label': 'Duração (Meses)*', 'tipo': 'number', 'placeholder': 'Ex: 12', 'valor': duracao},
                {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativo', 'Inativo'], 'selecionado': status}
            ]
            return render_template('crud_template.html', 
                titulo="Planos", items=db_planos, form_action=url_for('crud_planos'),
                campos_formulario=campos_preenchidos)
        
        for plano in db_planos.values():
            if plano['nome_plano'].lower() == nome.lower():
                flash(f'Erro: O plano "{nome}" já está cadastrado!', 'error')
                return redirect(url_for('crud_planos'))

        novo_plano = {
            "nome_plano": nome,
            "descricao": descricao,
            "valor_mensal": valor,
            "duracao_meses": duracao,
            "status": status
        }
        db_planos[next_plano_id] = novo_plano
        next_plano_id += 1
        
        flash('Plano cadastrado com sucesso!', 'success')
        return redirect(url_for('crud_planos'))

    search_nome_plano = request.args.get('search_nome_plano', '')
    search_status = request.args.get('search_status', 'Todos')
    
    planos_filtrados = db_planos
    
    if search_nome_plano:
        planos_filtrados = {id: plano for id, plano in planos_filtrados.items() 
                            if search_nome_plano.lower() in plano['nome_plano'].lower()}
    
    if search_status != 'Todos':
        planos_filtrados = {id: plano for id, plano in planos_filtrados.items() 
                            if plano['status'] == search_status}
                            
    return render_template('crud_template.html', 
        titulo="Planos", 
        items=planos_filtrados, 
        form_action=url_for('crud_planos'),
        campos_formulario=campos_form_plano,
        search_nome_plano_value=search_nome_plano,
        search_status_value=search_status
    )

@app.route('/planos/remover/<int:plano_id>', methods=['POST'])
def remover_plano(plano_id):
    # REGRA DE NEGÓCIO [RFS08]: Verificar matrículas
    tem_matricula = False
    for matricula in db_matriculas.values():
        if matricula['plano_id'] == plano_id:
            tem_matricula = True
            break
            
    if tem_matricula:
        flash('Erro: Plano está associado a matrículas e não pode ser removido! (Inative-o)', 'error')
    elif plano_id in db_planos:
        del db_planos[plano_id]
        flash('Plano removido com sucesso!', 'success')
    else:
        flash('Plano não encontrado!', 'error')
    return redirect(url_for('crud_planos'))

@app.route('/planos/editar/<int:plano_id>', methods=['GET'])
def editar_plano_form(plano_id):
    if plano_id not in db_planos:
        flash('Plano não encontrado!', 'error')
        return redirect(url_for('crud_planos'))
    
    plano = db_planos[plano_id]
    return render_template('edit_template.html',
        titulo=f"Editando Plano: {plano['nome_plano']}",
        item=plano,
        form_action=url_for('editar_plano_salvar', plano_id=plano_id),
        campos_formulario=[
            {'nome': 'nome_plano', 'label': 'Nome do Plano*', 'tipo': 'text', 'valor': plano['nome_plano']},
            {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'text', 'valor': plano['descricao']},
            {'nome': 'valor_mensal', 'label': 'Valor Mensal (R$)*', 'tipo': 'text', 'valor': plano['valor_mensal']},
            {'nome': 'duracao_meses', 'label': 'Duração (Meses)*', 'tipo': 'number', 'valor': plano['duracao_meses']},
            {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativo', 'Inativo'], 'selecionado': plano['status']}
        ],
        campos_fixos=[],
        cancel_url=url_for('crud_planos')
    )

@app.route('/planos/editar/<int:plano_id>', methods=['POST'])
def editar_plano_salvar(plano_id):
    if plano_id not in db_planos:
        flash('Plano não encontrado!', 'error')
        return redirect(url_for('crud_planos'))
    
    nome = request.form['nome_plano']
    valor = request.form['valor_mensal']
    duracao = request.form['duracao_meses']
    
    if not nome or not valor or not duracao:
        flash('Erro: Nome, Valor e Duração são obrigatórios na edição!', 'error')
        return redirect(url_for('editar_plano_form', plano_id=plano_id))
    
    db_planos[plano_id]['nome_plano'] = nome
    db_planos[plano_id]['descricao'] = request.form['descricao']
    db_planos[plano_id]['valor_mensal'] = valor
    db_planos[plano_id]['duracao_meses'] = duracao
    db_planos[plano_id]['status'] = request.form['status']
    
    flash('Plano atualizado com sucesso!', 'success')
    return redirect(url_for('crud_planos'))

# *********************************
# ROTAS FUNCIONÁRIOS (MÓDULO 3)
# *********************************

@app.route('/funcionarios', methods=['GET', 'POST'])
def crud_funcionarios():
    global next_funcionario_id
    
    # [RFS09] Tabela 07
    campos_form_funcionario = [
        {'nome': 'nome', 'label': 'Nome Completo*', 'tipo': 'text', 'placeholder': 'Ex: Carlos Gerente'},
        {'nome': 'cpf', 'label': 'CPF*', 'tipo': 'text', 'placeholder': '333.333.333-33'},
        {'nome': 'cargo', 'label': 'Cargo*', 'tipo': 'select', 'opcoes': ['Recepcionista', 'Instrutor', 'Técnico de Manutenção', 'Gerente']},
        {'nome': 'data_admissao', 'label': 'Data de Admissão', 'tipo': 'date', 'placeholder': ''},
        {'nome': 'salario', 'label': 'Salário (R$)*', 'tipo': 'text', 'placeholder': '1800.00'},
        {'nome': 'contato', 'label': 'Contato (Telefone/Email)*', 'tipo': 'text', 'placeholder': 'Ex: (35) 94444-4444'}
    ]
    
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        cargo = request.form['cargo']
        salario = request.form['salario']
        contato = request.form['contato']
        
        if not nome or not cpf or not cargo or not salario or not contato:
            flash('Erro: Todos os campos com * são obrigatórios!', 'error')
            # Recria o form com dados preenchidos
            campos_preenchidos = [
                {'nome': 'nome', 'label': 'Nome Completo*', 'tipo': 'text', 'placeholder': 'Ex: Carlos Gerente', 'valor': nome},
                {'nome': 'cpf', 'label': 'CPF*', 'tipo': 'text', 'placeholder': '333.333.333-33', 'valor': cpf},
                {'nome': 'cargo', 'label': 'Cargo*', 'tipo': 'select', 'opcoes': ['Recepcionista', 'Instrutor', 'Técnico de Manutenção', 'Gerente'], 'selecionado': cargo},
                {'nome': 'data_admissao', 'label': 'Data de Admissão', 'tipo': 'date', 'valor': request.form['data_admissao']},
                {'nome': 'salario', 'label': 'Salário (R$)*', 'tipo': 'text', 'placeholder': '1800.00', 'valor': salario},
                {'nome': 'contato', 'label': 'Contato (Telefone/Email)*', 'tipo': 'text', 'placeholder': 'Ex: (35) 94444-4444', 'valor': contato}
            ]
            return render_template('crud_template.html', 
                titulo="Funcionários", items=db_funcionarios, form_action=url_for('crud_funcionarios'),
                campos_formulario=campos_preenchidos)
        
        # Validação de CPF (igual ao Aluno)
        for func in db_funcionarios.values():
            if func['cpf'] == cpf:
                flash(f'Erro: O CPF {cpf} já está cadastrado!', 'error')
                return redirect(url_for('crud_funcionarios'))

        novo_funcionario = {
            "nome": nome,
            "cpf": cpf,
            "cargo": cargo,
            "data_admissao": request.form['data_admissao'],
            "salario": salario,
            "contato": contato
        }
        db_funcionarios[next_funcionario_id] = novo_funcionario
        next_funcionario_id += 1
        
        flash('Funcionário cadastrado com sucesso!', 'success')
        return redirect(url_for('crud_funcionarios'))

    # Filtros [RFS10] Tabela 08
    search_nome = request.args.get('search_nome', '')
    search_cpf = request.args.get('search_cpf', '')
    search_cargo = request.args.get('search_cargo', 'Todos')
    
    funcionarios_filtrados = db_funcionarios
    
    if search_nome:
        funcionarios_filtrados = {id: f for id, f in funcionarios_filtrados.items() 
                                  if search_nome.lower() in f['nome'].lower()}
    if search_cpf:
        funcionarios_filtrados = {id: f for id, f in funcionarios_filtrados.items() 
                                  if search_cpf in f['cpf']}
    if search_cargo != 'Todos':
        funcionarios_filtrados = {id: f for id, f in funcionarios_filtrados.items() 
                                  if f['cargo'] == search_cargo}
                            
    return render_template('crud_template.html', 
        titulo="Funcionários", 
        items=funcionarios_filtrados, 
        form_action=url_for('crud_funcionarios'),
        campos_formulario=campos_form_funcionario,
        search_nome_value=search_nome,
        search_cpf_value=search_cpf,
        search_cargo_value=search_cargo
    )

@app.route('/funcionarios/remover/<int:funcionario_id>', methods=['POST'])
def remover_funcionario(funcionario_id):
    # REGRA DE NEGÓCIO [RFS12]: Verificar associações com Manutenções
    tem_manutencao = False
    for manutencao in db_manutencoes.values():
        if manutencao['funcionario_id'] == funcionario_id:
            tem_manutencao = True
            break
            
    if tem_manutencao:
        flash('Erro: Funcionário está associado a registros de manutenção e não pode ser removido!', 'error')
    elif funcionario_id in db_funcionarios:
        del db_funcionarios[funcionario_id]
        flash('Funcionário removido com sucesso!', 'success')
    else:
        flash('Funcionário não encontrado!', 'error')
    return redirect(url_for('crud_funcionarios'))

@app.route('/funcionarios/editar/<int:funcionario_id>', methods=['GET'])
def editar_funcionario_form(funcionario_id):
    if funcionario_id not in db_funcionarios:
        flash('Funcionário não encontrado!', 'error')
        return redirect(url_for('crud_funcionarios'))
    
    func = db_funcionarios[funcionario_id]
    return render_template('edit_template.html',
        titulo=f"Editando Funcionário: {func['nome']}",
        item=func,
        form_action=url_for('editar_funcionario_salvar', funcionario_id=funcionario_id),
        campos_formulario=[ # [RFS11] Tabela 07
            {'nome': 'nome', 'label': 'Nome Completo*', 'tipo': 'text', 'valor': func['nome']},
            {'nome': 'cargo', 'label': 'Cargo*', 'tipo': 'select', 'opcoes': ['Recepcionista', 'Instrutor', 'Técnico de Manutenção', 'Gerente'], 'selecionado': func['cargo']},
            {'nome': 'data_admissao', 'label': 'Data de Admissão', 'tipo': 'date', 'valor': func['data_admissao']},
            {'nome': 'salario', 'label': 'Salário (R$)*', 'tipo': 'text', 'valor': func['salario']},
            {'nome': 'contato', 'label': 'Contato (Telefone/Email)*', 'tipo': 'text', 'valor': func['contato']}
        ],
        campos_fixos=[
            {'label': 'CPF (Fixo)', 'valor': func['cpf']}
        ],
        cancel_url=url_for('crud_funcionarios')
    )

@app.route('/funcionarios/editar/<int:funcionario_id>', methods=['POST'])
def editar_funcionario_salvar(funcionario_id):
    if funcionario_id not in db_funcionarios:
        flash('Funcionário não encontrado!', 'error')
        return redirect(url_for('crud_funcionarios'))
    
    nome = request.form['nome']
    cargo = request.form['cargo']
    salario = request.form['salario']
    contato = request.form['contato']
    
    if not nome or not cargo or not salario or not contato:
        flash('Erro: Todos os campos com * são obrigatórios na edição!', 'error')
        return redirect(url_for('editar_funcionario_form', funcionario_id=funcionario_id))

    db_funcionarios[funcionario_id]['nome'] = nome
    db_funcionarios[funcionario_id]['cargo'] = cargo
    db_funcionarios[funcionario_id]['data_admissao'] = request.form['data_admissao']
    db_funcionarios[funcionario_id]['salario'] = salario
    db_funcionarios[funcionario_id]['contato'] = contato
    
    flash('Funcionário atualizado com sucesso!', 'success')
    return redirect(url_for('crud_funcionarios'))

# *********************************
# ROTAS APARELHOS (MÓDULO 4)
# *********************************

@app.route('/aparelhos', methods=['GET', 'POST'])
def crud_aparelhos():
    global next_aparelho_id
    
    # [RFS13] Tabela 10
    campos_form_aparelho = [
        {'nome': 'nome_aparelho', 'label': 'Nome do Aparelho*', 'tipo': 'text', 'placeholder': 'Ex: Esteira XPTO'},
        {'nome': 'marca', 'label': 'Marca', 'tipo': 'text', 'placeholder': 'Ex: RunFast'},
        {'nome': 'data_compra', 'label': 'Data da Compra', 'tipo': 'date', 'placeholder': ''},
        {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Em uso', 'Em manutenção', 'Fora de serviço']}
    ]
    
    if request.method == 'POST':
        nome = request.form['nome_aparelho']
        status = request.form['status']
        
        if not nome or not status:
            flash('Erro: Nome do Aparelho e Status são obrigatórios!', 'error')
            return redirect(url_for('crud_aparelhos'))

        novo_aparelho = {
            "nome_aparelho": nome,
            "marca": request.form['marca'],
            "data_compra": request.form['data_compra'],
            "status": status
        }
        db_aparelhos[next_aparelho_id] = novo_aparelho
        next_aparelho_id += 1
        
        flash('Aparelho cadastrado com sucesso!', 'success')
        return redirect(url_for('crud_aparelhos'))

    # [RFS14] Filtros
    search_nome = request.args.get('search_nome', '')
    search_status = request.args.get('search_status', 'Todos')
    
    aparelhos_filtrados = db_aparelhos
    
    if search_nome:
        aparelhos_filtrados = {id: a for id, a in aparelhos_filtrados.items() 
                            if search_nome.lower() in a['nome_aparelho'].lower()}
    
    if search_status != 'Todos':
        aparelhos_filtrados = {id: a for id, a in aparelhos_filtrados.items() 
                            if a['status'] == search_status}
                            
    return render_template('crud_template.html', 
        titulo="Aparelhos", 
        items=aparelhos_filtrados, 
        form_action=url_for('crud_aparelhos'),
        campos_formulario=campos_form_aparelho,
        search_nome_value=search_nome,
        search_status_value=search_status
    )

@app.route('/aparelhos/remover/<int:aparelho_id>', methods=['POST'])
def remover_aparelho(aparelho_id):
    # REGRA DE NEGÓCIO [RFS16]: Verificar Manutenções em aberto
    em_manutencao = False
    for manutencao in db_manutencoes.values():
        if manutencao['aparelho_id'] == aparelho_id and manutencao['data_conclusao'] == "":
            em_manutencao = True
            break
            
    if em_manutencao:
        flash('Erro: Aparelho possui manutenção em aberto e não pode ser excluído!', 'error')
    elif aparelho_id in db_aparelhos:
        del db_aparelhos[aparelho_id]
        flash('Aparelho excluído com sucesso (baixa de patrimônio)!', 'success')
    else:
        flash('Aparelho não encontrado!', 'error')
    return redirect(url_for('crud_aparelhos'))

@app.route('/aparelhos/editar/<int:aparelho_id>', methods=['GET'])
def editar_aparelho_form(aparelho_id):
    if aparelho_id not in db_aparelhos:
        flash('Aparelho não encontrado!', 'error')
        return redirect(url_for('crud_aparelhos'))
    
    aparelho = db_aparelhos[aparelho_id]
    return render_template('edit_template.html',
        titulo=f"Editando Aparelho: {aparelho['nome_aparelho']}",
        item=aparelho,
        form_action=url_for('editar_aparelho_salvar', aparelho_id=aparelho_id),
        campos_formulario=[ 
            {'nome': 'nome_aparelho', 'label': 'Nome do Aparelho*', 'tipo': 'text', 'valor': aparelho['nome_aparelho']},
            {'nome': 'marca', 'label': 'Marca', 'tipo': 'text', 'valor': aparelho['marca']},
            {'nome': 'data_compra', 'label': 'Data da Compra', 'tipo': 'date', 'valor': aparelho['data_compra']},
            # O Status só pode ser alterado manualmente com log, ou por RFS21/RFS23.
            {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Em uso', 'Em manutenção', 'Fora de serviço'], 'selecionado': aparelho['status']}
        ],
        campos_fixos=[],
        cancel_url=url_for('crud_aparelhos')
    )

@app.route('/aparelhos/editar/<int:aparelho_id>', methods=['POST'])
def editar_aparelho_salvar(aparelho_id):
    if aparelho_id not in db_aparelhos:
        flash('Aparelho não encontrado!', 'error')
        return redirect(url_for('crud_aparelhos'))
    
    nome = request.form['nome_aparelho']
    status = request.form['status']
    
    if not nome or not status:
        flash('Erro: Nome do Aparelho e Status são obrigatórios na edição!', 'error')
        return redirect(url_for('editar_aparelho_form', aparelho_id=aparelho_id))
    
    db_aparelhos[aparelho_id]['nome_aparelho'] = nome
    db_aparelhos[aparelho_id]['marca'] = request.form['marca']
    db_aparelhos[aparelho_id]['data_compra'] = request.form['data_compra']
    db_aparelhos[aparelho_id]['status'] = status
    
    # [RFS15] O log de alteração manual de status seria implementado aqui.
    
    flash('Aparelho atualizado com sucesso!', 'success')
    return redirect(url_for('crud_aparelhos'))

# *********************************
# ROTAS MANUTENÇÕES (MÓDULO 6)
# *********************************

@app.route('/manutencoes', methods=['GET', 'POST'])
def crud_manutencoes():
    global next_manutencao_id
    
    # REGRA DE NEGÓCIO [RFS21]: Filtra funcionários APENAS para Técnico de Manutenção
    funcionarios_validos = [{'id': id, 'nome': f['nome']} 
                            for id, f in db_funcionarios.items() 
                            if f['cargo'] == 'Técnico de Manutenção'] # ESTREITO PARA APENAS TÉCNICO
                            
    aparelhos_select = [{'id': id, 'nome': a['nome_aparelho']} 
                        for id, a in db_aparelhos.items()]

    # [RFS21] Tabela 16
    campos_form_manutencao = [
        {'nome': 'aparelho_id', 'label': 'Aparelho*', 'tipo': 'select_dinamico', 'opcoes': aparelhos_select},
        {'nome': 'funcionario_id', 'label': 'Funcionário Responsável*', 'tipo': 'select_dinamico', 'opcoes': funcionarios_validos},
        {'nome': 'data_inicio', 'label': 'Data de Início*', 'tipo': 'date'},
        {'nome': 'descricao_problema', 'label': 'Descrição do Problema*', 'tipo': 'text', 'placeholder': 'Ex: Ruído no motor, correia gasta.'},
        {'nome': 'custo', 'label': 'Custo (R$)*', 'tipo': 'text', 'placeholder': 'Ex: 50.00 ou 0.00'},
    ]
    
    if request.method == 'POST':
        aparelho_id = int(request.form['aparelho_id'])
        funcionario_id = int(request.form['funcionario_id'])
        data_inicio = request.form['data_inicio']
        descricao = request.form['descricao_problema']
        custo = request.form['custo']
        
        if not aparelho_id or not funcionario_id or not data_inicio or not descricao or not custo:
            flash('Erro: Todos os campos com * são obrigatórios!', 'error')
            return redirect(url_for('crud_manutencoes'))
            
        # REGRA DE NEGÓCIO [RFS21]: Alterar status do Aparelho para "Em manutenção"
        if aparelho_id in db_aparelhos:
            db_aparelhos[aparelho_id]['status'] = 'Em manutenção'

        nova_manutencao = {
            "aparelho_id": aparelho_id,
            "funcionario_id": funcionario_id,
            "data_inicio": data_inicio,
            "data_conclusao": "", # Inicia em aberto
            "descricao_problema": descricao,
            "custo": custo,
            "criacao_timestamp": datetime.now() # Usado para a regra de exclusão [RFS24]
        }
        db_manutencoes[next_manutencao_id] = nova_manutencao
        next_manutencao_id += 1
        
        flash('Manutenção registrada! Status do aparelho alterado para "Em manutenção".', 'success')
        return redirect(url_for('crud_manutencoes'))

    # [RFS22] Filtros
    search_aparelho_id = request.args.get('search_aparelho_id', '')
    search_funcionario_id = request.args.get('search_funcionario_id', '')
    
    manutencoes_filtradas = db_manutencoes
    
    if search_aparelho_id:
        manutencoes_filtradas = {id: m for id, m in manutencoes_filtradas.items() 
                                 if m['aparelho_id'] == int(search_aparelho_id)}
    if search_funcionario_id:
        manutencoes_filtradas = {id: m for id, m in manutencoes_filtradas.items() 
                                 if m['funcionario_id'] == int(search_funcionario_id)}

    # Enriquecer dados para exibição na tabela
    items_para_template = {}
    for id, manutencao in manutencoes_filtradas.items():
        aparelho_nome = db_aparelhos.get(manutencao['aparelho_id'], {}).get('nome_aparelho', 'APARELHO REMOVIDO')
        funcionario_nome = db_funcionarios.get(manutencao['funcionario_id'], {}).get('nome', 'FUNCIONÁRIO REMOVIDO')
        items_para_template[id] = {
            **manutencao, 
            'aparelho_nome': aparelho_nome,
            'funcionario_nome': funcionario_nome,
            'status': 'Concluída' if manutencao['data_conclusao'] else 'Em Aberto'
        }
                            
    return render_template('crud_template.html', 
        titulo="Manutenções", 
        items=items_para_template, 
        form_action=url_for('crud_manutencoes'),
        campos_formulario=campos_form_manutencao,
        aparelhos_filtro=aparelhos_select,
        funcionarios_filtro=funcionarios_validos,
        search_aparelho_id_value=search_aparelho_id,
        search_funcionario_id_value=search_funcionario_id,
    )

@app.route('/manutencoes/remover/<int:manutencao_id>', methods=['POST'])
def remover_manutencao(manutencao_id):
    # REGRA DE NEGÓCIO [RFS24]: Exclusão só é permitida se criada nas últimas 24 horas
    if manutencao_id not in db_manutencoes:
        flash('Manutenção não encontrada!', 'error')
        return redirect(url_for('crud_manutencoes'))
        
    manutencao = db_manutencoes[manutencao_id]
    tempo_limite = datetime.now() - timedelta(hours=24)

    if manutencao['criacao_timestamp'] < tempo_limite:
        flash('Erro: A exclusão só é permitida para registros criados nas últimas 24 horas.', 'error')
    else:
        # Se excluída, o status do aparelho precisa voltar para 'Em uso', se não houver outra em aberto
        aparelho_id = manutencao['aparelho_id']
        del db_manutencoes[manutencao_id]
        
        # Lógica simplificada: Se o status do aparelho estava 'Em manutenção', presumimos que foi por essa.
        if db_aparelhos.get(aparelho_id, {}).get('status') == 'Em manutenção':
             db_aparelhos[aparelho_id]['status'] = 'Em uso'
        
        flash('Manutenção removida com sucesso! (Dentro do período de 24h)', 'success')
        
    return redirect(url_for('crud_manutencoes'))

@app.route('/manutencoes/editar/<int:manutencao_id>', methods=['GET'])
def editar_manutencao_form(manutencao_id):
    if manutencao_id not in db_manutencoes:
        flash('Manutenção não encontrada!', 'error')
        return redirect(url_for('crud_manutencoes'))
    
    manutencao = db_manutencoes[manutencao_id]
    
    aparelho_nome = db_aparelhos.get(manutencao['aparelho_id'], {}).get('nome_aparelho', 'REMOVIDO')
    funcionario_nome = db_funcionarios.get(manutencao['funcionario_id'], {}).get('nome', 'REMOVIDO')

    return render_template('edit_template.html',
        titulo=f"Editando Manutenção: {aparelho_nome}",
        item=manutencao,
        form_action=url_for('editar_manutencao_salvar', manutencao_id=manutencao_id),
        # [RFS23] Data de Conclusão é o campo chave na edição
        campos_formulario=[
            {'nome': 'data_conclusao', 'label': 'Data de Conclusão', 'tipo': 'date', 'valor': manutencao['data_conclusao']},
            {'nome': 'custo', 'label': 'Custo (R$)*', 'tipo': 'text', 'valor': manutencao['custo']},
            {'nome': 'descricao_problema', 'label': 'Descrição do Problema*', 'tipo': 'text', 'valor': manutencao['descricao_problema']},
        ],
        campos_fixos=[
            {'label': 'Aparelho (Fixo)', 'valor': aparelho_nome},
            {'label': 'Funcionário (Fixo)', 'valor': funcionario_nome},
            {'label': 'Data de Início', 'valor': manutencao['data_inicio']}
        ],
        cancel_url=url_for('crud_manutencoes')
    )

@app.route('/manutencoes/editar/<int:manutencao_id>', methods=['POST'])
def editar_manutencao_salvar(manutencao_id):
    if manutencao_id not in db_manutencoes:
        flash('Manutenção não encontrada!', 'error')
        return redirect(url_for('crud_manutencoes'))
        
    manutencao = db_manutencoes[manutencao_id]
    data_conclusao = request.form['data_conclusao']
    
    if not data_conclusao and manutencao['data_conclusao']:
        flash('Erro: Não é permitido remover a data de conclusão após preenchimento.', 'error')
        return redirect(url_for('editar_manutencao_form', manutencao_id=manutencao_id))

    # Se a data de conclusão foi preenchida ou alterada, atualiza o status do aparelho
    if data_conclusao and data_conclusao != manutencao['data_conclusao']:
        # REGRA DE NEGÓCIO [RFS23]: Alterar Status do Aparelho para "Em uso"
        aparelho_id = manutencao['aparelho_id']
        if aparelho_id in db_aparelhos:
            db_aparelhos[aparelho_id]['status'] = 'Em uso'
            flash(f"Status do aparelho '{db_aparelhos[aparelho_id]['nome_aparelho']}' alterado para 'Em uso'.", 'success')
            
    manutencao['data_conclusao'] = data_conclusao
    manutencao['custo'] = request.form['custo']
    manutencao['descricao_problema'] = request.form['descricao_problema']
    
    flash('Manutenção atualizada com sucesso!', 'success')
    return redirect(url_for('crud_manutencoes'))


# *********************************
# ROTAS MATRÍCULAS (MÓDULO 5)
# *********************************

@app.route('/matriculas', methods=['GET', 'POST'])
def crud_matriculas():
    global next_matricula_id
    
    # [RFS17] Tabela 13 - Campos dinâmicos
    # Precisamos buscar os alunos e planos para os <select>
    alunos_para_select = [{'id': id, 'nome': f"{aluno['nome_completo']} ({aluno['cpf']})"} 
                          for id, aluno in db_alunos.items()]
    planos_para_select = [{'id': id, 'nome': plano['nome_plano']} 
                          for id, plano in db_planos.items() if plano['status'] == 'Ativo']

    campos_form_matricula = [
        {'nome': 'aluno_id', 'label': 'Aluno*', 'tipo': 'select_dinamico', 'opcoes': alunos_para_select},
        {'nome': 'plano_id', 'label': 'Plano*', 'tipo': 'select_dinamico', 'opcoes': planos_para_select},
        {'nome': 'data_inicio', 'label': 'Data de Início*', 'tipo': 'date'},
        {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativa', 'Inativa', 'Cancelada']}
    ]
    
    if request.method == 'POST':
        aluno_id = int(request.form['aluno_id'])
        plano_id = int(request.form['plano_id'])
        data_inicio = request.form['data_inicio']
        status = request.form['status']

        if not aluno_id or not plano_id or not data_inicio or not status:
            flash('Erro: Todos os campos com * são obrigatórios!', 'error')
            # (O ideal era recarregar os campos preenchidos, mas simplificamos aqui)
            return redirect(url_for('crud_matriculas'))

        # REGRA DE NEGÓCIO [RFS17]: "Um aluno não pode ter mais de uma Matrícula com status 'Ativa'"
        if status == 'Ativa':
            for matricula in db_matriculas.values():
                if matricula['aluno_id'] == aluno_id and matricula['status'] == 'Ativa':
                    aluno_nome = db_alunos[aluno_id]['nome_completo']
                    flash(f'Erro: O aluno {aluno_nome} já possui uma matrícula ativa!', 'error')
                    return redirect(url_for('crud_matriculas'))

        # REGRA DE NEGÓCIO [RFS17]: "A Data de Término deve ser calculada"
        try:
            plano = db_planos[plano_id]
            duracao = int(plano['duracao_meses'])
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            data_termino_obj = data_inicio_obj + relativedelta(months=duracao)
            data_termino = data_termino_obj.strftime('%Y-%m-%d')
        except Exception as e:
            flash(f'Erro ao calcular data de término: {e}', 'error')
            return redirect(url_for('crud_matriculas'))

        nova_matricula = {
            "aluno_id": aluno_id,
            "plano_id": plano_id,
            "data_inicio": data_inicio,
            "data_termino": data_termino,
            "status": status
        }
        db_matriculas[next_matricula_id] = nova_matricula
        next_matricula_id += 1
        
        flash('Matrícula cadastrada com sucesso!', 'success')
        return redirect(url_for('crud_matriculas'))

    # [RFS18] Tabela 14 - Filtros
    search_aluno_id = request.args.get('search_aluno_id', '')
    search_plano_id = request.args.get('search_plano_id', '')
    search_status = request.args.get('search_status', 'Todos')
    
    matriculas_filtradas = db_matriculas
    
    if search_aluno_id:
        matriculas_filtradas = {id: m for id, m in matriculas_filtradas.items() 
                                if m['aluno_id'] == int(search_aluno_id)}
    if search_plano_id:
        matriculas_filtradas = {id: m for id, m in matriculas_filtradas.items() 
                                if m['plano_id'] == int(search_plano_id)}
    if search_status != 'Todos':
        matriculas_filtradas = {id: m for id, m in matriculas_filtradas.items() 
                                if m['status'] == search_status}
    
    # Precisamos "enriquecer" os itens com os nomes, para o template exibir
    items_para_template = {}
    for id, matricula in matriculas_filtradas.items():
        aluno_nome = db_alunos.get(matricula['aluno_id'], {}).get('nome_completo', 'ALUNO REMOVIDO')
        plano_nome = db_planos.get(matricula['plano_id'], {}).get('nome_plano', 'PLANO REMOVIDO')
        items_para_template[id] = {
            **matricula, # Copia os campos originais (id, data_inicio, etc)
            'aluno_nome': aluno_nome,
            'plano_nome': plano_nome
        }
                            
    return render_template('crud_template.html', 
        titulo="Matrículas", 
        items=items_para_template, # Passa os itens "enriquecidos"
        form_action=url_for('crud_matriculas'),
        campos_formulario=campos_form_matricula,
        
        # Passa os dados para os filtros
        alunos_filtro=alunos_para_select,
        planos_filtro=planos_para_select,
        search_aluno_id_value=search_aluno_id,
        search_plano_id_value=search_plano_id,
        search_status_value=search_status
    )

@app.route('/matriculas/remover/<int:matricula_id>', methods=['POST'])
def remover_matricula(matricula_id):
    # [RFS20] A DRE pede verificação de 24h. Faremos a remoção simples.
    if matricula_id in db_matriculas:
        del db_matriculas[matricula_id]
        flash('Matrícula removida com sucesso!', 'success')
    else:
        flash('Matrícula não encontrada!', 'error')
    return redirect(url_for('crud_matriculas'))

@app.route('/matriculas/editar/<int:matricula_id>', methods=['GET'])
def editar_matricula_form(matricula_id):
    if matricula_id not in db_matriculas:
        flash('Matrícula não encontrada!', 'error')
        return redirect(url_for('crud_matriculas'))
    
    matricula = db_matriculas[matricula_id]
    
    # Pega os nomes para exibir
    aluno_nome = db_alunos.get(matricula['aluno_id'], {}).get('nome_completo', 'ALUNO REMOVIDO')
    plano_nome = db_planos.get(matricula['plano_id'], {}).get('nome_plano', 'PLANO REMOVIDO')

    return render_template('edit_template.html',
        titulo=f"Editando Matrícula: {aluno_nome}",
        item=matricula,
        form_action=url_for('editar_matricula_salvar', matricula_id=matricula_id),
        # [RFS19] Apenas Status e Datas são editáveis
        campos_formulario=[
            {'nome': 'data_inicio', 'label': 'Data de Início*', 'tipo': 'date', 'valor': matricula['data_inicio']},
            {'nome': 'data_termino', 'label': 'Data de Término (auto)', 'tipo': 'date', 'valor': matricula['data_termino']},
            {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativa', 'Inativa', 'Cancelada'], 'selecionado': matricula['status']}
        ],
        campos_fixos=[
            {'label': 'Aluno (Fixo)', 'valor': aluno_nome},
            {'label': 'Plano (Fixo)', 'valor': plano_nome}
        ],
        cancel_url=url_for('crud_matriculas')
    )

@app.route('/matriculas/editar/<int:matricula_id>', methods=['POST'])
def editar_matricula_salvar(matricula_id):
    if matricula_id not in db_matriculas:
        flash('Matrícula não encontrada!', 'error')
        return redirect(url_for('crud_matriculas'))
    
    matricula_original = db_matriculas[matricula_id]
    data_inicio = request.form['data_inicio']
    status = request.form['status']
    
    if not data_inicio or not status:
        flash('Erro: Data de Início e Status são obrigatórios!', 'error')
        return redirect(url_for('editar_matricula_form', matricula_id=matricula_id))

    # REGRA DE NEGÓCIO [RFS17]: "Um aluno não pode ter mais de uma Matrícula com status 'Ativa'"
    aluno_id = matricula_original['aluno_id']
    if status == 'Ativa':
        for id, matricula in db_matriculas.items():
            # Verifica se outro aluno (que não seja ele mesmo) já tem matricula ativa
            if id != matricula_id and matricula['aluno_id'] == aluno_id and matricula['status'] == 'Ativa':
                aluno_nome = db_alunos[aluno_id]['nome_completo']
                flash(f'Erro: O aluno {aluno_nome} já possui OUTRA matrícula ativa!', 'error')
                return redirect(url_for('editar_matricula_form', matricula_id=matricula_id))

    # REGRA DE NEGÓCIO: Recalcular Data de Término se a Data de Início mudou
    data_termino = matricula_original['data_termino'] # Mantém a original por padrão
    if data_inicio != matricula_original['data_inicio']:
        try:
            plano = db_planos[matricula_original['plano_id']]
            duracao = int(plano['duracao_meses'])
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d')
            data_termino_obj = data_inicio_obj + relativedelta(months=duracao)
            data_termino = data_termino_obj.strftime('%Y-%m-%d')
            flash('Data de término recalculada devido à alteração da data de início.', 'success')
        except Exception as e:
            flash(f'Erro ao recalcular data de término: {e}', 'error')
            return redirect(url_for('editar_matricula_form', matricula_id=matricula_id))
            
    # Salva as alterações
    db_matriculas[matricula_id]['data_inicio'] = data_inicio
    db_matriculas[matricula_id]['data_termino'] = data_termino
    db_matriculas[matricula_id]['status'] = status
    
    flash('Matrícula atualizada com sucesso!', 'success')
    return redirect(url_for('crud_matriculas'))

# *********************************
# ROTAS RELATÓRIOS (MÓDULO 9)
# *********************************

# --- ROTA JSON DE DADOS (USADA PELO JS NO FRONTEND) ---
@app.route('/relatorios/api/alunos_ativos', methods=['GET'])
def relatorio_alunos_ativos_json():
    # [RFS25]
    matriculas_ativas = [m for m in db_matriculas.values() if m['status'] == 'Ativa']
    contagem_por_plano = defaultdict(int)
    for m in matriculas_ativas:
        plano_id = m['plano_id']
        plano_nome = db_planos.get(plano_id, {}).get('nome_plano', 'Plano Desconhecido')
        contagem_por_plano[plano_nome] += 1
        
    labels = list(contagem_por_plano.keys())
    data = list(contagem_por_plano.values())
    
    return jsonify(labels=labels, data=data, tipo_grafico='bar')

@app.route('/relatorios/api/faturamento', methods=['GET'])
def relatorio_faturamento_json():
    # [RFS26]
    faturamento_por_plano = defaultdict(float)
    
    for m in db_matriculas.values():
        plano_id = m['plano_id']
        plano = db_planos.get(plano_id)
        if plano:
            try:
                valor_mensal = float(plano['valor_mensal'])
                duracao = int(plano['duracao_meses'])
                faturamento = valor_mensal * duracao
                plano_nome = plano['nome_plano']
                faturamento_por_plano[plano_nome] += faturamento
            except ValueError:
                pass

    labels = list(faturamento_por_plano.keys())
    data = list(faturamento_por_plano.values())
    
    return jsonify(labels=labels, data=data, tipo_grafico='bar')

@app.route('/relatorios/api/manutencoes', methods=['GET'])
def relatorio_manutencoes_json():
    # [RFS27]
    custos_por_funcionario = defaultdict(lambda: {"Custo Total": 0.0, "Contagem": 0})
    
    for m in db_manutencoes.values():
        funcionario_id = m['funcionario_id']
        funcionario_nome = db_funcionarios.get(funcionario_id, {}).get('nome', 'Funcionário Desconhecido')
        
        try:
            custo = float(m['custo'])
            custos_por_funcionario[funcionario_nome]["Custo Total"] += custo
            custos_por_funcionario[funcionario_nome]["Contagem"] += 1
        except ValueError:
            pass

    labels = list(custos_por_funcionario.keys())
    custos = [data['Custo Total'] for data in custos_por_funcionario.values()]
    contagem = [data['Contagem'] for data in custos_por_funcionario.values()]
    
    return jsonify(labels=labels, custos=custos, contagem=contagem, tipo_grafico='combinado')


@app.route('/relatorios', methods=['GET'])
def relatorios():
    # Estrutura para os links de relatórios
    relatorios_disponiveis = [
        {'id': 'alunos_ativos', 'nome': 'Alunos Ativos por Plano', 'url': url_for('relatorio_alunos_ativos')},
        {'id': 'faturamento', 'nome': 'Faturamento por Plano', 'url': url_for('relatorio_faturamento')},
        {'id': 'manutencoes', 'nome': 'Manutenções e Custos', 'url': url_for('relatorio_manutencoes')},
    ]
    
    return render_template('relatorios_template.html', 
        titulo="Relatórios", 
        relatorios=relatorios_disponiveis
    )

@app.route('/relatorios/alunos_ativos', methods=['GET'])
def relatorio_alunos_ativos():
    # [RFS25]
    
    matriculas_ativas = [m for m in db_matriculas.values() if m['status'] == 'Ativa']
    contagem_por_plano = defaultdict(int)
    for m in matriculas_ativas:
        plano_id = m['plano_id']
        plano_nome = db_planos.get(plano_id, {}).get('nome_plano', 'Plano Desconhecido')
        contagem_por_plano[plano_nome] += 1
        
    dados_tabela = [{"Plano": plano, "Total": count} for plano, count in contagem_por_plano.items()]
    total_geral = len(matriculas_ativas)

    return render_template('relatorio_detalhe.html',
        titulo="Relatório de Alunos Ativos por Plano",
        descricao="Contagem de alunos com matrículas ativas, agrupados por plano (Simulação).",
        tipo_grafico='bar', 
        endpoint_api=url_for('relatorio_alunos_ativos_json'),
        dados=dados_tabela, 
        total_geral=f"Total de Alunos Ativos: {total_geral}"
    )
    
@app.route('/relatorios/faturamento', methods=['GET'])
def relatorio_faturamento():
    # [RFS26]
    
    faturamento_por_plano = defaultdict(float)
    
    for m in db_matriculas.values():
        plano_id = m['plano_id']
        plano = db_planos.get(plano_id)
        if plano:
            try:
                valor_mensal = float(plano['valor_mensal'])
                duracao = int(plano['duracao_meses'])
                faturamento = valor_mensal * duracao
                plano_nome = plano['nome_plano']
                faturamento_por_plano[plano_nome] += faturamento
            except ValueError:
                pass

    dados_tabela = [{"Plano": plano, "Valor Total (R$)": f"R$ {valor:.2f}", "Valor_RAW": valor} 
                     for plano, valor in faturamento_por_plano.items()]
    total_geral = sum(item['Valor_RAW'] for item in dados_tabela)

    return render_template('relatorio_detalhe.html',
        titulo="Relatório de Faturamento (Total Bruto)",
        descricao="Faturamento bruto simulado com base nas matrículas (Valor Mensal * Duração).",
        dados=dados_tabela,
        tipo_grafico='bar', 
        endpoint_api=url_for('relatorio_faturamento_json'),
        total_geral=f"Valor Total Gerado: R$ {total_geral:.2f}"
    )

@app.route('/relatorios/manutencoes', methods=['GET'])
def relatorio_manutencoes():
    # [RFS27]
    
    custos_por_funcionario = defaultdict(lambda: {"Custo Total": 0.0, "Contagem": 0})
    
    for m in db_manutencoes.values():
        funcionario_id = m['funcionario_id']
        funcionario_nome = db_funcionarios.get(funcionario_id, {}).get('nome', 'Funcionário Desconhecido')
        
        try:
            custo = float(m['custo'])
            custos_por_funcionario[funcionario_nome]["Custo Total"] += custo
            custos_por_funcionario[funcionario_nome]["Contagem"] += 1
        except ValueError:
            pass

    dados_tabela = [{"Funcionário": nome, "Custo Total (R$)": f"R$ {data['Custo Total']:.2f}", "Contagem": data['Contagem']} 
                     for nome, data in custos_por_funcionario.items()]
    
    total_geral_custo = sum(float(m['custo']) for m in db_manutencoes.values() if m['custo'])

    return render_template('relatorio_detalhe.html',
        titulo="Relatório de Custos e Frequência de Manutenções",
        descricao="Custo total e número de manutenções agrupadas por Funcionário Responsável.",
        dados=dados_tabela,
        tipo_grafico='combinado', 
        endpoint_api=url_for('relatorio_manutencoes_json'),
        total_geral=f"Custo Total: R$ {total_geral_custo:.2f} | Contagem Total: {len(db_manutencoes)}"
    )

# --- INICIALIZAÇÃO E ARQUIVOS HTML ---

if __name__ == '__main__':
    
    css_global = """
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

        :root {
            --sidebar-bg: #222831;
            --content-bg: #f4f7f6;
            --card-bg: #ffffff;
            --primary-color: #00897b; 
            --text-dark: #333;
            --text-light: #f0f0f0;
            --border-color: #e0e0e0;
        }

        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0; 
            background-color: var(--content-bg);
            color: var(--text-dark);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }
        
        .sidebar {
            width: 260px;
            background-color: var(--sidebar-bg);
            color: var(--text-light);
            padding: 20px;
            height: 100vh;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
        }
        .sidebar-header {
            text-align: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #444;
        }
        .sidebar-header h1 {
            color: #fff;
            font-size: 1.5em;
            margin: 0;
            border: none;
            text-transform: uppercase;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        .sidebar-menu {
            list-style: none;
            padding: 20px 0;
            margin: 0;
            flex-grow: 1;
        }
        .sidebar-menu li a {
            color: var(--text-light);
            text-decoration: none;
            font-weight: 500;
            font-size: 1.1em;
            padding: 15px 10px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: background-color 0.2s, color 0.2s;
        }
        .sidebar-menu li a:hover {
            background-color: var(--primary-color);
            color: #fff;
        }
        .sidebar-menu li a.active {
             background-color: var(--primary-color);
             color: #fff;
        }
        
        .main-content {
            flex: 1;
            height: 100vh;
            overflow-y: auto;
            box-sizing: border-box;
        }
        
        .container {
            max-width: 1100px;
            margin: 20px auto;
            padding: 20px;
        }
        
        /* HIERARQUIA DE TÍTULOS */
        h1 {
            color: var(--text-dark);
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 8px;
            margin-top: 15px;
            margin-bottom: 25px; 
            font-size: 2.0em; 
            font-weight: 700;
            text-transform: none;
        }
        h2 { 
            color: var(--text-dark);
            border-bottom: 1px solid #ddd; 
            padding-bottom: 5px;
            margin-top: 30px; 
            margin-bottom: 20px;
            font-size: 1.5em; 
            font-weight: 500;
            text-transform: none;
        }
        
        form { 
            background: var(--card-bg); 
            padding: 25px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
        }
        
        /* FORM GRID RESPONSIVO */
        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        
        form div { 
            margin-bottom: 10px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500; 
            color: #555;
        }
        
        input[type='text'], input[type='email'], input[type='tel'], input[type='date'], input[type='number'], select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc; 
            border-radius: 4px;
            box-sizing: border-box; 
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus, select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 5px rgba(0,123,255,0.3);
            outline: none;
        }
        
        ::placeholder {
            color: #aaa;
            font-style: italic;
        }
        
        button, .btn {
            background: var(--primary-color); 
            color: white; 
            padding: 12px 20px; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: background-color 0.2s;
            text-decoration: none;
            display: inline-block;
        }
        button:hover, .btn:hover { 
            background: #006a5f; 
        }
        
        .form-filtro {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap; 
            gap: 10px;
            align-items: center;
        }
        .form-filtro input, .form-filtro select {
            width: auto;
            flex-grow: 1; 
            margin-bottom: 0;
        }
        .form-filtro button {
            padding: 12px 15px;
        }
        .form-filtro .btn-cancelar {
            background: #6c757d;
            padding: 12px 15px;
            font-size: 16px;
        }
        
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
            background: var(--card-bg);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-radius: 8px;
            overflow: hidden; 
        }
        th, td { 
            border-bottom: 1px solid var(--border-color); 
            padding: 15px; 
            text-align: left; 
            vertical-align: middle;
        }
        th { 
            background: #f0f0f0; 
            color: var(--text-dark);
            font-weight: 700;
        }
        tr:hover {
            background-color: #f9f9f9;
        }

        /* CLASSES DE ALINHAMENTO DA TABELA */
        th.col-id, td.col-id {
            text-align: center;
            width: 60px; 
        }
        th.col-status, td.col-status {
            text-align: center;
            width: 120px;
        }
        th.col-acoes, td.col-acoes {
            text-align: center;
            width: 180px; 
        }
        
        .acoes { 
            display: flex; 
            gap: 10px; 
            justify-content: center; 
        }
        .btn-editar { 
            background: #ffc107; color: black; padding: 6px 10px; font-size: 14px;
        }
        .btn-editar:hover { background: #e0a800; }
        .btn-remover { 
            background: #dc3545; color: white; padding: 6px 10px; font-size: 14px;
        }
        .btn-remover:hover { background: #c82333; }
        
        .bi {
            vertical-align: middle;
            margin-right: 4px;
        }
        
        .msg-sucesso { 
            background: #d4edda; 
            color: #155724; 
            padding: 15px; 
            border-radius: 4px; 
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }
        
        .msg-erro {
            background: #f8d7da;
            color: #721c24;
            padding: 15px; 
            border-radius: 4px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }
        
        .campo-fixo {
            background: #eee;
            padding: 10px 15px;
            border-radius: 4px;
        }
        .campo-fixo label {
            color: #777;
        }
        .campo-fixo span {
            font-size: 1.1em;
            color: #000;
            font-weight: 500;
        }
        .btn-verde { background: #28a745; }
        .btn-verde:hover { background: #218838; }
        .btn-cancelar {
            background: #6c757d;
            margin-left: 10px;
        }
        .btn-cancelar:hover { background: #5a6268; }
        
        /* STATUS TAGS ATUALIZADAS */
        .status-ativo, .status-inativo, .status-cancelada, .status-em-uso, .status-em-manutencao, .status-fora-de-servico, .status-em-aberto, .status-concluída {
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.85em;
            display: inline-block; 
        }
        .status-ativo, .status-em-uso, .status-concluída {
            background-color: #d4edda;
            color: #155724;
        }
        .status-inativo, .status-fora-de-servico {
            background-color: #f8d7da;
            color: #721c24;
        }
        .status-cancelada, .status-em-manutencao, .status-em-aberto {
            background-color: #ffe599;
            color: #664d03;
        }

        /* CSS do Dashboard */
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .dashboard-card {
            background: var(--card-bg);
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .dashboard-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        }
        .dashboard-card .card-icon {
            font-size: 3em; 
            color: var(--primary-color);
        }
        .dashboard-card .card-info h3 {
            margin: 0;
            font-size: 2.5em; 
            color: var(--text-dark);
            border: none;
            padding: 0;
            margin: 0;
        }
        .dashboard-card .card-info p {
            margin: 0;
            font-size: 1.1em;
            color: #666;
        }
    """

    # --- ARQUIVO HTML: crud_template.html (MODIFICADO) ---
    html_crud_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Academia - {{ titulo }}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        
        <div class="sidebar">
            <div class="sidebar-header">
                <h1><i class="bi bi-barbell"></i> Academia</h1>
            </div>
            <ul class="sidebar-menu">
                <li><a href="/" class="{{ 'active' if titulo == 'Início' else '' }}"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                <li><a href="/alunos" class="{{ 'active' if titulo == 'Alunos' else '' }}"><i class="bi bi-people-fill"></i> Gerenciar Alunos</a></li>
                <li><a href="/planos" class="{{ 'active' if titulo == 'Planos' else '' }}"><i class="bi bi-card-checklist"></i> Gerenciar Planos</a></li>
                <li><a href="/funcionarios" class="{{ 'active' if titulo == 'Funcionários' else '' }}"><i class="bi bi-person-badge"></i> Gerenciar Funcionários</a></li>
                <li><a href="/matriculas" class="{{ 'active' if titulo == 'Matrículas' else '' }}"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
                <li><a href="/aparelhos" class="{{ 'active' if titulo == 'Aparelhos' else '' }}"><i class="bi bi-gear-wide-connected"></i> Gerenciar Aparelhos</a></li>
                <li><a href="/manutencoes" class="{{ 'active' if titulo == 'Manutenções' else '' }}"><i class="bi bi-tools"></i> Gerenciar Manutenções</a></li>
                <li><a href="/relatorios" class="{{ 'active' if titulo == 'Relatórios' else '' }}"><i class="bi bi-bar-chart-line-fill"></i> Relatórios</a></li>
            </ul>
        </div>
        
        <div class="main-content">
            <div class="container">
                
                {% if titulo == 'Início' %}
                    <h1><i class="bi bi-speedometer2"></i> Dashboard</h1>
                    <p>Visão geral do sistema da academia.</p>
                    
                    <div class="dashboard-grid">
                        <div class="dashboard-card">
                            <div class="card-icon"><i class="bi bi-people-fill"></i></div>
                            <div class="card-info">
                                <h3>{{ stats.total_alunos }}</h3>
                                <p>Total de Alunos</p>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <div class="card-icon"><i class="bi bi-journal-check"></i></div>
                            <div class="card-info">
                                <h3>{{ stats.total_matriculas_ativas }}</h3>
                                <p>Matrículas Ativas</p>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <div class="card-icon"><i class="bi bi-card-checklist"></i></div>
                            <div class="card-info">
                                <h3>{{ stats.total_planos_ativos }}</h3>
                                <p>Planos Ativos</p>
                            </div>
                        </div>
                        <div class="dashboard-card">
                            <div class="card-icon"><i class="bi bi-person-badge"></i></div>
                            <div class="card-info">
                                <h3>{{ stats.total_funcionarios }}</h3>
                                <p>Total de Funcionários</p>
                            </div>
                        </div>
                    </div>
                
                {% else %}
                    <h1>{{ titulo }}</h1> 
                    
                    {% with messages = get_flashed_messages(with_categories=true) %}
                        {% if messages %}
                            {% for category, message in messages %}
                                {% if category == 'error' %}
                                    <div class="msg-erro" id="id-mensagem-erro">
                                        {{ message }}
                                    </div>
                                {% else %}
                                    <div class="msg-sucesso" id="id-mensagem-sucesso">
                                        {{ message }}
                                    </div>
                                {% endif %}
                            {% endfor %}
                        {% endif %}
                    {% endwith %}

                    <h2><i class="bi bi-plus-circle-fill"></i> Cadastrar Novo 
                        {% if titulo == 'Alunos' %} Aluno
                        {% elif titulo == 'Planos' %} Plano
                        {% elif titulo == 'Funcionários' %} Funcionário
                        {% elif titulo == 'Aparelhos' %} Aparelho
                        {% elif titulo == 'Manutenções' %} Manutenção
                        {% elif titulo == 'Matrículas' %} Matrícula
                        {% endif %}
                    </h2>
                    
                    <form action="{{ form_action }}" method="POST">
                        <div class="form-grid">
                            {% for campo in campos_formulario %}
                            <div>
                                <label for="id-{{ campo.nome }}">{{ campo.label }}</label>
                                
                                {% if campo.tipo == 'select' %}
                                    <select name="{{ campo.nome }}" id="id-{{ campo.nome }}">
                                        {% for op in campo.opcoes %}
                                        <option value="{{ op }}" {% if op == campo.get('selecionado') %}selected{% endif %}>{{ op }}</option>
                                        {% endfor %}
                                    </select>
                                
                                {% elif campo.tipo == 'select_dinamico' %}
                                    <select name="{{ campo.nome }}" id="id-{{ campo.nome }}">
                                        <option value="">Selecione...</option>
                                        {% for op in campo.opcoes %}
                                        <option value="{{ op.id }}" {% if op.id|string == campo.get('valor') %}selected{% endif %}>{{ op.nome }}</option>
                                        {% endfor %}
                                    </select>
                                
                                {% else %}
                                    <input type="{{ campo.tipo }}" name="{{ campo.nome }}" id="id-{{ campo.nome }}" 
                                           value="{{ campo.get('valor', '') }}" 
                                           placeholder="{{ campo.get('placeholder', '') }}">
                                {% endif %}
                            </div>
                            {% endfor %}
                        </div>
                        <button type="submit" id="id-botao-salvar" style="margin-top: 20px;">
                            <i class="bi bi-check-lg"></i> Salvar
                        </button>
                    </form>

                    <h2><i class="bi bi-list-task"></i> Consultar {{ titulo }}</h2>
                    
                    {% if titulo == "Alunos" %}
                    <form action="{{ url_for('crud_alunos') }}" method="GET" class="form-filtro">
                        <input type="text" name="search_nome" placeholder="Filtrar por Nome..." value="{{ search_nome_value | default('') }}">
                        <input type="text" name="search_cpf" placeholder="Filtrar por CPF..." value="{{ search_cpf_value | default('') }}">
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_alunos') }}" class="btn btn-cancelar">Limpar</a>
                    </form>
                    
                    {% elif titulo == "Planos" %}
                    <form action="{{ url_for('crud_planos') }}" method="GET" class="form-filtro">
                        <input type="text" name="search_nome_plano" placeholder="Filtrar por Nome do Plano..." value="{{ search_nome_plano_value | default('') }}">
                        <select name="search_status">
                            <option value="Todos" {% if search_status_value == 'Todos' %}selected{% endif %}>Todos os Status</option>
                            <option value="Ativo" {% if search_status_value == 'Ativo' %}selected{% endif %}>Ativo</option>
                            <option value="Inativo" {% if search_status_value == 'Inativo' %}selected{% endif %}>Inativo</option>
                        </select>
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_planos') }}" class="btn btn-cancelar">Limpar</a>
                    </form>
                    
                    {% elif titulo == "Funcionários" %}
                    <form action="{{ url_for('crud_funcionarios') }}" method="GET" class="form-filtro">
                        <input type="text" name="search_nome" placeholder="Filtrar por Nome..." value="{{ search_nome_value | default('') }}">
                        <input type="text" name="search_cpf" placeholder="Filtrar por CPF..." value="{{ search_cpf_value | default('') }}">
                        <select name="search_cargo">
                            <option value="Todos" {% if search_cargo_value == 'Todos' %}selected{% endif %}>Todos os Cargos</option>
                            <option value="Recepcionista" {% if search_cargo_value == 'Recepcionista' %}selected{% endif %}>Recepcionista</option>
                            <option value="Instrutor" {% if search_cargo_value == 'Instrutor' %}selected{% endif %}>Instrutor</option>
                            <option value="Técnico de Manutenção" {% if search_cargo_value == 'Técnico de Manutenção' %}selected{% endif %}>Técnico de Manutenção</option>
                            <option value="Gerente" {% if search_cargo_value == 'Gerente' %}selected{% endif %}>Gerente</option>
                        </select>
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_funcionarios') }}" class="btn btn-cancelar">Limpar</a>
                    </form>
                    
                    {% elif titulo == "Aparelhos" %}
                    <form action="{{ url_for('crud_aparelhos') }}" method="GET" class="form-filtro">
                        <input type="text" name="search_nome" placeholder="Filtrar por Nome..." value="{{ search_nome_value | default('') }}">
                        <select name="search_status">
                            <option value="Todos" {% if search_status_value == 'Todos' %}selected{% endif %}>Todos os Status</option>
                            <option value="Em uso" {% if search_status_value == 'Em uso' %}selected{% endif %}>Em uso</option>
                            <option value="Em manutenção" {% if search_status_value == 'Em manutenção' %}selected{% endif %}>Em manutenção</option>
                            <option value="Fora de serviço" {% if search_status_value == 'Fora de serviço' %}selected{% endif %}>Fora de serviço</option>
                        </select>
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_aparelhos') }}" class="btn btn-cancelar">Limpar</a>
                    </form>
                    
                    {% elif titulo == "Manutenções" %}
                    <form action="{{ url_for('crud_manutencoes') }}" method="GET" class="form-filtro">
                        <select name="search_aparelho_id">
                            <option value="">Todos os Aparelhos</option>
                            {% for aparelho in aparelhos_filtro %}
                            <option value="{{ aparelho.id }}" {% if aparelho.id|string == search_aparelho_id_value %}selected{% endif %}>{{ aparelho.nome }}</option>
                            {% endfor %}
                        </select>
                        <select name="search_funcionario_id">
                            <option value="">Todos os Técnicos</option>
                            {% for func in funcionarios_filtro %}
                            <option value="{{ func.id }}" {% if func.id|string == search_funcionario_id_value %}selected{% endif %}>{{ func.nome }}</option>
                            {% endfor %}
                        </select>
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_manutencoes') }}" class="btn btn-cancelar">Limpar</a>
                    </form>

                    {% elif titulo == "Matrículas" %}
                    <form action="{{ url_for('crud_matriculas') }}" method="GET" class="form-filtro">
                        <select name="search_aluno_id">
                            <option value="">Todos os Alunos</option>
                            {% for aluno in alunos_filtro %}
                            <option value="{{ aluno.id }}" {% if aluno.id|string == search_aluno_id_value %}selected{% endif %}>{{ aluno.nome }}</option>
                            {% endfor %}
                        </select>
                        <select name="search_plano_id">
                            <option value="">Todos os Planos</option>
                            {% for plano in planos_filtro %}
                            <option value="{{ plano.id }}" {% if plano.id|string == search_plano_id_value %}selected{% endif %}>{{ plano.nome }}</option>
                            {% endfor %}
                        </select>
                        <select name="search_status">
                            <option value="Todos" {% if search_status_value == 'Todos' %}selected{% endif %}>Todos os Status</option>
                            <option value="Ativa" {% if search_status_value == 'Ativa' %}selected{% endif %}>Ativa</option>
                            <option value="Inativa" {% if search_status_value == 'Inativa' %}selected{% endif %}>Inativa</option>
                            <option value="Cancelada" {% if search_status_value == 'Cancelada' %}selected{% endif %}>Cancelada</option>
                        </select>
                        <button type="submit">Buscar</button>
                        <a href="{{ url_for('crud_matriculas') }}" class="btn btn-cancelar">Limpar</a>
                    </form>
                    {% elif titulo == "Relatórios" %}
                        <p>Selecione um relatório:</p>
                        <ul>
                        {% for rel in relatorios %}
                            <li><a href="{{ rel.url }}" class="btn" style="margin: 5px 0;"><i class="bi bi-eye-fill"></i> Visualizar {{ rel.nome }}</a></li>
                        {% endfor %}
                        </ul>
                    {% endif %}
                    
                    
                    {% if titulo != "Relatórios" %}
                    <table id="id-tabela-resultados">
                        <thead>
                            <tr>
                                {% if titulo == "Alunos" %}
                                    <th class="col-id">ID</th>
                                    <th>Nome</th>
                                    <th>CPF</th>
                                    <th>Email</th>
                                    <th>Telefone</th>
                                {% elif titulo == "Planos" %}
                                    <th class="col-id">ID</th>
                                    <th>Plano</th>
                                    <th>Valor (R$)</th>
                                    <th>Duração (Meses)</th>
                                    <th class="col-status">Status</th>
                                {% elif titulo == "Funcionários" %}
                                    <th class="col-id">ID</th>
                                    <th>Nome</th>
                                    <th>CPF</th>
                                    <th>Cargo</th>
                                    <th>Contato</th>
                                {% elif titulo == "Aparelhos" %}
                                    <th class="col-id">ID</th>
                                    <th>Aparelho</th>
                                    <th>Marca</th>
                                    <th class="col-status">Status</th>
                                {% elif titulo == "Manutenções" %}
                                    <th class="col-id">ID</th>
                                    <th>Aparelho</th>
                                    <th>Técnico</th>
                                    <th>Início</th>
                                    <th>Término</th>
                                    <th class="col-status">Status</th>
                                {% elif titulo == "Matrículas" %}
                                    <th class="col-id">ID</th>
                                    <th>Aluno</th>
                                    <th>Plano</th>
                                    <th>Início</th>
                                    <th>Término</th>
                                    <th class="col-status">Status</th>
                                {% endif %}
                                <th class="col-acoes">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for id, item in items.items() %}
                            <tr>
                                {% if titulo == "Alunos" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['nome_completo'] }}</td>
                                    <td>{{ item['cpf'] }}</td>
                                    <td>{{ item['email'] }}</td>
                                    <td>{{ item['telefone'] }}</td>
                                
                                {% elif titulo == "Planos" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['nome_plano'] }}</td>
                                    <td>{{ item['valor_mensal'] }}</td>
                                    <td>{{ item['duracao_meses'] }}</td>
                                    <td class="col-status"><span class="status-{{ item['status']|lower }}">{{ item['status'] }}</span></td>
                                
                                {% elif titulo == "Funcionários" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['nome'] }}</td>
                                    <td>{{ item['cpf'] }}</td>
                                    <td>{{ item['cargo'] }}</td>
                                    <td>{{ item['contato'] }}</td>
                                    
                                {% elif titulo == "Aparelhos" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['nome_aparelho'] }}</td>
                                    <td>{{ item['marca'] }}</td>
                                    <td class="col-status"><span class="status-{{ item['status']|lower|replace(' ', '-') }}">{{ item['status'] }}</span></td>
                                    
                                {% elif titulo == "Manutenções" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['aparelho_nome'] }}</td>
                                    <td>{{ item['funcionario_nome'] }}</td>
                                    <td>{{ item['data_inicio'] }}</td>
                                    <td>{{ item['data_conclusao'] if item['data_conclusao'] else 'Em Aberto' }}</td>
                                    <td class="col-status"><span class="status-{{ item['status']|lower|replace(' ', '-') }}">{{ item['status'] }}</span></td>

                                {% elif titulo == "Matrículas" %}
                                    <td class="col-id">{{ id }}</td>
                                    <td>{{ item['aluno_nome'] }}</td>
                                    <td>{{ item['plano_nome'] }}</td>
                                    <td>{{ item['data_inicio'] }}</td>
                                    <td>{{ item['data_termino'] }}</td>
                                    <td class="col-status"><span class="status-{{ item['status']|lower }}">{{ item['status'] }}</span></td>
                                {% endif %}
                                
                                <td class="col-acoes acoes">
                                    {% if titulo == "Alunos" %}
                                        <a href="/alunos/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Editar
                                        </a>
                                        <form action="/alunos/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% elif titulo == "Planos" %}
                                        <a href="/planos/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Editar
                                        </a>
                                        <form action="/planos/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% elif titulo == "Funcionários" %}
                                        <a href="/funcionarios/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Editar
                                        </a>
                                        <form action="/funcionarios/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% elif titulo == "Aparelhos" %}
                                        <a href="/aparelhos/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Editar
                                        </a>
                                        <form action="/aparelhos/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% elif titulo == "Manutenções" %}
                                        <a href="/manutencoes/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Concluir/Editar
                                        </a>
                                        <form action="/manutencoes/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% elif titulo == "Matrículas" %}
                                        <a href="/matriculas/editar/{{ id }}" class="btn btn-editar" id="id-btn-editar-{{ id }}">
                                            <i class="bi bi-pencil-fill"></i> Editar
                                        </a>
                                        <form action="/matriculas/remover/{{ id }}" method="POST" style="margin:0;">
                                            <button type="submit" class="btn btn-remover" id="id-btn-remover-{{ id }}">
                                                <i class="bi bi-trash-fill"></i> Remover
                                            </button>
                                        </form>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                    {% endif %}
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """

    # --- ARQUIVO HTML: edit_template.html (MODIFICADO) ---
    html_edit_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>{{ titulo }}</title>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h1><i class="bi bi-barbell"></i> Academia</h1>
            </div>
            <ul class="sidebar-menu">
                <li><a href="/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                <li><a href="/alunos" class="{{ 'active' if 'Aluno' in titulo else '' }}"><i class="bi bi-people-fill"></i> Gerenciar Alunos</a></li>
                <li><a href="/planos" class="{{ 'active' if 'Plano' in titulo else '' }}"><i class="bi bi-card-checklist"></i> Gerenciar Planos</a></li>
                <li><a href="/funcionarios" class="{{ 'active' if 'Funcionário' in titulo else '' }}"><i class="bi bi-person-badge"></i> Gerenciar Funcionários</a></li>
                <li><a href="/aparelhos" class="{{ 'active' if 'Aparelho' in titulo else '' }}"><i class="bi bi-gear-wide-connected"></i> Gerenciar Aparelhos</a></li>
                <li><a href="/manutencoes" class="{{ 'active' if 'Manutenção' in titulo else '' }}"><i class="bi bi-tools"></i> Gerenciar Manutenções</a></li>
                <li><a href="/matriculas" class="{{ 'active' if 'Matrícula' in titulo else '' }}"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
                <li><a href="/relatorios"><i class="bi bi-bar-chart-line-fill"></i> Relatórios</a></li>
            </ul>
        </div>
        
        <div class="main-content">
            <div class="container">
                <h1><i class="bi bi-pencil-square"></i> {{ titulo }}</h1>
                
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            {% if category == 'error' %}
                                <div class="msg-erro" id="id-mensagem-erro">
                                    {{ message }}
                                </div>
                            {% else %}
                                <div class="msg-sucesso" id="id-mensagem-sucesso">
                                    {{ message }}
                                </div>
                            {% endif %}
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                
                <form action="{{ form_action }}" method="POST">
                    
                    {% for campo in campos_fixos %}
                    <div class="campo-fixo" style="margin-bottom: 20px;">
                        <label>{{ campo.label }}</label>
                        <span>{{ campo.valor }}</span>
                    </div>
                    {% endfor %}

                    <div class="form-grid">
                        {% for campo in campos_formulario %}
                        <div>
                            <label for="id-{{ campo.nome }}">{{ campo.label }}</label>
                            
                            {% if campo.tipo == 'select' %}
                                <select name="{{ campo.nome }}" id="id-{{ campo.nome }}">
                                    {% for op in campo.opcoes %}
                                    <option value="{{ op }}" 
                                        {% if 'selecionado' in campo and op == campo.selecionado %}selected{% endif %}>
                                        {{ op }}
                                    </option>
                                    {% endfor %}
                                </select>
                            
                            {% elif campo.tipo == 'select_dinamico' %}
                                <select name="{{ campo.nome }}" id="id-{{ campo.nome }}">
                                    <option value="">Selecione...</option>
                                    {% for op in campo.opcoes %}
                                    <option value="{{ op.id }}" {% if op.id|string == campo.get('valor') %}selected{% endif %}>{{ op.nome }}</option>
                                    {% endfor %}
                                </select>
                                
                            {% else %}
                                <input type="{{ campo.tipo }}" name="{{ campo.nome }}" id="id-{{ campo.nome }}" 
                                       value="{{ campo.get('valor', '') }}"
                                       placeholder="{{ campo.get('placeholder', '') }}">
                            {% endif %}
                        </div>
                        {% endfor %}
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <button type="submit" id="id-botao-salvar-edicao" class="btn-verde">
                            <i class="bi bi-check-lg"></i> Salvar Edição
                        </button>
                        <a href="{{ cancel_url }}" class="btn btn-cancelar">
                            Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </body>
    </html>
    """

    # --- ARQUIVO HTML: relatorios_template.html (NOVO) ---
    html_relatorios_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Academia - {{ titulo }}</title>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h1><i class="bi bi-barbell"></i> Academia</h1>
            </div>
            <ul class="sidebar-menu">
                <li><a href="/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                <li><a href="/alunos"><i class="bi bi-people-fill"></i> Gerenciar Alunos</a></li>
                <li><a href="/planos"><i class="bi bi-card-checklist"></i> Gerenciar Planos</a></li>
                <li><a href="/funcionarios"><i class="bi bi-person-badge"></i> Gerenciar Funcionários</a></li>
                <li><a href="/aparelhos"><i class="bi bi-gear-wide-connected"></i> Gerenciar Aparelhos</a></li>
                <li><a href="/manutencoes"><i class="bi bi-tools"></i> Gerenciar Manutenções</a></li>
                <li><a href="/matriculas"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
                <li><a href="/relatorios" class="active"><i class="bi bi-bar-chart-line-fill"></i> Relatórios</a></li>
            </ul>
        </div>
        
        <div class="main-content">
            <div class="container">
                <h1><i class="bi bi-bar-chart-line-fill"></i> {{ titulo }}</h1>
                
                <h2>Relatórios de Gestão</h2>
                <div class="dashboard-grid">
                    {% for rel in relatorios %}
                    <div class="dashboard-card" style="display: block;">
                        <div class="card-info">
                            <h3 style="font-size: 1.5em; margin-bottom: 10px;">{{ rel.nome }}</h3>
                            <a href="{{ rel.url }}" class="btn" style="padding: 8px 15px; font-size: 0.9em; text-align: center;">
                                <i class="bi bi-eye-fill"></i> Visualizar
                            </a>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # --- ARQUIVO HTML: relatorio_detalhe.html (NOVO) ---
    html_relatorio_detalhe = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>Relatório - {{ titulo }}</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        <div class="sidebar">
            <div class="sidebar-header">
                <h1><i class="bi bi-barbell"></i> Academia</h1>
            </div>
            <ul class="sidebar-menu">
                <li><a href="/"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                <li><a href="/alunos"><i class="bi bi-people-fill"></i> Gerenciar Alunos</a></li>
                <li><a href="/planos"><i class="bi bi-card-checklist"></i> Gerenciar Planos</a></li>
                <li><a href="/funcionarios"><i class="bi bi-person-badge"></i> Gerenciar Funcionários</a></li>
                <li><a href="/matriculas"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
                <li><a href="/aparelhos"><i class="bi bi-gear-wide-connected"></i> Gerenciar Aparelhos</a></li>
                <li><a href="/manutencoes"><i class="bi bi-tools"></i> Gerenciar Manutenções</a></li>
                <li><a href="/relatorios" class="active"><i class="bi bi-bar-chart-line-fill"></i> Relatórios</a></li>
            </ul>
        </div>
        
        <div class="main-content">
            <div class="container">
                <h1>{{ titulo }}</h1>
                
                <p>{{ descricao }}</p>

                <div style="width: 80%; max-width: 800px; margin: 30px auto;">
                    <canvas id="reportChart"></canvas>
                </div>
                
                <h2 style="margin-top: 10px;">Resultado em Tabela</h2>

                {% if dados %}
                <table id="id-tabela-resultados">
                    <thead>
                        <tr>
                            {% for key in dados[0].keys() %}
                            {% if key != 'Valor_RAW' %} 
                            <th>{{ key }}</th>
                            {% endif %}
                            {% endfor %}
                        </tr>
                    </thead>
                    <tbody>
                        {% for item in dados %}
                        <tr>
                            {% for key, value in item.items() %}
                            {% if key != 'Valor_RAW' %}
                            <td>{{ value }}</td>
                            {% endif %}
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                    <div class="msg-erro">Nenhum dado encontrado para o período/critério atual.</div>
                {% endif %}
                
                <h2 style="margin-top: 30px;">Total Geral</h2>
                <div class="campo-fixo" style="padding: 15px;">
                    <span style="font-size: 1.2em; font-weight: 700;">{{ total_geral }}</span>
                </div>

                <a href="/relatorios" class="btn btn-cancelar" style="margin-top: 20px;">
                    <i class="bi bi-arrow-left"></i> Voltar aos Relatórios
                </a>
            </div>
        </div>
        
        <script>
            // --- Lógica de Geração dos Gráficos ---
            document.addEventListener('DOMContentLoaded', function() {
                const chartType = '{{ tipo_grafico }}';
                const endpointApi = '{{ endpoint_api }}';
                const ctx = document.getElementById('reportChart').getContext('2d');
                
                if (endpointApi && chartType) {
                    fetch(endpointApi)
                        .then(response => response.json())
                        .then(data => {
                            
                            const defaultBarColor = 'rgba(0, 137, 123, 0.8)'; // Teal/Primary
                            const defaultLineColor = 'rgba(220, 20, 60, 1)'; // Crimson for line
                            
                            let chartConfig = {};
                            let chartDatasets = [];

                            if (chartType === 'bar') {
                                chartDatasets.push({
                                    label: (data.labels && data.labels.length > 0 && data.labels[0].includes('Plano')) ? 'Faturamento Total (R$)' : 'Contagem de Alunos',
                                    data: data.data,
                                    backgroundColor: defaultBarColor,
                                    borderColor: defaultBarColor,
                                    borderWidth: 1
                                });
                                chartConfig = { type: 'bar', data: { labels: data.labels, datasets: chartDatasets } };
                            } else if (chartType === 'combinado') {
                                // Gráfico Combinado (RFS27: Custo como Barra, Contagem como Linha)
                                
                                // Dataset 1: Custo Total (Barra)
                                chartDatasets.push({
                                    type: 'bar',
                                    label: 'Custo Total (R$)',
                                    data: data.custos,
                                    backgroundColor: defaultBarColor,
                                    borderColor: '#006a5f',
                                    borderWidth: 1,
                                    yAxisID: 'y' // Eixo Y Principal (Esquerda)
                                });
                                
                                // Dataset 2: Contagem (Linha)
                                chartDatasets.push({
                                    type: 'line',
                                    label: 'Contagem',
                                    data: data.contagem,
                                    backgroundColor: 'transparent',
                                    borderColor: defaultLineColor, 
                                    borderWidth: 2,
                                    fill: false,
                                    tension: 0.5, // Aumentado para 0.5 para maior suavidade
                                    yAxisID: 'y1' // Eixo Y Secundário (Direita)
                                });
                                
                                chartConfig = { type: 'bar', data: { labels: data.labels, datasets: chartDatasets } };
                                
                                chartConfig.options = {
                                    responsive: true,
                                    interaction: {
                                        mode: 'index',
                                        intersect: false,
                                    },
                                    scales: {
                                        y: {
                                            type: 'linear',
                                            display: true,
                                            position: 'left',
                                            title: { display: true, text: 'Custo (R$)' }
                                        },
                                        y1: {
                                            type: 'linear',
                                            display: true,
                                            position: 'right',
                                            grid: { drawOnChartArea: false }, // Oculta linhas para o eixo da direita
                                            title: { display: true, text: 'Contagem de Manutenções' }
                                        }
                                    }
                                };
                            }
                            
                            // Configurações Comuns
                            if (!chartConfig.options) {
                                chartConfig.options = {
                                    responsive: true,
                                    scales: {
                                        y: { beginAtZero: true }
                                    }
                                };
                            }
                            
                            new Chart(ctx, chartConfig);
                        });
                }
            });
        </script>
    </body>
    </html>
    """

    # --- LÓGICA PARA CRIAR OS ARQUIVOS ---
    html_crud = html_crud_template.replace("__CSS_PLACEHOLDER__", css_global)
    html_edit = html_edit_template.replace("__CSS_PLACEHOLDER__", css_global)
    html_relatorios = html_relatorios_template.replace("__CSS_PLACEHOLDER__", css_global)
    html_relatorio_detalhe_output = html_relatorio_detalhe.replace("__CSS_PLACEHOLDER__", css_global)

    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/crud_template.html', 'w', encoding='utf-8') as f:
        f.write(html_crud)
    
    with open('templates/edit_template.html', 'w', encoding='utf-8') as f:
        f.write(html_edit)
        
    with open('templates/relatorios_template.html', 'w', encoding='utf-8') as f:
        f.write(html_relatorios)
        
    with open('templates/relatorio_detalhe.html', 'w', encoding='utf-8') as f:
        f.write(html_relatorio_detalhe_output)

    print("="*50)
    print("Servidor Academia v3.1 (FINAL - Sincronizado para Entrega)")
    print("Acesse em: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000)