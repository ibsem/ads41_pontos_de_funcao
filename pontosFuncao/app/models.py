# app/models.py
# Este arquivo pode ser usado para definir esquemas lógicos para ajudar no desenvolvimento, mas não é estritamente necessário.

class Parametros:
    valor_hora_homem = float  # Valor em reais
    qtd_horas_ponto_funcao = int  # Quantidade de horas

class TipoEntidade:
    nome = str
    descricao = str
    complexidade_baixa = int
    complexidade_media = int
    complexidade_alta = int

class Sistema:
    nome = str
    descricao = str
    cliente = str
    contato = str
    telefone = str

class Mensuracao:
    sistema_id = str  # Deve ser uma string representando um ObjectId
    tipo_entidade_id = str  # Deve ser uma string representando um ObjectId
    complexidade_escolhida = str  # 'baixa', 'media', 'alta'
    observacoes = str
