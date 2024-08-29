from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from .forms import ParametrosForm, TipoEntidadeForm, SistemaForm, MensuracaoForm
from flask_weasyprint import HTML, render_pdf
from . import mongo
from bson.objectid import ObjectId
from .utils import calcular_resumo
from flask_weasyprint import HTML, render_pdf

main = Blueprint('main', __name__)

@main.route('/')
def index():
    sistemas = mongo.db.sistemas.find()
    return render_template('index.html', sistemas=sistemas)

@main.route('/parametros', methods=['GET', 'POST'])
def parametros():
    form = ParametrosForm(request.form)
    if request.method == 'POST' and form.validate():
        mongo.db.parametros.update_one({}, {'$set': form.data}, upsert=True)
        flash('Parâmetros atualizados com sucesso!', 'success')
        return redirect(url_for('main.parametros'))
    parametros = mongo.db.parametros.find_one()
    if parametros:
        form.process(data=parametros)
    return render_template('parametros.html', form=form)

@main.route('/tipos_entidade')
def tipos_entidade():
    tipos = mongo.db.tipos_entidade.find()
    return render_template('tipos_entidade_list.html', tipos=tipos)

@main.route('/tipos_entidade/create', methods=['GET', 'POST'])
def create_tipo_entidade():
    form = TipoEntidadeForm()
    if form.validate_on_submit():
        mongo.db.tipos_entidade.insert_one(form.data)
        flash('Tipo de Entidade criado com sucesso!', 'success')
        return redirect(url_for('main.tipos_entidade'))
    return render_template('tipo_entidade_form.html', form=form, title='Criar Tipo de Entidade')

@main.route('/tipos_entidade/edit/<tipo_id>', methods=['GET', 'POST'])
def edit_tipo_entidade(tipo_id):
    tipo = mongo.db.tipos_entidade.find_one_or_404({'_id': ObjectId(tipo_id)})
    form = TipoEntidadeForm()

    # Inicialização manual dos dados no formulário
    if request.method == 'GET':
        form.nome.data = tipo['nome']
        form.descricao.data = tipo['descricao']
        form.complexidade_baixa.data = tipo['complexidade_baixa']
        form.complexidade_media.data = tipo['complexidade_media']
        form.complexidade_alta.data = tipo['complexidade_alta']
    
    print("Dados no formulário após a inicialização manual:", form.data)
    
    if form.validate_on_submit():
        mongo.db.tipos_entidade.update_one({'_id': ObjectId(tipo_id)}, {'$set': form.data})
        flash('Tipo de Entidade atualizado com sucesso!', 'success')
        return redirect(url_for('main.tipos_entidade'))

    return render_template('tipo_entidade_form.html', form=form, title='Editar Tipo de Entidade')

@main.route('/tipos_entidade/delete/<tipo_id>', methods=['POST'])
def delete_tipo_entidade(tipo_id):
    mongo.db.tipos_entidade.delete_one({'_id': ObjectId(tipo_id)})
    flash('Tipo de Entidade excluído com sucesso!', 'success')
    return redirect(url_for('main.tipos_entidade'))


@main.route('/sistemas')
def sistemas():
    sistemas = mongo.db.sistemas.find()
    return render_template('sistemas_list.html', sistemas=sistemas)

@main.route('/sistemas/create', methods=['GET', 'POST'])
def create_sistema():
    form = SistemaForm(request.form)
    if request.method == 'POST' and form.validate():
        sistema_id = mongo.db.sistemas.insert_one(form.data).inserted_id
        flash('Sistema criado com sucesso!', 'success')
        return redirect(url_for('main.sistemas'))
    return render_template('sistema_form.html', form=form, title='Criar Sistema')

@main.route('/sistemas/edit/<sistema_id>', methods=['GET', 'POST'])
def edit_sistema(sistema_id):
    sistema = mongo.db.sistemas.find_one_or_404({'_id': ObjectId(sistema_id)})
    form = SistemaForm()

    # Inicialização manual dos dados no formulário
    if request.method == 'GET':
        form.nome.data = sistema['nome']
        form.descricao.data = sistema.get('descricao', '')  # get usado para campos opcionais
        form.cliente.data = sistema['cliente']
        form.contato.data = sistema.get('contato', '')  # get usado para campos opcionais
        form.telefone.data = sistema.get('telefone', '')  # get usado para campos opcionais
    
    print("Dados no formulário após a inicialização manual:", form.data)
    
    if form.validate_on_submit():
        mongo.db.sistemas.update_one({'_id': ObjectId(sistema_id)}, {'$set': form.data})
        flash('Sistema atualizado com sucesso!', 'success')
        return redirect(url_for('main.sistemas'))

    return render_template('sistema_form.html', form=form, title='Editar Sistema')


@main.route('/sistemas/delete/<sistema_id>', methods=['POST'])
def delete_sistema(sistema_id):
    mongo.db.sistemas.delete_one({'_id': ObjectId(sistema_id)})
    flash('Sistema excluído com sucesso!', 'success')
    return redirect(url_for('main.sistemas'))

@main.route('/sistemas/<sistema_id>/relatorio', methods=['GET'])
def relatorio(sistema_id):
    sistema = mongo.db.sistemas.find_one_or_404({'_id': ObjectId(sistema_id)})
    mensuracoes = list(mongo.db.mensuracoes.find({'sistema_id': ObjectId(sistema_id)}))

    # Enriquecer os dados de cada mensuração com o tipo de entidade correspondente
    for mensuracao in mensuracoes:
        tipo_entidade = mongo.db.tipos_entidade.find_one({'_id': mensuracao['tipo_entidade_id']})
        mensuracao['tipo_entidade'] = tipo_entidade

    # Obter os parâmetros para o cálculo do resumo
    parametros = mongo.db.parametros.find_one()
    
    if not parametros:
        flash('Parâmetros não encontrados. Verifique as configurações.', 'danger')
        return redirect(url_for('main.index'))

    total_pontos, total_horas, custo_total = calcular_resumo(sistema, mensuracoes, parametros)

    # Obter os valores de classificação de todas as entidades cadastradas
    todas_entidades = list(mongo.db.tipos_entidade.find())

    return render_template('relatorio.html', sistema=sistema, mensuracoes=mensuracoes, total_pontos=total_pontos,
                           total_horas=total_horas, custo_total=custo_total, parametros=parametros, todas_entidades=todas_entidades)


@main.route('/sistemas/<sistema_id>/mensuracoes', methods=['GET', 'POST'])
def mensuracoes(sistema_id):
    sistema = mongo.db.sistemas.find_one_or_404({'_id': ObjectId(sistema_id)})
    form = MensuracaoForm()

    # Preenche as opções de Tipo de Entidade
    form.tipo_entidade_id.choices = [(str(tipo['_id']), tipo['nome']) for tipo in mongo.db.tipos_entidade.find()]

    if form.validate_on_submit():
        mensuracao_data = {
            'sistema_id': ObjectId(sistema_id),
            'tipo_entidade_id': ObjectId(form.tipo_entidade_id.data),
            'complexidade_escolhida': form.complexidade_escolhida.data,
            'observacoes': form.observacoes.data
        }
        mongo.db.mensuracoes.insert_one(mensuracao_data)
        flash('Mensuração adicionada com sucesso!', 'success')
        return redirect(url_for('main.mensuracoes', sistema_id=sistema_id))

    mensuracoes = list(mongo.db.mensuracoes.find({'sistema_id': ObjectId(sistema_id)}))

    # Enriquecer os dados das mensurações com o nome do tipo de entidade
    for mensuracao in mensuracoes:
        tipo_entidade = mongo.db.tipos_entidade.find_one({'_id': mensuracao['tipo_entidade_id']})
        mensuracao['tipo_entidade_nome'] = tipo_entidade['nome'] if tipo_entidade else 'Desconhecido'

    return render_template('mensuracoes.html', sistema=sistema, mensuracoes=mensuracoes, form=form, mensuracao=None)

@main.route('/sistemas/<sistema_id>/mensuracoes/edit/<mensuracao_id>', methods=['GET', 'POST'])
def edit_mensuracao(sistema_id, mensuracao_id):
    sistema = mongo.db.sistemas.find_one_or_404({'_id': ObjectId(sistema_id)})
    mensuracao = mongo.db.mensuracoes.find_one_or_404({'_id': ObjectId(mensuracao_id), 'sistema_id': ObjectId(sistema_id)})

    form = MensuracaoForm()

    # Preenche as opções de Tipo de Entidade
    form.tipo_entidade_id.choices = [(str(tipo['_id']), tipo['nome']) for tipo in mongo.db.tipos_entidade.find()]

    if request.method == 'GET':
        form.tipo_entidade_id.data = str(mensuracao['tipo_entidade_id'])
        form.complexidade_escolhida.data = mensuracao['complexidade_escolhida']
        form.observacoes.data = mensuracao.get('observacoes', '')

    if form.validate_on_submit():
        mensuracao_data = {
            'sistema_id': ObjectId(sistema_id),
            'tipo_entidade_id': ObjectId(form.tipo_entidade_id.data),
            'complexidade_escolhida': form.complexidade_escolhida.data,
            'observacoes': form.observacoes.data
        }
        mongo.db.mensuracoes.update_one({'_id': ObjectId(mensuracao_id)}, {'$set': mensuracao_data})
        flash('Mensuração atualizada com sucesso!', 'success')
        return redirect(url_for('main.mensuracoes', sistema_id=sistema_id))

    mensuracoes = list(mongo.db.mensuracoes.find({'sistema_id': ObjectId(sistema_id)}))
    return render_template('mensuracoes.html', sistema=sistema, mensuracoes=mensuracoes, form=form, mensuracao=mensuracao)

@main.route('/sistemas/<sistema_id>/mensuracoes/delete/<mensuracao_id>', methods=['POST'])
def delete_mensuracao(sistema_id, mensuracao_id):
    mongo.db.mensuracoes.delete_one({'_id': ObjectId(mensuracao_id)})
    flash('Mensuração removida com sucesso!', 'success')
    return redirect(url_for('main.mensuracoes', sistema_id=sistema_id))



@main.route('/sistemas/<sistema_id>/relatorio/pdf')
def relatorio_pdf(sistema_id):
    sistema = mongo.db.sistemas.find_one_or_404({'_id': ObjectId(sistema_id)})
    mensuracoes = list(mongo.db.mensuracoes.find({'sistema_id': ObjectId(sistema_id)}))

    # Enriquecer os dados de cada mensuração com o tipo de entidade correspondente
    for mensuracao in mensuracoes:
        tipo_entidade = mongo.db.tipos_entidade.find_one({'_id': mensuracao['tipo_entidade_id']})
        mensuracao['tipo_entidade'] = tipo_entidade

    # Obter os parâmetros para o cálculo do resumo
    parametros = mongo.db.parametros.find_one()
    
    if not parametros:
        flash('Parâmetros não encontrados. Verifique as configurações.', 'danger')
        return redirect(url_for('main.index'))

    total_pontos, total_horas, custo_total = calcular_resumo(sistema, mensuracoes, parametros)

    todas_entidades = list(mongo.db.tipos_entidade.find())

    # Renderizar o template exclusivo para o PDF
    rendered_html = render_template('relatorio_pdf.html', sistema=sistema, mensuracoes=mensuracoes, total_pontos=total_pontos,
                                    total_horas=total_horas, custo_total=custo_total, parametros=parametros, todas_entidades=todas_entidades)
    
    # Gerar o PDF usando o HTML renderizado
    return render_pdf(HTML(string=rendered_html))

