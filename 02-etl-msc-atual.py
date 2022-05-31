'''
Prepara o arquivo da MSC
'''

import pandas as pd

# Importa as configurações
exec(open('00-configuracoes.py').read())

logging.info('Preparando MSC...')

# Carrega os dados
logging.info('Carregando dados...')
msc = pd.read_excel(msc_atual, sheet_name='Sheet0', header=19, thousands='.', decimal=',')

# Troca o nome das colunas
msc.columns = ['conta_contabil', 'info_compl', 'saldo_inicial_valor', 'saldo_inicial_natureza', 'movimento_debito', 'movimento_credito', 'saldo_final_valor', 'saldo_final_natureza', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo']

# Mantém apenas as colunas de interesse
msc.drop(labels=['info_compl', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo'], axis='columns', inplace=True)

# Consolida os valores da MSC por conta contábil
logging.info('Consolidando os valores...')
msc = msc.groupby(by=['conta_contabil', 'saldo_inicial_natureza', 'saldo_final_natureza'], as_index=False).sum()
contas = msc['conta_contabil'].unique()
temp = []
for conta_contabil in contas:
    conta_contabil = str(conta_contabil)
    classe_contabil = int(conta_contabil[0:1])
    if classe_contabil in [1,3,5,7]:
        saldo_inicial = round(msc.query(f'conta_contabil == {conta_contabil} & saldo_inicial_natureza == "D"')['saldo_inicial_valor'].sum() - msc.query(f'conta_contabil == {conta_contabil} & saldo_inicial_natureza == "C"')['saldo_inicial_valor'].sum(), 2)
        saldo_final = round(msc.query(f'conta_contabil == {conta_contabil} & saldo_final_natureza == "D"')['saldo_final_valor'].sum() - msc.query(f'conta_contabil == {conta_contabil} & saldo_final_natureza == "C"')['saldo_final_valor'].sum(), 2)
        if saldo_inicial > 0:
            natureza_inicial = "D"
        else:
            saldo_inicial = abs(saldo_inicial)
            natureza_inicial = "C"
        if saldo_final > 0:
            natureza_final = "D"
        else:
            saldo_final = abs(saldo_final)
            natureza_final = "C"
    else:
        saldo_inicial = round(msc.query(f'conta_contabil == {conta_contabil} & saldo_inicial_natureza == "C"')['saldo_inicial_valor'].sum() - msc.query(f'conta_contabil == {conta_contabil} & saldo_inicial_natureza == "D"')['saldo_inicial_valor'].sum(), 2)
        saldo_final = round(msc.query(f'conta_contabil == {conta_contabil} & saldo_final_natureza == "C"')['saldo_final_valor'].sum() - msc.query(f'conta_contabil == {conta_contabil} & saldo_final_natureza == "D"')['saldo_final_valor'].sum(), 2)
        if saldo_inicial > 0:
            natureza_inicial = "C"
        else:
            saldo_inicial = abs(saldo_inicial)
            natureza_inicial = "D"
        if saldo_final > 0:
            natureza_final = "C"
        else:
            saldo_final = abs(saldo_final)
            natureza_final = "D"
    temp.append({
        'conta_contabil': conta_contabil,
        'saldo_inicial_valor': saldo_inicial,
        'saldo_inicial_natureza': natureza_inicial,
        'movimento_debito': round(msc.query(f'conta_contabil == {conta_contabil}')['movimento_debito'].sum(), 2),
        'movimento_credito': round(msc.query(f'conta_contabil == {conta_contabil}')['movimento_credito'].sum(), 2),
        'saldo_final_valor': saldo_final,
        'saldo_final_natureza': natureza_final
    })
msc = pd.DataFrame(temp)
msc = msc.astype({'conta_contabil': str})

# Ajusta as naturezas dos saldos inicial e final 0.00 e NaN
logging.info('Limpando os dados...')
msc['saldo_inicial_natureza'] = [None if row['saldo_inicial_valor'] == 0.0 else row['saldo_inicial_natureza'] for index, row in msc.iterrows()]
msc['saldo_final_natureza'] = [None if row['saldo_final_valor'] == 0.0 else row['saldo_final_natureza'] for index, row in msc.iterrows()]
msc['saldo_inicial_natureza'] = [None if row['saldo_inicial_valor'] is None else row['saldo_inicial_natureza'] for index, row in msc.iterrows()]
msc['saldo_final_natureza'] = [None if row['saldo_final_valor'] is None else row['saldo_final_natureza'] for index, row in msc.iterrows()]

# Remove linhas com saldo inicial, débitos, créditos e saldo final 0.00 ou NaN
msc.drop(msc[(msc['saldo_inicial_valor'] == 0.0) & (msc['movimento_debito'] == 0.0) & (msc['movimento_credito'] == 0.0) & (msc['saldo_final_valor'] == 0.0)].index, inplace=True)
msc.dropna(subset=['saldo_inicial_valor', 'movimento_debito', 'movimento_credito', 'saldo_final_valor'], inplace=True)
msc = msc.astype({'conta_contabil': str})

# Salva os dados
logging.info('Salvando a MSC...')
msc.to_excel(r'cache\msc_atual.xlsx', sheet_name='dados', header=True, index=False)

logging.info('MSC atual pronta...')