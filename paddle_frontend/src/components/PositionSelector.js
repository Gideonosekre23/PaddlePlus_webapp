import React, { useState, useEffect } from "react";
import { GoogleMap, Marker, useJsApiLoader } from "@react-google-maps/api";

const mapContainerStyle = {
  width: "100%",
  height: "300px",
};

const PositionSelector = ({ latitude, longitude, onLocationSelect }) => {
    const googleMapsApiKey = process.env.REACT_APP_GOOGLE_MAPS_KEY;
    const { isLoaded, loadError } = useJsApiLoader({
        id: "google-map-script",
        googleMapsApiKey,
        libraries: ["geometry", "drawing"],
    });

    const [mapCenter, setMapCenter] = useState({
        lat: parseFloat(latitude),
        lng: parseFloat(longitude),
    });

    const [markerPosition, setMarkerPosition] = useState(mapCenter);

    useEffect(() => {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
                setMarkerPosition(userLocation);
                setMapCenter(userLocation); // Only set center once at the beginning
                onLocationSelect(userLocation.lat, userLocation.lng);
            },
            () => {
                console.error("Geolocation permission denied. Using default location.");
            }
        );
    }, []); // Only runs once

    if (loadError) return <p>Error loading maps</p>;
    if (!isLoaded) return <p>Loading Maps...</p>;

    return (
        <GoogleMap
            mapContainerStyle={mapContainerStyle}
            zoom={12}
            center={mapCenter} // No longer tied to marker position changes
            onClick={(event) => {
                const newLat = event.latLng.lat();
                const newLng = event.latLng.lng();
                setMarkerPosition({ lat: newLat, lng: newLng });
                onLocationSelect(newLat, newLng);
            }}
        >
            <Marker position={markerPosition} draggable />
        </GoogleMap>
    );
};

export default PositionSelector;
