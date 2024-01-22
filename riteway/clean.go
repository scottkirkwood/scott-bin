package main

import (
	"flag"
	"fmt"
	"io/ioutil"
	"regexp"
	"strings"
)

var (
	fname = flag.String("f", "beer.html", "Filename")
)

var (
	rxLiProduct   = regexp.MustCompile(`(?ms)<li class=[^>]*js-product-item[^>]+>(.*?)</li>`)
	rxSku         = regexp.MustCompile(`class="product__sku">([^<]+)</span>`)
	rxPrice       = regexp.MustCompile(`data-price-amount="([0-9.]+)"`)
	rxProductName = regexp.MustCompile(`(?ms)product-item-name">[^>]*>\s*(.*?)\s*</a>`)
	rxWhiteSpace  = regexp.MustCompile(`\s+`)
	rxProductLink = regexp.MustCompile(`(?ms)"product-item-link".*?https://www.riteway.vg/([^"]+).html"`)
	rxPackSize    = regexp.MustCompile(`(?ms)<div class="pack-size__container">(.*?)</div>`)
	rxProductId   = regexp.MustCompile(`"product-id-(\d+)"`)
)

func parseProduct(txt string) error {
	sku := findOrEmpty(rxSku, txt)
	id := findOrEmpty(rxProductId, txt)
	name := cleanWhitespace(findOrEmpty(rxProductName, txt))
	packSize := cleanWhitespace(findOrEmpty(rxPackSize, txt))
	price := findOrEmpty(rxPrice, txt)
	link := findOrEmpty(rxProductLink, txt)
	fmt.Printf("sku: %s, id: %s, name: %q, pack: %q, price: %s, link: %q\n",
		sku, id, name, packSize, price, link)
	return nil
}

func cleanWhitespace(txt string) string {
	return rxWhiteSpace.ReplaceAllString(strings.TrimSpace(txt), " ")
}

func findOrEmpty(rx *regexp.Regexp, txt string) string {
	grab := rx.FindAllStringSubmatch(txt, 1)
	if len(grab) > 0 {
		return grab[0][1]
	}
	return ""
}

func parsePage(txt string) error {
	for _, product := range rxLiProduct.FindAllStringSubmatch(txt, -1) {
		parseProduct(product[1])
	}
	return nil
}

func doFile(fname string) error {
	body, err := ioutil.ReadFile(fname)
	if err != nil {
		return err
	}
	txt := string(body)
	return parsePage(txt)
}

func main() {
	flag.Parse()
	err := doFile(*fname)
	if err != nil {
		fmt.Printf("Err: %v\n", err)
		return
	}
}
