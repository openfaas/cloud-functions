package function

import (
	"fmt"
	"io/ioutil"
)

// Handle a serverless request
func Handle(req []byte) string {
	s3, err := ioutil.ReadFile("/var/openfaas/secrets/s3")
	if err != nil {
		return err.Error()
	}

	return fmt.Sprintf("Secret value: %s", s3)
}
