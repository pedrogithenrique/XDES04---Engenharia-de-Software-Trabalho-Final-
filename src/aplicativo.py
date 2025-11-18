from flask import Flask, render_template, request, redirect, url_for, flash
import os
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta # Para calcular data de término

app = Flask(__name__)
app.secret_key = "secreto-academia"

# --- BANCO DE DADOS EM MEMÓRIA (COM DADOS PRÉ-CADASTRADOS) ---

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
    }
}
next_aluno_id = 3 # Inicia no próximo ID livre

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
    }
}
next_plano_id = 4 # Inicia no próximo ID livre

db_funcionarios = {
    1: {
        "nome": "Carlos Gerente",
        "cpf": "333.333.333-33",
        "cargo": "Gerente",
        "data_admissao": "2020-01-10",
        "salario": "3500.00",
        "contato": "gerente@academia.com"
    },
    2: {
        "nome": "Debora Recepcionista",
        "cpf": "444.444.444-44",
        "cargo": "Recepcionista",
        "data_admissao": "2022-03-15",
        "salario": "1800.00",
        "contato": "(35) 94444-4444"
    }
}
next_funcionario_id = 3 # Inicia no próximo ID livre

db_matriculas = {
    1: {
        "aluno_id": 1, # Ana da Silva
        "plano_id": 2, # Plano Anual
        "data_inicio": "2023-01-15",
        "data_termino": "2024-01-15", # Calculado
        "status": "Ativa"
    },
    2: {
        "aluno_id": 2, # Bruno Costa
        "plano_id": 1, # Plano Mensal
        "data_inicio": "2023-10-01",
        "data_termino": "2023-11-01", # Calculado
        "status": "Inativa" # Já expirou
    }
}
next_matricula_id = 3 # Inicia no próximo ID livre


# --- ROTA PRINCIPAL (DASHBOARD) ---

@app.route('/')
def index():
    # Lógica do Dashboard
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

# --- CRUD ALUNOS (MÓDULO 1) ---

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
            {'nome': 'nome_completo', 'label': 'Nome Completo*', 'tipo': 'text', 'valor': aluno['nome_completo'], 'placeholder': 'Ex: João da Silva'},
            {'nome': 'data_nascimento', 'label': 'Data de Nascimento', 'tipo': 'date', 'valor': aluno['data_nascimento']},
            {'nome': 'email', 'label': 'E-mail*', 'tipo': 'email', 'valor': aluno['email'], 'placeholder': 'joao@email.com'},
            {'nome': 'telefone', 'label': 'Telefone*', 'tipo': 'tel', 'valor': aluno['telefone'], 'placeholder': '(35) 99999-8888'},
            {'nome': 'endereco', 'label': 'Endereço', 'tipo': 'text', 'valor': aluno['endereco'], 'placeholder': 'Rua Exemplo, 123'}
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


# --- CRUD PLANOS (MÓDULO 2) ---

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
            {'nome': 'nome_plano', 'label': 'Nome do Plano*', 'tipo': 'text', 'valor': plano['nome_plano'], 'placeholder': 'Ex: Plano Mensal'},
            {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'text', 'valor': plano['descricao'], 'placeholder': 'Acesso a todas as áreas'},
            {'nome': 'valor_mensal', 'label': 'Valor Mensal (R$)*', 'tipo': 'text', 'valor': plano['valor_mensal'], 'placeholder': 'Ex: 99.90'},
            {'nome': 'duracao_meses', 'label': 'Duração (Meses)*', 'tipo': 'number', 'valor': plano['duracao_meses'], 'placeholder': 'Ex: 12'},
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

# --- CRUD FUNCIONÁRIOS (MÓDULO 3) ---

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
    # [RFS12] A DRE pede verificação de registros. Por enquanto, faremos a remoção simples.
    if funcionario_id in db_funcionarios:
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


# --- CRUD MATRÍCULAS (MÓDULO 5) ---

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
        # [RFS19] Aluno e Plano não podem ser alterados
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


# --- INICIALIZAÇÃO E ARQUIVOS HTML ---

if __name__ == '__main__':
    
    css_global = """
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

        :root {
            --sidebar-bg: #222831;
            --content-bg: #f4f7f6;
            --card-bg: #ffffff;
            /* COR PRIMÁRIA ATUALIZADA */
            --primary-color: #00897b; /* Era #007bff */
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
        
        /* NOVO: HIERARQUIA DE TÍTULOS */
        h1 {
            color: var(--text-dark);
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 8px;
            margin-top: 15px;
            margin-bottom: 25px; /* Mais espaço após o título */
            font-size: 2.0em; /* Maior */
            font-weight: 700;
            text-transform: none;
        }
        h2 { 
            color: var(--text-dark);
            border-bottom: 1px solid #ddd; /* Borda mais leve */
            padding-bottom: 5px;
            margin-top: 30px; /* Mais espaço antes da seção */
            margin-bottom: 20px;
            font-size: 1.5em; /* Menor que h1 */
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
        
        /* NOVO: FORM GRID RESPONSIVO */
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
            background: #006a5f; /* Era #0056b3 */
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

        /* NOVO: CLASSES DE ALINHAMENTO DA TABELA */
        th.col-id, td.col-id {
            text-align: center;
            width: 60px; /* Largura fixa para ID */
        }
        th.col-status, td.col-status {
            text-align: center;
            width: 120px;
        }
        th.col-acoes, td.col-acoes {
            text-align: center;
            width: 180px; /* Largura fixa para Ações */
        }
        
        .acoes { 
            display: flex; 
            gap: 10px; 
            justify-content: center; /* Centraliza botões */
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
        .status-ativo, .status-inativo, .status-cancelada {
            padding: 4px 10px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.85em;
            display: inline-block; /* Permite centralização */
        }
        .status-ativo {
            background-color: #d4edda;
            color: #155724;
        }
        .status-inativo {
            background-color: #f8d7da;
            color: #721c24;
        }
        .status-cancelada {
            background-color: #e2e3e5;
            color: #383d41;
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
            font-size: 3em; /* 48px */
            color: var(--primary-color);
        }
        .dashboard-card .card-info h3 {
            margin: 0;
            font-size: 2.5em; /* 40px */
            color: var(--text-dark);
            /* NOVO: Reseta o H3 para não pegar estilo do h1/h2 */
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
    # Adicionadas classes .col-id, .col-status, .col-acoes
    html_crud_template = """
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
                <li><a href="/" class="{{ 'active' if titulo == 'Início' else '' }}"><i class="bi bi-speedometer2"></i> Dashboard</a></li>
                <li><a href="/alunos" class="{{ 'active' if titulo == 'Alunos' else '' }}"><i class="bi bi-people-fill"></i> Gerenciar Alunos</a></li>
                <li><a href="/planos" class="{{ 'active' if titulo == 'Planos' else '' }}"><i class="bi bi-card-checklist"></i> Gerenciar Planos</a></li>
                <li><a href="/funcionarios" class="{{ 'active' if titulo == 'Funcionários' else '' }}"><i class="bi bi-person-badge"></i> Gerenciar Funcionários</a></li>
                <li><a href="/matriculas" class="{{ 'active' if titulo == 'Matrículas' else '' }}"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
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
                    {% endif %}
                    
                    
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
                            {% else %}
                            <tr>
                                <td colspan="6">Nenhum item encontrado.</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """

    # --- ARQUIVO HTML: edit_template.html (MODIFICADO) ---
    # Apenas o ícone e CSS atualizados
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
                <li><a href="/matriculas" class="{{ 'active' if 'Matrícula' in titulo else '' }}"><i class="bi bi-journal-check"></i> Gerenciar Matrículas</a></li>
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
    
    # --- LÓGICA PARA CRIAR OS ARQUIVOS ---
    html_crud = html_crud_template.replace("__CSS_PLACEHOLDER__", css_global)
    html_edit = html_edit_template.replace("__CSS_PLACEHOLDER__", css_global)

    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/crud_template.html', 'w', encoding='utf-8') as f:
        f.write(html_crud)
    
    with open('templates/edit_template.html', 'w', encoding='utf-8') as f:
        f.write(html_edit)

    print("="*50)
    print("Servidor Academia v7.2 (UI Polida) está pronto!")
    print("Acesse em: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000)