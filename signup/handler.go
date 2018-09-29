package function

import (
	"net/http"
	"os"
)

func Handle(w http.ResponseWriter, r *http.Request) {
	gistURL := os.Getenv("gist_url")
	http.Redirect(w, r, gistURL, http.StatusTemporaryRedirect)
}
