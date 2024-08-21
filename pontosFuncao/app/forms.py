# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, IntegerField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class BaseForm(FlaskForm):
    @property
    def data(self):
        form_data = super().data
        # Remove os campos csrf_token e submit
        form_data.pop('csrf_token', None)
        form_data.pop('submit', None)
        return form_data

class ParametrosForm(BaseForm):
    valor_hora_homem = FloatField('Valor Hora Homem (R$)', validators=[DataRequired()])
    qtd_horas_ponto_funcao = IntegerField('Quantidade de Horas por Ponto de Função', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class TipoEntidadeForm(BaseForm):
    nome = StringField('Nome', validators=[DataRequired()])
    descricao = StringField('Descrição', validators=[DataRequired()])
    complexidade_baixa = IntegerField('Complexidade Baixa', validators=[DataRequired()])
    complexidade_media = IntegerField('Complexidade Média', validators=[DataRequired()])
    complexidade_alta = IntegerField('Complexidade Alta', validators=[DataRequired()])
    submit = SubmitField('Salvar')

class SistemaForm(BaseForm):
    nome = StringField('Nome do Sistema', validators=[DataRequired()])
    descricao = TextAreaField('Descrição do Sistema')
    cliente = StringField('Cliente', validators=[DataRequired()])
    contato = StringField('Contato')
    telefone = StringField('Telefone')
    submit = SubmitField('Salvar')

class MensuracaoForm(BaseForm):
    tipo_entidade_id = SelectField('Tipo de Entidade', choices=[], coerce=str, validators=[DataRequired()])
    complexidade_escolhida = SelectField('Complexidade', choices=[('baixa', 'Baixa'), ('media', 'Média'), ('alta', 'Alta')], validators=[DataRequired()])
    observacoes = TextAreaField('Observações')
    submit = SubmitField('Adicionar Entidade')
