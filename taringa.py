import requests 
import json
import re
#Script by SrBill / taringa.net/RokerL
class TaringApi:
	def __init__(self):#variables iniciales
		self.logeado = False
		self.sesion_actual = requests.Session()
		self.header = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"}
		self.pagina_home = "https://taringa.net/"
		self.pagina_login = "https://www.taringa.net/registro/login-submit.php"
		self.pagina_agregado_shout = "https://www.taringa.net/ajax/shout/add"
		self.pagina_agregado_post = "https://www.taringa.net/ajax/post/add"
		self.pagina_enviar_mensaje = "https://www.taringa.net/ajax/mp/compose"
		self.pagina_responder_mensaje = "https://www.taringa.net/ajax/mensajes/responder"
		self.pagina_subir_imagen = "https://www.taringa.net/ajax/shout/attach"
		self.pagina_deslogear = "http://www.taringa.net/ajax/user/logout"
		self.pagina_shoutear_en_muro = "https://www.taringa.net/ajax/wall/add-post"
		self.pagina_acciones = "http://www.taringa.net/notificaciones-ajax.php" #seguir
		self.pagina_denuncia = "http://www.taringa.net/denuncia.php"
		self.pagina_bloquear_usuario = "http://www.taringa.net/ajax/user/block"
		self.pagina_subir_miniatura = "http://www.taringa.net/ajax/kn3-signdata.php"
		self.pagina_agregar_fuente = "http://www.taringa.net/ajax/source/data-add"#
		self.pagina_recortar_imagen = "https://apikn3.taringa.net/image/crop"
		self.pagina_comentar_post = "http://www.taringa.net/ajax/comments/add"
		self.pagina_dar_like = "http://www.taringa.net/serv/shout/like"
		self.key_seguridad = None
		self.id_usuario = None
		self.usuario_actual = None
		
	def logear(self,usuario,contraseña):#Logear con cuenta en taringa
		self.usuario_actual = usuario
		print("[+]Logeando..")
		parametros_login = {
			"connect":"",
			"nick":usuario,
			"pass":contraseña,
			"redirect":"/"+usuario,
		}
		logeo = self.sesion_actual.post(
			self.pagina_login,
			data=parametros_login,
			verify=True
		)#solicitud de POST		
		json_generado = str(logeo.content)
		if "\"status\":1" in json_generado:
			print("[+]Logeado correctamente, sesión creada")
			print("[+]Extrayendo key..")
			if self.key_seguridad is None:
				code = self.sesion_actual.get(self.pagina_home+"/"+usuario)
				extracto = re.findall("var global_data = (.+);",str(code.text))
				if extracto:
					js = extracto[0]
					self.id_usuario = re.findall("user: '(.+)'",js.split(",")[0])[0]
					self.key_seguridad = re.findall("user_key: '(.+)'",js.split(",")[1])[0]
					print("[+]Datos extraidos..")
					print("[+]Tu key es "+self.key_seguridad)
			self.logeado = True
		else:
			print("[+]Fallo el logeo")

	def deslogear(self):#Deslogear de la pagina
		if self.sesion_actual:
			print("[+]Deslogeando..")
			parametros_deslogear = {"key":self.key_seguridad}
			deslog = self.sesion_actual.post(self.pagina_deslogear,data=parametros_deslogear,verify=True)
			print("[+]Listo")
			print(deslog.text)
	
	def subir_archivo_desde_url(self,url):#Subir un archivo al servidor de taringa
		parametros_subida = {
			"isImage":"1",
			"key":self.key_seguridad,
			"url":url
		}
		if self.logeado:
			print("[+]Subiendo imagen..")
			subida = self.sesion_actual.post(self.pagina_subir_imagen,data=parametros_subida,verify=True)
			if "no valido" in subida.text:
				print("[-]Error de subida..")
				return False
			else:
				json_img = json.loads(subida.text)
				url_final = json_img["data"]["url"]
				tipo_archivo = json_img["data"]["type"]
				return url_final
	
	def shoutear(self,contenido,media_url=None):#Publicar un shout: cuerpo del mensaje / url de contenido(opcional)
		if self.logeado:
			tipo_contenido = ""
			if media_url:
				if "youtu" in media_url:tipo_contenido = "2"
				else:tipo_contenido = "1"
				if "kn3" in media_url:url_subida = media_url#SI ya esta subido a taringa
				else:url_subida = self.subir_archivo_desde_url(media_url)
			else:url_subida = ""
			parametros_shout = {
					"attachment":url_subida,
					"attachment_type":tipo_contenido,
					"body":contenido,
					"key":self.key_seguridad,
					"privacy":"0"
			}
			shout = self.sesion_actual.post(
				self.pagina_agregado_shout,
				data=parametros_shout,
				verify=True
			)
			print("Informacion de POST:",shout.text)
			print("Shout creado::::::::::::")
			print(contenido)
			print(url_subida)
			print("::::::::::::::::::::::::")
			print("[+]Mensaje shouteado")
	
	def enviar_mensaje(self,asunto,mensaje,para):#Enviar mensaje a usuario
		if self.logeado:
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
			mensaje = self.sesion_actual.post(self.pagina_enviar_mensaje,data=json.dumps(parametros_mensaje), verify=True)
			print(mensaje.text)
			if "no valido" in mensaje:
				print("[-]Error al enviar el mensaje")
			else:
				print("[+]El mensaje fue enviado correctamente a "+para)
		
	def conseguir_id_usuario(self,usuario):
		codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
		id_muro = re.findall("<a obj=\"user\" objid=\"(.+)\" errorContainer=.",str(codigo_pagina.text))	
		if id_muro:
			return id_muro[0]
		else:
			return False

	def shoutear_usuario(self,usuario,mensaje,media_url=None):#Postear shout en muro de usuario
		if self.logeado:
			codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
			id_muro = self.conseguir_id_usuario(usuario)
			url_subida = ""
			tipo_contenido = ""
			if id_muro:
				print("[+]ID de muro:"+str(id_muro))
				if media_url:
					if "youtu" in media_url:tipo_contenido = "2"
					else:tipo_contenido = "1"
					if "kn3" in media_url:url_subida = media_url#SI ya esta subido a taringa
					else:url_subida = self.subir_archivo_desde_url(media_url)#si no se sube
				parametros_msg = {
					"attachment":url_subida,
					"attachment_type":tipo_contenido,
					"body":mensaje,
					"key":self.key_seguridad,
					"privacy":"undefined",
					"wall":id_muro[0]
					
				}
			shout = self.sesion_actual.post(self.pagina_shoutear_en_muro,data=parametros_msg,verify=True)
			if "es invalido" in shout.text:
				print("[-]Error al postear el shout en el muro del usuario "+usuario)
			else:
				print("[+]Shout publicado en el muro de "+usuario+" correctamente..")

	def subir_imagen_miniatura(self,url):#Subir una imagen miniatura para un post
		if self.logeado:
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
	
	def crear_post(self,titulo,contenido,imagen_previa,etiquetas,fuente_contenido,categoria,verificar=False):#Crear y publicar post
		if self.logeado:
			imagen_previa = self.subir_imagen_miniatura(imagen_previa)
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

	def seguir_usuario(self,usuario):#Seguir a un usuario
		if self.logeado:
			codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
			id_muro = self.conseguir_id_usuario(usuario)
			if id_muro:
				print("[+]Id de usuario:"+id_muro)
			parametros_seguir_usuario = {
				"action":"follow",
				"key":self.key_seguridad,
				"obj":id_muro[0],
				"type":"user"
				
			}
			foll = self.sesion_actual.post(self.pagina_acciones,data=parametros_seguir_usuario,verify=True)
			print(foll.text)
			print("[+]Usuario "+usuario+" seguido.")
	
	def desseguir_usuario(self,usuario):#No seguir mas a un usuario
		if self.logeado:
			codigo_pagina = self.sesion_actual.get(self.pagina_home+"/"+usuario)
			id_muro = self.conseguir_id_usuario(usuario)
			if id_muro:
				print("[+]Id de usuario:"+id_muro[0])
			parametros_seguir_usuario = {
				"action":"unfollow",
				"key":self.key_seguridad,
				"obj":id_muro[0],
				"type":"user"
				
			}
			foll = self.sesion_actual.post(self.pagina_acciones,data=parametros_seguir_usuario,verify=True)
			print(foll.text)
			print("[+]Usuario "+usuario+" no seguido")
	
	def denunciar_post(self,post,razon,aclaracion,preguntar=False):#Denunciar un post
		if self.logeado:
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
				den = self.sesion_actual.post(self.pagina_denuncia,data=parametros_denuncia,verify=True)
				if "Ya habias denunciado este post" in str(den.text):
					print("[-]Ya se habia denunciado este post con esta cuenta!")
				elif "La denuncia fue enviada" in str(den.text):
					print("[+]Denuncia enviada!")
				else:
					print("[?]Error al enviar la denuncia?")
			else:
				print("[-]Denuncia cancelada")
	
	def bloquear_usuario(self,usuario):#Bloquear usuario
		if self.logeado:
			print("[+]Bloqueando usuario")
			id_usuario = self.conseguir_id_usuario(usuario)
			parametros_bloqueo = {
				"bloqueado":"1",
				"key":self.key_seguridad,
				"user":id_usuario,
			}
			bloq = self.sesion_actual.post(self.pagina_bloquear_usuario,data=parametros_bloqueo,verify=True)
			if "satisfactoriamente" in bloq.text:
				print("[+]%s fue bloqueado"%usuario)
			else:
				print("[-]Error al bloquear usuario..")
				
	def desbloquear_usuario(self,usuario):#Desbloquear usuario
		if self.logeado:
			print("[+]Desbloqueando usuario")
			id_usuario = self.conseguir_id_usuario(usuario)
			parametros_bloqueo = {
				"key":self.key_seguridad,
				"user":id_usuario,
			}
			bloq = self.sesion_actual.post(self.pagina_bloquear_usuario,data=parametros_bloqueo,verify=True)
			if "satisfactoriamente" in bloq.text:
				print("[+]%s fue desbloqueado"%usuario)
			else:
				print("[-]Error al desbloquear usuario..")
	
	def comentar_post(self,post,comentario):#Comentar un post
		if self.logeado:
			if "http" in post:
				link_ = post.split("/")
				link = link_[5]
				print("	[+]Post a comentar:",link_[6])
			parametros_comentario = {
				"comment":comentario,
				"key":self.key_seguridad,
				"objectId":link,
				"objectOwner":self.id_usuario,
				"objectType":"post",
				"show":"True"
			
			}
			print(parametros_comentario)
			comentario = self.sesion_actual.post(self.pagina_comentar_post,data=parametros_comentario)
			if "agregado" in str(comentario.text):
				print("[+]Comentario agregado satisfactoriamente..")
				print(comentario.text)
			else:
				print("[-]Error al agregar el comentario..")
				print(comentario.text)

	def plantilla_solicitud_ajax(self,parametros):#Codigo de muestra 
		if self.logeado:
			parametros = {
			
			
			}
		solicitud = self.sesion_actual.post(link_ajax,data=parametros)


USUARIO = "usuario"
CONTRASEÑA = "contra"

if __name__ == "__main__":
	api = TaringApi()
	api.logear(USUARIO,CONTRASEÑA)
	#acciones
	#ex = api.comentar_post()
	api.deslogear()

