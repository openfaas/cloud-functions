package function

import (
	"net/http"
	"os"
)

// Handle a request with your middleware
func Handle(w http.ResponseWriter, r *http.Request) {
	if urlVal, ok := os.LookupEnv("gist_url"); ok && len(urlVal) > 0 {

		http.Redirect(w, r, urlVal, http.StatusPermanentRedirect)

	} else {
		http.Error(w, "Unable to find gist_url variable", http.StatusInternalServerError)

	}
}
