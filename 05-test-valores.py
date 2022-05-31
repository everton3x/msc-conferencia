'''
Testa se os saldos inicial e final e a movimentação são iguais
'''

import pandas as pd

# Importa as configurações
exec(open('00-configuracoes.py').read())

logging.info('Testando se os saldos e movimentação são equivalentes entre BAL_VER e MSC...')

# Carrega os dados
logging.info('Carregando dados...')
msc = pd.read_excel(r'cache\msc_atual.xlsx', sheet_name='dados', thousands='.', decimal=',')
balver = pd.read_excel(r'cache\balver.xlsx', sheet_name='dados', thousands='.', decimal=',')

inconsistencias = []

# Criando listas de contas
logging.info('Criando as listas de contas...')
contas_balver = sorted(balver['conta_contabil'].unique())
contas_msc = sorted(msc['conta_contabil'].unique())
contas = contas_balver + contas_msc
contas = sorted(set(contas))

# Apurando as inconsistências
for conta_contabil in contas:
    item = {
        'conta_contabil': int(conta_contabil),
        'saldo_inicial_valor_pad': None,
        'saldo_inicial_valor_msc': None,
        'saldo_inicial_natureza_pad': None,
        'saldo_inicial_natureza_msc': None,
        'movimento_debito_pad': None,
        'movimento_debito_msc': None,
        'movimento_credito_pad': None,
        'movimento_credito_msc': None,
        'saldo_final_valor_pad': None,
        'saldo_final_valor_msc': None,
        'saldo_final_natureza_pad': None,
        'saldo_final_natureza_msc': None
    }
    val1 = balver.query(f'conta_contabil == {conta_contabil}')
    val2 = msc.query(f'conta_contabil == {conta_contabil}')
    # Compara o valor do saldo inicial
    val_pad = round(val1['saldo_inicial_valor'].sum(), 2)
    val_msc = round(val2['saldo_inicial_valor'].sum(), 2)
    if val_pad != val_msc:
        item['saldo_inicial_valor_pad'] = float(val_pad)
        item['saldo_inicial_valor_msc'] = float(val_msc)
    # Compara a natureza do saldo inicial
    val_pad = val1['saldo_inicial_natureza'].values
    val_msc = val2['saldo_inicial_natureza'].values
    if (val_pad.size > 0) and (val_msc.size > 0):
        if str(val_pad) != str(val_msc):
            item['saldo_inicial_natureza_pad'] = str(val_pad[0])
            item['saldo_inicial_natureza_msc'] = str(val_msc[0])
    # Compara o valor do saldo final
    val_pad = round(val1['saldo_final_valor'].sum(), 2)
    val_msc = round(val2['saldo_final_valor'].sum(), 2)
    if val_pad != val_msc:
        item['saldo_final_valor_pad'] = float(val_pad)
        item['saldo_final_valor_msc'] = float(val_msc)
    # Compara a natureza do saldo final
    val_pad = val1['saldo_final_natureza'].values
    val_msc = val2['saldo_final_natureza'].values
    if (val_pad.size > 0) and (val_msc.size > 0):
        if str(val_pad) != str(val_msc):
            item['saldo_final_natureza_pad'] = str(val_pad[0])
            item['saldo_final_natureza_msc'] = str(val_msc[0])
    # Compara o movimento a débito
    val_pad = round(val1['movimento_debito'].sum(), 2)
    val_msc = round(val2['movimento_debito'].sum(), 2)
    if val_pad != val_msc:
        item['movimento_debito_pad'] = float(val_pad)
        item['movimento_debito_msc'] = float(val_msc)
    # Compara o movimento a crédito
    val_pad = round(val1['movimento_credito'].sum(), 2)
    val_msc = round(val2['movimento_credito'].sum(), 2)
    if val_pad != val_msc:
        item['movimento_credito_pad'] = float(val_pad)
        item['movimento_credito_msc'] = float(val_msc)
    inconsistencias.append(item)

inconsistencias = pd.DataFrame(inconsistencias)

# Limpando so dados
inconsistencias.dropna(subset=['saldo_inicial_valor_pad', 'saldo_inicial_valor_msc', 'saldo_inicial_natureza_pad', 'saldo_inicial_natureza_msc', 'movimento_debito_pad', 'movimento_debito_msc', 'movimento_credito_pad', 'movimento_credito_msc', 'saldo_final_valor_pad', 'saldo_final_valor_msc', 'saldo_final_natureza_pad', 'saldo_final_natureza_msc'], inplace=True, how='all')

# Mostrando resultados
num_inconsistencias = len(inconsistencias)
if num_inconsistencias == 0:
    logging.info('Não formam encontradas inconsistências!')
else:
    logging.warning(f'Foram encontradas {num_inconsistencias} inconsistências!')
    print(inconsistencias)

# Salvando resultados
logging.info('Salvando teste...')
inconsistencias.to_excel(r'output\teste-valores-balver-msc.xlsx', sheet_name='dados', header=True, index=False)

logging.info('Teste concluído!')