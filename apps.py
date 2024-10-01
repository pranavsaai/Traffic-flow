from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import requests
from twilio.rest import Client

app = Flask(__name__)
# CORS(app, resources={r"/":{"origins": ""}})

# API Keys (Consider using environment variables for security)
google_maps_api_key = 'AIzaSyAAbimNTW1vO_0KH8BKKlCIeU9cOSc0cg8'
weather_api_key = 'd43894f3d1447287554f7dd5ceab9537'
twilio_sid = 'SKf105fbc5af80a3e83670cc7fb20a1da7'
twilio_auth_token = '5f69a8138367739b65541048cd6009a8'
twilio_phone_number = '+14158779906'
user_phone_number = '+917981922455'

# Function to get latitude and longitude using Google Maps Geocoding API
def get_lat_lon(location):
    geocode_url = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={google_maps_api_key}'
    geocode_response = requests.get(geocode_url)
    geocode_data = geocode_response.json()

    if geocode_response.status_code == 200 and geocode_data['status'] == 'OK':
        lat = geocode_data['results'][0]['geometry']['location']['lat']
        lon = geocode_data['results'][0]['geometry']['location']['lng']
        return lat, lon
    else:
        return None, None

@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def index():
    distance = None
    duration = None
    weather_condition = None
    temperature = None
    alert_message = None
    end_address = None
    print("server called")

    if request.method == 'POST':
        print("post server called")
        origin = request.form.get('origin')
        destination = request.form.get('destination')
        print("origin = ",origin," destination = ", destination, request)
        
        origin_lat, origin_lon = get_lat_lon(origin)
        destination_lat, destination_lon = get_lat_lon(destination)

        if origin_lat is not None and destination_lat is not None:
            maps_url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origin_lat},{origin_lon}&destination={destination_lat},{destination_lon}&key={google_maps_api_key}'
            maps_response = requests.get(maps_url)
            routes = maps_response.json()
            print(routes)

            if maps_response.status_code == 200 and routes['status'] == 'OK':
                route = routes['routes'][0]['legs'][0]
                distance = route['distance']['text']
                duration = route['duration']['text']
                end_address = route['end_address']

                weather_url = f'https://api.openweathermap.org/data/2.5/weather?lat={destination_lat}&lon={destination_lon}&appid={weather_api_key}&units=metric'
                weather_response = requests.get(weather_url)
                weather_data = weather_response.json()
                print(weather_data)

                if weather_response.status_code == 200:
                    weather_condition = weather_data['weather'][0]['description']
                    temperature = weather_data['main']['temp']

                    if 'rain' in weather_condition or 'storm' in weather_condition or 'snow' in weather_condition:
                        alert_message = (f"Alert! Weather at {end_address} is {weather_condition} with a temperature of {temperature}°C. "
                                         f"Consider an alternative route to avoid delays or hazards.")

                        # Twilio API - Send Notification
                        client = Client(twilio_sid, twilio_auth_token)
                        message = client.messages.create(
                            body=alert_message,
                            from_=twilio_phone_number,
                            to=user_phone_number
                        )
                        alert_message = f"Notification sent! Message SID: {message.sid}"
                    
    return render_template('index.html', distance=distance, duration=duration, weather_condition=weather_condition, temperature=temperature, alert_message=alert_message, end_address=end_address)

if __name__ == '__main__':
    app.run(debug=True, port=8080)