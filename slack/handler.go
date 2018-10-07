package function

import (
	"net/http"
	"os"
)

// Handle a request with your middleware
func Handle(w http.ResponseWriter, r *http.Request) {
	if urlVal, ok := os.LookupEnv("slack_url"); ok && len(urlVal) > 0 {

		w.Write([]byte(`<html>
<head>
</head>
<body>
		<a href="` + urlVal + `">Redirecting.. click here.</a>
</body>
<script>
	setTimeout(function() {
		document.href = "` + urlVal + `";
	}, 100);
</script
</html>
)`))

	} else {
		http.Error(w, "Unable to find slack_url variable", http.StatusInternalServerError)

	}
}
