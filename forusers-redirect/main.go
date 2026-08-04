package main

import (
	"log"
	"net/http"
)

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		target := "https://www.forusers.com" + r.URL.Path
		if r.URL.RawQuery != "" {
			target += "?" + r.URL.RawQuery
		}
		log.Printf("Redirecting %s to %s", r.URL.Path, target)
		http.Redirect(w, r, target, http.StatusTemporaryRedirect)
	})
	log.Println("Starting forusers redirect service on :80...")
	log.Fatal(http.ListenAndServe(":80", nil))
}
