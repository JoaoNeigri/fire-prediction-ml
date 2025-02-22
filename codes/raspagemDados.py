# Bibliotecas para download e manipulacao das planilhas
import time
from selenium import webdriver
from zipfile import ZipFile
import pandas as pd
import math
import matplotlib.pyplot as plt
import os


anos = [2005, 2006, 2007, 2008, 2009]

# Baixa a base de dados
def sheetDownload(years): # obs: years é uma lista de anos (inteiro)

    # configurar o  navegador
    navigator = webdriver.Chrome()

    for year in years:       
        
        try: 
            # Download das planilhas dos anos solicitados
            url = 'https://portal.inmet.gov.br/uploads/dadoshistoricos/' + str(year) + '.zip'
            navigator.get(url)
        except Exception as eDataDownload:
            time.sleep(0.5)

        time.sleep(25)

# Extrai as pastas que foram baixadas
def unZipFolder(years):

    for year in years:

        filePath = 'C:\\Users\\pedro\\Downloads\\' + str(year) + '.zip'

        with ZipFile(filePath, 'r') as zip:
            zip.extractall('data_folder')    

# TESTE
def teste(years):
    for year in years:
        filePath = 'C:\\Users\\pedro\\Downloads\\' + str(year) + '.zip'
        
        with ZipFile(filePath, 'r') as zip:
            # Pasta onde os arquivos serão extraídos
            extract_path = 'data_folder/'+ str(year)
            os.makedirs(extract_path, exist_ok=True)  # Garante que a pasta do ano existe
            zip.extractall(extract_path)  # Extrai os arquivos para a pasta do ano
            
            # Reorganização (se necessário)
            extracted_items = os.listdir(extract_path)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(extract_path, extracted_items[0])):
                # Move o conteúdo da única pasta para a pasta do ano
                subfolder_path = os.path.join(extract_path, extracted_items[0])
                for item in os.listdir(subfolder_path):
                    os.rename(os.path.join(subfolder_path, item), os.path.join(extract_path, item))
                os.rmdir(subfolder_path)  # Remove a pasta extra

# Carrega o dataframe
def loadDf(years):
    
    dataframes = []

    # Carrega todas as planilhas em dataframes
    for year in years:

        filePath = 'C:\\Users\\pedro\\OneDrive\\Documentos\\FACULDADE\\7º Periodo\\Sistemas Inteligentes\\Projeto\\data_folder\\' + str(year) + '\\INMET_S_PR_A819_CASTRO_01-01-' + str(year) + '_A_31-12-' + str(year) + '.csv'

        try:

            df_aux = (pd.read_csv(filePath, sep=';', decimal=',', encoding='latin1', skiprows=8))
            
            # obs: renomeia as colunas, pois ao passar dos anos o padrão do INMET foi alterado (A partir da base de 2019)
            df_aux.rename(columns={df_aux.columns[0]: 'DATA', df_aux.columns[1]: 'HORA', df_aux.columns[9]: 'temp', df_aux.columns[15]: 'umidade'}, inplace=True)

            dataframes.append(df_aux)
        except Exception as eDataFrame:
            print('ERRO: Falha ao carregar Data Frame')

    # Concatena os dataframes
    df = pd.concat(dataframes, ignore_index=True, join='outer')
    
    # Filtra todas as linhas para ter apenas os horários 16 UTC
    df = df[(df['HORA'] == '16:00') | (df['HORA'] == '1600 UTC')]

    # Padroniza os horários
    df.loc[df['HORA'] != '16:00', 'HORA'] = '16:00'
    df['HORA'] = pd.to_datetime(df['HORA'], format='%H:%M').dt.time

    # Tranforma o tipo primitivo das datas para (datetime)
    df['DATA'] = df['DATA'].str.replace('/', '-')
    df['DATA'] = pd.to_datetime(df['DATA'])

    # Transforma a data num indice
    df.set_index('DATA', inplace=True)


    df.to_csv('output.csv', index=False, sep=';')
    print("Arquivo CSV exportado com sucesso!")

    return df

sheetDownload(anos)
unZipFolder(anos)
