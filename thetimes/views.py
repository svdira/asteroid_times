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


def plantilla(request):
	return render(request,'base_times.html',{})

def addItem(request):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

		if categoria.category.lower() in ['manga volume','book','bunko','manga series','comic book','movie','anime season','anime film','tv series','show season','persona','album','band']:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		    newI.save()
		else:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		    newI.save()


		return redirect(f'/edit-item/{newI.id}')

	return render(request,'add.html',{'cats':cats})

def addMovie(request):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'add-movie.html',{'cats':cats})

def editItem(request,i):
	wiki = request.GET.get('wiki', 0)
	this_item = Item.objects.get(pk=int(i))
	search_results = None
	item_rels = AttrItem.objects.filter(child=this_item)
	item_imgs = AttrImage.objects.filter(item=this_item)
	item_dates = AttrDate.objects.filter(item=this_item)
	item_ints = AttrInteger.objects.filter(item=this_item)
	item_texts = AttrText.objects.filter(item=this_item)

	cadena = ""

	conteo = Atributos.objects.filter(item = this_item).count()

	if conteo > 0:
		atts = Atributos.objects.filter(item = this_item).order_by('orden')

		for a in atts:
			cadena = cadena + f"{a.orden}|{a.nombre}|{a.tipo}|{a.valor}\n"

	if request.method == 'POST':
		if request.POST.get("formulario") == '1':
			this_item.contenido = request.POST.get("contenido")
			this_item.fecha_edicion = datetime.now()
			this_item.save()
			if request.POST.get("guardar") == "Save and View":
				if wiki == 0:
					return redirect(f"/item/{this_item.id}")
				else:
					return redirect(f"/wikipage/{this_item.id}/{wiki}")
		if request.POST.get("formulario") == '2':
			kw = request.POST.get('keywords')
			if len(kw)>4:
				search_results = Item.objects.filter(titulo__contains=kw)

		if request.POST.get("formulario")=='3':
			parent_id = request.POST.get("item_id")
			parent = Item.objects.get(pk=int(parent_id))
			relacion = request.POST.get("relacion")

			newRel = AttrItem.objects.create(item=parent,child=this_item,rel_name=relacion)
			newRel.save()

			if request.POST.get("relacion")=='lista-item':
			    return redirect(f"/item/{request.POST.get('lista')}")
		if request.POST.get("formulario")=='4':
			if len(request.FILES.get("imagen"))>2:
				photo = request.FILES.get("imagen")
				tipo = request.POST.get("tipo")
				caption = request.POST.get("caption")
				if len(caption) == 0 :
					caption = "tba"

				newI = AttrImage.objects.create(item=this_item, imagen=photo,caption=caption,tipo=tipo)
				newI.save()

		if request.POST.get("formulario")=='5':
			nom = request.POST.get("attrNvo")
			val = request.POST.get("attrVal")

			newA = AttrDate.objects.create(item=this_item,att_name=nom,att_value=val)
			newA.save()

		if request.POST.get("formulario")=='6':
			nom = request.POST.get("attrNvo")
			val = request.POST.get("attrVal")

			newA = AttrInteger.objects.create(item=this_item,att_name=nom,att_value=val)
			newA.save()

		if request.POST.get("formulario")=='7':
			nom = request.POST.get("attrNvo")
			val = request.POST.get("attrVal")

			newA = AttrText.objects.create(item=this_item,att_name=nom,att_value=val)
			newA.save()

		if request.POST.get("formulario")=='8':
			Atributos.objects.filter(item=this_item).delete()
			txt_atributos = request.POST.get("txt_atributos")
			lineas = []
			for line in txt_atributos.splitlines():
				parts = line.split('|')
				lineas.append(parts)

			for l in lineas:
				if l[2]=='txt':
					newAtt = Atributos.objects.create(item=this_item,orden=int(l[0]),tipo=l[2],nombre=l[1],texto=l[3])
					newAtt.save()
				elif l[2]=='fec':
					newAtt = Atributos.objects.create(item=this_item,orden=int(l[0]),tipo=l[2],nombre=l[1],fecha=l[3])
					newAtt.save()
				elif l[2]=='int':
					newAtt = Atributos.objects.create(item=this_item,orden=int(l[0]),tipo=l[2],nombre=l[1],entero=l[3])
					newAtt.save()
				elif l[2]=='dec':
					newAtt = Atributos.objects.create(item=this_item,orden=int(l[0]),tipo=l[2],nombre=l[1],decimal=float(l[3]))
					newAtt.save()

		redirect(request.path)

		cadena = ""
		conteo = Atributos.objects.filter(item = this_item).count()
		if conteo > 0:
			atts = Atributos.objects.filter(item = this_item).order_by('orden')
			for a in atts:
				cadena = cadena + f"{a.orden}|{a.nombre}|{a.tipo}|{a.valor}\n"


	return render(request,'edit-item.html',{'this_item':this_item,'sr':search_results,'items':item_rels,'pics':item_imgs,'fechas':item_dates,'ints':item_ints,'texts':item_texts,'cadena':cadena,'largo_c':len(cadena)})


def homepage(request):
	page = request.GET.get('page', 1)
	articles = Item.objects.exclude(tipo__id__in=[3,8,11,14,22,6,23,24,25]).order_by('-fecha_creacion')
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)
	cats = sorted(Category.objects.exclude(id__in=[22,6,23,24,25]),key=lambda t: t.nitems, reverse=True)
	if page == 1:
	    in_progress = Consumo.objects.filter(fec_fin__isnull=True).order_by('-id')
	else:
	    in_progress = None

	return render(request,'homepage.html',{'articles':resultados,'cats':cats,'in_progress':in_progress})

def gallery(request,item_id):
	page = request.GET.get('page', 1)
	if int(item_id) == 0:
		articles = AttrImage.objects.all().order_by('-item__fecha_creacion')
		this_item = None
	else:
		articles = AttrImage.objects.filter(item__id=int(item_id)).order_by('-item__fecha_creacion')
		this_item = Item.objects.get(pk=int(item_id))
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'gallery.html',{'articles':resultados,'this_item':this_item,'cats':cats})

def photo(request,photo_id):
	this_photo = AttrImage.objects.get(pk=int(photo_id))
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'photo.html',{'this_photo':this_photo,'cats':cats})


def categoria(request,c):

	if int(c)==14:
		return redirect('/journal')
	page = request.GET.get('page', 1)
	this_cat = Category.objects.get(pk=int(c))
	articles = Item.objects.filter(tipo__id=int(c)).order_by('-fecha_creacion')
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)

	return render(request,'category.html',{'this_cat':this_cat,'articles':resultados,'cats':cats})


def item(request,i):
	this_item = Item.objects.get(pk=int(i))
	es_parent = 0
	if this_item.tipo.category in ['TV Series','Book List','Collection','Book Series','Anime Series','Anime Film','Bunko Series','Manga Series']:
		es_parent = 1
	atributos = Atributos.objects.filter(item=this_item).order_by('orden')
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	ncon = Consumo.objects.filter(item = this_item, fec_fin__isnull=True).count()
	if ncon > 0:
		con_in_prog = Consumo.objects.filter(item = this_item, fec_fin__isnull=True).latest('id')
	else:
		con_in_prog = None

	conteo_rel = AttrItem.objects.filter(item=this_item).count()
	conteo_pars = AttrItem.objects.filter(child=this_item).count()
	parents = AttrItem.objects.filter(child=this_item).order_by('item__titulo')

	tweets = Tweet.objects.filter(item=this_item)

	tipos = []
	cats_show_ratio = ['Book', 'Bunko', 'Manga Volume', 'Show Season', 'Anime Season','Anime Film']
	categories = AttrItem.objects.filter(item=this_item).values_list('child__tipo__category', flat=True).distinct()
	for cat in categories:
		if this_item.tipo.category.lower() != 'book list':
		    items_cat = sorted(AttrItem.objects.filter(item=this_item, child__tipo__category=cat),  key=lambda t: t.child.periodo, reverse=False)
		else:
		    items_cat = AttrItem.objects.filter(item=this_item, child__tipo__category=cat).order_by('id')
		consumidos = sum(1 for t in items_cat if t.child.consumido == True)
		tipos.append({'cat':cat,'items':items_cat,'nitems':len(items_cat),'ncon':consumidos})

	if request.method == 'POST':
		conteo_pb = BarraProgreso.objects.filter(consumo=con_in_prog).count()
		anterior = 0

		if conteo_pb > 0:
			last_barra = BarraProgreso.objects.filter(consumo=con_in_prog).latest('id')
			anterior = last_barra.progreso

		newB = BarraProgreso.objects.create(consumo=con_in_prog,
			fecha=request.POST.get("fec_fin"),
			progreso=con_in_prog.cantidad,
			anterior=anterior )
		newB.save()

		con_in_prog.fec_fin = request.POST.get("fec_fin")
		con_in_prog.save()
		this_item.fecha_creacion = request.POST.get("fec_fin")
		this_item.consumido = True
		this_item.save()




		con_in_prog = None

	director = False
	main_cast = False
	enlaces_d = ""
	enlaces_c = ""

	if this_item.tipo.category.lower() == 'movie':
		director = AttrText.objects.filter(item=this_item,att_name='Director')
		main_cast = AttrText.objects.filter(item=this_item,att_name='Main Cast')

		for d in director:
			enlaces_d = enlaces_d + "<a href='/movie-credits/"+d.att_value+"' style='text-decoration:none; color:#6F8FAF;'>"+d.att_value+"</a>,&nbsp;"

		for c in main_cast:
			enlaces_c = enlaces_c + "<a href='/movie-credits/"+c.att_value+"' style='text-decoration:none; color:#6F8FAF;'>"+c.att_value+"</a>,&nbsp;"

		enlaces_d = enlaces_d[:-7]
		enlaces_c = enlaces_c[:-7]


	return render(request,'item.html',{'this_item':this_item,'tweets':tweets,'cats':cats,'natt':len(atributos),'atributos':atributos,'es_parent':es_parent,'cons':con_in_prog,'conteo_r':conteo_rel,'conteo_p':conteo_pars,'parents':parents,'enlaces_d':enlaces_d,'enlaces_c':enlaces_c,'tipos':tipos,'cats_show_ratio':cats_show_ratio})

def startConsumo(request,i):
	this_item = Item.objects.get(pk=int(i))

	duracion = 0

	if AttrInteger.objects.filter(item=this_item, att_name='runtime').count() > 0:

		obj_duracion = AttrInteger.objects.filter(item=this_item, att_name='runtime').latest('id')
		duracion = obj_duracion.att_value


	if this_item.tipo.category.lower() in ['manga volume','book','bunko','manga series','comic book']:
		formatos = ['printed','kindle','boox','audiobook']
		units = ['paginas','location','minutos','chapters']

	if this_item.tipo.category.lower() in ['movie','album']:
		formatos = ['streaming','download','theater','cd/dvd/lp']
		units = ['minutes']

	if this_item.tipo.category.lower() in ['anime season','tv series','show season','anime film']:
		formatos = ['streaming','download','theater','cd/dvd/lp']
		units = ['episodes']
	if this_item.tipo.category.lower() in ['beer']:
		formatos = ['lata','botella','tacon alto','chola']
		units = ['bebida']


	if request.method == 'POST':
		fec_ini = request.POST.get("fec_ini")
		if this_item.tipo.category.lower() in ['movie','album']:
		    fec_fin = fec_ini
		else:
		    fec_fin = request.POST.get("fec_fin","no")
		formato = request.POST.get("formato")
		unidades = request.POST.get("unidades")
		cantidad = request.POST.get("cantidad")
		multiplicador = request.POST.get("multiplicador")

		if len(fec_fin)<10:
			newC = Consumo.objects.create(item=this_item,
				fec_ini=fec_ini,
				formato=formato,
				unidades = unidades,
				cantidad=int(cantidad),
				multiplicador=multiplicador,
				consumo=0)
			newC.save()
		else:
			newC = Consumo.objects.create(item=this_item,
				fec_ini=fec_ini,
				fec_fin = fec_fin,
				formato=formato,
				unidades = unidades,
				cantidad=int(cantidad),
				multiplicador=multiplicador,
				consumo=cantidad)
			newC.save()

			this_item.consumido = True
			this_item.save()

			this_item.fecha_creacion = fec_fin
			this_item.save()
			this_item.fecha_edicion = fec_fin
			this_item.save()
		return redirect(f"/item/{this_item.id}")


	return render(request,'start_consumo.html',{'this_item':this_item,'formatos':formatos,'units':units,'duracion':duracion})


def bookHistory(request):
	get_y = request.GET.get('y', 1)

	conteo_0 = Consumo.objects.filter(item__tipo__category='Book',item__consumido=True,fec_fin__isnull=False).count()
	if conteo_0 == 0:
	    return redirect('/book-queue/')

	max_year = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).order_by('-fec_fin').first()

	this_y = max_year.fec_fin.year if int(get_y) == 1 else int(get_y)

	books = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False, fec_fin__year=this_y).order_by('-fec_fin')
	rbooks = len(books)
	qbooks = Item.objects.filter(tipo__category='Book',consumo__item__isnull=True, consumido= False).count()
	in_progress = Consumo.objects.filter(item__tipo__category='Book', fec_fin__isnull=True)

	nr_books = Item.objects.filter(tipo__category='Book',consumido	= True).count()


	anhos = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).values('fec_fin__year').annotate(qbooks=Count('id')).order_by('-fec_fin__year')


	qbooks = qbooks + len(in_progress)
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'read-history.html',{'books':books,'nr_books':nr_books,'this_y':this_y,'anhos':anhos,'rbooks':rbooks,'qbooks':qbooks,'cats':cats,'anhos':anhos})

def covers(request,c):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	page = request.GET.get('page', 1)
	categoria = Category.objects.get(pk=int(c))
	articles = Consumo.objects.filter(item__tipo__id=int(c),fec_fin__isnull=False, item__attrimage__isnull=False).order_by('-fec_fin')
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)

	if not articles:
		return redirect(f'/category/{c}')

	return render(request,'covers.html',{'articles':resultados,'cat':categoria,'cats':cats})

def movieHistory(request):
	get_y = request.GET.get('y', 1)
	conteo_0 = Consumo.objects.filter(item__tipo__category='Movie',fec_fin__isnull=False).count()
	if conteo_0 == 0:
	    return redirect('/movie-queue/')
	max_year = Consumo.objects.filter(item__tipo__category='Movie',fec_fin__isnull=False).order_by('-fec_fin').first()

	this_y = max_year.fec_fin.year if int(get_y) == 1 else int(get_y)

	books = Consumo.objects.filter(item__tipo__category='Movie',fec_fin__isnull=False, fec_fin__year=this_y).order_by('-fec_fin')
	rbooks = len(books)
	qbooks = Item.objects.filter(tipo__category='Movie',consumo__item__isnull=True, consumido=False).count()
	in_progress = Consumo.objects.filter(item__tipo__category='Movie', fec_fin__isnull=True)

	nr_books = Item.objects.filter(tipo__category='Movie',consumido	= True).count()


	anhos = Consumo.objects.filter(item__tipo__category='Movie',fec_fin__isnull=False).values('fec_fin__year').annotate(qbooks=Count('id')).order_by('-fec_fin__year')


	qbooks = qbooks + len(in_progress)
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'watch-history.html',{'books':books,'nr_books':nr_books,'this_y':this_y,'anhos':anhos,'rbooks':rbooks,'qbooks':qbooks,'cats':cats,'anhos':anhos})

def movieQueue(request):
	books = sorted(Item.objects.filter(tipo__category='Movie',consumo__item__isnull=True, consumido=False), key=lambda t: t.periodo, reverse=False)
	qbooks = len(books)
	rbooks =  Consumo.objects.filter(item__tipo__category='Movie',fec_fin__isnull=False).count()
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	in_progress = Consumo.objects.filter(item__tipo__category='Movie', fec_fin__isnull=True)
	qbooks = qbooks + len(in_progress)
	return render(request,'watch-queue.html',{'now_reading':in_progress,'books':books,'rbooks':rbooks,'qbooks':qbooks,'cats':cats})

def bookQueue(request):
	books = sorted(Item.objects.filter(tipo__category='Book',consumo__item__isnull=True, consumido= False), key=lambda t: t.periodo, reverse=False)
	qbooks = len(books)
	rbooks =  Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).count()
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	in_progress = Consumo.objects.filter(item__tipo__category='Book', fec_fin__isnull=True)
	qbooks = qbooks + len(in_progress)
	return render(request,'read-queue.html',{'now_reading':in_progress,'books':books,'rbooks':rbooks,'qbooks':qbooks,'cats':cats})

def relatedItems(request,item):
	this_item = Item.objects.get(pk=int(item))

	tipos = []
	cats_show_ratio = ['Book', 'Bunko', 'Manga Volume', 'Show Season', 'Anime Season','Anime Film']
	categories = AttrItem.objects.filter(item=this_item).values_list('child__tipo__category', flat=True).distinct()
	for cat in categories:
		items_cat = sorted(AttrItem.objects.filter(item=this_item, child__tipo__category=cat),  key=lambda t: t.child.periodo, reverse=False)
		consumidos = sum(1 for t in items_cat if t.child.consumido == 1)
		tipos.append({'cat':cat,'items':items_cat,'nitems':len(items_cat),'ncon':consumidos})

	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)

	return render(request,'related-items.html',{'this_item':this_item,'tipos':tipos,'cats':cats,'cats_show_ratio':cats_show_ratio})

def addChildItem(request, parent):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	this_parent = Item.objects.get(pk=int(parent))

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		relacion = request.POST.get("relacion")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

		if categoria.category.lower() in ['manga volume','book','bunko','manga volume','comic book','movie','anime season','anime film','tv series','show season','persona','band','album']:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		    newI.save()
		else:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		    newI.save()


		newRel = AttrItem.objects.create(item=this_parent,child=newI,rel_name=relacion)
		newRel.save()

		return redirect(f'/edit-item/{newI.id}')

	return render(request,'add-child-item.html',{'cats':cats,'this_parent':this_parent})

def searchPage(request):
	results = None
	results_2 = None
	lista = None
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)

	if request.method == 'POST':
		lista = request.POST.get("parent")
		key_word = request.POST.get("key_word")
		results = Item.objects.filter(titulo__contains=key_word)
		ids =  Item.objects.filter(titulo__contains=key_word).values_list('id', flat=True)
		ids_list = list(ids)
		results_2 = Item.objects.filter(contenido__contains=key_word).exclude(id__in=ids_list)

	return render(request,'search-page.html',{'cats':cats,'rt':results,'rc':results_2,'lista':lista})

def printHTML(request, cid):
	this_item = Item.objects.get(pk=int(cid))
	related = AttrItem.objects.filter(item=this_item).order_by('id')

	return render(request,'print_html.html',{'this_item':this_item, 'related':related })


def addContrato(request,equipo):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	equipo = Equipo.objects.get(pk=int(equipo))

	if request.method == 'POST':
		nombre = request.POST.get("nombre")
		pais = request.POST.get("pais")
		info = request.POST.get("info")

		fec_ini = request.POST.get("fec_ini")
		posicion = request.POST.get("posicion")
		dorsal = request.POST.get("dorsal")

		if posicion == 'arquero':
			n_p = 1
		elif posicion == 'defensa':
			n_p = 2
		elif posicion == 'centrocampista':
			n_p = 3
		elif posicion == 'delantero':
			n_p = 4
		else:
			n_p = 0



		newJ = Jugador.objects.create(nombre=nombre, pais=pais, info=info)
		newJ.save()
		newC = Contrato.objects.create(equipo=equipo,jugador=newJ, fec_ini = fec_ini, posicion=posicion,n_posicion=n_p, dorsal=dorsal,last_edited=datetime.today().date())
		newC.save()

		return redirect(f'/nomina/{equipo.id}')

	return render(request,'add-contrato.html',{'cats':cats,'this_equipo':equipo})

def addContratoShort(request):
	equipo = Equipo.objects.get(pk=int(request.POST.get("equipo")))
	partido = Partido.objects.get(pk=int(request.POST.get("partido")))
	nombre = request.POST.get("nombre")

	conteo_x = Jugador.objects.filter(nombre=nombre).count()
	if conteo_x > 0:
		newJ = Jugador.objects.filter(nombre=nombre).latest('id')
	else:
		newJ = Jugador.objects.create(nombre=nombre, pais='TBA', info='TBA')
		newJ.save()

	newC = Contrato.objects.create(equipo=equipo,jugador=newJ, fec_ini = '1999-12-31', posicion='TBA',n_posicion=0, dorsal=0,last_edited=datetime.today().date())
	newC.save()

	return redirect(f"/alineacion/{partido.id}/{equipo.id}")


def equipo(request,equipo):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	equipo = Equipo.objects.get(pk=int(equipo))
	ligas = Torneo.objects.all().order_by('-id')

	arqueros = Contrato.objects.filter(equipo=equipo, posicion='arquero', fec_fin__isnull=True).order_by('dorsal')
	defensas = Contrato.objects.filter(equipo=equipo, posicion='defensa', fec_fin__isnull=True).order_by('dorsal')
	centros = Contrato.objects.filter(equipo=equipo, posicion='centrocampista', fec_fin__isnull=True).order_by('dorsal')
	delanteros = Contrato.objects.filter(equipo=equipo, posicion='delantero', fec_fin__isnull=True).order_by('dorsal')
	dt = Contrato.objects.filter(equipo=equipo, posicion='dt', fec_fin__isnull=True).order_by('dorsal')

	partidos = Partido.objects.filter(Q(local=equipo) | Q(visita=equipo)).exclude(terminado=False).order_by('-fecha')[0:100]

	vector_p = ''
	for p in partidos:
		if  p.goles_local == p.goles_visita:
			this_r = 'D'
		elif p.local == equipo and p.goles_local > p.goles_visita:
			this_r = 'W'
		elif p.local == equipo and p.goles_local < p.goles_visita:
			this_r = 'L'
		elif p.visita == equipo and p.goles_local > p.goles_visita:
			this_r = 'L'
		elif p.visita == equipo and p.goles_local < p.goles_visita:
			this_r = 'W'

		vector_p = vector_p + this_r


	conteo = len(vector_p)
	ganes = vector_p.count("W")
	empates = vector_p.count("D")
	perdidos = vector_p.count("L")

	stats = [conteo,ganes,empates,perdidos]

	return render(request,'equipo.html',{'cats':cats,'this_equipo':equipo,'arqueros':arqueros,'defensas':defensas, 'centros':centros,'delanteros':delanteros,'vector_p':vector_p,'stats':stats,'dt':dt,'ligas':ligas,'partidos':partidos})




def nomina(request,equipo):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	equipo = Equipo.objects.get(pk=int(equipo))
	ligas = Torneo.objects.all().order_by('-id')

	arqueros = Contrato.objects.filter(equipo=equipo, posicion='arquero', fec_fin__isnull=True).order_by('dorsal')
	defensas = Contrato.objects.filter(equipo=equipo, posicion='defensa', fec_fin__isnull=True).order_by('dorsal')
	centros = Contrato.objects.filter(equipo=equipo, posicion='centrocampista', fec_fin__isnull=True).order_by('dorsal')
	delanteros = Contrato.objects.filter(equipo=equipo, posicion='delantero', fec_fin__isnull=True).order_by('dorsal')
	dt = Contrato.objects.filter(equipo=equipo, posicion='dt', fec_fin__isnull=True).order_by('dorsal')

	partidos = Partido.objects.filter(Q(local=equipo) | Q(visita=equipo)).exclude(terminado=False).order_by('-fecha')[0:25]

	vector_p = ''
	for p in partidos:
		if  p.goles_local == p.goles_visita:
			this_r = 'D'
		elif p.local == equipo and p.goles_local > p.goles_visita:
			this_r = 'W'
		elif p.local == equipo and p.goles_local < p.goles_visita:
			this_r = 'L'
		elif p.visita == equipo and p.goles_local > p.goles_visita:
			this_r = 'L'
		elif p.visita == equipo and p.goles_local < p.goles_visita:
			this_r = 'W'

		vector_p = vector_p + this_r


	conteo = len(vector_p)
	ganes = vector_p.count("W")
	empates = vector_p.count("D")
	perdidos = vector_p.count("L")

	stats = [conteo,ganes,empates,perdidos]




	return render(request,'nomina.html',{'cats':cats,'this_equipo':equipo,'arqueros':arqueros,'defensas':defensas, 'centros':centros,'delanteros':delanteros,'vector_p':vector_p,'stats':stats,'dt':dt,'ligas':ligas,'partidos':partidos})



def liga(request,liga):
	ligas = Torneo.objects.all().order_by('-id')
	this_liga = Torneo.objects.get(pk=int(liga))
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	pp = Partido.objects.filter(torneo=this_liga, terminado=False).order_by('fecha','id')
	pt = Partido.objects.filter(torneo=this_liga, terminado=True).filter(Q(fase__contains='MD-') | Q(fase__contains='Group')).order_by('-fecha','id')[0:30]
	pe = Partido.objects.filter(torneo=this_liga, terminado=True).exclude(Q(fase__contains='MD-') | Q(fase__contains='Group')).order_by('-fecha','id')
	tabla = None
	if pt:
		tabla = Partido.objects.raw(f"select * from posiciones where id={this_liga.id} order by pts desc, DG desc, GF desc, PJ desc")

	return render(request,'liga.html',{'cats':cats,'this_liga':this_liga,'pe':pe,'pp':pp,'pt':pt,'ligas':ligas,'tabla':tabla})


def ligaEquipo(request,liga,equipo):
	ligas = Torneo.objects.all().order_by('-id')
	this_liga = Torneo.objects.get(pk=int(liga))
	this_equipo = Equipo.objects.get(pk=int(equipo))
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	pt = Partido.objects.filter(torneo=this_liga, terminado=True).filter(Q(local=this_equipo) | Q(visita=this_equipo)).order_by('-fecha','id')
	tabla = None
	if pt:
		tabla = Partido.objects.raw(f"select * from posiciones where id={this_liga.id} order by pts desc, DG desc, GF desc, PJ desc")

	return render(request,'liga-equipo.html',{'cats':cats,'npars':len(pt),'this_liga':this_liga,'this_equipo':this_equipo,'pt':pt,'ligas':ligas})

def ligaFase(request,liga,fase):
	ligas = Torneo.objects.all().order_by('-id')
	this_liga = Torneo.objects.get(pk=int(liga))
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	pp = Partido.objects.filter(torneo=this_liga, fase = fase).order_by('fecha','id')
	pt = Partido.objects.filter(torneo=this_liga, fase=fase).order_by('-fecha','id')
	tabla = None
	if pt:
		tabla = Partido.objects.raw(f"select * from posiciones where id={this_liga.id} order by pts desc, DG desc, GF desc, PJ desc")

	return render(request,'liga-fase.html',{'fase':fase, 'cats':cats,'npars':len(pt),'this_liga':this_liga,'pt':pt,'ligas':ligas,'tabla':tabla})



def addMatch(request,liga):
	this_liga = Torneo.objects.get(pk=int(liga))
	ligas = Torneo.objects.all().order_by('-id')
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	equipos = RelTorneoEquipo.objects.filter(torneo=this_liga).order_by('equipo__nombre')
	ult_partido = Partido.objects.latest('id')

	recent_partidos = Partido.objects.all().order_by('-id')[0:16]

	if request.method == 'POST':
		local = Equipo.objects.get(pk=int(request.POST.get("local")))
		visit = Equipo.objects.get(pk=int(request.POST.get("visit")))
		fase = request.POST.get("fase")
		fecha = request.POST.get("fecha")

		newP = Partido.objects.create(fecha = fecha,torneo = this_liga,  local = local, visita = visit,fase =fase,  goles_local = 0,  goles_visita = 0,  rondap_local = 0,  rondap_visita = 0,    terminado = False)
		newP.save()

		ult_partido = Partido.objects.latest('id')


	return render(request,'add-match.html',{'cats':cats,'this_liga':this_liga,'equipos':equipos,'up':ult_partido,'ligas':ligas,'rp':recent_partidos})

def partido(request,p):
	ligas = Torneo.objects.all().order_by('-id')
	this_partido = Partido.objects.get(pk=int(p))
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	pl = None
	pv = None
	comms = NotaPartido.objects.filter(partido=this_partido).order_by('minuto')
	contratos_l = None
	contratos_v = None

	goles = Gol.objects.filter(partido=this_partido).order_by('minuto','adicional')

	contratos_l = Contrato.objects.filter(equipo=this_partido.local, fec_fin__isnull=True).order_by('jugador__nombre')

	contratos_v = Contrato.objects.filter(equipo=this_partido.visita, fec_fin__isnull=True).order_by('jugador__nombre')


	next_m = Partido.objects.filter(torneo=this_partido.torneo, fecha__gte=this_partido.fecha,terminado=False).exclude(id=this_partido.id).order_by('fecha','id')

	if request.method == 'POST':
		pl = None
		pv = None
		marcador = request.POST.get("marcador").split("-")
		goles_local = marcador[0].strip()
		goles_visita = marcador[1].strip()

		if len(marcador)==4:
			pl = marcador[2].strip()
			pv = marcador[3].strip()



		this_partido.goles_local = int(goles_local)
		this_partido.goles_visita = int(goles_visita)
		if pl or pv:
			this_partido.rondap_local = int(pl)
			this_partido.rondap_visita = int(pv)
		this_partido.terminado = True
		this_partido.save()

	return render(request,'partido.html',{'cats':cats,'comms':comms,'this_partido':this_partido,'next_m':next_m,'ligas':ligas,'contratos_l':contratos_l,'contratos_v':contratos_v,'goles':goles})

def addnotapartido(request,p):
	this_partido = Partido.objects.get(pk=int(p))

	if request.method == 'POST':
		if len(request.POST.get("minuto"))==0:
			minuto = 0
		else:
			minuto = int(request.POST.get("minuto",0))

		comentario = request.POST.get("comment")

		newN = NotaPartido.objects.create(partido = this_partido, minuto = minuto, comentario = comentario)
		newN.save()

		return redirect(f'/partido/{this_partido.id}')



	return render(request,'add-nota-partido.html',{'this_partido':this_partido})



def futbol(request,p):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	ligas = Torneo.objects.all().order_by('-id')
	conteo_p = Partido.objects.filter(terminado=False).count()

	cm = []
	if p == '0':
		matches = Partido.objects.filter(terminado=False).select_related('torneo').order_by('torneo__nombre', 'fecha')
		for liga, group in groupby(matches, key=lambda x: x.torneo.nombre):
			group_list = list(group)
			min_fecha = min(p.fecha for p in group_list)
			cm.append({'liga': liga, 'partidos': group_list, 'min_fecha': min_fecha})
		cm.sort(key=lambda x: x['min_fecha'])
	else:
		matches = Partido.objects.filter(terminado=True).select_related('torneo').order_by('torneo__nombre', '-fecha')
		for liga, group in groupby(matches, key=lambda x: x.torneo.nombre):
			group_list = list(group)
			min_fecha = max(p.fecha for p in group_list)
			cm.append({'liga': liga, 'partidos': group_list[0:5], 'min_fecha': min_fecha})
		cm.sort(key=lambda x: x['min_fecha'], reverse=True)


	return render(request,'futbol.html',{'cats':cats,'ligas':ligas,'tc':p,'cm':cm})

def regGol(request):
	contrato = request.POST.get("contrato")
	goal_str = request.POST.get("goal_str")
	tipo = request.POST.get("tipo")
	partido = request.POST.get("partido")

	this_partido = Partido.objects.get(pk=int(partido))
	this_contrato = Contrato.objects.get(pk=int(contrato))
	is_local = True if tipo == 'local' else False

	pedazos = goal_str.split(',')

	if len(pedazos) == 1:
		minutos = pedazos[0].split('+')
		if len(minutos) == 1:
			minuto = int(minutos[0])
			adicional = 0
		else:
			minuto = int(minutos[0])
			adicional = int(minutos[1])

		autogol = False
		penalty = False
	elif len(pedazos) == 2:
		minutos = pedazos[0].split('+')
		if len(minutos) == 1:
			minuto = int(minutos[0])
			adicional = 0
		else:
			minuto = int(minutos[0])
			adicional = int(minutos[1])
		attr = pedazos[1]
		if attr.lower() == 'p':
			autogol = False
			penalty = True
		elif attr.lower() == 'a':
			autogol = True
			penalty = False

	if autogol == True:
		this_contrato = Contrato.objects.get(pk=52)


	newG = Gol.objects.create(partido=this_partido,
		contrato=this_contrato,
		minuto=minuto,
		adicional = adicional,
		penalty=penalty,
		autogol=autogol,
		gol_local = is_local
		)
	newG.save()

	return redirect(f"/partido/{this_partido.id}")

def addTeams(request,liga):
	this_liga = Torneo.objects.get(pk=int(liga))

	ligas = Torneo.objects.all().order_by('-id')
	listed_teams = RelTorneoEquipo.objects.filter(torneo = this_liga).values_list('equipo__id', flat=True)
	ids_list = list(listed_teams)

	equipos = Equipo.objects.exclude(id__in=ids_list).order_by('nombre')

	if request.method == 'POST':
		for e in equipos:
			if e.nombre in request.POST:
				equ = Equipo.objects.get(pk=e.id)
				nL = RelTorneoEquipo.objects.create(torneo=this_liga, equipo = equ)
		return redirect(f'/liga/{this_liga.id}')

	return render(request,'relacionar.html',{'this_liga':this_liga,'equipos':equipos,'ligas':ligas})

def alineacion(request,partido,equipo):
	this_partido = Partido.objects.get(pk=int(partido))
	this_equipo = Equipo.objects.get(pk=int(equipo))
	ligas = Torneo.objects.all().order_by('-id')

	these_alineaciones = Alineacion.objects.filter(partido=this_partido, equipo=this_equipo).order_by('contrato__n_posicion','contrato__dorsal')
	alineaciones = Alineacion.objects.filter(partido=this_partido, equipo=this_equipo).values_list('contrato__id', flat=True)
	ids_list = list(alineaciones)
	contratos = Contrato.objects.filter(equipo=this_equipo).exclude(id__in=ids_list).order_by('jugador__nombre')

	if request.method == 'POST':
		for c in contratos:
			if str(c.id) in request.POST:
				tipo = request.POST.get(str(c.id))
				this_contrato = Contrato.objects.get(pk=c.id)

				newA = Alineacion.objects.create(partido=this_partido, equipo=this_equipo, contrato=this_contrato, tipo= tipo)
				newA.save()
		return redirect(f"/alineacion/{this_partido.id}/{this_equipo.id}")


	return render(request,'alineacion.html',{'this_partido':this_partido,'contratos':contratos,'ligas':ligas,'this_equipo':this_equipo,'alineaciones':these_alineaciones})


def journal(request):
	get_y = request.GET.get('y', 1)
	conteo = JournalEntry.objects.all().count()
	if conteo > 0:
		max_year = JournalEntry.objects.all().order_by('-fecha').first()
	else:
		max_year = 0

	this_y = max_year.fecha.year if int(get_y) == 1 and conteo > 0 else int(get_y)

	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	entries = JournalEntry.objects.filter(fecha__year=this_y).order_by('-fecha','-id')

	anhos = JournalEntry.objects.all().values('fecha__year').exclude(fecha__year=this_y).annotate(qbooks=Count('id')).order_by('-fecha__year')

	if request.method == 'POST':
		fecha = request.POST.get("fecha")
		# Convert string to datetime object
		date_obj = datetime.strptime(fecha, "%Y-%m-%d")
		# Format it to desired string
		formatted_date = date_obj.strftime("%A, %B %e, %Y")
		tipo = Category.objects.get(pk=14)
		contenido = request.POST.get("contenido")
		newI = Item.objects.create(titulo=formatted_date,tipo=tipo,contenido=contenido,fecha_creacion=datetime.now(),fecha_edicion=datetime.now(),consumido=False)
		newI.save()

		newJ = JournalEntry.objects.create(fecha=fecha, item = newI)
		newJ.save()
	return render(request,'journal.html',{'cats':cats,'entries':entries,'this_y':this_y,'anhos':anhos})

def printedJournal(request,y):
	entries = JournalEntry.objects.filter(fecha__year=int(y)).order_by('-fecha','-id')
	return render(request,'print_journal_html.html',{'this_year':y,'entries':entries})

def addTweet(request):
	item = Item.objects.get(pk=int(request.POST.get("item_id")))
	texto = request.POST.get("tweet")
	if len(texto)>10:
		newT = Tweet.objects.create(item=item,ttext=texto)
		newT.save()

	return redirect(f"/item/{item.id}")


def moviedbImport(request):
    import requests
    import json

    movie_id = request.POST.get("title")

    url = "https://api.themoviedb.org/3/movie/{}?language=en-US".format(movie_id)
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NmM4MjVlMDFiY2RiMWQ1NWQ4YjRmYzNiNDQ0ODFhZiIsInN1YiI6IjYwMWM1NmFkNzMxNGExMDAzZGZjMzhiOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.vnpzsejhhlKDqssAg1dHiMH64Ja4_bP2UPcJFgHrW3k"
    }

    response = requests.get(url, headers=headers)
    movie_dict = json.loads(response.text)
    movie_dict3 = json.loads(response.text)

    str_titulo = movie_dict['original_title']
    str_overview = movie_dict['overview']
    str_premiere = movie_dict['release_date']
    str_runtime= movie_dict['runtime']
    str_poster = "https://image.tmdb.org/t/p/w400{}".format(movie_dict['poster_path'])

    url = "https://api.themoviedb.org/3/movie/{}/credits?language=en-US".format(movie_id)

    headers = {
        "accept": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI0NmM4MjVlMDFiY2RiMWQ1NWQ4YjRmYzNiNDQ0ODFhZiIsInN1YiI6IjYwMWM1NmFkNzMxNGExMDAzZGZjMzhiOSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.vnpzsejhhlKDqssAg1dHiMH64Ja4_bP2UPcJFgHrW3k"
    }

    response = requests.get(url, headers=headers)
    movie_dict = json.loads(response.text)

    int_c = 0
    str_director = ""
    for c in movie_dict['crew']:
        if c['job']=='Director':
            str_director = str_director+c['original_name']+","

    str_director = str_director[:-1]

    str_cast = ""
    for c in movie_dict['cast'][0:12]:
        str_cast = str_cast+c['original_name']+","

    str_cast = str_cast[:-1]

    str_tags = str_director+","+str_premiere[0:4]+","+str_cast

    return render(request,'add-moviedb.html',{'str_tags':str_tags,'str_titulo':str_titulo,'str_overview':str_overview,'str_premiere':str_premiere[0:4],'str_runtime':str_runtime,'str_poster':str_poster,'str_director':str_director,'str_cast':str_cast})

def savemovie(request):
	mtitle = request.POST.get("title")
	mpremiere = request.POST.get("premiere")
	mruntime = request.POST.get("runtime")
	minfo = request.POST.get("info")+"==headtext=="

	tipo = Category.objects.get(pk=2)

	this_item = Item.objects.create(titulo=mtitle,tipo=tipo,contenido=minfo,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31',consumido=False)
	this_item.save()

	newA = AttrInteger.objects.create(item=this_item,att_name='premiere',att_value=int(mpremiere))
	newA.save()

	newA = Atributos.objects.create(item=this_item,nombre='premiere',tipo='int',orden=1,entero=int(mpremiere))
	newA.save()

	newA = AttrInteger.objects.create(item=this_item,att_name='runtime',att_value=int(mruntime))
	newA.save()



	director = request.POST.get("director")
	cast = request.POST.get("cast")


	for strC in request.POST.get("director","").split(","):
		newA = AttrText.objects.create(item=this_item,att_name='Director',att_value=strC)
		newA.save()

	for strC in request.POST.get("cast","").split(","):
		newA = AttrText.objects.create(item=this_item,att_name='Main Cast',att_value=strC)
		newA.save()



	return redirect('/edit-item/{}'.format(this_item.id))


def movieCredits(request,nombre):
	this_credits = sorted(AttrText.objects.filter(att_value=nombre,item__tipo__category='Movie'),key=lambda t: t.item.periodo, reverse=True)
	this_nombre = nombre
	cats = AttrText.objects.filter(item__tipo__category='Movie').values('att_value').annotate(qmovies=Count('id')).order_by('-qmovies')[0:30]
	return render(request,'movie-credits.html',{'nombre':nombre,'this_credits':this_credits,'cats':cats})

def regProgress(request):
	con_id = int(request.POST.get("con_id"))
	consumo = Consumo.objects.get(pk=con_id)
	conteo = BarraProgreso.objects.filter(consumo=consumo).count()
	progreso = int(request.POST.get("progreso"))
	anterior = 0
	fecha_prog = request.POST.get("prog_date")



	if conteo > 0:
		last_barra = BarraProgreso.objects.filter(consumo=consumo).latest('id')
		anterior = last_barra.progreso

	if progreso <= consumo.cantidad and progreso > anterior:
		if len(fecha_prog)>0:
			fecha_obj = datetime.strptime(fecha_prog, "%Y-%m-%d").date()
			if anterior > 0 and fecha_obj >= last_barra.fecha:
				newB = BarraProgreso.objects.create(consumo=consumo, fecha = fecha_prog,	progreso = progreso,anterior = anterior)
				newB.save()
			elif anterior == 0 and fecha_obj >= last_barra.consumo.fec_fin:
				newB = BarraProgreso.objects.create(consumo=consumo, fecha = fecha_prog,	progreso = progreso,anterior = anterior)
				newB.save()
		else:
			newB = BarraProgreso.objects.create(consumo=consumo, fecha = date.today(),	progreso = progreso,anterior = anterior)
			newB.save()

	return redirect(f"/item/{consumo.item.id}")



def wikihome(request):
	return render(request,'base_wiki.html',{})


def addwiki(request):
	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		categoria = Category.objects.get(pk=22)
		contenido = request.POST.get("info")

		newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		newI.save()

		return redirect(f'/wiki/{newI.id}')

	return render(request,'add-wiki.html',{})


def wikis(request):
	page = request.GET.get('page', 1)
	wikis = Item.objects.filter(tipo__id=22).order_by('titulo')
	paginator = Paginator(wikis, 30)
	resultados = paginator.get_page(page)
	return render(request,'wikis.html',{'wikis':resultados})


def wiki(request,w):

	page = request.GET.get('page', 1)

	this_item = Item.objects.get(pk=int(w))
	wikipages = AttrItem.objects.filter(item=this_item).order_by('-child__fecha_edicion')
	paginator = Paginator(wikipages, 30)
	resultados = paginator.get_page(page)



	return render(request,'wiki.html',{'wiki':this_item,'wikis':resultados})


def wikipage(request,p,w):
	this_item = Item.objects.get(pk=int(p))
	this_wiki = Item.objects.get(pk=int(w))

	atributos = Atributos.objects.filter(item=this_item).order_by('orden')
	return render(request,'page.html',{'this_item':this_item,'this_wiki':this_wiki,'atributos':atributos})


def addwikipage(request,w):
	wiki = Item.objects.get(pk=int(w))
	cats = Category.objects.filter(id__in=[6,7,23,24,25])

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("info")
		newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		newI.save()

		newRel = AttrItem.objects.create(item=wiki,child=newI,rel_name='wikipage')
		newRel.save()

		wiki_id =request.POST.get("wiki")
		return redirect(f'/edit-item/{newI.id}?wiki={wiki_id}')


	return render(request,'add-wiki-page.html',{'wiki':wiki,'cats':cats})


def wikiatts(request,i,w):

	this_item = Item.objects.get(pk=int(i))
	wiki = int(w)
	cadena = ""

	conteo = Atributos.objects.filter(item = this_item).count()

	if conteo > 0:
		atts = Atributos.objects.filter(item = this_item).order_by('orden')

		for a in atts:
			cadena = cadena + f"{a.orden}|{a.nombre}|{a.tipo}|{a.valor}\n"

	if request.method == 'POST':
		Atributos.objects.filter(item=this_item).delete()

		txt_atributos = request.POST.get("txt_atributos")

		lineas = []
		for line in txt_atributos.splitlines():
			parts = line.split('|')
			lineas.append(parts)

		for l in lineas:
			if l[2]=='txt':
				newAtt = Atributos.objects.create(item=this_item,
					orden=int(l[0]),
					tipo=l[2],
					nombre=l[1],
					texto=l[3])
				newAtt.save()
			elif l[2]=='fec':
				newAtt = Atributos.objects.create(item=this_item,
					orden=int(l[0]),
					tipo=l[2],
					nombre=l[1],
					fecha=l[3])
				newAtt.save()
			elif l[2]=='int':
				newAtt = Atributos.objects.create(item=this_item,
					orden=int(l[0]),
					tipo=l[2],
					nombre=l[1],
					entero=l[3])
				newAtt.save()
			elif l[2]=='dec':
				newAtt = Atributos.objects.create(item=this_item,
					orden=int(l[0]),
					tipo=l[2],
					nombre=l[1],
					decimal=float(l[3]))
				newAtt.save()
		return redirect(request.path)

	return render(request,'wiki-atts.html',{'this_item':this_item,'cadena':cadena,'largo_c':len(cadena)})

def viewphotos(request,i,w):
	this_item = Item.objects.get(pk=int(i))

	nphotos = AttrImage.objects.filter(item=this_item,tipo='panorma').count()

	if nphotos > 0:
		vphotos = AttrImage.objects.filter(item=this_item,tipo='panorma', vista = False).count()
		if vphotos == 0:
			AttrImage.objects.filter(item=this_item,tipo='panorma', vista = True).update(vista=False)

		pks = AttrImage.objects.filter(item=this_item,tipo='panorma', vista = False).values_list('pk', flat=True)
		random_pk = choice(pks)
		random_obj = AttrImage.objects.get(pk=random_pk)
		random_obj.vista = True
		random_obj.save()

		return render(request,'view-photos.html',{'this_item':this_item,'this_pic':random_obj,'wiki_id':w})
	else:
		return redirect(f'/wikipage/{i}/{w}')

def quemar(request,i):
    Item.objects.filter(id=int(i)).update(consumido=True)
    return redirect(f'/item/{i}')


def beerlog(request):
	beers = Item.objects.filter(tipo__category='Beer', consumido=True).order_by('-fecha_edicion')

	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'beer.html',{'beers':beers,'cats':cats,'nbeers':len(beers)})

def logbeer(request,t):

	this_beer = Item.objects.get(pk=int(t))


	newC = Consumo.objects.create(item=this_beer,
				fec_ini=datetime.today().date(),
				fec_fin = datetime.today().date(),
				formato='cerveza',
				unidades = 'bebida',
				cantidad=1,
				multiplicador=1,
				consumo=1)
	newC.save()
	this_beer.consumido = True
	this_beer.fecha_edicion = datetime.now()
	this_beer.save()
	return redirect("/beer-log/")

def addBeer(request):
	if request.method == 'POST':
		categoria = Category.objects.get(pk=11)
		post_nombre = request.POST.get("nombre")
		post_tipo =  request.POST.get("tipo")
		post_graduacion =  request.POST.get("graduacion")
		post_origen =  request.POST.get("origen")
		post_contenido = request.POST.get("contenido")
		newItem = Item.objects.create(titulo = post_nombre,
			tipo = categoria,
			contenido = post_contenido,
			fecha_creacion='1999-12-31',
			fecha_edicion='1999-12-31')

		newAtt = Atributos.objects.create(item=newItem,
			orden=1,
			tipo='txt',
			nombre='origen',
			texto=post_origen)
		newAtt.save()

		newAtt = Atributos.objects.create(item=newItem,
			orden=2,
			tipo='dec',
			nombre='graduacion',
			decimal=post_graduacion)
		newAtt.save()

		newAtt = Atributos.objects.create(item=newItem,
			orden=3,
			tipo='txt',
			nombre='tipo',
			texto=post_tipo)
		newAtt.save()

		return redirect(f"/item/{newItem.id}")

	return render(request,'add-beer.html',{})

def addTimesItem(request):
	cats = sorted(Category.objects.exclude(id__in=[1,2,20,14]),key=lambda t: t.nitems, reverse=True)

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

		if categoria.category.lower() in ['manga volume','book','bunko','manga series','comic book','movie','anime season','anime film','tv series','show season','persona','album','band']:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		    newI.save()
		else:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		    newI.save()


		return redirect(f'/edit-item/{newI.id}')

	return render(request,'add-times-item.html',{'cats':cats})


def addBook(request):
	cat = Category.objects.get(pk=1)
	authors = Item.objects.filter(tipo__category='Persona').order_by('titulo')
	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		contenido = request.POST.get("contenido")
		author_id = request.POST.get("author_id")
		autor = Item.objects.get(pk=int(author_id))

		newI = Item.objects.create(titulo=titulo,tipo=cat,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		newI.save()

		photo = request.FILES.get("imagen")

		newIimg = AttrImage.objects.create(item=newI, imagen=photo,caption='tba',tipo='cover')
		newIimg.save()

		newAtt = Atributos.objects.create(item=newI,orden=1,tipo='int',nombre='pubyear',entero=int(request.POST.get("pubyear")))
		newAtt.save()

		newRel = AttrItem.objects.create(item=autor,child=newI,rel_name='author')
		newRel.save()

		return redirect(f'/item/{newI.id}')

	return render(request,'add-book.html',{'authors':authors})

def addbunko(request):
	cat = Category.objects.get(pk=9)
	authors = Item.objects.filter(tipo__category='Bunko Series').order_by('titulo')
	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		contenido = request.POST.get("contenido")
		author_id = request.POST.get("author_id")
		autor = Item.objects.get(pk=int(author_id))

		newI = Item.objects.create(titulo=titulo,tipo=cat,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		newI.save()

		photo = request.FILES.get("imagen")

		newIimg = AttrImage.objects.create(item=newI, imagen=photo,caption='tba',tipo='cover')
		newIimg.save()

		newAtt = Atributos.objects.create(item=newI,orden=1,tipo='int',nombre='pubyear',entero=int(request.POST.get("pubyear")))
		newAtt.save()

		newRel = AttrItem.objects.create(item=autor,child=newI,rel_name='volume')
		newRel.save()

		return redirect(f'/item/{newI.id}')

	return render(request,'add-bunko.html',{'authors':authors})

def addAlbum(request):
	if request.method == 'POST':
		photo = request.FILES.get("imagen")
		newAlbum = Album.objects.create(titulo = request.POST.get("titulo"),
			artista = request.POST.get("artista"),
			anho = int(request.POST.get("anho")),
			imagen = photo,
			last_played=datetime.now())
		return redirect(f"/album/{newAlbum.id}")
	return render(request,'add-album.html',{})

def album(request,album):
	this_album = Album.objects.get(pk=int(album))
	songs = Song.objects.filter(album=this_album)

	return render(request,'album.html',{'this_album':this_album,'songs':songs})

def logalbum(request,album):
	this_album = Album.objects.get(pk=int(album))
	newA = AlbumLog.objects.create(album = this_album, fecha = datetime.now() )
	newA.save()
	this_album.last_played = datetime.now()
	this_album.save()
	return redirect(f"/album/{this_album.id}")

def addsong(request,album):
	this_album = Album.objects.get(pk=int(album))
	if request.method == 'POST':
		songs = request.POST.get("contenido").split("\n")
		for s in songs:
			if len(s)>0:
				newS = Song.objects.create(album = this_album,
					titulo_cancion = s)
				newS.save()
		return redirect(f'/album/{this_album.id}')


	return render(request,'add-songs.html',{'this_album':this_album})

def addcharbatch(request,wiki):
	this_wiki = Item.objects.get(pk=int(wiki))
	categoria = Category.objects.get(pk=6)

	if request.method == 'POST':
		chars = request.POST.get("contenido").split("\n")
		for s in chars:
			if len(s)>0:
				item = s.split(":")
				if len(item) > 1:
					ctitulo = item[0].strip()
					ccontenido = item[1].strip() + "==headtext=="

					newI = Item.objects.create(titulo=ctitulo,tipo=categoria,contenido=ccontenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
					newI.save()

					newRel = AttrItem.objects.create(item=this_wiki,child=newI,rel_name='wikipage')
					newRel.save()

		return redirect(f'/wiki/{this_wiki.id}')



	return render(request,'add-char-batch.html',{'this_wiki':this_wiki})



def albums(request):
	page = request.GET.get('page', 1)
	albums = Album.objects.all().order_by('-last_played')
	paginator = Paginator(albums, 30)
	resultados = paginator.get_page(page)
	return render(request,'albums.html',{'wikis':resultados})

def menu(request):
	cats = sorted(Category.objects.exclude(id=14),key=lambda t: t.nitems, reverse=True)
	return render(request,'menu.html',{'cats':cats})

def addseason(request):
	cats = Category.objects.filter(id__in=[5,12,27])
	authors = Item.objects.filter(tipo__category='Persona').order_by('titulo')
	if request.method == 'POST':
		post_titulo = request.POST.get("titulo")
		post_premiere = request.POST.get("premiere-date")
		post_finale = request.POST.get("finale-date")
		post_tipo = request.POST.get("cat_id")
		categoria = Category.objects.get(pk=int(post_tipo))
		post_eps = request.POST.get("n-episodes")
		post_contenido = request.POST.get("contenido")


		newI = Item.objects.create(titulo=post_titulo,tipo=categoria,contenido=post_contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		newI.save()

		photo = request.FILES.get("imagen")

		newIimg = AttrImage.objects.create(item=newI, imagen=photo,caption='tba',tipo='cover')
		newIimg.save()

		newAtt = Atributos.objects.create(item=newI,orden=1,tipo='fec',nombre='premiere',fecha=post_premiere)
		newAtt.save()

		newAtt = Atributos.objects.create(item=newI,orden=2,tipo='fec',nombre='finale',fecha=post_finale)
		newAtt.save()

		newAtt = Atributos.objects.create(item=newI,orden=3,tipo='int',nombre='episodes',entero=post_eps)
		newAtt.save()

		return redirect(f'/item/{newI.id}')

	return render(request,'add-season.html',{'cats':cats})







