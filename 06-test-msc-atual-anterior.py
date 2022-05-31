'''
Testa a compatibilidade de contas entre a MSC atual e anterior
'''

import pandas as pd

# Importa as configurações
exec(open('00-configuracoes.py').read())

logging.info('Preparando MSC Atual e Anterior...')

# Carrega os dados
logging.info('Carregando dados...')
atual = pd.read_excel(msc_atual, sheet_name='Sheet0', header=19, thousands='.', decimal=',')
anterior = pd.read_excel(msc_anterior, sheet_name='Sheet0', header=19, thousands='.', decimal=',')

# Troca o nome das colunas
logging.info('Ajustando colunas...')
atual.columns = ['conta_contabil', 'info_compl', 'saldo_inicial_valor', 'saldo_inicial_natureza', 'movimento_debito', 'movimento_credito', 'saldo_final_valor', 'saldo_final_natureza', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo']
anterior.columns = ['conta_contabil', 'info_compl', 'saldo_inicial_valor', 'saldo_inicial_natureza', 'movimento_debito', 'movimento_credito', 'saldo_final_valor', 'saldo_final_natureza', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo']

# Mantém apenas as colunas de interesse
atual.drop(labels=['movimento_debito', 'movimento_credito', 'saldo_final_valor', 'saldo_final_natureza', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo'], axis='columns', inplace=True)
anterior.drop(labels=['movimento_debito', 'movimento_credito', 'saldo_inicial_valor', 'saldo_inicial_natureza', 'lb', 'ld', 'lc', 'le', 'movimento_saldo', 'diferenca_movimento_saldo'], axis='columns', inplace=True)

# Cria a lista de contas únicas
logging.info('Preparando o teste...')
temp = pd.concat([atual[['conta_contabil', 'info_compl']], anterior[['conta_contabil', 'info_compl']]], ignore_index=True)
contas_qualificadas = temp.groupby(by=['conta_contabil', 'info_compl'], as_index=False).sum()

# Realizando o teste
logging.info('Testando contas...')
inconsistencias = []
for index, row in contas_qualificadas.iterrows():
    conta_contabil = row['conta_contabil']
    info_compl = row['info_compl']
    item_atual = atual.query(f'conta_contabil == {conta_contabil} and info_compl == "{info_compl}"')
    item_anterior = anterior.query(f'conta_contabil == {conta_contabil} and info_compl == "{info_compl}"')
    # Testa se o saldo final anterior é igual ao saldo inicial atual
    saldo_final = round(item_anterior['saldo_final_valor'].sum(), 2)
    saldo_inicial = round(item_atual['saldo_inicial_valor'].sum(), 2)
    natureza_final = item_anterior['saldo_final_natureza'].values
    natureza_inicial = item_atual['saldo_inicial_natureza'].values
    if len(natureza_final) > 0:
        natureza_final = natureza_final[0]
    else:
        natureza_final = ''
    if len(natureza_inicial) > 0:
        natureza_inicial = natureza_inicial[0]
    else:
        natureza_inicial = ''
    if saldo_final != saldo_inicial:
        inconsistencias.append({'conta_contabil': conta_contabil, 'info_compl': info_compl, 'val_anterior': saldo_final, 'nat_anterior': natureza_final, 'nat_atual': natureza_inicial, 'val_atual': saldo_inicial})
    elif natureza_final != natureza_inicial:
        if saldo_final != 0 and saldo_inicial != 0:
            inconsistencias.append({'conta_contabil': conta_contabil, 'info_compl': info_compl, 'val_anterior': saldo_final, 'nat_anterior': natureza_final, 'nat_atual': natureza_inicial, 'val_atual': saldo_inicial})

inconsistencias = pd.DataFrame(inconsistencias)


# Mostrando resultados
num_inconsistencias = len(inconsistencias)
if num_inconsistencias == 0:
    logging.info('Não formam encontradas inconsistências!')
else:
    logging.warning(f'Foram encontradas {num_inconsistencias} inconsistências!')
    inconsistencias = inconsistencias[['conta_contabil', 'info_compl', 'val_anterior', 'nat_anterior', 'val_atual', 'nat_atual']]
    print(inconsistencias)

# Salva os dados
logging.info('Salvando a MSC...')
inconsistencias.to_excel(r'output\teste-msc-anterior-atual.xlsx', sheet_name='dados', header=True, index=False)

logging.info('Teste concluído...')