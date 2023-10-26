from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from .forms import PolTekstowe
from .models import Contestant, SwimmingTime
from datetime import datetime


def index(request: HttpRequest) -> HttpResponse:
    """Creating a form"""
    if request.method == "POST":
        form = PolTekstowe(request.POST)
    else:
        form = PolTekstowe()

    def qr_elements(code: str) -> tuple:
        """Split elements of qr code to id, data, command"""

        elements = code.split("_")

        if len(elements) == 2:
            return elements[0], elements[1], None
        else:
            return elements[0], elements[1], elements[2]

    def contestant_from_database():
        """Returns the last added player, only if he/she is added to database and not swimming"""
        contestant = Contestant.objects.raw \
            ("SELECT * FROM time_measurement_contestant "
             "ORDER BY ID DESC LIMIT 1")

        if len(list(contestant)) == 0:
            return None

        number_cont_sw = SwimmingTime.objects.filter(contestant=contestant[0]).count()

        if number_cont_sw != 0:
            return None
        # różny od zera to wystartowany zawodnik, 0 to niewystartowany zawodnik

        return contestant[0]  # ostatnio dodany zawodnik, niewystartowany

    def handle_tor_command(command: str, track: int):
        """START: creating obj. Swimming time
        STOP: Extract an obj. SwimmingTime and set time_stop to now
        and Errors handling"""

        if command == "START":

            contestant = contestant_from_database()

            if contestant is None:
                raise ValueError("Brak zawodnika na torze, zarejestruj zawodnika")

            occupied_track = SwimmingTime.objects.filter(swimming_track=track,
                                                         time_stop__isnull=True).count()

            if occupied_track != 0:
                raise ValueError("Tor jest zajęty")

            SwimmingTime.objects.create(swimming_track=track,
                                        contestant=contestant,
                                        time_start=datetime.now())

        elif command == "STOP":
            try:
                swimming_time = SwimmingTime.objects.get(swimming_track=track,
                                                         time_stop__isnull=True)
            except SwimmingTime.DoesNotExist:
                raise ValueError("Na torze nie ma zawodnika")
            swimming_time.time_stop = datetime.now()
            swimming_time.save()

    def handle_cancel_command(command):
        """Escape code support - deleting an incorrectly scanned player from the database"""
        contestant = contestant_from_database()  # Zwraca zawodnika, który był zeskanowany, a nie płynie
        if contestant:
            contestant.delete()

    def handle_qr_code(id_number: str, data: str):
        """Appropriate action depending on whether the contestant or track or escape code
        was scanned"""

        if id_number == "ZAW":
            name, surname = data.split(".")
            Contestant.objects.create(name=name, surname=surname)
        elif id_number == "TOR":
            track = int(data)
            handle_tor_command(qr_command, track)
        elif id_number == "cnc":
            handle_cancel_command(qr_command)

    if form.is_valid():
        qr_id, qr_data, qr_command = qr_elements(form.cleaned_data['code'])

        try:
            handle_qr_code(qr_id, qr_data)
        except ValueError as e:
            form.add_error("code", e)

    tory = {}
    for i in range(5):
        try:
            tory[i + 1] = SwimmingTime.objects.get(swimming_track=(i + 1), time_stop__isnull=True)
        except SwimmingTime.DoesNotExist:
            tory[i + 1] = ""

    return render(request, 'index.html', {'form': form, 'tory': tory})


def stats(request):
    swimming_times = SwimmingTime.objects.all()
    return render(request, 'stats.html', {'stats': swimming_times})
