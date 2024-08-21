# Continuação em app/utils.py
from . import mongo
from bson.objectid import ObjectId

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def criar_pdf(sistema, mensuracoes, total_pontos, total_horas, custo_total):
    """ Gera um arquivo PDF com os detalhes do relatório do sistema. """
    filename = f"relatorio_{sistema['nome']}.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(72, 720, f"Relatório de Sistema: {sistema['nome']}")
    c.drawString(72, 700, f"Cliente: {sistema['cliente']}")
    c.drawString(72, 680, f"Total de Pontos de Função: {total_pontos}")
    c.drawString(72, 660, f"Total de Horas: {total_horas}")
    c.drawString(72, 640, f"Custo Total: R$ {custo_total:.2f}")
    c.showPage()
    c.save()
    return filename


def calcular_resumo(sistema, mensuracoes, parametros):
    """ Calcula o resumo de pontos, horas e custos para um sistema. """
    
    total_pontos = 0
    for m in mensuracoes:
        tipo_entidade = mongo.db.tipos_entidade.find_one({'_id': m['tipo_entidade_id']})
        if tipo_entidade:
            total_pontos += calcular_pontos(m, tipo_entidade)
        else:
            raise ValueError(f"Tipo de Entidade não encontrado para ID: {m['tipo_entidade_id']}")

    total_horas = calcular_horas(total_pontos, parametros['qtd_horas_ponto_funcao'])
    custo_total = calcular_custo(total_horas, parametros['valor_hora_homem'])
    return total_pontos, total_horas, custo_total


def get_tipos_entidade():
    """
    Busca todos os tipos de entidade disponíveis no banco de dados e retorna uma lista.
    """
    tipos = mongo.db.tipos_entidade.find()
    return list(tipos)

def calcular_pontos(mensuracao, tipo_entidade):
    """
    Calcula os pontos de função para uma única mensuração com base na complexidade escolhida.
    """
    complexidade = mensuracao['complexidade_escolhida']
    pontos = tipo_entidade['complexidade_' + complexidade]
    return pontos


def calcular_horas(total_pontos, horas_por_ponto):
    """
    Calcula o total de horas de trabalho com base nos pontos de função e na configuração de horas por ponto.
    """
    total_horas = total_pontos * horas_por_ponto
    return total_horas


def calcular_custo(total_horas, valor_hora_homem):
    """
    Calcula o custo total do projeto com base no total de horas e no valor hora homem.
    """
    custo_total = total_horas * valor_hora_homem
    return custo_total



