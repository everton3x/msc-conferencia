'''
Testa se todas as contas da MSC estão no BAL_VER
'''

import pandas as pd

# Importa as configurações
exec(open('00-configuracoes.py').read())

logging.info('Testando se todas as contas da MSC estão no BAL_VER...')

# Carrega os dados
logging.info('Carregando dados...')
msc = pd.read_excel(r'cache\msc_atual.xlsx', sheet_name='dados', thousands='.', decimal=',')
balver = pd.read_excel(r'cache\balver.xlsx', sheet_name='dados', thousands='.', decimal=',')

# Criando listas de contas
logging.info('Criando as listas de contas...')
contas_balver = sorted(balver['conta_contabil'].unique())
contas_msc = sorted(msc['conta_contabil'].unique())

# Verifica se todas as contas do BAL_VER estão na MSC
logging.info('Procurando inconsistências...')
inconsistencias = pd.DataFrame()
for conta_contabil in contas_msc:
    existe_balver = balver.query(f'conta_contabil == {conta_contabil}')
    if len(existe_balver) == 0:
        if inconsistencias.empty:
            inconsistencias = msc.query(f'conta_contabil == {conta_contabil}')
        else:
            inconsistencias = pd.concat([inconsistencias, msc.query(f'conta_contabil == {conta_contabil}')])
    
num_inconsistencias = len(inconsistencias)
if num_inconsistencias == 0:
    logging.info('Não formam encontradas inconsistências!')
else:
    logging.warning(f'Foram encontradas {num_inconsistencias} inconsistências!')
    print(inconsistencias)

# Salvando resultados
logging.info('Salvando teste...')
inconsistencias.to_excel(r'output\teste-contas-msc-balver.xlsx', sheet_name='dados', header=True, index=False)

logging.info('Teste concluído!')