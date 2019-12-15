package function

import (
	"io"
	"net/http"
)

func Handle(w http.ResponseWriter, r *http.Request) {

	if r.Body != nil {
		defer r.Body.Close()
	}

	res, err := http.Get("https://api.ipify.org")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if res.Body != nil {
		defer res.Body.Close()
		io.Copy(w, res.Body)
	}
}
