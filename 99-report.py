'''
Gera uma relatório HTML dos resultados.
'''

import logging
#import pdfkit
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# Importa as configurações
exec(open('00-configuracoes.py').read())

with open(r'cache/data_base.txt', 'r') as f:
    data_base = f.read()

logging.info('Carregando os resultados...')

teste_balver_msc = pd.read_excel(r'output/teste-contas-balver-msc.xlsx', sheet_name='dados').fillna('').to_dict('records')
teste_msc_balver = pd.read_excel(r'output/teste-contas-msc-balver.xlsx', sheet_name='dados').fillna('').to_dict('records')
teste_valores_balver_msc = pd.read_excel(r'output/teste-valores-balver-msc.xlsx', sheet_name='dados').fillna('').to_dict('records')
teste_msc_anterior_atual = pd.read_excel(r'output/teste-msc-anterior-atual.xlsx', sheet_name='dados').fillna('').to_dict('records')

logging.info('Criando o ambiente de template...')
env = Environment(
    loader=FileSystemLoader('templates')
)

logging.info('Gerando o relatório...')
template = env.get_template('report.html')
template.globals['datetime'] = datetime
html = template.render(
    data_base=data_base,
    teste_balver_msc=teste_balver_msc,
    teste_msc_balver=teste_msc_balver,
    teste_valores_balver_msc=teste_valores_balver_msc,
    teste_msc_anterior_atual=teste_msc_anterior_atual
)

logging.info('Salvando o relatório HTML...')
with open(r'output/report.html', 'w', encoding='utf-8') as f:
    f.write(html)

import os
print(r'file:///'+os.path.join(os.getcwd(), r'output/report.html').replace('\\', '/'))

# logging.info('Salvando o relatório PDF...')
# pdf_options = {
#     'grayscale': True,
#     'margin-bottom': '0.5in',
#     'margin-left': '1in',
#     'margin-right': '0.5in',
#     'margin-top': '1in',
#     'orientation': 'Portrait',
#     'title': 'Conferência da MSC de {}'.format(data_base),
#     'encoding': 'UTF-8',
#     'page-offset': 1,
#     'page-size': 'A4',
#     'enable-local-file-access': None
# }
# pdfkit.from_file(r'output/report.html', r'output/report.pdf', options=pdf_options)

logging.info('Geração dos relatórios concluída!')