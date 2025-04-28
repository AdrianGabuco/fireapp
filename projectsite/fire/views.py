import json
from django.db import connection
from django.http import JsonResponse
from django.db.models.functions import ExtractMonth
from django.db.models import Count
from datetime import datetime
from django.shortcuts import render
from django.views.generic.list import ListView
from fire.models import Locations, Incident, FireStation


class HomePageView(ListView):
    model = Locations
    context_object_name = 'home'
    template_name = "home.html"

class ChartView(ListView):
    template_name = 'chart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
    def get_queryset(self, *args, **kwargs):
        pass

def PieCountDySeverity(request):
    query = '''
    SELECT severity_level, COUNT(*) as count
    FROM fire_incident
    GROUP BY severity_level
    '''
    data = {}
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    if rows:
    # Construct the dictionary with severity level as keys and count as values
        data = {severity: count for severity, count in rows}
    else:
        data = {}

    return JsonResponse(data)


def map_station(request):
    fireStations = FireStation.objects.values('name', 'latitude', 'longitude')

    for fs in fireStations:
        fs['latitude'] = float(fs['latitude'])
        fs['longitude'] = float(fs['longitude'])

    fireStations_list = list(fireStations)

    context = {
    'fireStations': fireStations_list,
    }

    return render(request, 'map_station.html', context)


def map_incidents(request):
    incidents_qs = Incident.objects.select_related('location').values(
        'location__latitude', 'location__longitude',
        'severity_level', 'description', 'date_time'
    )

    incidents = []
    for i in incidents_qs:
        incidents.append({
            'latitude': float(i['location__latitude']),
            'longitude': float(i['location__longitude']),
            'severity_level': i['severity_level'],
            'description': i['description'],
            'date_time': i['date_time'].strftime('%Y-%m-%d %H:%M:%S'),
        })

    context = {
        'incidents_json': json.dumps(incidents)  # Serialize to safe JSON
    }
    return render(request, 'map_incident.html', context)