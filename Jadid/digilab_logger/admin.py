from __future__ import unicode_literals
import logging
from django.contrib import admin
from django.utils.html import format_html
from .models import StatusLog


class StatusLogAdmin(admin.ModelAdmin):
    list_display = (
        'colored_msg',
        'create_datetime_format',
        'user',
        # 'cut_traceback' habe ich hier entfernt, weil es bei mir (Hendrik) einen Error (bei return format_html(message[-240:])) erzeugt hat, weswegen ich die StatusLog-Admin-Seite nicht mehr aufrufen konnte
    )
    list_display_links = ('colored_msg', )
    list_filter = ('level', )
    #list_per_page = 20

    def cut_traceback(self, obj):
        current_traceback = obj.trace
        counter = 0
        message = ""

        if current_traceback is not None:
            #print('länge:', len(current_traceback))
            for sign in current_traceback: #nach 60 zeichen findet ein Umbruch statt
                if counter % 60 == 0:
                    part_of_message = current_traceback[counter-60:counter]
                    message += part_of_message + "<br>"
                
                counter += 1

            if len(current_traceback) % 60 != 0: #hier wird der rest vom string angehängt
                last_part = current_traceback[-(len(current_traceback) % 60):]
                message += last_part
            
            if len(message) > 240: #Hier werden nur die letzten 240 Zeichen angezeigt, damit die Nachricht nicht zulang wird
                return format_html(message[-240:]) # erzeugt bei mir (Hendrik) einen "KeyError: 'labels' "; konnte nicht herausfinden warum
            else:
                return format_html(message)

    cut_traceback.short_description = 'Traceback'

    def colored_msg(self, instance):
        if instance.level in [logging.NOTSET, logging.INFO]:
            color = 'green'
        elif instance.level == logging.WARNING:
            color = 'orange'
        elif instance.level == logging.DEBUG:
            color = 'blue'
        else:
            color = 'red'

        return format_html('<span style="color: {color};">{msg}</span>', color=color, msg=instance.msg)

    colored_msg.short_description = 'Message'

    def traceback(self, instance):
        return format_html('<pre><code>{content}</code></pre>', content=instance.trace if instance.trace else '')

    def create_datetime_format(self, instance):
        return instance.create_datetime.strftime('%Y-%m-%d %X')

    create_datetime_format.short_description = 'Created at'


admin.site.register(StatusLog, StatusLogAdmin)
