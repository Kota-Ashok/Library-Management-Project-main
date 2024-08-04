from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from django.contrib.auth.models import User
from .models import *
from ouvrages.models import *

from django.template.loader import render_to_string


from django.core.mail import send_mail
from django.conf import settings


# @receiver(post_save, sender=Profile)


def createProfile(sender, instance, created, **kwargs):
    if created:
        user = instance
        profile = Profile.objects.create(
            user=user,
            username=user.username,
            email=user.email,
            prenom=user.first_name,
            nom=user.last_name,
        )

        subject = 'Welcome to Bibliotheque'
        message = 'We are glad you are here!'

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [profile.email],
            fail_silently=False,
        )


def updateUser(sender, instance, created, **kwargs):
    profile = instance
    user = profile.user

    if created == False:
        user.first_name = profile.prenom
        user.last_name = profile.nom
        user.username = profile.username
        user.email = profile.email
        user.save()


def deleteUser(sender, instance, **kwargs):
    try:
        user = instance.user
        user.delete()
    except:
        pass

def envoyer_email_nouvel_ouvrage(pk):
    instance = Ouvrage.objects.get(id=pk)
    sujet = f'Nouvel ouvrage ajouté à la bibliothèque: {instance.titre}'
    emails = UserEmail.objects.values_list('email', flat=True)

    contexte = {
        'titre': instance.titre,
        'description': instance.description,
        'lien_details': f"http://localhost:8000/ouvrage/{instance.id}"  # Link to the ouvrage details page
    }
    message = render_to_string('adherants/nouvel_ouvrage_email.html', contexte)
    send_mail(sujet, message, 'kotaashok331@gmail.com', emails)
    

@receiver(post_save, sender=Ouvrage)
def post_save_ouvrage(sender, instance, created, **kwargs):
    if created:
        envoyer_email_nouvel_ouvrage(instance.id)
        
        
# @receiver(post_save, sender=Reservation)
def send_reservation_confirmation_email(pk):
    instance = Reservation.objects.get(id=pk)
    exemplaire = instance.selected_copy
    sujet = f'Votre Réservation est acceptée, votre exemplaire est celui-ci : Code - {exemplaire.id}'
    # emails = UserEmail.objects.values_list('email', flat=True)  
    owner_email = instance.owner.email 
    return_date = instance.date_retour_prevue
    date_reservation = instance.date_reservation
    
    # Calculate the deadline for returning the item (48 hours after return date)
    deadline = return_date + timedelta(days=2)

    contexte = {
        'titre': exemplaire.ouvrage.titre,
        'code': exemplaire.id,
        'date_reservation': date_reservation.strftime("%d-%m-%Y"),
        'return_date': return_date.strftime("%d-%m-%Y"),
        'deadline': deadline.strftime("%d-%m-%Y"),
    }

    message = render_to_string('adherants/reservation_confirmation_email.html', contexte)
    # send_mail(sujet, message, 'kotaashok331@gmail.com', emails)
    send_mail(sujet, message, 'kotaashok331@gmail.com', [owner_email])
    # send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.user.email], fail_silently=False)

@receiver(post_save, sender=Reservation)
def post_save_reservation(sender, instance, created, **kwargs):
    if instance.statut == 'acceptee':
        send_reservation_confirmation_email(instance.id)
        
def send_cancellation_notification(pk):
    instance = Reservation.objects.get(id=pk)
    exemplaire = instance.selected_copy
    sujet = f'Annulation de votre réservation : Code - {exemplaire.id}'
    owner_email = instance.owner.email 
    
    contexte = {
        'titre': exemplaire.ouvrage.titre,
        'code': exemplaire.id,
    }
    
    message = render_to_string('adherants/reservation_cancellation_email.html', contexte)
    send_mail(sujet, message, 'kotaashok331@gmail.com', [owner_email])
    
@receiver(pre_delete, sender=Reservation)
def pre_delete_reservation(sender, instance, **kwargs):
    send_cancellation_notification(instance.id)

        
post_save.connect(createProfile, sender=User)
post_save.connect(updateUser, sender=Profile)
post_delete.connect(deleteUser, sender=Profile)

@receiver(post_save, sender=Reclamation)
def send_email_to_admin(sender, instance, created, **kwargs):
    if created:
        nom_utilisateur = instance.nom
        email_utilisateur = instance.email
        sujet_reclamation = instance.sujet
        message_reclamation = instance.message
        
        id_ouvrage = instance.ouvrage.id if instance.ouvrage else None

        sujet = f"Nouvelle réclamation : {sujet_reclamation}"
        contenu = f"Une nouvelle réclamation a été ajoutée :\n\nNom de l'utilisateur : {nom_utilisateur}\nE-mail de l'utilisateur : {email_utilisateur}\n\nSujet de la réclamation : {sujet_reclamation}\n\nContenu de la réclamation :\n{message_reclamation}\n\nID de l'ouvrage : {id_ouvrage}"
        # Envoyer l'e-mail à l'administrateur
        send_mail(
            sujet,
            contenu,
            'email_utilisateur',  
            ['kotaashok331@gmail.com'], 
            fail_silently=False,)