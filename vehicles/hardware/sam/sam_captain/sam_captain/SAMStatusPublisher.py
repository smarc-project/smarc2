
class SAMStatusPublisher:
    """Publish status topics for the SAM Captain node."""
    def __init__(self, cap: 'SAMCaptain') -> None:
        self._cap = cap

        # TODO: create publishers

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"

    def status_str(self) -> str:
        """Create a status string for SAM status data."""
        battery = (
            f"{self._battery_percent * 100:.1f}%"
            if self._battery_percent is not None
            else "N/A"
        )
        return (
            "Status:\n"
            f"  Battery Percent: {battery}\n"
        )

    def nav_status_str(self) -> str:
        """Create a status string for navigation data."""
        position = "N/A"
        if self._latest_latlon is not None:
            position = (
                f"{self._latest_latlon.latitude:.6f}, "
                f"{self._latest_latlon.longitude:.6f}"
            )

        utm_frame = self.utm_frame or "N/A"
        depth = self._value_or_na(self._latest_depth, "m")
        altitude = self._value_or_na(self._latest_altitude, "m")
        heading = self._value_or_na(self._latest_heading, "deg")
        course = self._value_or_na(self._latest_course, "deg")
        speed = self._value_or_na(self._latest_speed, "m/s")

        return (
            "Navigation:\n"
            f"  UTM Frame: {utm_frame}\n"
            f"  Position: {position}\n"
            f"  Depth: {depth}\n"
            f"  Altitude: {altitude}\n"
            f"  Heading: {heading}\n"
            f"  Course: {course}\n"
            f"  Speed: {speed}\n"
        )
