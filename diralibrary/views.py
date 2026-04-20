from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django import template
from .models import *
from django.db.models import Avg, Count, Min, Sum
from django.db.models import Q, Max
from django.db.models import FloatField
from django.db.models import F
from django.db.models.functions import Round
from django.db.models.functions import Cast
from datetime import datetime
from datetime import date
import math
import random
import re
import locale
from itertools import groupby
from operator import itemgetter

def addPersona(request):
	if request.method == 'POST':
		post_nombre = request.POST.get("nombre")
		post_bio = request.POST.get("bio")

		newP = Persona.objects.create(nombre=post_nombre, bio=post_bio)
		newP.save()

		return redirect(f'/lib/persona/{newP.id}')
	return render(request,'add-persona.html',{})

def persona(request,persona_id):
	this_persona = Persona.objects.get(pk=int(persona_id))
	creditos = Credito.objects.filter(persona=this_persona).order_by('libro__anho_publicacion')
	return render(request,'persona.html',{'this_persona':this_persona,'creditos':creditos})

def editPersona(request,persona_id):
	this_persona = Persona.objects.get(pk=int(persona_id))
	if request.method == 'POST':
		post_nombre = request.POST.get("nombre")
		post_bio = request.POST.get("bio")
		this_persona.nombre = post_nombre
		this_persona.bio = post_bio

		return redirect(f'/lib/persona/{this_persona.id}')
	return render(request,'edit-persona.html',{'this_persona':this_persona})

def addTitulo(request):
	tipos = Tipo.objects.all().order_by('id')
	personas = Persona.objects.all().order_by('nombre')

	if request.method == 'POST':
		post_titulo = request.POST.get("titulo")
		post_titulo_original = request.POST.get("titulo_original")
		post_fecha_publicacion = request.POST.get("fecha_publicacion")
		post_idioma_original = request.POST.get("idioma_original")
		post_synopsis = request.POST.get("synopsis")
		post_tipo = Tipo.objects.get(pk=int(request.POST.get("tipo")))
		post_persona = Persona.objects.get(pk=int(request.POST.get("pid")))

		if len(post_fecha_publicacion)==10:
			newB = Titulo.objects.create(titulo = post_titulo,
				titulo_original = post_titulo_original,
				fecha_publicacion= post_fecha_publicacion,
				idioma_original = post_idioma_original,
				anho_publicacion = int(post_fecha_publicacion[:4]),
				tipo = post_tipo,
				synopsis = post_synopsis)
		else:
			newB = Titulo.objects.create(titulo = post_titulo,
				titulo_original = post_titulo_original,
				idioma_original = post_idioma_original,
				anho_publicacion = int(post_fecha_publicacion),
				tipo = post_tipo,
				synopsis = post_synopsis)

		newC = Credito.objects.create(persona = post_persona, libro = newB, credito='autor' )
		newC.save()

		if len(request.FILES.get("imagen"))>0:
			newC = Cubiertas.objects.create(titulo = newB,
				imagen = request.FILES.get("imagen"),
				caption= "Book Cover",
				tipo = 'cover',
				vista=False)
			newC.save()

	return render(request,'add-titulo.html',{'tipos':tipos,'personas':personas})


def titulo(request,titulo_id):

	this_titulo = Titulo.objects.get(pk=int(titulo_id))
	consumos = Consumo.objects.filter(titulo=this_titulo)
	comentarios = Comentario.objects.filter(titulo=this_titulo)
	return render(request,'titulo.html',{'comentarios':comentarios,'this_titulo':this_titulo,'consumos':consumos})

def aggNota(request):
	this_titulo = Titulo.objects.get(pk=int( request.POST.get("tid")))
	post_comm = request.POST.get("comentario")
	post_head = request.POST.get("encabezado")



	encabezado = post_head.replace(".char", "") if len(post_head)>3 else None

	if len(post_head)>4 and ".char" in post_head:
		ischar = True
	else:
		ischar = False
	
	newC = Comentario.objects.create(titulo=this_titulo,texto=post_comm, encabezado=encabezado, es_personaje=ischar)

	newC.save()

	return	redirect(f"/lib/titulo/{this_titulo.id}")

def editNota(request,nota,tipo):
	this_nota = Comentario.objects.get(pk=int(nota))
	if request.method == 'POST':
		post_encabezado = request.POST.get("encabezado")
		encabezado = post_encabezado if len(post_encabezado)>3 or len(post_encabezado)=='None' else None
		post_contenido = request.POST.get("texto")

		this_nota.encabezado = encabezado
		this_nota.texto = post_contenido
		this_nota.save()

		if tipo == 'edit-perfil':
			return redirect(f"/lib/nota/{this_nota.id}/view")
		else:
			return redirect(f"/lib/titulo/{this_nota.titulo.id}")


		
	return render(request,'edit-nota.html',{'this_nota':this_nota,'tipo':tipo})

def aggCredito(request,titulo):
	this_titulo = Titulo.objects.get(pk=int(titulo))
	personas = Persona.objects.all().order_by('nombre')

	if request.method == 'POST':
		post_credito = request.POST.get("credito")
		persona = Persona.objects.get(pk=int(request.POST.get("pid")))
		nc = Credito.objects.create(libro = this_titulo, persona=persona,credito=post_credito)
		nc.save()
		return	redirect(f"/lib/titulo/{this_titulo.id}")

	return render(request,'add-creditos.html',{'this_titulo':this_titulo,'personas':personas})

def comenzar(request,titulo_id):
	this_titulo = Titulo.objects.get(pk=int(titulo_id))
	if request.method == 'POST':
		post_fecha_ini = request.POST.get("fecha_ini")
		post_fecha_fin = request.POST.get("fecha_fin")
		post_formato = request.POST.get("formato")
		post_idioma = request.POST.get("idioma")
		post_unidades = request.POST.get("unidades")
		post_cantidad = request.POST.get("cantidad")

		if len(post_fecha_fin)==10:
			newC = Consumo.objects.create(titulo=this_titulo,
				fecha_ini = post_fecha_ini,
				fecha_fin = post_fecha_fin,
				formato = post_formato,
				idioma = post_idioma,
				unidades = post_unidades,
				cantidad = post_cantidad)
		else:
			newC = Consumo.objects.create(titulo=this_titulo,
				fecha_ini = post_fecha_ini,
				formato = post_formato,
				idioma = post_idioma,
				unidades = post_unidades,
				cantidad = post_cantidad)

		newC.save()

		return redirect(f'/lib/titulo/{this_titulo.id}')
		
		
	return render(request,'comenzar.html',{'this_titulo':this_titulo})

def inicio(request):
	page = request.GET.get('page', 1)
	lecturas = Consumo.objects.filter(fecha_fin__isnull=False).order_by('-fecha_fin')
	now_reading = Consumo.objects.filter(fecha_fin__isnull=True).order_by('-fecha_ini')
	paginator = Paginator(lecturas, 12)
	resultados = paginator.get_page(page)
	return render(request,'inicio.html',{'now_reading':now_reading	,'resultados':resultados})

def cola(request):
	page = request.GET.get('page', 1)
	lecturas = Titulo.objects.filter(consumo__titulo__isnull=True).order_by('-anho_publicacion')
	paginator = Paginator(lecturas, 50)
	resultados = paginator.get_page(page)
	return render(request,'cola.html',{'resultados':resultados})

def perfiles(request):
	page = request.GET.get('page', 1)
	perfiles = Comentario.objects.filter(es_personaje=True).order_by('encabezado')
	paginator = Paginator(perfiles, 18)
	resultados = paginator.get_page(page)
	return render(request,'perfiles.html',{'wikis':resultados})


def terminarLectura(request):
	Consumo.objects.filter(id=int(request.POST.get("consumo"))).update(fecha_fin=request.POST.get("fecha_fin"))
	return redirect(f"/lib/titulo/{request.POST.get("tid")}") 

