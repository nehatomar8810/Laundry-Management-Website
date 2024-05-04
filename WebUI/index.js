
  function getLocation() {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(showPosition);
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  }
  
  function showPosition(position) {
    const lat = position.coords.latitude;
    const lng = position.coords.longitude;
  
    // Now you have the latitude and longitude, you can use it to search for nearby laundry services
    searchNearbyLaundryServices(lat, lng);
  }
  
  getLocation();