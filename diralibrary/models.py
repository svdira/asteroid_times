from django.db import models
from datetime import datetime
from django.db import models
from django.utils import timezone
import os
from uuid import uuid4
from django.db.models import Q, Avg, Count, Min, Sum
from random import choice
import markdown
from PIL import Image

def path_and_name(instance, filename):
    upload_to = 'item_media'
    ext = filename.split('.')[-1]
    # get filename
    if instance.pk:
        filename = '{}.{}'.format(instance.pk, ext)
    else:
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join(upload_to, filename)

class Persona(models.Model):
	nombre = models.CharField(max_length=512)
	bio = models.TextField()

	@property
	def headtext(self):
		n_corte = self.bio.find('==headtext==')
		if n_corte == -1:
			return self.bio[0:350]
		else:
			return markdown.markdown(self.bio[0:n_corte],extensions=['extra'])

	@property
	def mdOutput(self):
		n_corte = self.bio.find('==headtext==')
		if n_corte == -1:
			this_texto = self.bio
		else:
			this_texto = self.bio.replace('==headtext==','')

		return(markdown.markdown(this_texto,extensions=['extra']))

	def __str__(self):
		return self.nombre

class Tipo(models.Model):
	nombre = models.CharField(max_length=512)
	desc = models.TextField()

	def __str__(self):
		return self.nombre

class Titulo(models.Model):
	titulo = models.CharField(max_length=512)
	titulo_original = models.CharField(max_length=512)
	idioma_original = models.CharField(max_length=80)
	fecha_publicacion = models.DateField(blank=True,null=True)
	tipo = models.ForeignKey(Tipo, on_delete=models.CASCADE)
	anho_publicacion = models.IntegerField()
	synopsis = models.TextField()

	@property
	def headtext(self):
		n_corte = self.synopsis.find('==headtext==')
		if n_corte == -1:
			return self.synopsis[0:350]
		else:
			return markdown.markdown(self.synopsis[0:n_corte],extensions=['extra'])

	@property
	def mdOutput(self):
		n_corte = self.synopsis.find('==headtext==')
		if n_corte == -1:
			this_texto = self.synopsis
		else:
			this_texto = self.synopsis.replace('==headtext==','')

		return(markdown.markdown(this_texto,extensions=['extra']))

	@property
	def mainPic(self):
		npics = Cubiertas.objects.filter(titulo=self,tipo='cover').count()
		if npics == 0:
			return None
		else:
			pks = Cubiertas.objects.filter(titulo=self,tipo='cover').values_list('pk', flat=True)
			random_pk = choice(pks)
			ppic = Cubiertas.objects.get(pk=random_pk)
			return ppic.thumbnail_path

	@property
	def tcredits(self):
		this_creditos = Credito.objects.filter(libro=self)
		enlaces = ""
		for c in this_creditos:
			enlaces = enlaces + "<a href='/lib/persona/"+str(c.persona.id)+"' style='text-decoration:none; color:#6F8FAF;'>"+c.persona.nombre+"</a>,&nbsp;"

		clinks = enlaces[:-7]
		return clinks

	def __str__(self):
		return self.titulo

class Comentario(models.Model):
	titulo = models.ForeignKey(Titulo, on_delete=models.CASCADE)
	tiempo = models.DateTimeField(auto_now_add=True)
	texto = models.TextField()
	encabezado = models.CharField(max_length=512,default=None,null=True, blank=True)
	es_personaje = models.BooleanField(default=False)

	def __str__(self):
		return self.titulo.titulo




class Credito(models.Model):
	persona = models.ForeignKey(Persona, on_delete=models.CASCADE)
	libro = models.ForeignKey(Titulo, on_delete=models.CASCADE)
	credito = models.CharField(max_length=200)

	def __str__(self):
		return self.persona.nombre + ' @ ' + self.libro.titulo

class MetaData(models.Model):
	titulo = models.ForeignKey(Titulo, on_delete=models.CASCADE)
	tipomd = models.CharField(max_length=200)
	tag = models.CharField(max_length=200)

	def __str__(self):
		return self.tag + ' @ ' + self.titulo.titulo

class Consumo(models.Model):
	titulo = models.ForeignKey(Titulo, on_delete = models.CASCADE)
	fecha_ini = models.DateField()
	fecha_fin = models.DateField(null=True,blank=True)
	formato = models.CharField(max_length=128)
	idioma = models.CharField(max_length=128)
	unidades = models.CharField(max_length=128)
	cantidad = models.IntegerField()

	def __str__(self):
		return self.titulo.titulo

class Cubiertas(models.Model):
    titulo = models.ForeignKey(Titulo,on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)
    caption = models.TextField()
    tipo = models.CharField(max_length=30)
    vista = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.imagen:
            img_path = self.imagen.path
            thumb_path = os.path.join(os.path.dirname(img_path),
                "thumbnails/" + os.path.basename(img_path))
            img = Image.open(img_path)
            img.thumbnail((400, 400))  # <--- thumbnail size
            img.save(thumb_path)

    @property
    def thumbnail_path(self):
        parts = self.imagen.url.split('/')
        parts.insert(3, 'thumbnails')
        result = '/'.join(parts)
        return result


    def __str__(self):
        return self.tipo + ' @ ' + self.titulo.titulo


