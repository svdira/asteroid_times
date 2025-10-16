from django.db import models
from datetime import datetime
from django.db import models
from django.utils import timezone
import os
from uuid import uuid4
from django.db.models import Q, Avg, Count, Min, Sum
from random import choice
import markdown

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

class Category(models.Model):
    category = models.CharField(max_length=255)

    @property
    def nitems(self):
        n_w = Item.objects.filter(tipo = self).count()
        return n_w

    def __str__(self):
        return self.category


class Item(models.Model):
    titulo = models.CharField(max_length=255)
    tipo = models.ForeignKey(Category, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField()
    fecha_edicion = models.DateTimeField()
    consumido = models.BooleanField(default=False)

    @property
    def headtext(self):
        n_corte = self.contenido.find('==headtext==')
        if n_corte == -1:
            return self.contenido[0:350]
        else:
            return markdown.markdown(self.contenido[0:n_corte],extensions=['extra'])

    @property
    def mdOutput(self):
        n_corte = self.contenido.find('==headtext==')
        if n_corte == -1:
            this_texto = self.contenido
        else:
            this_texto = self.contenido.replace('==headtext==','')
        return(markdown.markdown(this_texto,extensions=['extra']))


    @property
    def credit_links(self):

        if self.tipo.category.lower() == 'book':
            ncreds = AttrItem.objects.filter(child=self, rel_name__in=['author','illustratror','pseudonym']).count()
            if ncreds > 0:
                creds = AttrItem.objects.filter(child=self, rel_name__in=['author','illustratror','pseudonym'])

                enlaces = ""

                for c in creds:
                    if c.rel_name != 'author':
                        this_c = "(" + c.credito +")"
                    else:
                        this_c = ""
                    enlaces = enlaces + "<a href='/item/"+str(c.item.id)+"' style='text-decoration:none; color:#6F8FAF;'>"+c.item.titulo+this_c+"</a>,&nbsp;"

                clinks = enlaces = enlaces[:-7]
            else:
                clinks = None
        else:
            clinks = None

        return clinks

    @property
    def periodo(self):
        this_v = None
        pubyear = None
        if self.tipo.category.lower() in ['book','bunko']:
            npubyear = AttrInteger.objects.filter(item=self,att_name='pubyear').count()
            if npubyear > 0:
                pubyear = AttrInteger.objects.filter(item=self,att_name='pubyear').latest('id')
                this_v = f"({pubyear.att_value})"
        if self.tipo.category.lower() in ['movie','season','tv series','anime']:
            npubyear = AttrInteger.objects.filter(item=self,att_name='premiere').count()
            nfin = AttrInteger.objects.filter(item=self,att_name='finale').count()
            if npubyear > 0:
                pubyear = AttrInteger.objects.filter(item=self,att_name='premiere').latest('id')
            if nfin > 0:
                finale = AttrInteger.objects.filter(item=self,att_name='finale').latest('id')

            if nfin == 0 and npubyear > 0:
                this_v = f"({pubyear.att_value})"
            elif nfin > 0 and npubyear > 0 and finale == pubyear:
                this_v = f"({pubyear.att_value})"
            elif nfin > 0 and npubyear > 0 and finale != pubyear:
                this_v = f"({pubyear.att_value} - {finale.att_value})"


        return this_v

    @property
    def mainPic(self):
        npics = AttrImage.objects.filter(item=self,tipo='cover').count()
        if npics == 0:
            return None
        else:
            pks = AttrImage.objects.filter(item=self,tipo='cover').values_list('pk', flat=True)
            random_pk = choice(pks)
            ppic = AttrImage.objects.get(pk=random_pk)
            return ppic.imagen.url

    @property
    def aplica_consumo(self):
        if self.tipo.category.lower() in ['book','movie','bunko','tv series','anime','season']:
            return True
        else:
            return None

    @property
    def nrelated(self):
        conteo = AttrItem.objects.filter(item=self).count()
        return conteo

    def __str__(self):
        return self.titulo

class Consumo(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    fec_ini = models.DateField()
    fec_fin = models.DateField(null=True, blank=True)
    unidades = models.CharField(max_length=100)
    cantidad = models.IntegerField()
    multiplicador = models.IntegerField()
    consumo = models.IntegerField()
    formato = models.CharField(max_length=200)

    def __str__(self):
        return self.item.titulo

class AttrItem(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE,related_name="parent_item")
    child = models.ForeignKey(Item,on_delete=models.CASCADE,related_name="child_item")
    rel_name = models.CharField(max_length=255)

    def __str__(self):
        return self.child.titulo + ' @ ' + self.item.titulo

class AttrImage(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to=path_and_name, max_length=255, null=True, blank=True)
    caption = models.TextField()
    tipo = models.CharField(max_length=30)

    def __str__(self):
        return self.tipo + ' @ ' + self.item.titulo

class AttrDate(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    att_name = models.CharField(max_length=255)
    att_value = models.DateField()

    def __str__(self):
        return self.att_name + ' @ ' + self.item.titulo

class AttrInteger(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    att_name = models.CharField(max_length=255)
    att_value = models.IntegerField()

    def __str__(self):
        return self.att_name + ' @ ' + self.item.titulo

class AttrText(models.Model):
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    att_name = models.CharField(max_length=255)
    att_value = models.TextField()

    def __str__(self):
        return self.att_name + ' @ ' + self.item.titulo





