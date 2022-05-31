'''
Prepara o BAL_VER
'''

import pandas as pd
from datetime import datetime, timedelta

# Importa as configurações
exec(open('00-configuracoes.py').read())

logging.info('Preparando BAL_VER...')

# Carrega os dados
logging.info('Carregando dados...')
balver = pd.read_csv(bal_ver, sep=';', thousands='.', decimal=',', encoding='cp1252')
diario = pd.read_csv(tce_4111, sep=';', thousands='.', decimal=',', encoding='cp1252', parse_dates=['data_lancamento'], infer_datetime_format=True, dayfirst=True)

# Salva a data_base
data_base = balver['data_final'].unique()[0]
with open(r'cache/data_base.txt', 'w') as f:
    f.write(data_base)

# Calcula data de corte
dt = datetime.strptime(data_base, '%d/%m/%Y').replace(day=1)
data_corte = dt - timedelta(days=1)
data_corte = data_corte.strftime('%Y-%m-%d')

# Filtra apenas as contas analíticas/escrituráveis
balver = balver.query('escrituracao == "S" | escrituracao == "s"')

# Carrega os mapeamentos
cc_map = pd.read_excel('mapeamentos.xlsx', sheet_name='Contábil')
cc_map.columns = ['cc_tce', 'cc_msc']

# Troca os códigos do TCE pelos da STN conforme o mapeamento
logging.info('Trocando códigos do TCE pelos da MSC...')
if not cc_map.empty:
    for index, row in cc_map.iterrows():
        cc_tce = row['cc_tce']
        cc_msc = row['cc_msc']
        balver.loc[balver['conta_contabil'].str.startswith(cc_tce), 'conta_contabil'] = cc_msc
        diario.loc[diario['conta_contabil'].str.startswith(cc_tce), 'conta_contabil'] = cc_msc
# Converte os códigos contábeis ao padrão da MSC
balver['conta_contabil'] = balver.conta_contabil.str.replace('.', '', regex=False).str[0:9]
diario['conta_contabil'] = diario.conta_contabil.str.replace('.', '', regex=False).str[0:9]

# Agrega os valores por conta contábil do bal_ver e mantém as colunas de interesse
logging.info('Agregando valores e selecionando colunas de interesse...')
balver = balver[[
    'conta_contabil',
    'saldo_anterior_debito',
    'saldo_anterior_credito',
]].groupby(by='conta_contabil', as_index=False).sum()

# Seleciona as colunas de interesse do diário
diario = diario[[
    'conta_contabil',
    'data_lancamento',
    'valor',
    'tipo_lancamento'
]]

# Modifica a forma de exibição da natureza do saldo para ser igual à MSC
logging.info('Ajustando saldo inicial do período...')
balver['saldo_inicial_valor'] = abs(balver.saldo_anterior_debito - balver.saldo_anterior_credito)
balver['saldo_inicial_natureza'] = ["D" if row['saldo_anterior_debito'] > row['saldo_anterior_credito'] else "C" for index, row in balver.iterrows()]
balver['saldo_inicial_natureza'] = [row['saldo_inicial_natureza'] if row['saldo_inicial_valor'] != 0 else '' for index, row in balver.iterrows()]
balver.drop(labels=['saldo_anterior_debito', 'saldo_anterior_credito'], axis='columns', inplace=True)
balver['classe_contabil'] = balver.conta_contabil.str[0:1]
balver.astype({'classe_contabil': int})

# Calcula o saldo final do período anterior
movimento_debito_anterior = diario.query(f'data_lancamento <= "{data_corte}" & (tipo_lancamento == "D" | tipo_lancamento == "d")')[['conta_contabil', 'valor']].groupby(by='conta_contabil').sum()
movimento_credito_anterior = diario.query(f'data_lancamento <= "{data_corte}" & (tipo_lancamento == "C" | tipo_lancamento == "c")')[['conta_contabil', 'valor']].groupby(by='conta_contabil').sum()

# Calcula o saldo inicial do mês da conferência
temp = []
for index, row in balver.iterrows():
    conta_contabil = row['conta_contabil']
    saldo_inicial_valor = round(row['saldo_inicial_valor'], 2)
    saldo_inicial_natureza = row['saldo_inicial_natureza']
    debitos = round(movimento_debito_anterior.query(f'conta_contabil == "{conta_contabil}"')['valor'].sum(), 2)
    creditos = round(movimento_credito_anterior.query(f'conta_contabil == "{conta_contabil}"')['valor'].sum(), 2)
    classe_contabil = int(row['classe_contabil'])
    if classe_contabil in [1, 3, 5, 7]:
        if saldo_inicial_natureza == 'D':
            saldo_inicial_valor = round(saldo_inicial_valor + debitos - creditos, 2)
            if saldo_inicial_valor > 0:
                saldo_inicial_natureza = 'D'
            else:
                saldo_inicial_natureza = 'C'
                saldo_inicial_valor = abs(saldo_inicial_valor)
        else:
            saldo_inicial_valor = round(saldo_inicial_valor - debitos + creditos, 2)
            if saldo_inicial_valor > 0:
                saldo_inicial_natureza = 'C'
            else:
                saldo_inicial_natureza = 'D'
                saldo_inicial_valor = abs(saldo_inicial_valor)
    else:
        if saldo_inicial_natureza == 'C':
            saldo_inicial_valor = round(saldo_inicial_valor - debitos + creditos, 2)
            if saldo_inicial_valor > 0:
                saldo_inicial_natureza = 'C'
            else:
                saldo_inicial_natureza = 'D'
                saldo_inicial_valor = abs(saldo_inicial_valor)
        else:
            saldo_inicial_valor = round(saldo_inicial_valor + debitos - creditos, 2)
            if saldo_inicial_valor > 0:
                saldo_inicial_natureza = 'D'
            else:
                saldo_inicial_natureza = 'C'
                saldo_inicial_valor = abs(saldo_inicial_valor)
    temp.append({'conta_contabil': conta_contabil, 'saldo_inicial_valor': saldo_inicial_valor, 'saldo_inicial_natureza': saldo_inicial_natureza, 'classe_contabil': classe_contabil})

balver = pd.DataFrame(temp)


# Calcula o movimento de débito/crédito do mês
logging.info('Calculando o movimento e saldo final do período...')
movimento_debito = diario.query(f'data_lancamento > "{data_corte}" & (tipo_lancamento == "D" | tipo_lancamento == "d")')[['conta_contabil', 'valor']].groupby(by='conta_contabil', as_index=False).sum()
movimento_credito = diario.query(f'data_lancamento > "{data_corte}" & (tipo_lancamento == "C" | tipo_lancamento == "c")')[['conta_contabil', 'valor']].groupby(by='conta_contabil', as_index=False).sum()
movimento_debito['debito'] = round(movimento_debito['valor'], 2)
movimento_credito['credito'] = round(movimento_credito['valor'], 2)
movimento_debito.drop(labels=['valor'], axis='columns', inplace=True)
movimento_credito.drop(labels=['valor'], axis='columns', inplace=True)

# Incorpora a movimentação de débito/crédito do mês e calcula o saldo final
temp = []
for index, row in balver.iterrows():
    conta_contabil = row['conta_contabil']
    saldo_inicial_valor = round(row['saldo_inicial_valor'], 2)
    saldo_inicial_natureza = row['saldo_inicial_natureza']
    debito = round(movimento_debito.query(f'conta_contabil == "{conta_contabil}"')['debito'].sum(), 2)
    credito = round(movimento_credito.query(f'conta_contabil == "{conta_contabil}"')['credito'].sum(), 2)
    classe_contabil = int(row['classe_contabil'])
    if classe_contabil in [1, 3, 5, 7]:
        if saldo_inicial_natureza == 'D':
            saldo_final_valor = round(saldo_inicial_valor + debito - credito, 2)
            if saldo_final_valor > 0:
                saldo_final_natureza = 'D'
            else:
                saldo_final_natureza = 'C'
                saldo_final_valor = abs(saldo_final_valor)
        else:
            saldo_final_valor = round(saldo_inicial_valor - debito + credito, 2)
            if saldo_final_valor > 0:
                saldo_final_natureza = 'C'
            else:
                saldo_final_natureza = 'D'
                saldo_final_valor = abs(saldo_final_valor)
    else:
        if saldo_inicial_natureza == 'C':
            saldo_final_valor = round(saldo_inicial_valor - debito + credito, 2)
            if saldo_final_valor > 0:
                saldo_final_natureza = 'C'
            else:
                saldo_final_natureza = 'D'
                saldo_final_valor = abs(saldo_final_valor)
        else:
            saldo_final_valor = round(saldo_inicial_valor + debito - credito, 2)
            if saldo_final_valor > 0:
                saldo_final_natureza = 'D'
            else:
                saldo_final_natureza = 'C'
                saldo_final_valor = abs(saldo_final_valor)
    temp.append({
        'conta_contabil': conta_contabil,
        'saldo_inicial_valor': saldo_inicial_valor,
        'saldo_inicial_natureza': saldo_inicial_natureza,
        'movimento_debito': debito,
        'movimento_credito': credito,
        'saldo_final_valor': round(saldo_final_valor, 2),
        'saldo_final_natureza': saldo_final_natureza
    })

balver = pd.DataFrame(temp)

# Remove as naturezas dos saldos inicial e final 0.00 e NaN
logging.info('Limpando dados...')
balver['saldo_inicial_natureza'] = [None if row['saldo_inicial_valor'] == 0.0 else row['saldo_inicial_natureza'] for index, row in balver.iterrows()]
balver['saldo_final_natureza'] = [None if row['saldo_final_valor'] == 0.0 else row['saldo_final_natureza'] for index, row in balver.iterrows()]
balver['saldo_inicial_natureza'] = [None if row['saldo_inicial_valor'] is None else row['saldo_inicial_natureza'] for index, row in balver.iterrows()]
balver['saldo_final_natureza'] = [None if row['saldo_final_valor'] is None else row['saldo_final_natureza'] for index, row in balver.iterrows()]

# Remove linhas com saldo inicial, débitos, créditos e saldo final 0.00 ou NaN
balver.drop(balver[(balver['saldo_inicial_valor'] == 0.0) & (balver['movimento_debito'] == 0.0) & (balver['movimento_credito'] == 0.0) & (balver['saldo_final_valor'] == 0.0)].index, inplace=True)
balver.dropna(subset=['saldo_inicial_valor', 'movimento_debito', 'movimento_credito', 'saldo_final_valor'], inplace=True)

# Salvando os dados
logging.info('Salvando o BAL_VER no cache...')
balver.to_excel(r'cache\balver.xlsx', sheet_name='dados', header=True, index=False)

logging.info('BAL_VER pronto!')