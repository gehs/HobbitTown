int getHour() {
	struct tm timeinfo;
	if (!getLocalTime(&timeinfo)) {
		// Fallback to daytime behavior if time is not yet synchronized.
		return 12;
	}
	return timeinfo.tm_hour;
}
