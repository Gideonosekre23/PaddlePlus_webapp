import React, { useState, useEffect, useCallback } from "react";
import {
  GoogleMap,
  Marker,
  InfoWindow,
  useJsApiLoader
} from "@react-google-maps/api";
import {
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress
} from "@mui/material";
import NavBar from "../components/NavBar";
import { io } from 'socket.io-client';
import { getNearbyBikes, updateRiderLocation, requestRide } from "../utils/api"; // <-- Import updateRiderLocation here
import bikeIcon from "../assets/bike-transparent.jpg";
import "../styles/HomePageRider.css";
import { createNgrokSocketUrlAlt } from "../utils/utils";

const libraries = ["geometry", "drawing"];

const HomePageRider = () => {
  const googleMapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_KEY;

  const [userLocation, setUserLocation] = useState(null);
  const [error, setError] = useState(null);
  const [bikes, setBikes] = useState([]);
  const [selectedBike, setSelectedBike] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const [isChangeLocationActive, setIsChangeLocationActive] = useState(false);
  const [tempLocation, setTempLocation] = useState(null);

  const [webSocketUrl, setWebSocketUrl] = useState(null);
  const [socket, setSocket] = useState(null);

  const { isLoaded, loadError } = useJsApiLoader({
    id: "google-map-script",
    googleMapsApiKey,
    libraries: libraries,
  });

  useEffect(() => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
        setUserLocation({ lat: latitude, lng: longitude });
        setError(null);
      },
      (err) => {
        console.error("Geolocation error:", err.message);
        setError(err.message);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0,
      }
    );

    setWebSocketUrl(createNgrokSocketUrlAlt(localStorage.getItem("ws_url")));

    const token = localStorage.getItem('access');
    const rawWsUrl = createNgrokSocketUrlAlt(localStorage.getItem("ws_url"));

    const proxyUrl = `ws://localhost:8080?token=${token}&wsUrl=${rawWsUrl}`;
    const ws = new WebSocket(proxyUrl);

    ws.onopen = () => {
      console.log('Connected to the proxy');
    };

    ws.onmessage = (event) => {
      console.log('Message from proxy (ultimately from real server):', event.data);
    };

    ws.onerror = (err) => {
      console.error('Proxy WebSocket error:', err);
    };

    ws.onclose = () => {
      console.log('Proxy WebSocket closed.');
    };

    // Cleanup on unmount
    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    if (userLocation) {
      const fetchBikes = async () => {
        try {
          console.log(userLocation);
          const nearbyBikes = await getNearbyBikes({
            latitude:userLocation.lat,
            longitude: userLocation.lng,
          });
          console.log("Fetched Bikes:", nearbyBikes);
          setBikes(nearbyBikes);
        } catch (error) {
          console.error("Failed to fetch bikes:", error.message);
        }
      };

      fetchBikes();
    }
  }, [userLocation]);

  const handleRequest = async () => {
    setIsLoading(true);

    const formData = {
      pickup_latitude: userLocation.lat,
      pickup_longitude: userLocation.lng,
      destination_latitude: 45.763645,
      destination_longitude: 21.253291,
      payment_type: "cash"
    }

    try {
      const data = await requestRide(formData);
      console.log(data);
    } catch (error) {
      console.log("das")
    } finally {
      setTimeout(() => {
        setIsLoading(false);
      }, 2000);
    }
  };

  const handleChangeLocationClick = () => {
    setIsChangeLocationActive(true);
    setTempLocation(userLocation);
  };

  const handleMapClick = useCallback((event) => {
    if (isChangeLocationActive) {
      const lat = event.latLng.lat();
      const lng = event.latLng.lng();
      setTempLocation({ lat, lng });
    }
  }, [isChangeLocationActive]);

  const handleConfirmLocation = async () => {
    if (tempLocation) {
      setUserLocation(tempLocation);

      try {
        // await updateRiderLocation({
        //   latitude: tempLocation.lat,
        //   longitude: tempLocation.lng,
        // });
        console.log("Rider location updated successfully.");
      } catch (err) {
        console.error("Failed to update rider location:", err);
      }

      setIsChangeLocationActive(false);
    }
  };

  const handleCancelLocation = () => {
    setTempLocation(null);
    setIsChangeLocationActive(false);
  };

  if (loadError) {
    return <div className="error-message">Error loading Google Maps API</div>;
  }

  return (
    <div className="main-page">
      {isLoading && (
        <div className="loading-overlay">
          <CircularProgress />
          <Typography variant="body1" sx={{ mt: 2, color: "white" }}>
            Requesting a ride... Please wait.
          </Typography>
        </div>
      )}

      <NavBar />

      <div className="map-container">
        {/* Request a ride button */}
        <Button
          className="req-btn"
          onClick={handleRequest}
          variant="contained"
          color="primary"
          size="large"
        >
          Request a ride
        </Button>

        <div
          className="change-loc-div"
        >
          {!isChangeLocationActive ? (
            <Button
              variant="outlined"
              color="primary"
              onClick={handleChangeLocationClick}
            >
              Change Location
            </Button>
          ) : (
            <>
              <Button
                variant="contained"
                color="success"
                onClick={handleConfirmLocation}
                style={{ marginRight: "8px" }}
              >
                Confirm
              </Button>
              <Button variant="contained" color="error" onClick={handleCancelLocation}>
                Cancel
              </Button>
            </>
          )}
        </div>

        {error ? (
          <div className="error-message">
            <p>We couldn't access your location.</p>
            <p>
              Please enable location services in your browser settings or allow
              location access when prompted.
            </p>
          </div>
        ) : !isLoaded ? (
          <div className="loading-message">Loading Google Maps...</div>
        ) : (
          <GoogleMap
            onClick={handleMapClick}
            center={userLocation || { lat: 51.505, lng: -0.09 }} // Default if userLocation is null
            zoom={13}
            mapContainerStyle={{ height: "100%", width: "100%" }}
            options={{
              streetViewControl: false,
              fullscreenControl: false,
            }}
          >
            {/* Display user marker (or temp marker if isChangeLocationActive) */}
            {(tempLocation && isChangeLocationActive) ? (
              <Marker
                position={tempLocation}
                icon={{
                  url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
                  scaledSize: new window.google.maps.Size(40, 40),
                }}
              />
            ) : userLocation && (
              <Marker
                position={userLocation}
                icon={{
                  url: "https://maps.google.com/mapfiles/ms/icons/blue-dot.png",
                  scaledSize: new window.google.maps.Size(40, 40),
                }}
              />
            )}

            {selectedBike && (
              <InfoWindow
                position={{
                  lat: selectedBike.location.latitude + 0.0001, // Slight offset to prevent overlap
                  lng: selectedBike.location.longitude,
                }}
                onCloseClick={() => setSelectedBike(null)}
              >
                <Card sx={{ minWidth: 250, maxWidth: 320 }}>
                  <CardContent>
                    <Typography variant="h6" sx={{ fontWeight: "bold" }}>
                      {selectedBike.bike_name}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Brand:</strong> {selectedBike.brand}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Model:</strong> {selectedBike.model}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Distance:</strong> {selectedBike.distance} km
                    </Typography>
                    <Typography variant="body2">
                      <strong>Battery Level:</strong>{" "}
                      <span
                        style={{
                          color:
                            selectedBike.battery_level > 80
                              ? "green"
                              : selectedBike.battery_level > 50
                              ? "orange"
                              : "red",
                          fontWeight: "bold",
                        }}
                      >
                        {selectedBike.battery_level}%
                      </span>
                    </Typography>
                  </CardContent>
                </Card>
              </InfoWindow>
            )}

            {bikes &&
              bikes.map((bike) => (
                <Marker
                  key={bike.id}
                  position={{
                    lat: bike.location.latitude,
                    lng: bike.location.longitude,
                  }}
                  icon={{
                    url: bikeIcon, // Path to custom marker
                    scaledSize: new window.google.maps.Size(55, 40),
                    origin: new window.google.maps.Point(0, 0),
                    anchor: new window.google.maps.Point(25, 25),
                  }}
                  zIndex={9999}
                  title={`${bike.bike_name} - ${bike.brand} ${bike.model}`}
                  onClick={() => setSelectedBike(bike)}
                />
              ))}
          </GoogleMap>
        )}
      </div>
    </div>
  );
};

export default HomePageRider;
