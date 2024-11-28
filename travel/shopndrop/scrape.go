package main

import (
	"flag"
	"fmt"
	"regexp"
)

var fname = flag.String("f", "home.html", "Filename")

var rxLiProduct = regexp.MustCompile(`(?ms)<li class=[^>]*js-product-item[^>]+>(.*?)</li>`)

// Page contains information about one page to download
type Page struct {
	PageName string
	Link     string
}

func main() {
	flag.Parse()
	fmt.Printf("Parsing %s\n", *fname)
}
