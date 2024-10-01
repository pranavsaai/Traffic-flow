const express = require('express');
const axios = require('axios');
const cors = require('cors');
const twilio = require('twilio');

// API Keys (Consider using environment variables for security)
// API Keys (Use environment variables in production)
const googleMapsApiKey = 'AIzaSyAAbimNTW1vO_0KH8BKKlCIeU9cOSc0cg8';
const weatherApiKey = 'd43894f3d1447287554f7dd5ceab9537';
const twilioSid = 'ACSKf105fbc5af80a3e83670cc7fb20a1da7';
const twilioAuthToken = '5f69a8138367739b65541048cd6009a8';
const twilioPhoneNumber = '+14158779906';
const userPhoneNumber = '+917981922455';
const app = express();
app.use(cors())
app.use(express.json());

// Function to get latitude and longitude using Google Maps Geocoding API
async function getLatLon(location) {
    const geocodeUrl = `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(location)}&key=${googleMapsApiKey}`;
    try {
        const response = await axios.get(geocodeUrl);
        const data = response.data;

        if (response.status === 200 && data.status === 'OK') {
            const lat = data.results[0].geometry.location.lat;
            const lon = data.results[0].geometry.location.lng;
            return [lat, lon];
        } else {
            console.error(`Error fetching geolocation for ${location}: ${data.status}`);
            return [null, null];
        }
    } catch (error) {
        console.error("Error fetching geolocation:", error);
        return [null, null];
    }
}

// Function to get route information between two locations
async function getRouteInfo(origin, destination) {
    const [originLat, originLon] = await getLatLon(origin);
    const [destinationLat, destinationLon] = await getLatLon(destination);

    if (originLat !== null && destinationLat !== null) {
        const mapsUrl = `https://maps.googleapis.com/maps/api/directions/json?origin=${originLat},${originLon}&destination=${destinationLat},${destinationLon}&key=${googleMapsApiKey}`;

        try {
            const response = await axios.get(mapsUrl);
            const routes = response.data;

            if (response.status === 200 && routes.status === 'OK') {
                const route = routes.routes[0].legs[0];
                const distance = route.distance.text;
                const duration = route.duration.text;
                const endAddress = route.end_address;

                console.log(`Distance: ${distance}, Duration: ${duration}, Destination Address: ${endAddress}`);
                return [destinationLat, destinationLon, endAddress, distance, duration];
            } else {
                console.error("Error fetching route information.");
                return [null, null, null, null, null];
            }
        } catch (error) {
            console.error("Error fetching route information:", error);
            return [null, null, null, null, null];
        }
    } else {
        return [null, null, null, null, null];
    }
}

// Function to get weather information
async function getWeatherInfo(lat, lon) {
    const weatherUrl = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&appid=${weatherApiKey}&units=metric`;
    try {
        const response = await axios.get(weatherUrl);
        const weatherData = response.data;

        if (response.status === 200) {
            const weatherCondition = weatherData.weather[0].description;
            const temperature = weatherData.main.temp;
            console.log(`Weather Condition: ${weatherCondition}, Temperature: ${temperature}°C`);
            return [weatherCondition, temperature];
        } else {
            console.error("Error fetching weather information.");
            return [null, null];
        }
    } catch (error) {
        console.error("Error fetching weather information:", error);
        return [null, null];
    }
}

// Function to send an alert via Twilio
async function sendAlert(message) {
    const client = twilio(twilioSid, twilioAuthToken);
    try {
        const twilioMessage = await client.messages.create({
            body: message,
            from: twilioPhoneNumber,
            to: userPhoneNumber
        });
        console.log(`Notification sent! Message SID: ${twilioMessage.sid}`);
    } catch (error) {
        console.error("Error sending alert:", error);
    }
}

// Endpoint to handle route and weather requests
app.post('/', async (req, res) => {
    const { origin, destination } = req.body;

    const [lat, lon, address, distance, duration] = await getRouteInfo(origin, destination);

    if (lat !== null) {
        const [weatherCondition, temperature] = await getWeatherInfo(lat, lon);

        if (weatherCondition && (weatherCondition.includes('rain') || weatherCondition.includes('storm') || weatherCondition.includes('snow'))) {
            const alertMessage = `Alert! Weather at ${address} is ${weatherCondition} with a temperature of ${temperature}°C. Consider an alternative route to avoid delays or hazards.`;
            await sendAlert(alertMessage);
            res.json({ success: true, distance, duration, address, weather_condition: weatherCondition, temperature, alert_message: alertMessage });
        } else {
            res.json({ success: true, distance, duration, address, weather_condition: weatherCondition, temperature, alert_message: null });
        }
    } else {
        res.json({ success: false, message: "Failed to fetch route or weather information." });
    }
});

// Start the Express server
const PORT = 8080;
app.listen(PORT, () => {
    console.log(`Server is running on http://127.0.0.1:${PORT}`);
});

