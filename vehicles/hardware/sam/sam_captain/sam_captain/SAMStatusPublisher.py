# TODO: imports
from sam_captain.sam_captain import SAMCaptain

class SAMStatusPublisher:
    """Publish status topics for the SAM Captain node."""
    def __init__(self, cap: 'SAMCaptain') -> None:
        self.cap = cap

        # TODO: create publishers

    def _value_or_na(self, value: float | None, unit: str) -> str:
        """Return a formatted string for a value or 'N/A' if None."""
        return f"{value:.2f} {unit}" if value is not None else "N/A"

    def status_str(self) -> str:
        """Create a status string for SAM status and nav data."""
        battery = (
            f"{self.cap.battery_percent * 100:.1f}%"
            if self.cap.battery_percent is not None
            else "N/A"
        )
        position = "N/A"
        if self.cap.latest_latlon is not None:
            position = (
                f"{self.cap.latest_latlon.latitude:.6f}, "
                f"{self.cap.latest_latlon.longitude:.6f}"
            )

        utm_frame = self.cap.utm_frame or "N/A"
        depth = self._value_or_na(self.cap.latest_depth, "m")
        altitude = self._value_or_na(self.cap.latest_altitude, "m")
        heading = self._value_or_na(self.cap.latest_heading, "deg")
        course = self._value_or_na(self.cap.latest_course, "deg")
        speed = self._value_or_na(self.cap.latest_speed, "m/s")

        return (
            "Status:\n"
            f"  Battery Percent: {battery}\n"
            "Navigation:\n"
            f"  UTM Frame: {utm_frame}\n"
            f"  Position: {position}\n"
            f"  Depth: {depth}\n"
            f"  Altitude: {altitude}\n"
            f"  Heading: {heading}\n"
            f"  Course: {course}\n"
            f"  Speed: {speed}\n"
        )

    # TODO: add publish status