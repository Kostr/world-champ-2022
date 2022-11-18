from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nicevt = models.BooleanField(default=True, verbose_name=u'НИЦЭВТ')
    money = models.BooleanField(default=False, verbose_name=u'Поставил деньги')

    def __str__(self):
        return self.user.username
    def __unicode__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if (not hasattr(instance, 'player')):
        Player.objects.create(user=instance)
    instance.player.save()

class Command(models.Model):
    name = models.CharField(max_length=255, verbose_name=u'команда')
    group = models.CharField(max_length=1, verbose_name=u'группа', default="A")
    flag = models.ImageField(blank=True, verbose_name=u'флаг')

    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name

class Match(models.Model):
    time = models.DateTimeField(verbose_name=u'время матча')

    MATCH_CLASS_GROUP = u'group'
    MATCH_CLASS_1_8 = u'1/8'
    MATCH_CLASS_1_4 = u'1/4'
    MATCH_CLASS_1_2 = u'1/2'
    MATCH_CLASS_FINAL = u'final'
    MATCH_CLASS_3RD = u'3rd'
    MATCH_CLASSES = (
        (MATCH_CLASS_GROUP, u'Групповой этап'),
        (MATCH_CLASS_1_8, u'1/8 финала'),
        (MATCH_CLASS_1_4, u'Четвертьфинал'),
        (MATCH_CLASS_1_2, u'Полуфинал'),
        (MATCH_CLASS_FINAL, u'Финал'),
        (MATCH_CLASS_3RD, u'Матч за 3 место'),
    )
    stage = models.CharField(max_length=255, choices=MATCH_CLASSES, default=MATCH_CLASS_GROUP, verbose_name=u'класс матча')

    command_1 = models.ForeignKey(Command, related_name='command_1', verbose_name=u'команда 1', blank=True, null=True, on_delete=models.CASCADE)
    command_2 = models.ForeignKey(Command, related_name='command_2', verbose_name=u'команда 2', blank=True, null=True, on_delete=models.CASCADE)
    score_1 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 1')
    score_2 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 2')
    extra_score_1 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 1 в доп. время')
    extra_score_2 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 2 в доп. время')
    penalty_score_1 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 1 в серии пенальти')
    penalty_score_2 = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=u'голы команды 2 в серии пенальти')

    def __str__(self):
        if self.command_1 and self.command_2:
            return self.command_1.name + " - " + self.command_2.name + " (" + self.stage + ")"
        else:
            return "? - ?" + " (" + self.stage + ")"
    def __unicode__(self):
        if self.command_1 and self.command_2:
            return self.command_1.name + " - " + self.command_2.name + " (" + self.stage + ")"
        else:
            return "? - ?" + " (" + self.stage + ")"

class MatchGuess(models.Model):
    guesser = models.ForeignKey(User, verbose_name=u'угадывающий', on_delete=models.CASCADE)
    match = models.ForeignKey(Match, verbose_name=u'матч', on_delete=models.CASCADE)
    guess_score_1 = models.PositiveSmallIntegerField(verbose_name=u'голы команды 1')
    guess_score_2 = models.PositiveSmallIntegerField(verbose_name=u'голы команды 2')
    updated = models.DateTimeField(auto_now=True, verbose_name=u'время прогноза')