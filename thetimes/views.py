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
import math
import random
import re
import locale


def plantilla(request):
	return render(request,'base_times.html',{})

def addItem(request):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

		if categoria.category.lower() in ['book','bunko','manga volume','comic book','movie','anime','tv series','season']:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion='1999-12-31', fecha_edicion='1999-12-31')
		else:
		    newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		newI.save()

		return redirect(f'/edit-item/{newI.id}')

	return render(request,'add-item.html',{'cats':cats})

def editItem(request,i):
	this_item = Item.objects.get(pk=int(i))
	search_results = None
	item_rels = AttrItem.objects.filter(child=this_item)
	item_imgs = AttrImage.objects.filter(item=this_item)
	item_dates = AttrDate.objects.filter(item=this_item)
	item_ints = AttrInteger.objects.filter(item=this_item)
	item_texts = AttrText.objects.filter(item=this_item)

	if request.method == 'POST':
		if request.POST.get("formulario") == '1':
			this_item.contenido = request.POST.get("contenido")
			this_item.fecha_edicion = datetime.now()
			this_item.save()
			if request.POST.get("guardar") == "Save and View":
			    return redirect(f"/item/{this_item.id}")
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


	return render(request,'edit-item.html',{'this_item':this_item,'sr':search_results,'items':item_rels,'pics':item_imgs,'fechas':item_dates,'ints':item_ints,'texts':item_texts})


def homepage(request):
	page = request.GET.get('page', 1)
	articles = Item.objects.all().order_by('-fecha_creacion')
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	if page == 1:
	    in_progress = Consumo.objects.filter(fec_fin__isnull=True)
	else:
	    in_progress = None

	return render(request,'homepage.html',{'articles':resultados,'cats':cats,'in_progress':in_progress})


def categoria(request,c):
	page = request.GET.get('page', 1)
	this_cat = Category.objects.get(pk=int(c))
	articles = Item.objects.filter(tipo__id=int(c)).order_by('-fecha_creacion')
	paginator = Paginator(articles, 12)
	resultados = paginator.get_page(page)
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)

	return render(request,'category.html',{'this_cat':this_cat,'articles':resultados,'cats':cats})


def item(request,i):
	this_item = Item.objects.get(pk=int(i))
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	ncon = Consumo.objects.filter(item = this_item, fec_fin__isnull=True).count()
	if ncon > 0:
		con_in_prog = Consumo.objects.filter(item = this_item, fec_fin__isnull=True).latest('id')
	else:
		con_in_prog = None

	conteo_rel = AttrItem.objects.filter(item=this_item).count()

	if request.method == 'POST':
		con_in_prog.fec_fin = request.POST.get("fec_fin")
		con_in_prog.save()
		this_item.fecha_creacion = request.POST.get("fec_fin")
		this_item.consumido = True
		this_item.save()

	return render(request,'item.html',{'this_item':this_item,'cats':cats,'cons':con_in_prog,'conteo_r':conteo_rel})

def startConsumo(request,i):
	this_item = Item.objects.get(pk=int(i))

	if this_item.tipo.category.lower() in ['book','bunko','manga volume','comic book']:
		formatos = ['printed','kindle','audiobook']
		units = ['paginas','minutos','location']

	if this_item.tipo.category.lower() in ['movie','anime','tv series','season']:
		formatos = ['streaming','download','theater']
		units = ['minutes','episodes']


	if request.method == 'POST':
		fec_ini = request.POST.get("fec_ini")
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


	return render(request,'start_consumo.html',{'this_item':this_item,'formatos':formatos,'units':units})


def bookHistory(request):
	get_y = request.GET.get('y', 1)
	max_year = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).order_by('-fec_fin').first()

	this_y = max_year.fec_fin.year if int(get_y) == 1 else int(get_y)

	books = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False, fec_fin__year=this_y).order_by('-fec_fin')
	rbooks = len(books)
	qbooks = Item.objects.filter(tipo__category='Book',consumo__item__isnull=True).count()
	in_progress = Consumo.objects.filter(item__tipo__category='Book', fec_fin__isnull=True)

	nr_books = Item.objects.filter(tipo__category='Book',consumido	= True).count()


	anhos = Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).values('fec_fin__year').annotate(qbooks=Count('id')).order_by('-fec_fin__year')


	qbooks = qbooks + len(in_progress)
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	return render(request,'read-history.html',{'books':books,'nr_books':nr_books,'this_y':this_y,'anhos':anhos,'rbooks':rbooks,'qbooks':qbooks,'cats':cats,'anhos':anhos})

def bookQueue(request):
	books = Item.objects.filter(tipo__category='Book',consumo__item__isnull=True).order_by('titulo')
	qbooks = len(books)
	rbooks =  Consumo.objects.filter(item__tipo__category='Book',fec_fin__isnull=False).count()
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	in_progress = Consumo.objects.filter(item__tipo__category='Book', fec_fin__isnull=True)
	qbooks = qbooks + len(in_progress)
	return render(request,'read-queue.html',{'now_reading':in_progress,'books':books,'rbooks':rbooks,'qbooks':qbooks,'cats':cats})

def relatedItems(request,item):
	this_item = Item.objects.get(pk=int(item))

	tipos = []
	categories = AttrItem.objects.filter(item=this_item).values_list('child__tipo__category', flat=True).distinct()
	for cat in categories:
		items_cat = AttrItem.objects.filter(item=this_item, child__tipo__category=cat)
		tipos.append({'cat':cat,'items':items_cat})

	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)

	return render(request,'related-items.html',{'this_item':this_item,'tipos':tipos,'cats':cats})

def addChildItem(request, parent):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	this_parent = Item.objects.get(pk=int(parent))

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		relacion = request.POST.get("relacion")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

		newI = Item.objects.create(titulo=titulo,tipo=categoria,contenido=contenido,fecha_creacion=datetime.now(), fecha_edicion=datetime.now())
		newI.save()

		newRel = AttrItem.objects.create(item=this_parent,child=newI,rel_name=relacion)
		newRel.save()

		return redirect(f'/edit-item/{newI.id}')

	return render(request,'add-child-item.html',{'cats':cats,'this_parent':this_parent})

def searchPage(request):
	results = None
	results_2 = None
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)

	if request.method == 'POST':
		key_word = request.POST.get("key_word")
		results = Item.objects.filter(titulo__contains=key_word)
		ids =  Item.objects.filter(titulo__contains=key_word).values_list('id', flat=True)
		ids_list = list(ids)
		results_2 = Item.objects.filter(contenido__contains=key_word).exclude(id__in=ids_list)

	return render(request,'search-page.html',{'cats':cats,'rt':results,'rc':results_2})

def printHTML(request, cid):
	this_item = Item.objects.get(pk=int(cid))
	related = AttrItem.objects.filter(item=this_item).order_by('id')

	return render(request,'print_html.html',{'this_item':this_item, 'related':related })


def addContrato(request,equipo):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
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

		return redirect(f'/equipo/{equipo.id}')

	return render(request,'add-contrato.html',{'cats':cats,'this_equipo':equipo})


def equipo(request,equipo):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	equipo = Equipo.objects.get(pk=int(equipo))
	ligas = Torneo.objects.all().order_by('-id')

	arqueros = Contrato.objects.filter(equipo=equipo, posicion='arquero', fec_fin__isnull=True).order_by('dorsal')
	defensas = Contrato.objects.filter(equipo=equipo, posicion='defensa', fec_fin__isnull=True).order_by('dorsal')
	centros = Contrato.objects.filter(equipo=equipo, posicion='centrocampista', fec_fin__isnull=True).order_by('dorsal')
	delanteros = Contrato.objects.filter(equipo=equipo, posicion='delantero', fec_fin__isnull=True).order_by('dorsal')
	dt = Contrato.objects.filter(equipo=equipo, posicion='dt', fec_fin__isnull=True).order_by('dorsal')



	return render(request,'equipo.html',{'cats':cats,'this_equipo':equipo,'arqueros':arqueros,'defensas':defensas, 'centros':centros,'delanteros':delanteros,'dt':dt,'ligas':ligas})

def liga(request,liga):
	ligas = Torneo.objects.all().order_by('-id')
	this_liga = Torneo.objects.get(pk=int(liga))
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	pp = Partido.objects.filter(torneo=this_liga, terminado=False).order_by('fecha','id')
	pt = Partido.objects.filter(torneo=this_liga, terminado=True).order_by('-fecha','id')

	return render(request,'liga.html',{'cats':cats,'this_liga':this_liga,'pp':pp,'pt':pt,'ligas':ligas})

def addMatch(request,liga):
	this_liga = Torneo.objects.get(pk=int(liga))
	ligas = Torneo.objects.all().order_by('-id')
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
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


	return render(request,'add-match.html',{'cats':cats,'this_liga':this_liga,'equipos':equipos,'up':ult_partido,'ligas':ligas,'rp':recent_partidos})

def partido(request,p):
	ligas = Torneo.objects.all().order_by('-id')
	this_partido = Partido.objects.get(pk=int(p))
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	pl = None
	pv = None
	contratos_l = None
	contratos_v = None

	goles = Gol.objects.filter(partido=this_partido).order_by('minuto','adicional')

	if this_partido.local.id in [1,2,3]:
		contratos_l = Contrato.objects.filter(equipo=this_partido.local, fec_fin__isnull=True).order_by('jugador__nombre')

	if this_partido.visita.id in [1,2,3]:
		contratos_v = Contrato.objects.filter(equipo=this_partido.visita, fec_fin__isnull=True).order_by('jugador__nombre')


	next_m = Partido.objects.filter(torneo=this_partido.torneo, fecha__gte=this_partido.fecha,terminado=False).exclude(id=this_partido.id).order_by('fecha','id')

	if request.method == 'POST':
		goles_local = request.POST.get("goles_local")
		goles_visita = request.POST.get("goles_visita")

		if request.POST.get("pl",""):
			pl = request.POST.get("pl","")
		if request.POST.get("pv",""):
			pv = request.POST.get("pv","")

		this_partido.goles_local = int(goles_local)
		this_partido.goles_visita = int(goles_visita)
		if pl or pv:
			this_partido.rondap_local = int(pl)
			this_partido.rondap_visita = int(pv)
		this_partido.terminado = True
		this_partido.save()

	return render(request,'partido.html',{'cats':cats,'this_partido':this_partido,'next_m':next_m,'ligas':ligas,'contratos_l':contratos_l,'contratos_v':contratos_v,'goles':goles})


def futbol(request,p):
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	ligas = Torneo.objects.all().order_by('-id')
	conteo_p = Partido.objects.filter(terminado=False).count()
	if p == '0' and conteo_p > 0:
		partidos = Partido.objects.filter(terminado=False).order_by('fecha','id')
	else:
		partidos = Partido.objects.filter(terminado=True).order_by('-fecha','id')


	cm = []
	cligas = Partido.objects.filter(terminado=False).values_list('torneo__nombre', flat=True).distinct()
	for l in cligas:
		partidos_pj = Partido.objects.filter(terminado=False, torneo__nombre=l)
		cm.append({'liga':l,'partidos':partidos_pj})

	return render(request,'futbol.html',{'cats':cats,'ligas':ligas,'partidos':partidos,'tc':p,'cm':cm})

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
		this_contrato = Contrato.objects.get(pk=4)


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
	equipos = Equipo.objects.all().order_by('nombre')
	ligas = Torneo.objects.all().order_by('-id')
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


	return render(request,'alineacion.html',{'this_partido':this_partido,'contratos':contratos,'ligas':ligas,'alineaciones':these_alineaciones})


def journal(request):
	get_y = request.GET.get('y', 1)
	max_year = JournalEntry.objects.all().order_by('-fecha').first()

	this_y = max_year.fecha.year if int(get_y) == 1 else int(get_y)

	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)
	entries = JournalEntry.objects.filter(fecha__year=this_y).order_by('-fecha','-id')

	anhos = JournalEntry.objects.all().values('fecha__year').exclude(fecha__year=this_y).annotate(qbooks=Count('id')).order_by('-fecha__year')

	if request.method == 'POST':
		fecha = request.POST.get("fecha")
		# Convert string to datetime object
		date_obj = datetime.strptime(fecha, "%Y-%m-%d")
		# Format it to desired string
		formatted_date = date_obj.strftime("%A, %B %d, %Y")
		tipo = Category.objects.get(pk=14)
		contenido = request.POST.get("contenido")
		newI = Item.objects.create(titulo=formatted_date,tipo=tipo,contenido=contenido,fecha_creacion=datetime.now(),fecha_edicion=datetime.now(),consumido=False)
		newI.save()

		newJ = JournalEntry.objects.create(fecha=fecha, item = newI)
		newJ.save()
	return render(request,'journal.html',{'cats':cats,'entries':entries,'this_y':this_y,'anhos':anhos})



