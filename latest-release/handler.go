package function

import (
	"fmt"
	"net/http"
)

// Handle a serverless request
func Handle(req []byte) string {

	urls := map[string]string{
		"faas-cli":   "https://github.com/openfaas/faas-cli/releases/latest",
		"faas":       "https://github.com/openfaas/faas/releases/latest",
		"faas-netes": "https://github.com/openfaas/faas-netes/releases/latest",
		"faas-swarm": "https://github.com/openfaas/faas-swarm/releases/latest",
	}

	c := http.Client{}
	c.CheckRedirect = func(req *http.Request, via []*http.Request) error {
		return http.ErrUseLastResponse
	}
	out := `<html>
<body>
	<h3>OpenFaaS - latest releases</h3>
	<ul>
`
	for k, v := range urls {
		req, _ := http.NewRequest(http.MethodGet, v, nil)
		res, resErr := c.Do(req)
		if resErr == nil {
			if res.Body != nil {
				defer res.Body.Close()
				location := res.Header.Get("Location")
				out = out + fmt.Sprintf(`<li>%s - <a href="`+location+`">%s</a></li>
`, k, location)
			}
		}
	}

	out = out + "</body></html><ul>"
	return out
}
