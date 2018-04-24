import requests 
import time
import sys
import json
import re
import random

#Script by SrBill / taringa.net/RokerL
#Script funcional solo para la V7
shoutss = []
class TaringApi:
	def __init__(self):#variables iniciales
		self.logeado = False
		self.header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
		self.pagina_home = "https://taringa.net/"
		self.pagina_login = "https://www.taringa.net/registro/login-submit.php"
		self.pagina_deslogear = "https://www.taringa.net/ajax/user/logout"
		self.pagina_agregado_shout = "https://www.taringa.net/ajax/shout/add"
		self.pagina_agregado_post = "https://www.taringa.net/ajax/post/add"
		self.pagina_enviarMensaje = "https://www.taringa.net/ajax/mp/compose"
		self.pagina_responder_mensaje = "https://www.taringa.net/ajax/mensajes/responder"
		self.pagina_subir_imagen = "https://www.taringa.net/ajax/shout/attach"
		self.pagina_shoutear_en_muro = "https://www.taringa.net/ajax/wall/add-post"
		self.pagina_shoutear = "https://www.taringa.net/ajax/shout/add"
		self.pagina_acciones = "https://www.taringa.net/notificaciones-ajax.php" #seguir
		self.pagina_denuncia = "http://www.taringa.net/denuncia.php"
		self.pagina_bloquearUsuario = "https://www.taringa.net/ajax/user/block"
		self.pagina_subir_miniatura = "https://www.taringa.net/ajax/kn3-signdata.php"
		self.pagina_agregar_fuente = "https://www.taringa.net/ajax/source/data-add"#
		self.pagina_recortar_imagen = "https://apikn3.taringa.net/image/crop"
		self.pagina_comentarUnPost = "https://www.taringa.net/ajax/comments/add"
		self.pagina_dar_like = "https://www.taringa.net/serv/shout/like"
		self.pagina_dar_unlike = "https://www.taringa.net/serv/shout/unlike"
		self.pagina_reshoutear = "https://www.taringa.net/serv/shout/reshout"
		self.pagina_comentarShout = "https://www.taringa.net/serv/comment/add/"
		self.pagina_votar_shout = "https://www.taringa.net/ajax/shout/vote"
		self.pagina_posts_recientes = "https://www.taringa.net/posts/recientes"
		self.pagina_posts_ascenso = "https://www.taringa.net/posts/ascenso"
		self.pagina_puntuar_post = "https://www.taringa.net/ajax/post/vote"
		self.key_seguridad = None
		self.id_usuario = None
		self.usuario_actual = None
		self.sesion_actual = requests.Session()
		#Etiquetas de referencia para extraer del html de alguna pagina, el '(.+)' es el dato a extraer
		self.html_regex = {
			"id_usuario_propio":	"'User_Id', '(.+)', 2 ]", 
			"id_usuario":"<a obj=\"user\" objid=\"(.+)\" er",
			"id_muro":		"<a obj=\"user\" objid=\"(.+)\" errorContainer",  
			"id_shout": "\"id\":\"(.+)\",\"url\"",
			"nickname_usuario": "class=\"hovercard shout-user_name\">(.+)</a>" ,
			"key_seguridad": "user_key: '(.+)', postid:",
			"shout_feed_id": "<article class=\"shout-item shout-item_simple  \" id=\"item_(.+)\" data-fetchid",
			"shout_feed_url": "<li><a href=\"(.+)\" class=\"og-link icon-comments light-shoutbox \"",
			"post_id":"Comments.objectOwner =  '(.+)';",
			"posts_feed_url": "<a href=\"(.+)\" class=\"avatar list-l__avatar\">",
	
		}

	def peticionPOST(self, url, datos={}):
		return self.sesion_actual.post(url, data=datos, verify=True)
	
	def recode(self, text): #para el Error de chrmap
		return str(text).encode("utf-8").decode("utf-8")
		
	def peticionGET(self, url):
		return self.sesion_actual.get(url)
		
	def extraerDatoHtml(self, etiqueta, codigo):
		""" Para evitar el uso de bs4 se pasa directamente alguna referencia de la etiqueta 
		    en formato regex para extraer un dato de la pagina"""
		return re.findall(etiqueta, str(codigo))
		
	def estasLogeado(wrp): #wrapper para verificar que haya una sesion iniciada
		def verificarLogin(self, *args, **kwargs):
			if(self.logeado):
				print("==========================")
				try:
					return wrp(self, *args, **kwargs)
				except Exception:
					print("Ocurrió un error desconocido:", sys.exc_info()[1])
				print("==========================")
			else:
				print("[-]No hay una sesion iniciada o expiro(?)")
			
		return verificarLogin
				
	def logear(self,usuario,contraseña):#Logear con cuenta en taringa
		self.usuario_actual = usuario
		print("[+]Logeando..")
		parametros_login = {
			"connect":"",
			"nick":usuario,
			"pass":contraseña,
			"redirect":"/"+usuario,
		}
		logeo = self.peticionPOST(self.pagina_login,datos=parametros_login,)#solicitud de POST		
		json_generado = str(logeo.content)
		if "\"status\":1" in json_generado:
			print("[+]Logeado correctamente, sesión creada")
			print("[+]Extrayendo key..")
			if self.key_seguridad is None:
				code = self.peticionGET(self.pagina_home+"/"+usuario).text
				self.id_usuario = self.extraerDatoHtml(self.html_regex["id_usuario_propio"], code)[0]
				self.key_seguridad = self.extraerDatoHtml(self.html_regex["key_seguridad"], code)[0]
				print("[+]Datos extraidos..")
				print("[+]Tu key es "+self.key_seguridad)
			self.logeado = True
		else:
			print("[+]Fallo el logeo")

	def deslogear(self):#Deslogear de la pagina
		if self.sesion_actual:
			print("[+]Deslogeando..")
			parametros_deslogear = {"key":self.key_seguridad}
			deslog = self.peticionPOST(self.pagina_deslogear,datos=parametros_deslogear)
			print("[+]Listo")
			print(deslog.text)
			
	@estasLogeado
	def enviarMensaje(self,asunto,mensaje,para):#Enviar mensaje a usuario
		parametros_mensaje = {
			"captcha":"a",
			"key": self.key_seguridad,
			"msgSubject": asunto,
			"msgText": mensaje,
			"msgTo": para,
			"recaptcha":"indefinedd"
		}
		print("Payload de mensaje:",parametros_mensaje)
		print("[+]Enviando mensaje..")
		mensaje = self.sesion_actual.post(self.pagina_enviarMensaje,data=json.dumps(parametros_mensaje), verify=True)
		print(mensaje.text)
		if "no valido" in mensaje:
			print("[-]Error al enviar el mensaje")
		else:
			print("[+]El mensaje fue enviado correctamente a "+para)
	
	def conseguirIdDeUsuario(self,usuario):
		codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
		id_usuario = self.extraerDatoHtml(self.html_regex["id_usuario"], codigo_pagina.text)	
		if id_usuario:
			return id_usuario[0]
		else:
			return False
	
####Acciones de Shouts
	def conseguirIdMuroDeUsuario(self, usuario):
		codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
		id_muro = self.extraerDatoHtml(self.html_regex["id_muro"], str(codigo_pagina.text))
		if id_muro:
			return id_muro[0]
		else:
			return False
	
	def conseguirInfoDeShout(self, url_shout):
		codigo_pagina = self.sesion_actual.get(url_shout)
		id_shout = self.extraerDatoHtml(self.html_regex['id_shout'],codigo_pagina.text)	
		nombre_usuario = self.extraerDatoHtml(self.html_regex['nickname_usuario'],codigo_pagina.text)	
		id_muro = self.extraerDatoHtml(self.html_regex['id_muro'], codigo_pagina.text)
		#~ if id_muro == []:id_muro = [""]
		if id_shout:
			return {'id':id_shout[0],
					'nombre_usuario':nombre_usuario[0],
					'id_muro':id_muro[0],
					}
		else:
			return False

	@estasLogeado
	def votarShout(self, url_shout):
		info_shout = self.conseguirInfoDeShout(url_shout)
		parametros_votar = {
			"key":self.key_seguridad,
			"uuid":info_shout['id'],
			"owner":info_shout['id_muro'],
			"score":1
		}
		voto = self.peticionPOST(self.pagina_votar_shout, datos=parametros_votar)
		print("Mensaje del servidor: " , voto.text)
		
	@estasLogeado
	def shoutear(self,contenido,media_url=None):#Publicar un shout: cuerpo del mensaje / url de contenido(opcional)
		tipo_contenido = "1"
		if media_url:
			if "youtu" in media_url:
				tipo_contenido = "2"
			if "kn3" in media_url:
				url_subida = media_url#SI ya esta subido a taringa
			else:
				url_subida = self.subirArchivoDesdeUrl(media_url)
				
		else:url_subida = ""
		parametros_shout = {
				"attachment":url_subida,
				"attachment_type":tipo_contenido,
				"body":contenido,
				"key":self.key_seguridad,
				"privacy":"0"
		}
		print(parametros_shout)
		shout = self.peticionPOST(self.pagina_shoutear, datos=parametros_shout)
		print("Informacion de POST:",shout.text)
		print("Shout creado::::::::::::")
		print(contenido)
		print(url_subida)
		print("::::::::::::::::::::::::")
		print("[+]Mensaje shouteado")

	@estasLogeado		
	def shoutearAUsuario(self,usuario,mensaje,media_url=None):#Postear shout en muro de usuario
		id_muro = self.conseguirIdMuroDeUsuario(usuario)
		url_subida = ""
		tipo_contenido = 0
		if id_muro:
			print("[+]ID de muro:"+str(id_muro))
			if media_url:
				if "youtu" in media_url:tipo_contenido = "2"
				else:tipo_contenido = "1"
				if "kn3" in media_url:url_subida = media_url#SI ya esta subido a taringa
				else:url_subida = self.subirArchivoDesdeUrl(media_url)#si no se sube
			parametros_shoutear_muro = {
				"key":self.key_seguridad,
				"body":mensaje,
				"privacy":"undefined",
				"attachment_type":tipo_contenido,
				"attachment":url_subida,
				"wall":id_muro
			}
			print(parametros_shoutear_muro)
		shout = self.peticionPOST(self.pagina_shoutear_en_muro,datos=parametros_shoutear_muro)
		print(shout.text)
		if "No puedes" in shout.text:
			print("[-]Error al postear el shout en el muro del usuario "+usuario)
		else:
			print("[+]Shout publicado en el muro de "+usuario+" correctamente..")

	@estasLogeado
	def likearShout(self,url_shout=None):#Darle Like a un shout
		if "https" in url_shout:
			info_shout = self.conseguirInfoDeShout(url_shout)
			id_shout = info_shout['id']
		else:
			info_shout = None
			id_shout = url_shout #en caso de que se inserte el id directamente
		if id_shout:
			print("[+]Id de shout:"+id_shout)
		parametros_likearShout  = {
			"key":self.key_seguridad,
			"object_id": id_shout,
		}
		post =self.peticionPOST(self.pagina_dar_like, datos=parametros_likearShout)
		if "successfully" in str(post.text):
			print("[+]Se le dio Like al shout "+ id_shout + " del usuario " + info_shout['nombre_usuario'] )
		else:
			print("[-]Error al dar Likeal shout "+ id_shout + " del usuario " + info_shout['nombre_usuario'] )
	
	@estasLogeado
	def comentarShout(self,url_shout,comentario):#Comentar un shout por url
		info_shout = self.conseguirInfoDeShout(url_shout)
		id_shout = info_shout['id']
		if id_shout:
			print("[+]Id de shout:"+id_shout)
		parametros_comentarShout  = {
			"key":self.key_seguridad,
			"object_type": 'shout',
			"body":comentario,
		}
		post = self.peticionPOST(self.pagina_comentarShout+id_shout, datos=parametros_comentarShout)
		print(post.text)
		print("[+]Se agrego un comentario al shout "+ id_shout + " del usuario " + info_shout['nombre_usuario'] )
	
	@estasLogeado
	def reshoutear(self,url_shout):#compartir en el muro un shout
		info_shout = self.conseguirInfoDeShout(url_shout)
		id_shout = info_shout['id']
		if id_shout:
			print("[+]Id de shout:"+id_shout)
		parametros_reshoutear  = {
			"key":self.key_seguridad,
			"object_id": id_shout,
		}
		post = self.peticionPOST(self.pagina_reshoutear, datos=parametros_reshoutear)
		print(post.text)
		print("[+]Se reshouteo el shout "+ id_shout + " del usuario " + info_shout['nombre_usuario'] )
	
	@estasLogeado
	def unlikearShout(self,url_shout):#Darle Unlike a un shout
		info_shout = self.conseguirInfoDeShout(url_shout)
		id_shout = info_shout['id']
		if id_shout:
			print("[+]Id de shout:"+id_shout)
		parametros_unlikearShout  = {
			"key":self.key_seguridad,
			"object_id": id_shout,
		}
		post = self.peticionPOST(self.pagina_dar_unlike, datos=parametros_unlikearShout)
		print(post.text)
		print("[+]Se le dio Unlike al shout "+ id_shout + " del usuario " + info_shout['nombre_usuario'] )
	
####Acciones generales
	def subirArchivoDesdeUrl(self,url):#Subir un archivo al servidor de taringa
		parametros_subida = {
			"isImage":"1",
			"key":self.key_seguridad,
			"url":url
		}
		if self.logeado:
			print("[+]Subiendo imagen..")
			subida = self.peticionPOST(self.pagina_subir_imagen,datos=parametros_subida)
			if "no valido" in subida.text:
				print("[-]Error de subida..")
				return False
			else:
				json_img = json.loads(subida.text)
				url_final = json_img["data"]["url"]
				tipo_archivo = json_img["data"]["type"]
				return url_final
	
	@estasLogeado
	def comentarUnPost(self,url_post,comentario, url_imagen=None):#Comentar un post
		if "http" in url_post:
			post = self.peticionGET(url_post).text
			id_post = url_post.split("/")[5]
			id_objeto = self.extraerDatoHtml(self.html_regex["post_id"], post)[0]
			print("	[+]Post a comentar:",url_post)
		if url_imagen:
			comentario = comentario + "[img="+url_imagen+"]"
		parametros_comentario = {
			"comment":comentario,
			"key":self.key_seguridad,
			"objectId":id_post,
			"objectOwner":id_objeto,
			"objectType":"post",
			"show":"True"
		
		}
		comentario = self.peticionPOST(self.pagina_comentarUnPost,datos=parametros_comentario)
		print("Mensaje Post:", comentario.text)
		if "agregado" in str(comentario.text):
			print("[+]Comentario agregado satisfactoriamente..")
			print(comentario.text)
		else:
			print("[-]Error al agregar el comentario..")
			print(comentario.text)
	
	@estasLogeado
	def subirImagenEnMiniatura(self,url):#Subir una imagen miniatura para un post
		print("[+]Subiendo imagen")
		parametros_subida = {
			"key":self.key_seguridad,
			"url":url,
			"x1": "138",
			"x2": "487",
			"y1":"0",
			"y2": "350"
		}
		subir_imagen = self.sesion_actual.post(
				self.pagina_subir_miniatura,
				data=parametros_subida,
				verify=True)
		subida_final = self.sesion_actual.post(
			self.pagina_recortar_imagen,
			data=json.loads(str(subir_imagen.text)),
			verify=True
		)
		url_subida = json.loads(subida_final.text)
		if "url" in url_subida:
			print("[+]Imagen miniatura subida correctamente:"+url_subida["url"])
			return url_subida["url"]
	
	@estasLogeado
	def crearPost(self,titulo,contenido,imagen_previa,etiquetas,fuente_contenido,categoria,verificar=False):#Crear y publicar post
		imagen_previa = self.subirImagenEnMiniatura(imagen_previa)
		categorias = {
			"categoria":"10",
			"animaciones":"7",
			"apuntes y monografia":"18",
			"arte":"4",
			"autos y motos":"25",
			"celulares":"17",
			"ciencia y educacion":"33",
			"comics":"19",
			"deportes":"16",
			"downloads":"9",
			"ebooks y tutoriales":"23",
			"ecologia":"34",
			"economia y negocios":"29",
			"femme":"24",
			"hazlo tu mismo":"35",
			"humor":"26",
			"imagenes":"1",
			"info":"12",
			"juegos":"0",
			"juegos online":"38",
			"links":"2",
			"linux":"15",
			"mac":"22",
			"manga y anime":"32",
			"mascotas":"30",
			"musica":"8",
			"noticias":"10",
			"offtopic":"5",
			"paranormal":"36",
			"recetas y cocinas":"21",
			"reviews":"37",
			"salud y bienestar":"27",
			"solidaridad":"20",
			"taringa":"28",
			"turismo":"31",
			"tv, peliculas y series":"13",
			"videos":"3",
		}
		#Agregar fuente de contenido en servidor:
		if fuente_contenido != "":
			parametros_fuente = {
				"key":self.key_seguridad,
				"url":fuente_contenido,
			}
			print("[+]Cargando fuente de contenido al servidor..")
			fuente_ = self.sesion_actual.post(self.pagina_agregar_fuente,data=parametros_fuente,verify=True)
			expr = re.findall("{\"id\":\"(.+)\",\"url\"",str(fuente_.text))
			if expr:
				fuente_contenido_id = expr[0]
		parametros_post = {
			"categoria":categorias[categoria],
			"borrador_id":"",#conseguir
			"cuerpo":contenido,
			"facebook-vinculation":"false",
			"id":"",
			"image_1x1":imagen_previa,#Imagen miniatura en 1x1
			"image_4x3":imagen_previa,#Imagen previa
			"key":self.key_seguridad,#key seguridad
			"own-source":"0",
			"sin_comentarios":"0",
			"source_url[]":fuente_contenido,#Fuente del contenido
			"sources_url_id[]":fuente_contenido_id,#??
			"tags":",".join([i for i in etiquetas.split(",")]),#tags separado en comas
			"titulo":titulo,#titulo
			"twitter-vinculation":"false",
			"vinculation_offer":"false",
		}
		if verificar:
			confirmar = input("[+]Deseas publicar el post? s/n:")
			if confirmar.lower() == "s":
				print("[+]Enviando post...")
				post = self.sesion_actual.post(self.pagina_agregado_post,data=parametros_post)
				if "\"status\":1" in str(post.text):
					print(post.text)
					print("[+]Post agregado exitosamente..")
		else:
				print("[+]Enviando post...")
				post = self.sesion_actual.post(self.pagina_agregado_post,data=parametros_post)
				if "\"status\":1" in str(post.text):
					print(post.text)
					print("[+]Post agregado exitosamente..")

	@estasLogeado
	def seguirUsuario(self,usuario):#Seguir a un usuario
		codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
		id_muro = self.conseguirIdDeUsuario(usuario)
		if id_muro:
			print("[+]Id de usuario:"+id_muro)
		parametros_seguirUsuario = {
			"action":"follow",
			"key":self.key_seguridad,
			"obj":id_muro,
			"type":"user"
			
		}
		print(parametros_seguirUsuario)
		foll = self.sesion_actual.post(self.pagina_acciones,data=parametros_seguirUsuario,verify=True)
		print(foll.text)
		print("[+]Usuario "+usuario+" seguido.")
	
	@estasLogeado
	def dejarDeSeguirUsuario(self,usuario):#No seguir mas a un usuario
		codigo_pagina = self.peticionGET(self.pagina_home+"/"+usuario)
		id_muro = self.conseguirIdDeUsuario(usuario)
		if id_muro:
			print("[+]Id de usuario:"+id_muro[0])
		parametros_seguirUsuario = {
			"action":"unfollow",
			"key":self.key_seguridad,
			"obj":id_muro,
			"type":"user"
			
		}
		post = self.peticionPOST(self.pagina_acciones,datos=parametros_seguirUsuario)
		print(post.text)
		print("[+]Usuario "+usuario+" no seguido")
	
	@estasLogeado
	def denunciarPost(self,post,razon,aclaracion,preguntar=False):#Denunciar un post
		print("[+]Iniciando denuncia..")
		razones = {
			"ofensivo":"108",
			"contenido para mi taringa!":"104",
			"agresivo":"112",
			"contenido no disponible":"111",
			"contenido para mi taringa":"104",
			"contenido para comunidad":"103",
			"pedofilia":"107",
			"violencia":"102",
			"informacion personal":"109",
			"descargas":"106",
			"virus":"105",
			"mala fuente":"110",
			"categoria incorrecta":"101",
			"muchas mayusculas":"113",
			"114":"violacion copyrigth",
			"115":"otros"
			}#Buscar mas id de razones
		if preguntar:
			print("[+]Elegir una razon para la denuncia (titulo):")
			for i in razones:
				print(str(i)+"==>"+str(razones[i]))
			raz = input("razon:")
			for i in razones:
				if raz in i:
					razon_final = razones[i]
		else:
			if razon not in razones:
				print("[-]No se encuentra una razon..")
				return False
			razon_final = razones[razon]
		if "http" in post:
			link_ = post.split("/")
			link = link_[5]
			print("	[+]Post a denunciar:",link_[6])
		else:
			link = post
			print("	[+]ID de post a denunciar:",link)
		parametros_denuncia = {
			"cuerpo":aclaracion,
			"razon":razon_final,
			"id":link
		}
		print("	[+]Razón:"+razon)
		print(" 	[+]Aclaración:"+aclaracion)
		print(parametros_denuncia)
		confirmacion = input("Proceder con la denuncia? s/n:")
		if confirmacion.lower() == "s":
			den = self.peticionPOST(self.pagina_denuncia,datos=parametros_denuncia)
			if "Ya habias denunciado este post" in str(den.text):
				print("[-]Ya se habia denunciado este post con esta cuenta!")
			elif "La denuncia fue enviada" in str(den.text):
				print("[+]Denuncia enviada!")
			else:
				print("[?]Error al enviar la denuncia?")
		else:
			print("[-]Denuncia cancelada")

	def votarPost(self, url_post, cantidad_puntos=10):
		print("[+]Puntuando ", url_post)
		if "http" in url_post:
			id_post = url_post.split("/")[5]
			peticion_token = self.recode(self.peticionGET(url_post).text)
			regex = str(cantidad_puntos) + ", '(.+)'\)\" class=\"require-login\""
			token = self.extraerDatoHtml(regex, peticion_token)
		else:
			return False
		if token:
			token = token[0]
		else:
			print("[-]No se pudo obtener el token o no tienes mas puntos para dar hoy.")
		parametros_puntuar = {
				"key":self.key_seguridad,
				"puntos":cantidad_puntos,
				"x":token,
				"postid":id_post,
		}
		puntuacion = self.peticionPOST(self.pagina_puntuar_post, datos=parametros_puntuar)
		print("Mensaje servidor:", puntuacion.text)
		return 
#####Acciones usuarios
	@estasLogeado
	def bloquearUsuario(self,usuario):#Bloquear usuario
		print("[+]Bloqueando usuario")
		id_usuario = self.conseguirIdDeUsuario(usuario)
		parametros_bloqueo = {
			"bloqueado":"1",
			"key":self.key_seguridad,
			"user":id_usuario,
		}
		print(parametros_bloqueo)
		bloq = self.peticionPOST(self.pagina_bloquearUsuario,datos=parametros_bloqueo)
		if "satisfactoriamente" in bloq.text:
			print("[+]%s fue bloqueado"%usuario)
		else:
			print("[-]Error al bloquear usuario..")
		
	@estasLogeado		
	def desbloquearUsuario(self,usuario):#Desbloquear usuario
		print("[+]Desbloqueando usuario")
		id_usuario = self.conseguirIdDeUsuario(usuario)
		parametros_bloqueo = {
			"key":self.key_seguridad,
			"user":id_usuario,
		}
		post = self.peticionPOST(self.pagina_bloquearUsuario,datos=parametros_bloqueo)
		if "satisfactoriamente" in post.text:
			print("[+]%s fue desbloqueado"%usuario)
		else:
			print("[-]Error al desbloquear usuario..")
####Varias
	@estasLogeado
	def feedShouts(self):#Lanza la id/url de los shouts mas recientes
		peticion_feed = self.peticionGET("https://www.taringa.net/shouts/recent")
		recientes = self.extraerDatoHtml(self.html_regex["shout_feed_id"], peticion_feed.text)
		url = self.extraerDatoHtml(self.html_regex["shout_feed_url"], peticion_feed.text)
		shouts = []
		for a,b in zip(recientes,url):
			shouts.append((a,b))
		return shouts

	@estasLogeado
	def feedPost(self, tipo="home", pagina=0): #Lista de posts en su categoria reciente por defecto
		if tipo == "recientes":
			url_posts = self.pagina_posts_recientes
		elif tipo == "ascenso":
			url_posts = self.pagina_posts_ascenso
		else:
			url_posts = self.pagina_home
		if pagina:
			url_posts = url_posts+"/pagina"+pagina
		peticion_posts = self.peticionGET(url_posts).text
		recientes = self.extraerDatoHtml(self.html_regex["posts_feed_url"], self.recode(peticion_posts))
		return recientes
	
	@estasLogeado
	def comentarFeedPost(self, comentario, url_imagen=None): #comentar los posts de una pagina principal
		posts = self.feedPost(tipo="recientes")
		for post in posts:
			print("Comentando el post ", post)
			self.comentarUnPost(post, comentario, url_imagen)
			time.sleep(45)
			
	@estasLogeado
	def likearFeedShout(self):#Likea shouts de los recientes
		shouts_recientes  = self.feedShouts()
		mensajes = ["Interesante","Muy bueno xD", "Jajajajaja", ":winky",":grin:","auch",":L"]
		for shout_id in shouts_recientes:
			print("Likeando el shout ", shout_id[1])
			if(shout_id[1] in shoutss):pass
			else:
				shoutss.append(shout_id[1])
				self.likearShout(shout_id[1]) #likea el shout
				self.reshoutear(shout_id[1]) #lo reshoutea
				self.comentarShout(shout_id[1], random.choice(mensajes)) #comenta el shout
				self.seguirUsuario(shout_id[1].split("/")[3]) #sigue al usuario
				time.sleep(10) #espera 10 segundos
		


USUARIO = "Acá va el usuario"
CONTRASEÑA = "Acá va la contraseña"

if __name__ == "__main__":
	api = TaringApi()
	api.logear(USUARIO, CONTRASEÑA)
	api.shoutear("Python is Love <3")
	api.votarPost("https://www.taringa.net/posts/linux/19401863/Python-Controlar-funciones-taringa-Act-2018.html", cantidad_puntos=5)
	api.deslogear()
	
#24/04/2018
