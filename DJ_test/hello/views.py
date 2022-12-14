from imp import reload
import json
from hello.models import Event
import random
from django.urls import reverse
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.timezone import datetime
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt # whatsapp
from twilio.twiml.messaging_response import MessagingResponse # for Whatsapp

import time
import openai
import deepl
import googlemaps
from twilio.rest import Client
from django.conf import settings


# Twilio data
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN    
client = Client(account_sid, auth_token)

# Openai key
openai.api_key = settings.OPENAI_API_KEY

# Deepl key
deepl_key = settings.DEEPL_KEY

# Google maps key
maps_key = settings.GOOGLE_MAPS_API_KEY_COORDINATES
gmaps = googlemaps.Client(key=maps_key)


def home2(request):
    return HttpResponse("Bienvenido a AI Way, tu aliado en mantenerte seguro")

def home(request):

    events = [{"category": entry.category, 
                "latitude": entry.latitude, 
                "longitude": entry.longitude, 
                "description": entry.description} 
                for entry in Event.objects.all()]
    print("$&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&", events)

    return render(
        request,
        'hello/hello_there.html',
        {
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'someDjangoVariable' : json.dumps(events)
        }
    )


# Function that reads the last message
def read_message() -> str:
    message = client.messages.list()[0]
    print(message.body)
    return message.body


# Function that checks whether the response is complete
def is_none(response: str) -> bool:
    lst_response = response.split("|")
    return "None" == lst_response[3]


# Function that translates the message
def translate_message(message: str) -> str:
    translator = deepl.Translator(deepl_key)
    result = translator.translate_text(message, target_lang="EN-US")
    return result.text


# Function that if the location is not None, it sends a message
def ask_location(user):
    client.messages.create(from_="whatsapp:+14155238886",
                        body="¿Donde ocurrio el evento?",
                        to=user)
    # time.sleep(10)
    # while message() == "¿Donde ocurrio el evento?":
    #     time.sleep(10)
    return read_message()


# Function that recognize the important aspects of an alert
def recognize_alert(message, user):
    # message = message()
    message = translate_message(message)
    print(message)
    table = "|Traffic or Security or None|Event|Location or None|\n|:---:|:---:|:---:|"    # Temporal
    response = openai.Completion.create(
            model="text-davinci-002",
            prompt=f"A table that parse the following alert if it applies\n{message}\n{table}\n",
            temperature=0.03,
            max_tokens=100,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    )
    response = response.choices[0].text
    # None in response?
    if is_none(response):
        location = ask_location(user)
        location = translate_message(location)
        response = response.replace("None", location)
    
    # Prints the response
    print(response)

    return response


@csrf_exempt
def message(request):
    if request.method == 'POST':
        user = request.POST.get('From')
        message = request.POST.get('Body')
        # data_client = client.messages.list(limit=1, )[0]
        # msg_id = request.POST.get('MessageSid')
        
        # print(request.POST)
        # print(date_created) # when was the message forwarded
        print(f'{user} says {message}')

        resp = recognize_alert(f'{message}', user)

        response = MessagingResponse()
        response.message('¡Ay Wey! Gracias por reportar.')

        cat, desc, loc = [x for x in resp.split("|") if x]
        geocode = gmaps.geocode(loc)
        print("GEOCODE: ", geocode)
        
        lat = geocode[0]["geometry"]["location"]["lat"]
        lng = geocode[0]["geometry"]["location"]["lng"]
 
        event = Event(category=cat, latitude=lat, longitude=lng, description=desc)
        event.save()

        return HttpResponse(str(response))
    else:
        return render(request, 'hello/hello_there.html',
            {
                'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
                'someDjangoVariable' : json.dumps([{"category": entry.category, 
                    "latitude": entry.latitude, 
                    "longitude": entry.longitude, 
                    "description": entry.description} 
                    for entry in Event.objects.all()])
            }
        )