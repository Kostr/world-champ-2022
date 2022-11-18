from django.conf.locale.en import formats as en_formats
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Player, Command, Match, MatchGuess

en_formats.DATETIME_FORMAT = "d b Y H:i:s"

class CommandAdmin(admin.ModelAdmin):
    list_display = ('name', 'group')
    list_display_links = ('name', )
    list_per_page = 50
    search_fields = ('name', 'group')
    list_filter = ('name', 'group')

class MatchAdmin(admin.ModelAdmin):
    list_display = ('time', 'command_1', 'command_2', 'score_1', 'score_2', 'stage')
    list_display_links = ('time', 'command_1', 'command_2', 'score_1', 'score_2', 'stage')
    list_per_page = 50
    search_fields = ('time', 'command_1', 'command_2', 'score_1', 'score_2', 'stage')
    list_filter = ('time', 'command_1', 'command_2', 'score_1', 'score_2', 'stage')

class MatchGuessAdmin(admin.ModelAdmin):
    list_display = ('guesser', 'updated', 'match', 'guess_score_1', 'guess_score_2',)
    list_display_links = ('guesser', 'match', 'guess_score_1', 'guess_score_2',)
    list_per_page = 50
    search_fields = ('guesser', 'match', 'guess_score_1', 'guess_score_2',)
    list_filter = ('guesser', 'match', 'guess_score_1', 'guess_score_2',)

class PlayerInline(admin.StackedInline):
    model = Player
    can_delete = False
    verbose_name_plural = u'Профиль игрока'

class UserAdmin(BaseUserAdmin):
    inlines = (PlayerInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'nicevt', 'money')

    def nicevt(self, x):
        return x.player.nicevt
    nicevt.short_description = u'НИЦЭВТ'
    nicevt.boolean = True

    def money(self, x):
        return x.player.money
    money.short_description = u'Поставил деньги'
    money.boolean = True

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Command, CommandAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(MatchGuess, MatchGuessAdmin)
