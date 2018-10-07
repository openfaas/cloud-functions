package function

import (
	"net/http"
	"os"
)

// Handle a request with your middleware
func Handle(w http.ResponseWriter, r *http.Request) {
	gistURL := os.Getenv("webpage_url")
	http.Redirect(w, r, gistURL, http.StatusPermanentRedirect)
}
