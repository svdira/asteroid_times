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
	cats = Category.objects.all().order_by('category')

	if request.method == 'POST':
		titulo = request.POST.get("titulo")
		cat_id = request.POST.get("category")
		categoria = Category.objects.get(pk=int(cat_id))
		contenido = request.POST.get("contenido")

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

	return render(request,'homepage.html',{'articles':resultados,'cats':cats})


def item(request,i):
	this_item = Item.objects.get(pk=int(i))
	cats = sorted(Category.objects.all(),key=lambda t: t.nitems, reverse=True)

	return render(request,'item.html',{'this_item':this_item,'cats':cats})

