#encoding: utf-8

from bs4 import BeautifulSoup
import re
import requests
import filecmp
import time
import telebot
import os
import sys

# ENTRADA
'''
info = str(sys.argv[1])
file = open(info, 'r')

site = file.readline()[:-1]
materia = file.readline()[:-1]
tempo = file.readline()
dia = list(file.readline())

file.close()
'''

# ENTRADA PERSONALIZADA
site = "https://<Blog>.blogspot.com.br/" # Link do blog que deseja monitorar
materia = "<NomeDisciplina>" # Nome da disciplina
tempo = "<Tempo>" # Tempo em segundos
dia = [3,0,4] # <[d1,d2,d3]> onde di são os dias das aulas. Parâmetros: 0 - Dia Importante; 1 - Seg; 2 - Ter; ...; 4 - Qui; 5 - Sex

# COMUNICAÇÃO DO BOT COM O TELEGRAM
bot = telebot.TeleBot('<KeyBotTelegram>')

# FUNÇÕES

def sendToUser(message):
	bot.send_message('<ChatID>', message)

def getPosts(data):
	soup = BeautifulSoup(data, 'html.parser')
	section = soup.select(".blog-posts")
	return str(section)

while True:
	currentTime = "[" + time.strftime("%d/%m/%Y %H:%M:%S") + "]"
	
	# Criar arquivo de log
	try:
		log = open(materia+".log",'r') # Abre o arquivo caso ele já exista
		textLog = log.readlines() # Carregar logs antigos
		#textLog = [] # Sobrepor logs antigos
		log.close()
	except:
		print("ERRO: Não foi possível abrir arquivo de log")
		textLog = []
		log = open(materia+".log",'w')
		log.close()

	# Baixar página
	try:
		r = requests.get(site)
		data = r.text
		data = getPosts(data)
	except:
		print(currentTime + " Houve um erro ao efetuar o download da página.")
		textLog.append(currentTime + " Houve um erro ao efetuar o download da página.\n")
	
	# VERFICADOR DOS SITES
	try:
		old = open("old"+materia+".html","r")
	except:
		old = open("old"+materia+".html","w")
		old.write(data.encode('utf-8'))
		old.close()

	new = open("new"+materia+".html","w")
	new.write(data.encode('utf-8'))
	new.close()

	oldName = 'old'+materia+'.html'
	newName = 'new'+materia+'.html'

	if not (filecmp.cmp(oldName,newName)):
		message = "Houve mudanças no site de " + materia + ".\nLink: "+site+"\n"
		
		# Info p/ o log
		#print(currentTime + " -> Houve atualização.")
		textLog.append(currentTime + " -> Houve atualização.\n")

		# Enviar notificação para o Telegram
		try:
			sendToUser(message)	
		except:
			#print(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram")
			textLog.append(currentTime + " Ocorreu um erro na hora de enviar a mensagem para o Telegram\n")
		
		# Atualizar arquivo antigo
		old = open("old"+materia+".html","w")
		old.write(data.encode('utf-8'))
		old.close()
	else:
		# Info p/ o log
		#print(currentTime + " -> Sem atualização.")
		textLog.append(currentTime + " -> Sem atualização.\n")

	# Sleep
	week = int(time.strftime("%w"))

	if(int(dia[0]) == 0): # Dia de prova, verifica de 0,5h em 0,5h
		#print(currentTime + " Verificando de 0,5h em 0,5h")
		textLog.append(currentTime + " Verificando de 0,5h em 0,5h.\n")
		
		# Escreve no log, e fecha o arquivo.
		log = open(materia+".log",'w')
		log.writelines(textLog)
		log.close()

		time.sleep(1800)

	elif(int(dia[0]) == week or int(dia[2]) == week): # No dia da aula, verifica de 1h em 1h
		#print(currentTime + " Verificando de 1h em 1h.")
		textLog.append(currentTime + " Verificando de 1h em 1h.\n")
		
		# Escreve no log, e fecha o arquivo.
		log = open(materia+".log",'w')
		log.writelines(textLog)
		log.close()

		time.sleep(3600)

	elif(int(dia[0])-1 == week or int(dia[2])-1 == week): # Verificar no dia anterior à aula
		#print(currentTime + " Verificando de 2h em 2h")
		textLog.append(currentTime + " Verificando de 2h em 2h\n")
		
		# Escreve no log, e fecha o arquivo.
		log = open(materia+".log",'w')
		log.writelines(textLog)
		log.close()

		time.sleep(7200)

	else: # Caso, contrário, verifa pelo tempo dado
		# Escreve no log, e fecha o arquivo.
		log = open(materia+".log",'w')
		log.writelines(textLog)
		log.close()

		time.sleep(int(tempo))
