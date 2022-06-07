'''
Configurações
'''

# Caminho para balancete.xlsx do mês da conferência
msc_atual = r'C:\Users\Everton\OneDrive\Prefeitura\2022\MSC\2022-05\balancete.xls'
#msc_atual = r'teste/msc_atual.xls'

# Caminho para o balancete.xlsx do mês anterior
msc_anterior = r'C:\Users\Everton\OneDrive\Prefeitura\2022\MSC\2022-04\balancete.xls'
#msc_anterior = r'teste/msc_anterior.xls'


# Caminho para o BAL_VER.csv geerado pelo pad-converter
bal_ver = r'C:\Users\Everton\OneDrive\Prefeitura\PAD\2022-05\BAL_VER.csv'
#bal_ver = r'teste/BAL_VER.csv'

# Caminho para o tce_4111.csv geerado pelo pad-converter
tce_4111 = r'C:\Users\Everton\OneDrive\Prefeitura\PAD\2022-05\tce_4111.csv'
#tce_4111 = r'teste/tce_4111.csv'



# Configurações de logger (NÃO MUDAR se não souber o que está fazendo)
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S'
)
