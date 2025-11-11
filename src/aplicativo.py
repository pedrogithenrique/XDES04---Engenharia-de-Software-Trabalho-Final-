# Este é o seu programa: app.py (Versão 4.1 - Limpeza de Tags)
from flask import Flask, render_template, request, redirect, url_for, flash
import os # Necessário para criar os templates
import re # Usaremos para validar o CPF

# 1. Configuração do App Flask
app = Flask(__name__)
app.secret_key = "secreto-academia" # Necessário para 'flash'

# 2. Nosso "Banco de Dados" Falso (só na memória)
db_alunos = {}
db_planos = {}
next_aluno_id = 1
next_plano_id = 1

# 3. Rota Principal - Apenas para dizer "Olá"
@app.route('/')
def index():
    # Adicionamos um estilo básico para a página principal
    return """
    <head>
        <title>Academia - Início</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            body { 
                font-family: 'Roboto', sans-serif; 
                background-color: #222; 
                color: #fff;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }
            .container {
                text-align: center;
                background: #333;
                padding: 40px 60px;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            h1 {
                color: #007bff;
                margin-top: 0;
            }
            p {
                font-size: 1.1em;
                color: #ccc;
            }
            ul {
                list-style: none;
                padding: 0;
                margin-top: 30px;
            }
            li {
                margin: 10px 0;
            }
            a {
                color: #fff;
                background-color: #007bff;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                font-weight: bold;
                transition: background-color 0.2s;
            }
            a:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gerenciamento de Academia</h1>
            <p>Selecione o módulo para começar a treinar seus dados.</p>
            <ul>
                <li><a href="/alunos">Gerenciar Alunos</a></li>
                <li><a href="/planos">Gerenciar Planos</a></li>
            </ul>
        </div>
    </body>
    """

# --- CRUD DE ALUNO ---

@app.route('/alunos', methods=['GET', 'POST'])
def crud_alunos():
    global next_aluno_id
    
    # Campos do formulário com placeholders
    campos_form_aluno = [
        {'nome': 'nome_completo', 'label': 'Nome Completo*', 'tipo': 'text', 'placeholder': 'Ex: João da Silva'},
        {'nome': 'cpf', 'label': 'CPF*', 'tipo': 'text', 'placeholder': '111.111.111-11'},
        {'nome': 'data_nascimento', 'label': 'Data de Nascimento', 'tipo': 'date', 'placeholder': ''},
        {'nome': 'email', 'label': 'E-mail*', 'tipo': 'email', 'placeholder': 'joao@email.com'},
        {'nome': 'telefone', 'label': 'Telefone*', 'tipo': 'tel', 'placeholder': '(35) 99999-8888'},
        {'nome': 'endereco', 'label': 'Endereço', 'tipo': 'text', 'placeholder': 'Rua Exemplo, 123'}
    ]
    
    if request.method == 'POST':
        # Inserir Aluno
        
        # Pega os dados do formulário
        nome = request.form['nome_completo']
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']
        data_nasc = request.form['data_nascimento']
        endereco = request.form['endereco']
        
        # --- INÍCIO DAS VALIDAÇÕES ---
        
        # 1. Validação de campos obrigatórios (*)
        if not nome or not cpf or not email or not telefone:
            flash('Erro: Todos os campos com * (Nome, CPF, Email, Telefone) são obrigatórios!', 'error')
            
            # Recarrega o formulário mantendo os dados digitados
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
        
        # 2. Validação de formato de CPF (XXX.XXX.XXX-XX)
        if not re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf):
            flash('Erro: Formato de CPF inválido! Use o padrão 111.222.333-44.', 'error')
            return redirect(url_for('crud_alunos'))
            
        # 3. Validação de CPF único
        for aluno in db_alunos.values():
            if aluno['cpf'] == cpf:
                flash(f'Erro: O CPF {cpf} já está cadastrado!', 'error')
                return redirect(url_for('crud_alunos'))
        
        # --- FIM DAS VALIDAÇÕES ---

        novo_aluno = {
            "nome_completo": nome,
            "cpf": cpf, # Salva o CPF com a máscara
            "data_nascimento": data_nasc,
            "email": email,
            "telefone": telefone,
            "endereco": endereco
        }
        db_alunos[next_aluno_id] = novo_aluno
        next_aluno_id += 1
        
        flash('Aluno cadastrado com sucesso!', 'success') 
        return redirect(url_for('crud_alunos')) 

    # Consultar Aluno (GET)
    # --- Implementação do Filtro ---
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
        items=alunos_filtrados, # Passa a lista filtrada
        form_action=url_for('crud_alunos'),
        campos_formulario=campos_form_aluno,
        # Passa os valores da busca de volta
        search_nome_value=search_nome,
        search_cpf_value=search_cpf
    )

# Rota para DELETAR (DELETE)
# Excluir Aluno
@app.route('/alunos/remover/<int:aluno_id>', methods=['POST'])
def remover_aluno(aluno_id):
    # NOTA: O RFS04 real tem regras de negócio (matrícula ativa, etc)
    if aluno_id in db_alunos:
        del db_alunos[aluno_id]
        flash('Aluno removido com sucesso!', 'success')
    else:
        flash('Aluno não encontrado!', 'error')
    return redirect(url_for('crud_alunos'))

# Rota para EDITAR (UPDATE) - Etapa 1: Mostrar formulário
# Editar Aluno
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
            {'label': 'CPF (Fixo)', 'valor': aluno['cpf']} # CPF não pode ser alterado
        ],
        cancel_url=url_for('crud_alunos')
    )

# Rota para EDITAR (UPDATE) - Etapa 2: Salvar dados
@app.route('/alunos/editar/<int:aluno_id>', methods=['POST'])
def editar_aluno_salvar(aluno_id):
    if aluno_id not in db_alunos:
        flash('Aluno não encontrado!', 'error')
        return redirect(url_for('crud_alunos'))
    
    # Validação de campos obrigatórios na edição
    nome = request.form['nome_completo']
    email = request.form['email']
    telefone = request.form['telefone']
    
    if not nome or not email or not telefone:
        flash('Erro: Nome, Email e Telefone são obrigatórios na edição!', 'error')
        # Redireciona de volta para o formulário de edição
        return redirect(url_for('editar_aluno_form', aluno_id=aluno_id))

    db_alunos[aluno_id]['nome_completo'] = nome
    db_alunos[aluno_id]['data_nascimento'] = request.form['data_nascimento']
    db_alunos[aluno_id]['email'] = email
    db_alunos[aluno_id]['telefone'] = telefone
    db_alunos[aluno_id]['endereco'] = request.form['endereco']
    
    flash('Aluno atualizado com sucesso!', 'success')
    return redirect(url_for('crud_alunos'))


# --- CRUD DE PLANO ---

@app.route('/planos', methods=['GET', 'POST'])
def crud_planos():
    global next_plano_id
    
    # Campos do formulário com placeholders
    campos_form_plano = [
        {'nome': 'nome_plano', 'label': 'Nome do Plano*', 'tipo': 'text', 'placeholder': 'Ex: Plano Mensal'},
        {'nome': 'descricao', 'label': 'Descrição', 'tipo': 'text', 'placeholder': 'Acesso a todas as áreas'},
        {'nome': 'valor_mensal', 'label': 'Valor Mensal (R$)*', 'tipo': 'text', 'placeholder': 'Ex: 99.90'},
        {'nome': 'duracao_meses', 'label': 'Duração (Meses)*', 'tipo': 'number', 'placeholder': 'Ex: 12'},
        {'nome': 'status', 'label': 'Status*', 'tipo': 'select', 'opcoes': ['Ativo', 'Inativo']}
    ]
    
    if request.method == 'POST':
        # Inserir Plano
        nome = request.form['nome_plano']
        valor = request.form['valor_mensal']
        duracao = request.form['duracao_meses']
        status = request.form['status']
        descricao = request.form['descricao']

        # 1. Validação de campos obrigatórios (*)
        if not nome or not valor or not duracao or not status:
            flash('Erro: Todos os campos com * (Nome, Valor, Duração, Status) são obrigatórios!', 'error')
            
            # Recarrega o formulário mantendo os dados digitados
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
        
        # 2. Validação de Nome de Plano único
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

    # Consultar Plano (GET)
    # --- Implementação do Filtro ---
    search_nome_plano = request.args.get('search_nome_plano', '')
    search_status = request.args.get('search_status', 'Todos') #
    
    planos_filtrados = db_planos
    
    if search_nome_plano:
        planos_filtrados = {id: plano for id, plano in planos_filtrados.items() 
                            if search_nome_plano.lower() in plano['nome_plano'].lower()}
    
    if search_status != 'Todos':
        planos_filtrados = {id: plano for id, plano in planos_filtrados.items() 
                            if plano['status'] == search_status}
                            
    return render_template('crud_template.html', 
        titulo="Planos", 
        items=planos_filtrados, # Passa a lista filtrada
        form_action=url_for('crud_planos'),
        campos_formulario=campos_form_plano,
        # Passa os valores da busca de volta
        search_nome_plano_value=search_nome_plano,
        search_status_value=search_status
    )

# Rota para DELETAR (DELETE)
# Excluir Plano
@app.route('/planos/remover/<int:plano_id>', methods=['POST'])
def remover_plano(plano_id):
    # NOTA: O RFS08 real tem regras (verificar matrícula)
    if plano_id in db_planos:
        del db_planos[plano_id]
        flash('Plano removido com sucesso!', 'success')
    return redirect(url_for('crud_planos'))

# Rota para EDITAR (UPDATE) - Etapa 1: Mostrar formulário
# Editar Plano
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

# Rota para EDITAR (UPDATE) - Etapa 2: Salvar dados
@app.route('/planos/editar/<int:plano_id>', methods=['POST'])
def editar_plano_salvar(plano_id):
    if plano_id not in db_planos:
        flash('Plano não encontrado!', 'error')
        return redirect(url_for('crud_planos'))
    
    # Validação de campos obrigatórios na edição
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

# --- FIM DOS CRUDS ---

# 4. Inicia o servidor e cria os templates (com CSS de Academia)
if __name__ == '__main__':
    
    # --- CSS ATUALIZADO (com .form-filtro) ---
    css_global = """
        /* Importa a fonte Roboto */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        /* Importa ícones do Bootstrap */
        @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css');

        body { 
            font-family: 'Roboto', sans-serif; 
            margin: 0; 
            background-color: #f4f7f6; /* Um cinza bem claro */
            color: #333;
        }
        
        /* Navbar simples */
        .navbar {
            background-color: #222;
            padding: 15px 30px;
            color: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .navbar a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            margin-right: 20px;
            font-size: 16px;
        }
        .navbar a:hover {
            color: #007bff;
        }

        .container {
            max-width: 1100px;
            margin: 20px auto;
            padding: 20px;
        }
        
        h1, h2 { 
            color: #222;
            border-bottom: 2px solid #007bff;
            padding-bottom: 5px;
            margin-top: 20px;
        }
        
        /* Estilo de "Card" para formulários */
        form { 
            background: #ffffff; 
            padding: 25px; 
            border-radius: 8px; 
            margin-bottom: 30px; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
        }
        
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr; /* 2 colunas */
            gap: 20px;
        }
        
        form div { 
            margin-bottom: 10px; 
        }
        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 500; /* Mais forte */
            color: #555;
        }
        
        /* Inputs modernos */
        input[type='text'], input[type='email'], input[type='tel'], input[type='date'], input[type='number'], select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ccc; 
            border-radius: 4px;
            box-sizing: border-box; /* Garante que o padding não quebre o layout */
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus, select:focus {
            border-color: #007bff;
            box-shadow: 0 0 5px rgba(0,123,255,0.3);
            outline: none;
        }
        
        /* Estilo do Placeholder (mensagem "invisível") */
        ::placeholder {
            color: #aaa;
            font-style: italic;
        }
        
        /* Botões */
        button, .btn {
            background: #007bff; 
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
            background: #0056b3; 
        }
        
        /* --- NOVO: Estilo do Formulário de Filtro --- */
        .form-filtro {
            background: #e9ecef;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            flex-wrap: wrap; /* Permite quebrar a linha em telas menores */
            gap: 10px;
            align-items: center;
        }
        .form-filtro input, .form-filtro select {
            width: auto;
            flex-grow: 1; /* Faz os campos crescerem para preencher o espaço */
            margin-bottom: 0;
        }
        .form-filtro button {
            padding: 12px 15px;
        }
        .form-filtro .btn-cancelar {
            background: #6c757d;
            padding: 12px 15px;
            font-size: 16px; /* Ajuste para bater com o botão */
        }
        
        /* Tabela moderna */
        table { 
            width: 100%; 
            border-collapse: collapse; 
            margin-top: 20px; 
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-radius: 8px;
            overflow: hidden; /* Para o radius funcionar no header */
        }
        th, td { 
            border-bottom: 1px solid #ddd; 
            padding: 15px; 
            text-align: left; 
            vertical-align: middle;
        }
        th { 
            background: #f0f0f0; 
            color: #333;
            font-weight: 700;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        
        .acoes { 
            display: flex; 
            gap: 10px; 
        }
        .btn-editar { 
            background: #ffc107; color: black; padding: 8px 12px;
        }
        .btn-editar:hover { background: #e0a800; }
        .btn-remover { 
            background: #dc3545; color: white; padding: 8px 12px;
        }
        .btn-remover:hover { background: #c82333; }
        
        /* Ícones */
        .bi {
            vertical-align: middle;
            margin-right: 4px;
        }
        
        /* Mensagem de sucesso (Verde) */
        .msg-sucesso { 
            background: #d4edda; 
            color: #155724; 
            padding: 15px; 
            border-radius: 4px; 
            margin-bottom: 20px;
            border: 1px solid #c3e6cb;
        }
        
        /* Mensagem de erro (Vermelho) */
        .msg-erro {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border: 1px solid #f5c6cb;
        }
        
        /* Estilos do formulário de Edição */
        .campo-fixo {
            background: #eee;
            padding: 10px;
            border-radius: 4px;
        }
        .campo-fixo label {
            color: #777;
        }
        .campo-fixo span {
            font-size: 1.1em;
            color: #000;
        }
        .btn-verde { background: #28a745; }
        .btn-verde:hover { background: #218838; }
        .btn-cancelar {
            background: #6c757d;
            margin-left: 10px;
        }
        .btn-cancelar:hover { background: #5a6268; }
        
        /* Badge de Status (para tabela de Planos) */
        .status-ativo {
            background-color: #d4edda;
            color: #155724;
            padding: 5px 10px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.9em;
        }
        .status-inativo {
            background-color: #f8d7da;
            color: #721c24;
            padding: 5px 10px;
            border-radius: 12px;
            font-weight: 500;
            font-size: 0.9em;
        }
    """

    # Template principal do CRUD (Formulário + Tabela)
    html_crud_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>CRUD {{ titulo }}</title>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/">Academia</a>
            <a href="/alunos">Alunos</a>
            <a href="/planos">Planos</a>
        </nav>
        
        <div class="container">
            <h1>CRUD de {{ titulo }}</h1>
            
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

            <h2><i class="bi bi-plus-circle-fill"></i> Cadastrar Novo (Create)</h2>
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

            <h2><i class="bi bi-list-task"></i> Consultar (Read)</h2>
            
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
            {% endif %}
            <table id="id-tabela-resultados">
                <thead>
                    <tr>
                        <th>ID</th>
                        {% if titulo == "Alunos" %}
                            <th>Nome</th>
                            <th>CPF</th>
                        {% elif titulo == "Planos" %}
                            <th>Plano</th>
                            <th>Status</th>
                        {% endif %}
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {% for id, item in items.items() %}
                    <tr>
                        <td>{{ id }}</td>
                        {% if titulo == "Alunos" %}
                            <td>{{ item['nome_completo'] }}</td>
                            <td>{{ item['cpf'] }}</td>
                        {% elif titulo == "Planos" %}
                            <td>{{ item['nome_plano'] }}</td>
                            <td><span class="status-{{ item['status']|lower }}">{{ item['status'] }}</span></td>
                        {% endif %}
                        
                        <td class="acoes">
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
                            {% endif %}
                        </td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4">Nenhum item encontrado.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """

    # Template da página de Edição
    html_edit_template = """
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <title>{{ titulo }}</title>
        <style>__CSS_PLACEHOLDER__</style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/">Academia</a>
            <a href="/alunos">Alunos</a>
            <a href="/planos">Planos</a>
        </nav>
        
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
                <div class="campo-fixo">
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
    </body>
    </html>
    """
    
    # Injetamos o CSS nos templates
    html_crud = html_crud_template.replace("__CSS_PLACEHOLDER__", css_global)
    html_edit = html_edit_template.replace("__CSS_PLACEHOLDER__", css_global)

    # Cria os arquivos HTML fisicamente na pasta 'templates'
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/crud_template.html', 'w', encoding='utf-8') as f:
        f.write(html_crud)
    
    with open('templates/edit_template.html', 'w', encoding='utf-8') as f:
        f.write(html_edit)

    print("="*50)
    print("Servidor Academia v4.0 (Filtros e Validação) está pronto!")
    print("Acesse em: http://127.0.0.1:5000")
    print("="*50)
    app.run(debug=True, port=5000)